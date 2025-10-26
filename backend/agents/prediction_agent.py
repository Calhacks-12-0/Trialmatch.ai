"""
Prediction Agent: Forecasts enrollment timeline using pattern analysis.

Responsibilities:
- Receives matched patients and site recommendations
- Uses patient pattern success rates for prediction
- Forecasts enrollment timeline and milestones
- Identifies risk factors and optimization opportunities
- Returns enrollment forecast with confidence intervals

Uses historical pattern data to predict future enrollment.
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

from agents.models import PredictionRequest, EnrollmentForecast, AgentStatus
from agents.config import AgentConfig, AgentRegistry
from agentverse_config import (
    get_agent_address,
    is_agentverse_mode,
    get_agents_to_talk_to,
    validate_configuration
)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

config = AgentConfig.get_agent_config("prediction")
agent = Agent(**config)

# Initialize the official Fetch.AI chat protocol
chat_proto = Protocol(spec=chat_protocol_spec)

agent_state = {
    "requests_processed": 0,
    "start_time": time.time(),
    "agentverse_addresses": {},
    "is_agentverse": False,
    "coordinator_address": None
}


@agent.on_event("startup")
async def startup(ctx: Context):
    logger.info(f"✓ Prediction Agent started: {ctx.agent.address}")
    AgentRegistry.register("prediction", ctx.agent.address)
    

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
                        text="Hello from Prediction Agent! Ready to forecast enrollment timelines using pattern analysis!"
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

@agent.on_message(model=PredictionRequest)
async def handle_prediction_request(ctx: Context, sender: str, msg: PredictionRequest):
    """Generate enrollment forecast using pattern analysis"""
    logger.info(f"  → Prediction Agent forecasting for: {msg.trial_id}")

    try:
        target = msg.target_enrollment
        matches = msg.matches
        patterns = msg.patterns
        sites = msg.sites

        # Generate forecast
        forecast = generate_forecast(target, matches, patterns, sites)

        agent_state["requests_processed"] += 1
        logger.info(f"  ✓ Forecast: {forecast['predicted_enrollment']} patients in {forecast['estimated_weeks']:.1f} weeks")

        await ctx.send(sender, EnrollmentForecast(**forecast))

    except Exception as e:
        logger.error(f"Error in enrollment prediction: {e}")
        await ctx.send(sender, EnrollmentForecast(
            trial_id=msg.trial_id,
            target_enrollment=msg.target_enrollment,
            predicted_enrollment=0,
            estimated_weeks=0,
            confidence=0.0,
            weekly_enrollment_rate=0.0,
            milestones=[],
            risk_factors=[f"Error: {str(e)}"],
            recommendations=[],
            pattern_success_analysis={}
        ))


def generate_forecast(target: int, matches: list, patterns: list, sites: list) -> dict:
    """
    Generate enrollment forecast using patient pattern analysis.

    Methodology:
    1. Calculate average enrollment probability from patterns
    2. Estimate weekly enrollment rate based on site capacity
    3. Calculate timeline to reach target
    4. Generate milestone predictions
    5. Identify risks and recommendations
    """
    trial_id = matches[0].get("trial_id") if matches else "UNKNOWN"

    # Calculate pattern-based success rates
    if patterns:
        pattern_success_rates = [p.get("enrollment_success_rate", 0.75) for p in patterns]
        avg_success_rate = np.mean(pattern_success_rates)
    else:
        avg_success_rate = 0.75

    # Calculate eligible patient pool
    eligible_patients = len(matches)
    high_score_patients = sum(1 for m in matches if m.get("overall_score", 0) >= 0.8)

    # Estimate enrollment rate (patients per week)
    num_sites = len(sites)
    patients_per_site_per_week = 2.5  # Industry average
    weekly_enrollment_rate = num_sites * patients_per_site_per_week * avg_success_rate

    # Calculate timeline
    if weekly_enrollment_rate > 0:
        estimated_weeks = target / weekly_enrollment_rate
    else:
        estimated_weeks = 52  # Default 1 year

    # Adjust for realistic constraints
    estimated_weeks = max(estimated_weeks, 4)  # Minimum 4 weeks
    estimated_weeks = min(estimated_weeks, 104)  # Maximum 2 years

    # Predicted enrollment (may be less than target if not enough eligible patients)
    predicted_enrollment = min(
        int(weekly_enrollment_rate * estimated_weeks),
        int(eligible_patients * avg_success_rate),
        target
    )

    # Generate milestones (25%, 50%, 75%, 100%)
    milestones = []
    for percentage in [25, 50, 75, 100]:
        milestone_enrollment = int(predicted_enrollment * percentage / 100)
        milestone_week = estimated_weeks * percentage / 100

        milestones.append({
            "week": round(milestone_week, 1),
            "enrollment": milestone_enrollment,
            "percentage": percentage,
            "cumulative": milestone_enrollment
        })

    # Calculate confidence based on multiple factors
    confidence_factors = []

    # Factor 1: Eligible patient pool
    pool_confidence = min(eligible_patients / target, 1.0) if target > 0 else 0.5
    confidence_factors.append(pool_confidence * 0.3)

    # Factor 2: Pattern success rate
    confidence_factors.append(avg_success_rate * 0.3)

    # Factor 3: High-score patients
    high_score_ratio = high_score_patients / max(eligible_patients, 1)
    confidence_factors.append(high_score_ratio * 0.2)

    # Factor 4: Site coverage
    site_confidence = min(num_sites / 5, 1.0)  # Optimal at 5+ sites
    confidence_factors.append(site_confidence * 0.2)

    overall_confidence = sum(confidence_factors)

    # Identify risk factors
    risk_factors = []

    if eligible_patients < target:
        risk_factors.append(f"Limited patient pool: {eligible_patients} eligible vs {target} target")

    if num_sites < 3:
        risk_factors.append(f"Few sites: Only {num_sites} recommended sites")

    if avg_success_rate < 0.7:
        risk_factors.append(f"Low historical success rate: {avg_success_rate:.0%}")

    if estimated_weeks > 52:
        risk_factors.append(f"Long timeline: {estimated_weeks:.0f} weeks exceeds 1 year")

    if high_score_ratio < 0.5:
        risk_factors.append("Less than 50% of candidates have high match scores")

    # Generate recommendations
    recommendations = []

    if num_sites < 5:
        recommendations.append(f"Expand to {5 - num_sites} additional sites to accelerate enrollment")

    if eligible_patients < target * 1.5:
        recommendations.append("Broaden eligibility criteria to increase patient pool")

    if avg_success_rate < 0.8:
        recommendations.append("Focus outreach on high-scoring patients (>0.8) first")

    if estimated_weeks > 40:
        recommendations.append("Consider patient referral incentive program")

    recommendations.append("Use pattern insights to optimize recruitment messaging")

    # Pattern success analysis
    pattern_analysis = {
        "total_patterns_used": len(patterns),
        "average_success_rate": round(avg_success_rate, 3),
        "best_pattern_success": round(max(pattern_success_rates, default=0.75), 3),
        "worst_pattern_success": round(min(pattern_success_rates, default=0.75), 3),
        "eligible_patient_pool": eligible_patients,
        "high_confidence_patients": high_score_patients
    }

    return {
        "trial_id": trial_id,
        "target_enrollment": target,
        "predicted_enrollment": predicted_enrollment,
        "estimated_weeks": round(estimated_weeks, 1),
        "confidence": round(overall_confidence, 3),
        "weekly_enrollment_rate": round(weekly_enrollment_rate, 1),
        "milestones": milestones,
        "risk_factors": risk_factors[:5],  # Top 5
        "recommendations": recommendations[:5],  # Top 5
        "pattern_success_analysis": pattern_analysis
    }


@agent.on_message(model=AgentStatus)
async def handle_status(ctx: Context, sender: str, msg: AgentStatus):
    await ctx.send(sender, AgentStatus(
        agent_name="prediction_agent",
        status="healthy",
        address=agent.address,
        uptime=time.time() - agent_state["start_time"],
        requests_processed=agent_state["requests_processed"],
        metadata={}
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
            logger.info(f"💬 Prediction Agent received chat message from {sender}: {item.text}")

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
    logger.info(f"✓ Prediction received acknowledgement from {sender} for message: {msg.acknowledged_msg_id}")


# Include chat protocol in agent
agent.include(chat_proto, publish_manifest=True)


if __name__ == "__main__":
    agent.run()