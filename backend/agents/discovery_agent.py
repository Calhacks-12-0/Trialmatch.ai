"""
Discovery Agent: Searches patient database for candidates matching Conway patterns.

Responsibilities:
- Receives matching patterns from Pattern Agent
- Searches patient database for patients in those patterns
- Filters by basic eligibility criteria
- Returns list of patient candidates with embeddings

Uses Conway's discovered patterns to efficiently find relevant patients.
"""

from uagents import Agent, Context
import logging
import time
import numpy as np
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.models import DiscoveryRequest, DiscoveryResponse, AgentStatus
from agents.config import AgentConfig, AgentRegistry
from data_loader import ClinicalDataLoader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

config = AgentConfig.get_agent_config("discovery")
agent = Agent(**config)

agent_state = {
    "requests_processed": 0,
    "start_time": time.time(),
    "data_loader": None,
    "patient_cache": None
}


@agent.on_event("startup")
async def startup(ctx: Context):
    logger.info(f"✓ Discovery Agent started: {agent.address}")
    AgentRegistry.register("discovery", agent.address)
    agent_state["data_loader"] = ClinicalDataLoader()


@agent.on_message(model=DiscoveryRequest)
async def handle_discovery_request(ctx: Context, sender: str, msg: DiscoveryRequest):
    """Discover patient candidates using Conway patterns"""
    logger.info(f"  → Discovery Agent searching patients for: {msg.trial_id}")

    try:
        # Load patient data if not cached
        if agent_state["patient_cache"] is None:
            data_loader = agent_state["data_loader"]
            data = data_loader.prepare_for_conway()
            agent_state["patient_cache"] = data["patients"]

        patients = agent_state["patient_cache"]
        criteria = msg.eligibility_criteria
        patterns = msg.patterns

        # Find candidates matching patterns
        candidates = discover_candidates(patients, patterns, criteria, msg.max_results)

        agent_state["requests_processed"] += 1
        logger.info(f"  ✓ Discovered {len(candidates)} patient candidates from {len(patients)} total")

        await ctx.send(sender, DiscoveryResponse(
            trial_id=msg.trial_id,
            candidates=candidates,
            total_found=len(candidates),
            search_metadata={
                "total_patients_searched": len(patients),
                "patterns_used": len(patterns),
                "max_results": msg.max_results
            }
        ))

    except Exception as e:
        logger.error(f"Error in patient discovery: {e}")
        await ctx.send(sender, DiscoveryResponse(
            trial_id=msg.trial_id,
            candidates=[],
            total_found=0,
            search_metadata={"error": str(e)}
        ))


def discover_candidates(patients: list, patterns: list, criteria: dict, max_results: int) -> list:
    """
    Discover patient candidates based on Conway patterns and eligibility criteria.

    Strategy:
    1. For each pattern, select a sample of patients
    2. Filter by basic eligibility (age, gender, condition)
    3. Return candidates with pattern association
    """
    candidates = []

    age_min = criteria.get("age_range", {}).get("min", 18)
    age_max = criteria.get("age_range", {}).get("max", 99)
    required_gender = criteria.get("gender")
    required_conditions = criteria.get("conditions", [])

    # For each pattern, select candidate patients
    patients_per_pattern = max(10, max_results // max(len(patterns), 1))

    for pattern in patterns[:10]:  # Top 10 patterns
        pattern_id = pattern.get("pattern_id")
        pattern_size = pattern.get("size", 0)

        # Simulate selecting patients from this pattern
        # In production, would use actual pattern membership from Conway
        num_candidates = min(patients_per_pattern, pattern_size)

        for i, patient in enumerate(patients[:num_candidates]):
            # Basic eligibility filtering
            if not (age_min <= patient.get("age", 0) <= age_max):
                continue

            if required_gender and patient.get("gender") != required_gender:
                continue

            # Check condition match
            patient_condition = patient.get("primary_condition", "")
            if required_conditions and patient_condition not in required_conditions:
                # Allow partial match for hackathon
                if not any(cond.lower() in patient_condition.lower() for cond in required_conditions):
                    continue

            # Create candidate
            candidate = {
                "patient_id": patient["patient_id"],
                "pattern_id": pattern_id,
                "embedding": pattern.get("centroid", [0.0] * 50),  # Use pattern centroid
                "demographics": {
                    "age": patient["age"],
                    "gender": patient["gender"]
                },
                "clinical_data": {
                    "primary_condition": patient["primary_condition"],
                    "medications": patient.get("medications", []),
                    "lab_values": patient.get("lab_values", {}),
                    "enrollment_history": patient.get("enrollment_history", 0)
                },
                "location": {
                    "lat": patient.get("latitude", 0.0),
                    "lon": patient.get("longitude", 0.0)
                }
            }

            candidates.append(candidate)

            if len(candidates) >= max_results:
                break

        if len(candidates) >= max_results:
            break

    return candidates[:max_results]


@agent.on_message(model=AgentStatus)
async def handle_status(ctx: Context, sender: str, msg: AgentStatus):
    await ctx.send(sender, AgentStatus(
        agent_name="discovery_agent",
        status="healthy",
        address=agent.address,
        uptime=time.time() - agent_state["start_time"],
        requests_processed=agent_state["requests_processed"],
        metadata={
            "patients_cached": len(agent_state["patient_cache"]) if agent_state["patient_cache"] else 0
        }
    ))


if __name__ == "__main__":
    agent.run()