"""
Coordinator Agent: Orchestrates the entire multi-agent workflow.
Responsibilities:
- Receives queries with Conway-discovered patterns
- Coordinates 6 specialized agents sequentially
- Aggregates results from all agents
- Returns comprehensive matching results
Flow:
User Query → Eligibility → Pattern → Discovery → Matching → Site → Prediction → Results
"""

from uagents import Agent, Context, Protocol
import logging
import time
import asyncio
from typing import Dict, Any, List
from datetime import datetime
from uuid import uuid4
from anthropic import Anthropic
import os
from uagents_core.contrib.protocols.chat import (
    ChatMessage,
    ChatAcknowledgement,
    TextContent,
    chat_protocol_spec,
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
    SiteRequest,
    SiteResponse,
    PredictionRequest,
    EnrollmentForecast,
    AgentStatus
)
from agents.config import AgentConfig, AgentRegistry, QUERY_TIMEOUT

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize agent
config = AgentConfig.get_agent_config("coordinator")
agent = Agent(**config)

# Initialize the chat protocol
chat_proto = Protocol(spec=chat_protocol_spec)

# Initialize Claude (Anthropic) client
try:
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
    llm_client = Anthropic(api_key=anthropic_api_key) if anthropic_api_key else None
except Exception as e:
    logger.warning(f"LLM initialization failed: {e}")
    llm_client = None

# Agent state
agent_state = {
    "requests_processed": 0,
    "start_time": time.time(),
    "conway_patterns": [],
    "patient_data": None,
    "trial_data": None
}


@agent.on_event("startup")
async def startup(ctx: Context):
    """Initialize coordinator on startup"""
    logger.info("=" * 70)
    logger.info("COORDINATOR AGENT STARTING")
    logger.info("=" * 70)
    logger.info(f"  Name: {agent.name}")
    logger.info(f"  Address: {agent.address}")
    logger.info(f"  Port: {config['port']}")
    logger.info(f"  Endpoint: {config['endpoint']}")
    logger.info("=" * 70)
    AgentRegistry.register("coordinator", agent.address)
    ctx.logger.info("✓ Coordinator Agent ready to orchestrate!")


@agent.on_query(model=UserQuery, replies={CoordinatorResponse})
async def handle_user_query(ctx: Context, sender: str, msg: UserQuery) -> CoordinatorResponse:
    """
    Main entry point: Orchestrate full workflow across all agents,
    now enhanced with LLM reasoning using Claude.
    """
    logger.info("=" * 70)
    logger.info(f"COORDINATOR: Processing query for trial {msg.trial_id}")
    logger.info(f"Query: {msg.query}")
    logger.info("=" * 70)

    workflow_start = time.time()
    metadata = {"query": msg.query, "agents_called": [], "timing": {}}

    try:
        # Get agent addresses
        eligibility_addr = AgentRegistry.get("eligibility")
        pattern_addr = AgentRegistry.get("pattern")
        discovery_addr = AgentRegistry.get("discovery")
        matching_addr = AgentRegistry.get("matching")
        site_addr = AgentRegistry.get("site")
        prediction_addr = AgentRegistry.get("prediction")

        # ================================================================
        # STEP 1: Eligibility Agent
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

        # ================================================================
        # STEP 2: Pattern Agent
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

        # ================================================================
        # STEP 3: Discovery Agent
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

        # ================================================================
        # STEP 4: Matching Agent
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

        # ================================================================
        # STEP 5: Site Agent
        # ================================================================
        logger.info("STEP 5: Calling Site Agent...")
        step_start = time.time()
        site_response = await ctx.send(
            site_addr,
            SiteRequest(
                trial_id=msg.trial_id,
                matches=matching_response.matches if matching_response else [],
                max_sites=10
            ),
            timeout=QUERY_TIMEOUT
        )
        metadata["timing"]["site"] = time.time() - step_start
        metadata["agents_called"].append("site")

        # ================================================================
        # STEP 6: Prediction Agent
        # ================================================================
        logger.info("STEP 6: Calling Prediction Agent...")
        step_start = time.time()
        prediction_response = await ctx.send(
            prediction_addr,
            PredictionRequest(
                trial_id=msg.trial_id,
                target_enrollment=msg.filters.get("target_enrollment", 300),
                matches=matching_response.matches if matching_response else [],
                patterns=pattern_response.patterns if pattern_response else [],
                sites=site_response.recommended_sites if site_response else []
            ),
            timeout=QUERY_TIMEOUT
        )
        metadata["timing"]["prediction"] = time.time() - step_start
        metadata["agents_called"].append("prediction")

        # ================================================================
        # STEP 7: NEW — LLM Reasoning with Claude
        # ================================================================
        llm_summary = None
        if llm_client:
            try:
                logger.info("STEP 7: Generating LLM reasoning with Claude...")
                cluster_summary = ", ".join(
                    [f"{p.get('pattern_id', i)} ({p.get('size', 0)} patients)" for i, p in enumerate(pattern_response.patterns[:5])]
                )
                prompt = f"""
                You are an AI clinical trial coordinator reviewing patient-trial matching data.
                Trial ID: {msg.trial_id}
                Cluster summary: {cluster_summary}

                Based on this data:
                - Summarize which clusters look most promising for enrollment
                - Identify potential exclusion risks
                - Recommend an enrollment strategy

                Keep it under 150 words, concise and professional.
                """
                response = llm_client.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=400,
                    messages=[{"role": "user", "content": prompt}]
                )
                llm_summary = response.content[0].text.strip()
                logger.info(f"[LLM Reasoning Output]: {llm_summary}")
            except Exception as e:
                logger.warning(f"LLM reasoning step failed: {e}")

        # ================================================================
        # Aggregate Results
        # ================================================================
        total_time = time.time() - workflow_start
        metadata["timing"]["total"] = total_time

        agent_state["requests_processed"] += 1

        return CoordinatorResponse(
            trial_id=msg.trial_id,
            status="success",
            eligible_patients=matching_response.matches if matching_response else [],
            total_matches=matching_response.total_scored if matching_response else 0,
            recommended_sites=site_response.recommended_sites if site_response else [],
            enrollment_forecast=prediction_response.dict() if prediction_response else {},
            processing_time=total_time,
            metadata={**metadata, "llm_summary": llm_summary or "No reasoning generated"}
        )

    except Exception as e:
        logger.error(f"Error in coordinator workflow: {e}", exc_info=True)
        return CoordinatorResponse(
            trial_id=msg.trial_id,
            status="error",
            eligible_patients=[],
            total_matches=0,
            recommended_sites=[],
            enrollment_forecast={},
            processing_time=time.time() - workflow_start,
            metadata={"error": str(e), "agents_called": metadata["agents_called"]}
        )


@agent.on_query(model=AgentStatus, replies={AgentStatus})
async def handle_status(ctx: Context, sender: str, msg: AgentStatus) -> AgentStatus:
    """Health check endpoint"""
    uptime = time.time() - agent_state["start_time"]
    return AgentStatus(
        agent_name="coordinator_agent",
        status="healthy",
        address=agent.address,
        uptime=uptime,
        requests_processed=agent_state["requests_processed"],
        metadata={"agents_managed": 6}
    )


# Chat protocol
@chat_proto.on_message(ChatMessage)
async def handle_chat_message(ctx: Context, sender: str, msg: ChatMessage):
    ctx.logger.info(f"Received chat message from {sender}")
    ack = ChatAcknowledgement(timestamp=datetime.utcnow(), acknowledged_msg_id=msg.msg_id)
    await ctx.send(sender, ack)
    for item in msg.content:
        if isinstance(item, TextContent):
            ctx.logger.info(f"Message content: {item.text}")
            response = ChatMessage(
                timestamp=datetime.utcnow(),
                msg_id=uuid4(),
                content=[TextContent(type="text", text=f"Coordinator Agent received your message: {item.text}")]
            )
            await ctx.send(sender, response)


@chat_proto.on_message(ChatAcknowledgement)
async def handle_acknowledgement(ctx: Context, sender: str, msg: ChatAcknowledgement):
    ctx.logger.info(f"Received acknowledgement from {sender} for message: {msg.acknowledged_msg_id}")


# Include the chat protocol
agent.include(chat_proto, publish_manifest=True)

if __name__ == "__main__":
    logger.info("Starting Coordinator Agent...")
    agent.run()
