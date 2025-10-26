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

from uagents import Agent, Context
import logging
import time
import asyncio
from typing import Dict, Any, List

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

# Agent state
agent_state = {
    "requests_processed": 0,
    "start_time": time.time(),
    "conway_patterns": [],  # Store Conway patterns
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

    # Register with central registry
    AgentRegistry.register("coordinator", agent.address)

    ctx.logger.info("✓ Coordinator Agent ready to orchestrate!")


@agent.on_query(model=UserQuery, replies={CoordinatorResponse})
async def handle_user_query(
    ctx: Context,
    sender: str,
    msg: UserQuery
) -> CoordinatorResponse:
    """
    Main entry point: Orchestrate the entire multi-agent workflow.

    Input: UserQuery with trial_id, query text, and Conway-discovered patterns
    Output: CoordinatorResponse with all agent results aggregated

    Workflow:
    1. Eligibility Agent → Extract trial criteria
    2. Pattern Agent → Find matching Conway patterns
    3. Discovery Agent → Search patients using patterns
    4. Matching Agent → Score patients
    5. Site Agent → Geographic recommendations
    6. Prediction Agent → Enrollment forecast
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
        # Get agent addresses from registry
        eligibility_addr = AgentRegistry.get("eligibility")
        pattern_addr = AgentRegistry.get("pattern")
        discovery_addr = AgentRegistry.get("discovery")
        matching_addr = AgentRegistry.get("matching")
        site_addr = AgentRegistry.get("site")
        prediction_addr = AgentRegistry.get("prediction")

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
        # STEP 2: Pattern Agent - Find matching Conway patterns
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
        # STEP 5: Site Agent - Geographic recommendations
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
        logger.info(f"✓ Recommended {site_response.total_sites if site_response else 0} sites in {metadata['timing']['site']:.2f}s")

        # ================================================================
        # STEP 6: Prediction Agent - Enrollment forecast
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
        logger.info(f"✓ Generated enrollment forecast in {metadata['timing']['prediction']:.2f}s")

        # ================================================================
        # Aggregate Results
        # ================================================================
        total_time = time.time() - workflow_start
        metadata["timing"]["total"] = total_time

        logger.info("=" * 70)
        logger.info(f"COORDINATOR: Workflow completed in {total_time:.2f}s")
        logger.info(f"  Eligible patients: {matching_response.total_scored if matching_response else 0}")
        logger.info(f"  Recommended sites: {site_response.total_sites if site_response else 0}")
        logger.info(f"  Forecast: {prediction_response.estimated_weeks if prediction_response else 0} weeks")
        logger.info("=" * 70)

        # Update stats
        agent_state["requests_processed"] += 1

        return CoordinatorResponse(
            trial_id=msg.trial_id,
            status="success",
            eligible_patients=matching_response.matches if matching_response else [],
            total_matches=matching_response.total_scored if matching_response else 0,
            recommended_sites=site_response.recommended_sites if site_response else [],
            enrollment_forecast=prediction_response.dict() if prediction_response else {},
            processing_time=total_time,
            metadata=metadata
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


@agent.on_message(model=AgentStatus)
async def handle_status(ctx: Context, sender: str, msg: AgentStatus):
    """Health check endpoint"""
    uptime = time.time() - agent_state["start_time"]
    return AgentStatus(
        agent_name="coordinator_agent",
        status="healthy",
        address=agent.address,
        uptime=uptime,
        requests_processed=agent_state["requests_processed"],
        metadata={
            "agents_managed": 6
        }
    )


if __name__ == "__main__":
    logger.info("Starting Coordinator Agent...")
    agent.run()
