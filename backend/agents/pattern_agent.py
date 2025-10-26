"""
Pattern Agent: Finds matching patient patterns based on trial eligibility criteria.

Responsibilities:
- Receives pre-discovered patient patterns (from integration_service)
- Receives trial eligibility criteria from Eligibility Agent
- Matches patterns to trial requirements using similarity metrics
- Returns ranked list of matching patterns

KEY: This agent DOES NOT discover patterns - it works with Pattern Discovery's pre-discovered clusters.
"""

from uagents import Agent, Context, Protocol
import logging
import time
import numpy as np
import sys
import os
from datetime import datetime
from uuid import uuid4

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import Fetch.AI official chat protocol
from uagents_core.contrib.protocols.chat import (
    ChatMessage,
    ChatAcknowledgement,
    TextContent,
    chat_protocol_spec
)

from agents.models import PatternRequest, PatternResponse, AgentStatus
from agents.config import AgentConfig, AgentRegistry
from agentverse_config import (
    get_agent_address,
    is_agentverse_mode,
    get_agents_to_talk_to,
    validate_configuration
)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

config = AgentConfig.get_agent_config("pattern")
agent = Agent(**config)

# Initialize the official Fetch.AI chat protocol
chat_proto = Protocol(spec=chat_protocol_spec)

agent_state = {
    "requests_processed": 0,
    "start_time": time.time(),
    "conway_patterns": [],  # Stored from integration service
    "pattern_cache": {},
    "agentverse_addresses": {},
    "is_agentverse": False,
    "coordinator_address": None
}


@agent.on_event("startup")
async def startup(ctx: Context):
    logger.info(f"✓ Pattern Agent started: {ctx.agent.address}")
    AgentRegistry.register("pattern", ctx.agent.address)
    # Patterns will be loaded from context storage when needed

    # Check if running in Agentverse mode
    agent_state["is_agentverse"] = is_agentverse_mode()

    if agent_state["is_agentverse"]:
        logger.info("🌐 Running in AGENTVERSE MODE")

        # Get coordinator address
        coordinator_addr = get_agent_address("coordinator")
        if coordinator_addr:
            agent_state["coordinator_address"] = coordinator_addr
            logger.info(f"  ✓ Loaded coordinator address: {coordinator_addr[:20]}...")

            # Send greeting to coordinator
            try:
                greeting = ChatMessage(
                    timestamp=datetime.utcnow(),
                    msg_id=uuid4(),
                    content=[TextContent(
                        type="text",
                        text="Hello from Pattern Agent! Ready to match pre-discovered patient patterns to trial criteria!"
                    )]
                )
                await ctx.send(coordinator_addr, greeting)
                logger.info(f"  ✓ Sent greeting to coordinator")
            except Exception as e:
                logger.error(f"  ❌ Failed to send greeting to coordinator: {e}")
        else:
            logger.warning(f"  ⚠ Missing coordinator address - update agentverse_config.py")
    else:
        logger.info("🏠 Running in LOCAL MODE")

@agent.on_message(model=PatternRequest)
async def handle_pattern_request(ctx: Context, sender: str, msg: PatternRequest):
    """Find patient patterns matching trial eligibility criteria"""
    logger.info(f"  → Pattern Agent matching patterns for: {msg.trial_id}")

    try:
        # Get patient patterns from context storage (loaded by integration service)
        stored_patterns = ctx.storage.get("conway_patterns")
        if stored_patterns:
            conway_patterns = stored_patterns
        else:
            # Fallback: use cached patterns or empty
            conway_patterns = agent_state.get("conway_patterns", [])

        if not conway_patterns:
            logger.warning("No patient patterns available - returning empty")
            await ctx.send(sender, PatternResponse(
                trial_id=msg.trial_id,
                patterns=[],
                total_patterns=0,
                conway_metadata={"warning": "No patterns available"}
            ))
            return

        # Match patterns to criteria
        criteria = msg.criteria
        matching_patterns = match_patterns_to_criteria(conway_patterns, criteria, msg.min_pattern_size)

        agent_state["requests_processed"] += 1
        logger.info(f"  ✓ Found {len(matching_patterns)} matching patterns from {len(conway_patterns)} total")

        await ctx.send(sender, PatternResponse(
            trial_id=msg.trial_id,
            patterns=matching_patterns,
            total_patterns=len(matching_patterns),
            conway_metadata={
                "total_conway_patterns": len(conway_patterns),
                "min_pattern_size": msg.min_pattern_size
            }
        ))

    except Exception as e:
        logger.error(f"Error in pattern matching: {e}")
        await ctx.send(sender, PatternResponse(
            trial_id=msg.trial_id,
            patterns=[],
            total_patterns=0,
            conway_metadata={"error": str(e)}
        ))


def match_patterns_to_criteria(patterns: list, criteria: dict, min_size: int) -> list:
    """
    Match patient patterns to trial eligibility criteria.

    Scoring based on:
    - Pattern size (larger = more candidates)
    - Enrollment success rate (from Pattern Discovery)
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


@agent.on_message(model=AgentStatus)
async def handle_status(ctx: Context, sender: str, msg: AgentStatus):
    await ctx.send(sender, AgentStatus(
        agent_name="pattern_agent",
        status="healthy",
        address=agent.address,
        uptime=time.time() - agent_state["start_time"],
        requests_processed=agent_state["requests_processed"],
        metadata={"patterns_available": len(agent_state.get("conway_patterns", []))}
    ))


# ============================================================================
# CHAT PROTOCOL HANDLER (Official Fetch.AI)
# ============================================================================

@chat_proto.on_message(ChatMessage)
async def handle_chat_message(ctx: Context, sender: str, msg: ChatMessage):
    """Handle incoming chat messages using official Fetch.AI protocol"""
    for item in msg.content:
        if isinstance(item, TextContent):
            # Log received message
            logger.info(f"💬 Pattern Agent received chat message from {sender}: {item.text}")

            # Send acknowledgment
            ack = ChatAcknowledgement(
                timestamp=datetime.utcnow(),
                acknowledged_msg_id=msg.msg_id
            )
            await ctx.send(sender, ack)

            # NOTE: We don't send a response ChatMessage to avoid infinite loops.
            # Actual work requests should use specific message types (EligibilityRequest, etc.),
            # not ChatMessage.
            agent_state["requests_processed"] += 1


@chat_proto.on_message(ChatAcknowledgement)
async def handle_acknowledgement(ctx: Context, sender: str, msg: ChatAcknowledgement):
    """Handle chat acknowledgements"""
    logger.info(f"✓ Pattern received acknowledgement from {sender} for message: {msg.acknowledged_msg_id}")


# Include chat protocol in agent
agent.include(chat_proto, publish_manifest=True)


if __name__ == "__main__":
    agent.run()
