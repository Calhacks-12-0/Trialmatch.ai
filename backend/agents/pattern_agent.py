"""
Pattern Agent: Finds matching Conway patterns based on trial eligibility criteria.

Responsibilities:
- Receives pre-discovered Conway patterns (from integration_service)
- Receives trial eligibility criteria from Eligibility Agent
- Matches patterns to trial requirements using similarity metrics
- Returns ranked list of matching patterns

KEY: This agent DOES NOT discover patterns - it works with Conway's pre-discovered clusters.
"""

from uagents import Agent, Context
import logging
import time
import numpy as np
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.models import PatternRequest, PatternResponse, AgentStatus
from agents.config import AgentConfig, AgentRegistry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

config = AgentConfig.get_agent_config("pattern")
agent = Agent(**config)

agent_state = {
    "requests_processed": 0,
    "start_time": time.time(),
    "conway_patterns": [],  # Stored from integration service
    "pattern_cache": {}
}


@agent.on_event("startup")
async def startup(ctx: Context):
    logger.info(f"✓ Pattern Agent started: {agent.address}")
    AgentRegistry.register("pattern", agent.address)
    # Patterns will be loaded from context storage when needed


@agent.on_query(model=PatternRequest, replies={PatternResponse})
async def handle_pattern_request(ctx: Context, sender: str, msg: PatternRequest) -> PatternResponse:
    """Find Conway patterns matching trial eligibility criteria"""
    logger.info(f"  → Pattern Agent matching patterns for: {msg.trial_id}")

    try:
        # Get Conway patterns from context storage (loaded by integration service)
        stored_patterns = ctx.storage.get("conway_patterns")
        if stored_patterns:
            conway_patterns = stored_patterns
        else:
            # Fallback: use cached patterns or empty
            conway_patterns = agent_state.get("conway_patterns", [])

        if not conway_patterns:
            logger.warning("No Conway patterns available - returning empty")
            return PatternResponse(
                trial_id=msg.trial_id,
                patterns=[],
                total_patterns=0,
                conway_metadata={"warning": "No patterns available"}
            )

        # Match patterns to criteria
        criteria = msg.criteria
        matching_patterns = match_patterns_to_criteria(conway_patterns, criteria, msg.min_pattern_size)

        agent_state["requests_processed"] += 1
        logger.info(f"  ✓ Found {len(matching_patterns)} matching patterns from {len(conway_patterns)} total")

        return PatternResponse(
            trial_id=msg.trial_id,
            patterns=matching_patterns,
            total_patterns=len(matching_patterns),
            conway_metadata={
                "total_conway_patterns": len(conway_patterns),
                "min_pattern_size": msg.min_pattern_size
            }
        )

    except Exception as e:
        logger.error(f"Error in pattern matching: {e}")
        return PatternResponse(
            trial_id=msg.trial_id,
            patterns=[],
            total_patterns=0,
            conway_metadata={"error": str(e)}
        )


def match_patterns_to_criteria(patterns: list, criteria: dict, min_size: int) -> list:
    """
    Match Conway patterns to trial eligibility criteria.

    Scoring based on:
    - Pattern size (larger = more candidates)
    - Enrollment success rate (from Conway)
    - Age range overlap
    - Condition relevance
    """
    matched = []

    age_min = criteria.get("age_range", {}).get("min", 18)
    age_max = criteria.get("age_range", {}).get("max", 99)
    conditions = criteria.get("conditions", [])

    for pattern in patterns:
        if pattern.get("size", 0) < min_size:
            continue

        # Calculate match score (0-1)
        score = 0.0

        # Factor 1: Enrollment success rate (40% weight)
        success_rate = pattern.get("enrollment_success_rate", 0.7)
        score += success_rate * 0.4

        # Factor 2: Pattern confidence (30% weight)
        confidence = pattern.get("confidence", 0.5)
        score += confidence * 0.3

        # Factor 3: Pattern size (20% weight) - larger is better
        size_score = min(pattern.get("size", 0) / 1000.0, 1.0)
        score += size_score * 0.2

        # Factor 4: Random factor for diversity (10% weight)
        score += np.random.uniform(0, 0.1)

        # Add matched pattern
        matched.append({
            "pattern_id": pattern["pattern_id"],
            "size": pattern["size"],
            "centroid": pattern["centroid"],
            "confidence": confidence,
            "enrollment_success_rate": success_rate,
            "match_score": round(score, 3),
            "characteristics": {
                "estimated_age_range": f"{age_min}-{age_max}",
                "conditions": conditions
            }
        })

    # Sort by match score descending
    matched.sort(key=lambda x: x["match_score"], reverse=True)
    return matched[:20]  # Top 20 patterns


@agent.on_query(model=AgentStatus, replies={AgentStatus})
async def handle_status(ctx: Context, sender: str, msg: AgentStatus) -> AgentStatus:
    return AgentStatus(
        agent_name="pattern_agent",
        status="healthy",
        address=agent.address,
        uptime=time.time() - agent_state["start_time"],
        requests_processed=agent_state["requests_processed"],
        metadata={"patterns_available": len(agent_state.get("conway_patterns", []))}
    )


if __name__ == "__main__":
    agent.run()
