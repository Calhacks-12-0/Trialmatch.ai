"""
Coordinator Agent: Orchestrates the entire multi-agent workflow.

Responsibilities:
- Receives queries with Pattern Discovery-discovered patterns
- Coordinates 7 specialized agents sequentially
- Aggregates results from all agents
- Returns comprehensive matching results

Flow:
User Query → Eligibility → Pattern → Discovery → Matching → Validation → Site → Prediction → Results
"""

from uagents import Agent, Context, Protocol
import logging
import time
import asyncio
from typing import Dict, Any, List
from datetime import datetime
from uuid import uuid4

# Import Fetch.AI official chat protocol
from uagents_core.contrib.protocols.chat import (
    ChatMessage,
    ChatAcknowledgement,
    TextContent,
    chat_protocol_spec
)

from agents.models import (
    UserQuery,
    CoordinatorResponse,
    EligibilityRequest,
    EligibilityCriteria,
    PatternRequest,
    PatternResponse,
    DiscoveryRequest,
    DiscoveryResponse,
    MatchingRequest,
    MatchingResponse,
    ValidationRequest,
    ValidationResponse,
    SiteRequest,
    SiteResponse,
    PredictionRequest,
    EnrollmentForecast,
    AgentStatus
)
from agents.config import AgentConfig, AgentRegistry, QUERY_TIMEOUT
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agentverse_config import (
    get_agent_address,
    is_agentverse_mode,
    get_agents_to_talk_to,
    validate_configuration
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize agent
config = AgentConfig.get_agent_config("coordinator")
agent = Agent(**config)

# Initialize the official Fetch.AI chat protocol
chat_proto = Protocol(spec=chat_protocol_spec)

# Agent state
agent_state = {
    "requests_processed": 0,
    "start_time": time.time(),
    "conway_patterns": [],  # Store patient patterns
    "patient_data": None,
    "trial_data": None,
    "agentverse_addresses": {},  # Store Agentverse addresses
    "is_agentverse": False
}


@agent.on_event("startup")
async def startup(ctx: Context):
    """Initialize coordinator on startup"""
    logger.info("=" * 70)
    logger.info("COORDINATOR AGENT STARTING")
    logger.info("=" * 70)
    logger.info(f"  Name: {ctx.agent.name}")
    logger.info(f"  Address: {ctx.agent.address}")
    logger.info(f"  Port: {config['port']}")
    logger.info(f"  Endpoint: {config['endpoint']}")
    logger.info("=" * 70)

    # Register with central registry (for local mode)
    AgentRegistry.register("coordinator", ctx.agent.address)

    # Check if running in Agentverse mode
    agent_state["is_agentverse"] = is_agentverse_mode()

    if agent_state["is_agentverse"]:
        logger.info("🌐 Running in AGENTVERSE MODE")

        # Load Agentverse addresses for agents we need to talk to
        agents_to_contact = get_agents_to_talk_to("coordinator")
        for agent_name in agents_to_contact:
            addr = get_agent_address(agent_name)
            if addr:
                agent_state["agentverse_addresses"][agent_name] = addr
                logger.info(f"  ✓ Loaded {agent_name} address: {addr[:20]}...")
            else:
                logger.warning(f"  ⚠ Missing {agent_name} address - update agentverse_config.py")

        # Validate configuration
        is_valid, message = validate_configuration("coordinator")
        if not is_valid:
            logger.error(f"  ❌ Configuration error: {message}")
        else:
            logger.info(f"  ✓ {message}")

        # Send initial chat messages to all agents to establish communication
        logger.info("📤 Sending initial chat messages to establish connections...")
        for agent_name, addr in agent_state["agentverse_addresses"].items():
            try:
                initial_message = ChatMessage(
                    timestamp=datetime.utcnow(),
                    msg_id=uuid4(),
                    content=[TextContent(
                        type="text",
                        text=f"Hello from Coordinator Agent! I'm ready to orchestrate the multi-agent workflow."
                    )]
                )
                await ctx.send(addr, initial_message)
                logger.info(f"  ✓ Sent greeting to {agent_name}")
            except Exception as e:
                logger.error(f"  ❌ Failed to send greeting to {agent_name}: {e}")
    else:
        logger.info("🏠 Running in LOCAL MODE (no Agentverse addresses configured)")
        logger.info("  Using AgentRegistry for local agent communication")

    logger.info("=" * 70)
    ctx.logger.info("✓ Coordinator Agent ready to orchestrate!")


def get_agent_addr(agent_name: str) -> str:
    """
    Get agent address - uses Agentverse address if configured, otherwise local registry.

    Args:
        agent_name: Name of the agent

    Returns:
        Agent address string
    """
    if agent_state["is_agentverse"]:
        # Use Agentverse address
        addr = agent_state["agentverse_addresses"].get(agent_name)
        if not addr:
            logger.warning(f"⚠ Agentverse address not found for {agent_name}, falling back to registry")
            return AgentRegistry.get(agent_name)
        return addr
    else:
        # Use local registry
        return AgentRegistry.get(agent_name)


@agent.on_message(model=UserQuery)
async def handle_user_query(
    ctx: Context,
    sender: str,
    msg: UserQuery
):
    """
    Main entry point: Orchestrate the entire multi-agent workflow.

    Input: UserQuery with trial_id, query text, and Pattern Discovery-discovered patterns
    Output: CoordinatorResponse with all agent results aggregated

    Workflow:
    1. Eligibility Agent → Extract trial criteria with medical codes
    2. Pattern Agent → Find matching patient patterns
    3. Discovery Agent → Search patients using patterns
    4. Matching Agent → Score patients
    5. Validation Agent → Check exclusion criteria (NEW)
    6. Site Agent → Feasibility scoring + Geographic recommendations (UPDATED)
    7. Prediction Agent → Enrollment forecast
    """
    logger.info("=" * 70)
    logger.info(f"COORDINATOR: Processing query for trial {msg.trial_id}")
    logger.info(f"Query: {msg.query}")
    logger.info("=" * 70)

    workflow_start = time.time()
    metadata = {
        "query": msg.query,
        "agents_called": [],
        "timing": {}
    }

    try:
        # Get agent addresses (Agentverse or local registry)
        eligibility_addr = get_agent_addr("eligibility")
        pattern_addr = get_agent_addr("pattern")
        discovery_addr = get_agent_addr("discovery")
        matching_addr = get_agent_addr("matching")
        validation_addr = get_agent_addr("validation")
        site_addr = get_agent_addr("site")
        prediction_addr = get_agent_addr("prediction")

        # ================================================================
        # STEP 1: Eligibility Agent - Extract trial criteria
        # ================================================================
        logger.info("STEP 1: Calling Eligibility Agent...")
        step_start = time.time()

        eligibility_response = await ctx.send(
            eligibility_addr,
            EligibilityRequest(
                trial_id=msg.trial_id,
                trial_data=msg.filters.get("trial_data")
            ),
            timeout=QUERY_TIMEOUT
        )

        metadata["timing"]["eligibility"] = time.time() - step_start
        metadata["agents_called"].append("eligibility")
        logger.info(f"✓ Eligibility criteria extracted in {metadata['timing']['eligibility']:.2f}s")

        # ================================================================
        # STEP 2: Pattern Agent - Find matching patient patterns
        # ================================================================
        logger.info("STEP 2: Calling Pattern Agent...")
        step_start = time.time()

        pattern_response = await ctx.send(
            pattern_addr,
            PatternRequest(
                trial_id=msg.trial_id,
                criteria=eligibility_response.dict() if eligibility_response else {},
                min_pattern_size=50
            ),
            timeout=QUERY_TIMEOUT
        )

        metadata["timing"]["pattern"] = time.time() - step_start
        metadata["agents_called"].append("pattern")
        logger.info(f"✓ Found {pattern_response.total_patterns if pattern_response else 0} matching patterns in {metadata['timing']['pattern']:.2f}s")

        # ================================================================
        # STEP 3: Discovery Agent - Search patients using patterns
        # ================================================================
        logger.info("STEP 3: Calling Discovery Agent...")
        step_start = time.time()

        discovery_response = await ctx.send(
            discovery_addr,
            DiscoveryRequest(
                trial_id=msg.trial_id,
                patterns=pattern_response.patterns if pattern_response else [],
                eligibility_criteria=eligibility_response.dict() if eligibility_response else {},
                max_results=1000
            ),
            timeout=QUERY_TIMEOUT
        )

        metadata["timing"]["discovery"] = time.time() - step_start
        metadata["agents_called"].append("discovery")
        logger.info(f"✓ Discovered {discovery_response.total_found if discovery_response else 0} candidates in {metadata['timing']['discovery']:.2f}s")

        # ================================================================
        # STEP 4: Matching Agent - Score patients
        # ================================================================
        logger.info("STEP 4: Calling Matching Agent...")
        step_start = time.time()

        matching_response = await ctx.send(
            matching_addr,
            MatchingRequest(
                trial_id=msg.trial_id,
                candidates=discovery_response.candidates if discovery_response else [],
                eligibility_criteria=eligibility_response.dict() if eligibility_response else {},
                patterns=pattern_response.patterns if pattern_response else []
            ),
            timeout=QUERY_TIMEOUT
        )

        metadata["timing"]["matching"] = time.time() - step_start
        metadata["agents_called"].append("matching")
        logger.info(f"✓ Scored {matching_response.total_scored if matching_response else 0} patients in {metadata['timing']['matching']:.2f}s")

        # ================================================================
        # STEP 5: Validation Agent - Check exclusion criteria (NEW)
        # ================================================================
        logger.info("STEP 5: Calling Validation Agent...")
        step_start = time.time()

        validation_response = await ctx.send(
            validation_addr,
            ValidationRequest(
                trial_id=msg.trial_id,
                matches=matching_response.matches if matching_response else [],
                exclusion_codes=eligibility_response.exclusion_codes if eligibility_response else {}
            ),
            timeout=QUERY_TIMEOUT
        )

        metadata["timing"]["validation"] = time.time() - step_start
        metadata["agents_called"].append("validation")
        logger.info(f"✓ Validated {validation_response.total_validated if validation_response else 0} patients, excluded {validation_response.total_excluded if validation_response else 0} in {metadata['timing']['validation']:.2f}s")

        # Use validated matches for subsequent agents
        validated_matches = [v for v in (validation_response.validations if validation_response else []) if v.get("is_valid", False)]

        # ================================================================
        # STEP 6: Site Agent - Feasibility scoring + Geographic recommendations (UPDATED)
        # ================================================================
        logger.info("STEP 6: Calling Site Agent...")
        step_start = time.time()

        site_response = await ctx.send(
            site_addr,
            SiteRequest(
                trial_id=msg.trial_id,
                matches=validated_matches,
                max_sites=10,
                eligibility_criteria={
                    "inclusion_codes": eligibility_response.inclusion_codes if eligibility_response else {},
                    "exclusion_codes": eligibility_response.exclusion_codes if eligibility_response else {}
                },
                target_enrollment=msg.filters.get("target_enrollment", 300)
            ),
            timeout=QUERY_TIMEOUT
        )

        metadata["timing"]["site"] = time.time() - step_start
        metadata["agents_called"].append("site")
        logger.info(f"✓ Recommended {site_response.total_sites if site_response else 0} sites in {metadata['timing']['site']:.2f}s")

        # ================================================================
        # STEP 7: Prediction Agent - Enrollment forecast
        # ================================================================
        logger.info("STEP 7: Calling Prediction Agent...")
        step_start = time.time()

        prediction_response = await ctx.send(
            prediction_addr,
            PredictionRequest(
                trial_id=msg.trial_id,
                target_enrollment=msg.filters.get("target_enrollment", 300),
                matches=validated_matches,
                patterns=pattern_response.patterns if pattern_response else [],
                sites=site_response.recommended_sites if site_response else []
            ),
            timeout=QUERY_TIMEOUT
        )

        metadata["timing"]["prediction"] = time.time() - step_start
        metadata["agents_called"].append("prediction")
        logger.info(f"✓ Generated enrollment forecast in {metadata['timing']['prediction']:.2f}s")

        # ================================================================
        # Aggregate Results
        # ================================================================
        total_time = time.time() - workflow_start
        metadata["timing"]["total"] = total_time

        logger.info("=" * 70)
        logger.info(f"COORDINATOR: Workflow completed in {total_time:.2f}s")
        logger.info(f"  Matched patients: {matching_response.total_scored if matching_response else 0}")
        logger.info(f"  Validated patients: {len(validated_matches)}")
        logger.info(f"  Excluded patients: {validation_response.total_excluded if validation_response else 0}")
        logger.info(f"  Recommended sites: {site_response.total_sites if site_response else 0}")
        logger.info(f"  Forecast: {prediction_response.estimated_weeks if prediction_response else 0} weeks")
        logger.info("=" * 70)

        # Update stats
        agent_state["requests_processed"] += 1

        response = CoordinatorResponse(
            trial_id=msg.trial_id,
            status="success",
            eligible_patients=validated_matches,
            total_matches=len(validated_matches),
            recommended_sites=site_response.recommended_sites if site_response else [],
            enrollment_forecast=prediction_response.dict() if prediction_response else {},
            processing_time=total_time,
            metadata=metadata
        )

        await ctx.send(sender, response)

    except Exception as e:
        logger.error(f"Error in coordinator workflow: {e}", exc_info=True)
        error_response = CoordinatorResponse(
            trial_id=msg.trial_id,
            status="error",
            eligible_patients=[],
            total_matches=0,
            recommended_sites=[],
            enrollment_forecast={},
            processing_time=time.time() - workflow_start,
            metadata={"error": str(e), "agents_called": metadata["agents_called"]}
        )
        await ctx.send(sender, error_response)


@agent.on_message(model=AgentStatus)
async def handle_status(ctx: Context, sender: str, msg: AgentStatus):
    """Health check endpoint"""
    uptime = time.time() - agent_state["start_time"]
    status = AgentStatus(
        agent_name="coordinator_agent",
        status="healthy",
        address=agent.address,
        uptime=uptime,
        requests_processed=agent_state["requests_processed"],
        metadata={
            "agents_managed": 7
        }
    )
    await ctx.send(sender, status)


# ============================================================================
# CHAT PROTOCOL HANDLER (Official Fetch.AI)
# ============================================================================

@chat_proto.on_message(ChatMessage)
async def handle_chat_message(ctx: Context, sender: str, msg: ChatMessage):
    """Handle incoming chat messages using official Fetch.AI protocol"""
    for item in msg.content:
        if isinstance(item, TextContent):
            # Log received message (but don't respond to avoid message loops)
            logger.info(f"💬 Coordinator Agent received chat message from {sender}: {item.text}")

            # Send acknowledgment only (no response message to avoid loops)
            ack = ChatAcknowledgement(
                timestamp=datetime.utcnow(),
                acknowledged_msg_id=msg.msg_id
            )
            await ctx.send(sender, ack)

            # NOTE: We don't send a response ChatMessage to avoid infinite loops.
            # Actual work requests should use specific message types like UserQuery,
            # not ChatMessage.


@chat_proto.on_message(ChatAcknowledgement)
async def handle_acknowledgement(ctx: Context, sender: str, msg: ChatAcknowledgement):
    """Handle chat acknowledgements"""
    logger.info(f"✓ Coordinator received acknowledgement from {sender} for message: {msg.acknowledged_msg_id}")


# Include chat protocol in agent
agent.include(chat_proto, publish_manifest=True)


if __name__ == "__main__":
    logger.info("Starting Coordinator Agent...")
    agent.run()
