"""
Site Agent: Recommends trial sites based on patient geography.

Responsibilities:
- Receives scored patient matches with locations
- Clusters patients by geography
- Recommends optimal trial sites
- Calculates site capacity and coverage
- Returns site recommendations with patient assignments

Uses geographic clustering to optimize site selection.
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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

config = AgentConfig.get_agent_config("site")
agent = Agent(**config)

agent_state = {
    "requests_processed": 0,
    "start_time": time.time()
}

# US major cities with coordinates (for site recommendations)
MAJOR_CITIES = [
    {"city": "New York", "state": "NY", "lat": 40.7128, "lon": -74.0060},
    {"city": "Los Angeles", "state": "CA", "lat": 34.0522, "lon": -118.2437},
    {"city": "Chicago", "state": "IL", "lat": 41.8781, "lon": -87.6298},
    {"city": "Houston", "state": "TX", "lat": 29.7604, "lon": -95.3698},
    {"city": "Phoenix", "state": "AZ", "lat": 33.4484, "lon": -112.0740},
    {"city": "Philadelphia", "state": "PA", "lat": 39.9526, "lon": -75.1652},
    {"city": "San Antonio", "state": "TX", "lat": 29.4241, "lon": -98.4936},
    {"city": "San Diego", "state": "CA", "lat": 32.7157, "lon": -117.1611},
    {"city": "Dallas", "state": "TX", "lat": 32.7767, "lon": -96.7970},
    {"city": "San Francisco", "state": "CA", "lat": 37.7749, "lon": -122.4194},
    {"city": "Boston", "state": "MA", "lat": 42.3601, "lon": -71.0589},
    {"city": "Seattle", "state": "WA", "lat": 47.6062, "lon": -122.3321},
    {"city": "Miami", "state": "FL", "lat": 25.7617, "lon": -80.1918},
    {"city": "Atlanta", "state": "GA", "lat": 33.7490, "lon": -84.3880},
    {"city": "Denver", "state": "CO", "lat": 39.7392, "lon": -104.9903}
]


@agent.on_event("startup")
async def startup(ctx: Context):
    logger.info(f"✓ Site Agent started: {agent.address}")
    AgentRegistry.register("site", agent.address)


@agent.on_query(model=SiteRequest, replies={SiteResponse})
async def handle_site_request(ctx: Context, sender: str, msg: SiteRequest) -> SiteResponse:
    """Recommend trial sites based on patient geography"""
    logger.info(f"  → Site Agent recommending sites for: {msg.trial_id}")

    try:
        matches = msg.matches
        max_sites = msg.max_sites

        # Cluster patients geographically and recommend sites
        recommendations = recommend_sites(matches, max_sites)

        # Calculate coverage
        total_patients = len(matches)
        covered_patients = sum(site["patient_count"] for site in recommendations)
        coverage = (covered_patients / total_patients * 100) if total_patients > 0 else 0

        agent_state["requests_processed"] += 1
        logger.info(f"  ✓ Recommended {len(recommendations)} sites covering {coverage:.0f}% of patients")

        return SiteResponse(
            trial_id=msg.trial_id,
            recommended_sites=recommendations,
            total_sites=len(recommendations),
            coverage_percentage=round(coverage, 1),
            geographic_clusters={
                "total_patients": total_patients,
                "covered_patients": covered_patients
            }
        )

    except Exception as e:
        logger.error(f"Error in site recommendation: {e}")
        return SiteResponse(
            trial_id=msg.trial_id,
            recommended_sites=[],
            total_sites=0,
            coverage_percentage=0.0,
            geographic_clusters={"error": str(e)}
        )


def recommend_sites(matches: list, max_sites: int) -> list:
    """
    Recommend trial sites based on patient geographic clustering.

    Strategy:
    1. Assign each patient to nearest major city
    2. Count patients per city
    3. Rank cities by patient count
    4. Return top N cities as site recommendations
    """
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
        return []

    # Assign patients to nearest cities
    city_assignments = defaultdict(list)

    for patient in patient_locations:
        nearest_city = find_nearest_city(patient["lat"], patient["lon"])
        city_assignments[nearest_city].append(patient["patient_id"])

    # Create site recommendations
    recommendations = []

    for city_key, patient_ids in city_assignments.items():
        city_info = next((c for c in MAJOR_CITIES if f"{c['city']},{c['state']}" == city_key), None)

        if city_info:
            # Calculate average distance to patients (mock)
            avg_distance = np.random.uniform(5, 50)  # km

            # Estimate site capacity
            capacity = min(len(patient_ids) + np.random.randint(20, 100), 500)

            # Priority score based on patient count
            priority_score = min(len(patient_ids) / 100.0, 1.0)

            recommendation = {
                "site_name": f"{city_info['city']} Medical Center",
                "location": {
                    "city": city_info["city"],
                    "state": city_info["state"],
                    "lat": city_info["lat"],
                    "lon": city_info["lon"]
                },
                "patient_count": len(patient_ids),
                "average_distance": round(avg_distance, 1),
                "capacity": capacity,
                "current_trials": np.random.randint(3, 15),
                "priority_score": round(priority_score, 3),
                "patient_ids": patient_ids[:100]  # Limit for response size
            }

            recommendations.append(recommendation)

    # Sort by patient count (descending)
    recommendations.sort(key=lambda x: x["patient_count"], reverse=True)

    return recommendations[:max_sites]


def find_nearest_city(lat: float, lon: float) -> str:
    """Find nearest major city to given coordinates"""
    min_distance = float('inf')
    nearest = None

    for city in MAJOR_CITIES:
        distance = haversine_distance(lat, lon, city["lat"], city["lon"])
        if distance < min_distance:
            min_distance = distance
            nearest = f"{city['city']},{city['state']}"

    return nearest or "Unknown,XX"


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


@agent.on_query(model=AgentStatus, replies={AgentStatus})
async def handle_status(ctx: Context, sender: str, msg: AgentStatus) -> AgentStatus:
    return AgentStatus(
        agent_name="site_agent",
        status="healthy",
        address=agent.address,
        uptime=time.time() - agent_state["start_time"],
        requests_processed=agent_state["requests_processed"],
        metadata={"cities_available": len(MAJOR_CITIES)}
    )


if __name__ == "__main__":
    agent.run()
