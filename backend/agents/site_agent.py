"""
Site Agent: Recommends trial sites based on FEASIBILITY and patient geography.

Responsibilities:
- Receives scored patient matches with locations
- Receives trial eligibility criteria with medical codes
- Scores sites on 4 dimensions:
  1. CAPABILITY: Can site perform required LOINC lab tests?
  2. EXPERIENCE: Has site run trials in this ICD-10 chapter?
  3. POPULATION: Does site's EHR have patients with required codes?
  4. CAPACITY: Does site have bandwidth for another trial?
- Combines feasibility scores with geographic patient clustering
- Returns optimal trial sites with detailed feasibility breakdowns

This addresses the advisor's requirement for "trial and site feasibility
based on controlled terminology sets" using Epic EHR standards.
"""

from uagents import Agent, Context
import logging
import time
import numpy as np
from collections import defaultdict
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.models import SiteRequest, SiteResponse, AgentStatus
from agents.config import AgentConfig, AgentRegistry
from site_feasibility_scorer import SiteFeasibilityScorer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

config = AgentConfig.get_agent_config("site")
agent = Agent(**config)

agent_state = {
    "requests_processed": 0,
    "start_time": time.time(),
    "feasibility_scorer": None
}


@agent.on_event("startup")
async def startup(ctx: Context):
    logger.info(f"✓ Site Agent started: {agent.address}")
    AgentRegistry.register("site", agent.address)

    # Initialize feasibility scorer
    agent_state["feasibility_scorer"] = SiteFeasibilityScorer()
    logger.info(f"  ✓ Loaded {len(agent_state['feasibility_scorer'].sites)} sites for feasibility scoring")


@agent.on_message(model=SiteRequest)
async def handle_site_request(ctx: Context, sender: str, msg: SiteRequest):
    """Recommend trial sites based on feasibility AND patient geography"""
    logger.info(f"  → Site Agent recommending sites for: {msg.trial_id}")

    try:
        matches = msg.matches
        max_sites = msg.max_sites
        eligibility_criteria = msg.eligibility_criteria
        target_enrollment = msg.target_enrollment

        # Get feasibility scorer
        scorer = agent_state["feasibility_scorer"]

        # Rank sites by feasibility
        feasibility_rankings = scorer.rank_sites(
            trial_criteria=eligibility_criteria,
            target_enrollment=target_enrollment,
            top_n=max_sites * 2  # Get extra for geographic filtering
        )

        # Assign patients to sites based on both feasibility and geography
        recommendations = assign_patients_to_sites(
            feasibility_rankings,
            matches,
            max_sites
        )

        # Calculate coverage
        total_patients = len(matches)
        covered_patients = sum(site["patient_count"] for site in recommendations)
        coverage = (covered_patients / total_patients * 100) if total_patients > 0 else 0

        agent_state["requests_processed"] += 1

        logger.info(f"  ✓ Recommended {len(recommendations)} sites covering {coverage:.0f}% of patients")
        logger.info(f"    Top site: {recommendations[0]['site_name']} "
                   f"(feasibility: {recommendations[0]['feasibility_score']:.3f})")

        await ctx.send(sender, SiteResponse(
            trial_id=msg.trial_id,
            recommended_sites=recommendations,
            total_sites=len(recommendations),
            coverage_percentage=round(coverage, 1),
            geographic_clusters={
                "total_patients": total_patients,
                "covered_patients": covered_patients,
                "feasibility_based": True
            }
        ))

    except Exception as e:
        logger.error(f"Error in site recommendation: {e}")
        import traceback
        traceback.print_exc()
        await ctx.send(sender, SiteResponse(
            trial_id=msg.trial_id,
            recommended_sites=[],
            total_sites=0,
            coverage_percentage=0.0,
            geographic_clusters={"error": str(e)}
        ))


def assign_patients_to_sites(feasibility_rankings: list, matches: list, max_sites: int) -> list:
    """
    Assign patients to sites based on both feasibility and geographic proximity.

    Strategy:
    1. Start with top-feasibility sites
    2. For each patient, calculate distance to each feasible site
    3. Assign patient to nearest feasible site
    4. Filter out sites with too few patients
    5. Return top N sites by combined score (feasibility + patient count)
    """
    if not feasibility_rankings or not matches:
        return []

    # Extract patient locations
    patient_locations = []
    for match in matches:
        loc = match.get("location", {})
        lat = loc.get("lat", 0.0)
        lon = loc.get("lon", 0.0)
        patient_id = match.get("patient_id")

        if lat != 0.0 and lon != 0.0:
            patient_locations.append({
                "patient_id": patient_id,
                "lat": lat,
                "lon": lon,
                "match_score": match.get("overall_score", 0.0)
            })

    if not patient_locations:
        # No patient locations, return sites ranked by feasibility only
        return format_site_recommendations(feasibility_rankings[:max_sites], {})

    # Assign each patient to nearest feasible site
    site_assignments = defaultdict(lambda: {"patient_ids": [], "distances": []})

    for patient in patient_locations:
        # Find nearest site from feasibility-ranked sites
        min_distance = float('inf')
        nearest_site = None

        for site_score in feasibility_rankings:
            site_loc = site_score.get("location", {})
            site_lat = site_loc.get("lat", 0.0)
            site_lon = site_loc.get("lon", 0.0)

            if site_lat == 0.0 and site_lon == 0.0:
                continue

            distance = haversine_distance(patient["lat"], patient["lon"], site_lat, site_lon)

            if distance < min_distance:
                min_distance = distance
                nearest_site = site_score["site_id"]

        if nearest_site:
            site_assignments[nearest_site]["patient_ids"].append(patient["patient_id"])
            site_assignments[nearest_site]["distances"].append(min_distance)

    # Format recommendations
    recommendations = format_site_recommendations(feasibility_rankings, site_assignments)

    # Calculate combined priority score: 60% feasibility + 40% patient count
    for rec in recommendations:
        patient_count_score = min(rec["patient_count"] / 100.0, 1.0)
        combined_score = (
            rec["feasibility_score"] * 0.6 +
            patient_count_score * 0.4
        )
        rec["priority_score"] = round(combined_score, 3)

    # Sort by combined priority score
    recommendations.sort(key=lambda x: x["priority_score"], reverse=True)

    # Return top N sites
    return recommendations[:max_sites]


def format_site_recommendations(feasibility_rankings: list, site_assignments: dict) -> list:
    """
    Format site recommendations with feasibility scores and patient assignments.

    Args:
        feasibility_rankings: List of site feasibility scores from scorer
        site_assignments: Dict of site_id -> {patient_ids: [...], distances: [...]}

    Returns:
        List of formatted site recommendations
    """
    recommendations = []

    for site_score in feasibility_rankings:
        site_id = site_score["site_id"]
        assignment = site_assignments.get(site_id, {"patient_ids": [], "distances": []})

        patient_ids = assignment["patient_ids"]
        distances = assignment["distances"]

        # Calculate average distance
        avg_distance = np.mean(distances) if distances else 0.0

        # Get capacity info from feasibility score
        capacity_info = site_score.get("capacity", {})

        recommendation = {
            "site_name": site_score["site_name"],
            "location": site_score["location"],
            "patient_count": len(patient_ids),
            "average_distance": round(avg_distance, 1),
            "capacity": capacity_info.get("max_trials", 50),
            "current_trials": capacity_info.get("current_trials", 0),
            "priority_score": site_score["overall_score"],  # Will be updated later

            # Feasibility scores
            "feasibility_score": site_score["overall_score"],
            "capability_score": site_score["capability"]["score"],
            "experience_score": site_score["experience"]["score"],
            "population_score": site_score["population"]["score"],
            "capacity_score": site_score["capacity"]["score"],

            "patient_ids": patient_ids[:100]  # Limit for response size
        }

        recommendations.append(recommendation)

    return recommendations


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two coordinates in km"""
    from math import radians, sin, cos, sqrt, atan2

    R = 6371  # Earth radius in km

    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))

    return R * c


@agent.on_message(model=AgentStatus)
async def handle_status(ctx: Context, sender: str, msg: AgentStatus):
    scorer = agent_state.get("feasibility_scorer")
    sites_loaded = len(scorer.sites) if scorer else 0

    await ctx.send(sender, AgentStatus(
        agent_name="site_agent",
        status="healthy",
        address=agent.address,
        uptime=time.time() - agent_state["start_time"],
        requests_processed=agent_state["requests_processed"],
        metadata={
            "sites_available": sites_loaded,
            "feasibility_scoring": "enabled"
        }
    ))


if __name__ == "__main__":
    agent.run()
