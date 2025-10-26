"""
Discovery Agent: Searches patient database for candidates matching patient patterns.

Responsibilities:
- Receives matching patterns from Pattern Agent
- Searches patient database for patients in those patterns
- Filters by basic eligibility criteria
- Returns list of patient candidates with embeddings

Uses Pattern Discovery's discovered patterns to efficiently find relevant patients.
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

from agents.models import DiscoveryRequest, DiscoveryResponse, AgentStatus
from agents.config import AgentConfig, AgentRegistry
from data_loader import ClinicalDataLoader
from agentverse_config import (
    get_agent_address,
    is_agentverse_mode,
    get_agents_to_talk_to,
    validate_configuration
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

config = AgentConfig.get_agent_config("discovery")
agent = Agent(**config)

# Initialize the official Fetch.AI chat protocol
chat_proto = Protocol(spec=chat_protocol_spec)

agent_state = {
    "requests_processed": 0,
    "start_time": time.time(),
    "data_loader": None,
    "patient_cache": None,
    "agentverse_addresses": {},
    "is_agentverse": False,
    "coordinator_address": None
}


@agent.on_event("startup")
async def startup(ctx: Context):
    logger.info(f"✓ Discovery Agent started: {ctx.agent.address}")
    AgentRegistry.register("discovery", ctx.agent.address)
    agent_state["data_loader"] = ClinicalDataLoader()

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
                        text="Hello from Discovery Agent! Ready to search patient database for matching candidates."
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


@agent.on_message(model=DiscoveryRequest)
async def handle_discovery_request(ctx: Context, sender: str, msg: DiscoveryRequest):
    """Discover patient candidates using patient patterns"""
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
    Discover patient candidates based on patient patterns and eligibility criteria.

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
        # In production, would use actual pattern membership from Pattern Discovery
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


# ============================================================================
# CHAT PROTOCOL HANDLER (Official Fetch.AI)
# ============================================================================

@chat_proto.on_message(ChatMessage)
async def handle_chat_message(ctx: Context, sender: str, msg: ChatMessage):
    """Handle incoming chat messages using official Fetch.AI protocol"""
    for item in msg.content:
        if isinstance(item, TextContent):
            # Log received message
            logger.info(f"💬 Discovery Agent received chat message from {sender}: {item.text}")

            # Send acknowledgment
            ack = ChatAcknowledgement(
                timestamp=datetime.utcnow(),
                acknowledged_msg_id=msg.msg_id
            )
            await ctx.send(sender, ack)

            # NOTE: We don't send a response ChatMessage to avoid infinite loops.
            # Actual work requests should use specific message types (DiscoveryRequest, etc.),
            # not ChatMessage.


@chat_proto.on_message(ChatAcknowledgement)
async def handle_acknowledgement(ctx: Context, sender: str, msg: ChatAcknowledgement):
    """Handle chat acknowledgements"""
    logger.info(f"✓ Discovery received acknowledgement from {sender} for message: {msg.acknowledged_msg_id}")


# Include chat protocol in agent
agent.include(chat_proto, publish_manifest=True)


if __name__ == "__main__":
    agent.run()