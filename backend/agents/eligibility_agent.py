"""
Eligibility Agent: Extracts trial eligibility criteria using LLM (or structured parsing).

Responsibilities:
- Fetch trial protocol from ClinicalTrials.gov or database
- Parse inclusion/exclusion criteria
- Extract structured requirements (age, gender, conditions, lab values)
- Return machine-readable eligibility criteria for pattern matching

NOTE: In production, would use LLM (GPT-4, Claude) to parse natural language criteria.
For hackathon, uses structured field extraction from trial data.
"""

from uagents import Agent, Context, Protocol
import logging
import time
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

from agents.models import EligibilityRequest, EligibilityCriteria, AgentStatus
from agents.config import AgentConfig, AgentRegistry
from agentverse_config import (
    get_agent_address,
    is_agentverse_mode,
    get_agents_to_talk_to,
    validate_configuration
)

from data_loader import ClinicalDataLoader
from trial_criteria_mapper import TrialCriteriaMapper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

config = AgentConfig.get_agent_config("eligibility")
agent = Agent(**config)

# Initialize the official Fetch.AI chat protocol
chat_proto = Protocol(spec=chat_protocol_spec)

agent_state = {
    "requests_processed": 0,
    "start_time": time.time(),
    "data_loader": None,
    "trial_cache": {},
    "criteria_mapper": None,
    "agentverse_addresses": {},
    "is_agentverse": False,
    "coordinator_address": None
}


@agent.on_event("startup")
async def startup(ctx: Context):
    logger.info(f"✓ Eligibility Agent started: {ctx.agent.address}")
    AgentRegistry.register("eligibility", ctx.agent.address)
    agent_state["data_loader"] = ClinicalDataLoader()
    agent_state["criteria_mapper"] = TrialCriteriaMapper()

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
                        text="Hello from Eligibility Agent! Ready to extract and parse trial eligibility criteria!"
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

@agent.on_message(model=EligibilityRequest)
async def handle_eligibility_request(ctx: Context, sender: str, msg: EligibilityRequest):
    """Extract structured eligibility criteria from trial"""
    logger.info(f"  → Eligibility Agent processing: {msg.trial_id}")

    try:
        # Check cache
        if msg.trial_id in agent_state["trial_cache"]:
            trial_data = agent_state["trial_cache"][msg.trial_id]
        elif msg.trial_data:
            trial_data = msg.trial_data
            agent_state["trial_cache"][msg.trial_id] = trial_data
        else:
            # Fetch from data loader
            data_loader = agent_state["data_loader"]
            trials_df = data_loader.generate_synthetic_trials("diabetes", 100)
            matching = trials_df[trials_df['nct_id'] == msg.trial_id]
            trial_data = matching.iloc[0].to_dict() if not matching.empty else trials_df.iloc[0].to_dict()
            agent_state["trial_cache"][msg.trial_id] = trial_data

        # Extract criteria
        criteria = extract_criteria(trial_data)
        agent_state["requests_processed"] += 1

        logger.info(f"  ✓ Extracted criteria: age {criteria.age_range}, {len(criteria.inclusion_criteria)} criteria")
        await ctx.send(sender, criteria)

    except Exception as e:
        logger.error(f"Error in eligibility extraction: {e}")
        error_criteria = EligibilityCriteria(
            trial_id=msg.trial_id,
            inclusion_criteria=["Error"],
            exclusion_criteria=[],
            age_range={"min": 18, "max": 99},
            conditions=[],
            metadata={"error": str(e)}
        )
        await ctx.send(sender, error_criteria)


def extract_criteria(trial_data: dict) -> EligibilityCriteria:
    """
    Extract structured criteria from trial data WITH medical codes.

    Uses TrialCriteriaMapper to convert text criteria into ICD-10, SNOMED,
    LOINC, and RxNorm codes.
    """
    # Get basic info
    age_range = {
        "min": int(trial_data.get("min_age", 18)),
        "max": int(trial_data.get("max_age", 99))
    }

    gender = trial_data.get("gender")
    if gender and gender.lower() not in ["all", "both"]:
        gender = gender.capitalize()
    else:
        gender = None

    condition = trial_data.get("condition", "")
    conditions = [condition] if condition else []

    inclusion_raw = trial_data.get("inclusion_criteria", [])
    if isinstance(inclusion_raw, str):
        inclusion_criteria = [c.strip() for c in inclusion_raw.split(";") if c.strip()]
    else:
        inclusion_criteria = inclusion_raw if isinstance(inclusion_raw, list) else []

    # NEW: Use TrialCriteriaMapper to extract medical codes
    mapper = agent_state.get("criteria_mapper")
    if mapper is None:
        # Fallback if mapper not initialized
        mapper = TrialCriteriaMapper()

    # Combine condition and inclusion criteria for mapping
    all_criteria_text = [condition] + inclusion_criteria if condition else inclusion_criteria

    # Map to medical codes
    mapped_codes = mapper.map_criteria_to_codes(all_criteria_text)

    # Parse lab requirements based on condition (backward compatibility)
    lab_requirements = {}
    if "diabetes" in condition.lower():
        lab_requirements["HbA1c"] = {"min": 6.5, "max": 10.0}
    if "cardiovascular" in condition.lower():
        lab_requirements["cholesterol"] = {"min": 200, "max": 300}
    if "hypertension" in condition.lower():
        lab_requirements["blood_pressure_systolic"] = {"min": 140, "max": 180}

    # Override age/gender from mapped data if available
    if mapped_codes["demographics"]["age_range"]:
        age_range = mapped_codes["demographics"]["age_range"]
    if mapped_codes["demographics"]["gender"]:
        gender = mapped_codes["demographics"]["gender"]

    return EligibilityCriteria(
        trial_id=trial_data.get("nct_id", "UNKNOWN"),
        inclusion_criteria=inclusion_criteria,
        exclusion_criteria=[],
        age_range=age_range,
        gender=gender,
        conditions=conditions,
        lab_requirements=lab_requirements,
        medications=[],

        # NEW: Add medical codes
        inclusion_codes=mapped_codes["inclusion_codes"],
        exclusion_codes=mapped_codes["exclusion_codes"],
        found_terms=mapped_codes["found_terms"],

        metadata={
            "phase": trial_data.get("phase", "Unknown"),
            "status": trial_data.get("status", "Unknown"),
            "enrollment_target": trial_data.get("enrollment_target", 0),
            "code_extraction": "enabled"
        }
    )


@agent.on_message(model=AgentStatus)
async def handle_status(ctx: Context, sender: str, msg: AgentStatus):
    await ctx.send(sender, AgentStatus(
        agent_name="eligibility_agent",
        status="healthy",
        address=agent.address,
        uptime=time.time() - agent_state["start_time"],
        requests_processed=agent_state["requests_processed"],
        metadata={"cached_trials": len(agent_state["trial_cache"])}
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
            logger.info(f"💬 Eligibility Agent received chat message from {sender}: {item.text}")

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
    logger.info(f"✓ Eligibility received acknowledgement from {sender} for message: {msg.acknowledged_msg_id}")


# Include chat protocol in agent
agent.include(chat_proto, publish_manifest=True)


if __name__ == "__main__":
    agent.run()
