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

from uagents import Agent, Context
import logging
import time
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.models import EligibilityRequest, EligibilityCriteria, AgentStatus
from agents.config import AgentConfig, AgentRegistry
from data_loader import ClinicalDataLoader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

config = AgentConfig.get_agent_config("eligibility")
agent = Agent(**config)

agent_state = {
    "requests_processed": 0,
    "start_time": time.time(),
    "data_loader": None,
    "trial_cache": {}
}


@agent.on_event("startup")
async def startup(ctx: Context):
    logger.info(f"✓ Eligibility Agent started: {agent.address}")
    AgentRegistry.register("eligibility", agent.address)
    agent_state["data_loader"] = ClinicalDataLoader()


@agent.on_query(model=EligibilityRequest, replies={EligibilityCriteria})
async def handle_eligibility_request(ctx: Context, sender: str, msg: EligibilityRequest) -> EligibilityCriteria:
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
        return criteria

    except Exception as e:
        logger.error(f"Error in eligibility extraction: {e}")
        return EligibilityCriteria(
            trial_id=msg.trial_id,
            inclusion_criteria=["Error"],
            exclusion_criteria=[],
            age_range={"min": 18, "max": 99},
            conditions=[],
            metadata={"error": str(e)}
        )


def extract_criteria(trial_data: dict) -> EligibilityCriteria:
    """Extract structured criteria from trial data"""
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

    # Parse lab requirements based on condition
    lab_requirements = {}
    if "diabetes" in condition.lower():
        lab_requirements["HbA1c"] = {"min": 6.5, "max": 10.0}
    if "cardiovascular" in condition.lower():
        lab_requirements["cholesterol"] = {"min": 200, "max": 300}
    if "hypertension" in condition.lower():
        lab_requirements["blood_pressure_systolic"] = {"min": 140, "max": 180}

    return EligibilityCriteria(
        trial_id=trial_data.get("nct_id", "UNKNOWN"),
        inclusion_criteria=inclusion_criteria,
        exclusion_criteria=[],
        age_range=age_range,
        gender=gender,
        conditions=conditions,
        lab_requirements=lab_requirements,
        medications=[],
        metadata={
            "phase": trial_data.get("phase", "Unknown"),
            "status": trial_data.get("status", "Unknown"),
            "enrollment_target": trial_data.get("enrollment_target", 0)
        }
    )


@agent.on_query(model=AgentStatus, replies={AgentStatus})
async def handle_status(ctx: Context, sender: str, msg: AgentStatus) -> AgentStatus:
    return AgentStatus(
        agent_name="eligibility_agent",
        status="healthy",
        address=agent.address,
        uptime=time.time() - agent_state["start_time"],
        requests_processed=agent_state["requests_processed"],
        metadata={"cached_trials": len(agent_state["trial_cache"])}
    )


if __name__ == "__main__":
    agent.run()
