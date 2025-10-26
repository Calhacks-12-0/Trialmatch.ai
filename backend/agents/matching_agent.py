"""
Matching Agent: Scores patients using Pattern Discovery's similarity metrics.

Responsibilities:
- Receives patient candidates from Discovery Agent
- Scores each patient using Pattern Discovery embedding similarity
- Calculates eligibility score, enrollment probability
- Generates match reasons and risk factors
- Returns ranked list of patient matches

Uses Pattern Discovery's pre-computed embeddings for similarity calculation.
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

from agents.models import MatchingRequest, MatchingResponse, AgentStatus
from agents.config import AgentConfig, AgentRegistry
from agentverse_config import (
    get_agent_address,
    is_agentverse_mode,
    get_agents_to_talk_to,
    validate_configuration
)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

config = AgentConfig.get_agent_config("matching")
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
    logger.info(f"✓ Matching Agent started: {ctx.agent.address}")
    AgentRegistry.register("matching", ctx.agent.address)
    

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
                        text="Hello from Matching Agent! Ready to score patient candidates using Pattern Discovery similarity metrics!"
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

@agent.on_message(model=MatchingRequest)
async def handle_matching_request(ctx: Context, sender: str, msg: MatchingRequest):
    """Score patients using Pattern Discovery similarity metrics"""
    logger.info(f"  → Matching Agent scoring {len(msg.candidates)} candidates for: {msg.trial_id}")

    try:
        criteria = msg.eligibility_criteria
        candidates = msg.candidates
        patterns = msg.patterns

        # Score each candidate
        matches = score_candidates(candidates, criteria, patterns)

        # Calculate score distribution
        distribution = calculate_distribution(matches)

        agent_state["requests_processed"] += 1
        logger.info(f"  ✓ Scored {len(matches)} patients (avg score: {distribution.get('average', 0):.2f})")

        await ctx.send(sender, MatchingResponse(
            trial_id=msg.trial_id,
            matches=matches,
            total_scored=len(matches),
            score_distribution=distribution
        ))

    except Exception as e:
        logger.error(f"Error in patient matching: {e}")
        await ctx.send(sender, MatchingResponse(
            trial_id=msg.trial_id,
            matches=[],
            total_scored=0,
            score_distribution={"error": str(e)}
        ))


def score_candidates(candidates: list, criteria: dict, patterns: list) -> list:
    """
    Score each candidate using Pattern Discovery similarity metrics.

    Scoring components:
    1. Eligibility score: How well patient meets criteria
    2. Similarity score: Pattern Discovery embedding distance to pattern centroid
    3. Enrollment probability: Based on pattern success rate
    4. Overall score: Weighted combination
    """
    matches = []

    # Build pattern lookup for success rates
    pattern_lookup = {p.get("pattern_id"): p for p in patterns}

    for candidate in candidates:
        patient_id = candidate.get("patient_id")
        pattern_id = candidate.get("pattern_id")
        demographics = candidate.get("demographics", {})
        clinical_data = candidate.get("clinical_data", {})
        location = candidate.get("location", {})

        # Get associated pattern
        pattern = pattern_lookup.get(pattern_id, {})

        # Calculate eligibility score (0-1)
        eligibility_score = calculate_eligibility_score(demographics, clinical_data, criteria)

        # Calculate similarity score using Pattern Discovery embeddings (0-1)
        candidate_embedding = candidate.get("embedding", [])
        pattern_centroid = pattern.get("centroid", [])
        similarity_score = calculate_similarity(candidate_embedding, pattern_centroid)

        # Get enrollment probability from pattern
        enrollment_probability = pattern.get("enrollment_success_rate", 0.75)

        # Calculate overall score (weighted combination)
        overall_score = (
            eligibility_score * 0.4 +
            similarity_score * 0.3 +
            enrollment_probability * 0.3
        )

        # Generate match reasons
        match_reasons = generate_match_reasons(demographics, clinical_data, criteria, pattern)

        # Generate risk factors
        risk_factors = generate_risk_factors(demographics, clinical_data, criteria)

        match = {
            "patient_id": patient_id,
            "pattern_id": pattern_id,
            "overall_score": round(overall_score, 3),
            "eligibility_score": round(eligibility_score, 3),
            "similarity_score": round(similarity_score, 3),
            "enrollment_probability": round(enrollment_probability, 3),
            "demographics": demographics,
            "location": location,
            "match_reasons": match_reasons,
            "risk_factors": risk_factors
        }

        matches.append(match)

    # Sort by overall score descending
    matches.sort(key=lambda x: x["overall_score"], reverse=True)

    return matches


def calculate_eligibility_score(demographics: dict, clinical_data: dict, criteria: dict) -> float:
    """Calculate how well patient meets eligibility criteria"""
    score = 1.0

    # Age check
    age = demographics.get("age", 0)
    age_min = criteria.get("age_range", {}).get("min", 18)
    age_max = criteria.get("age_range", {}).get("max", 99)
    if not (age_min <= age <= age_max):
        score *= 0.5  # Penalize if outside range

    # Lab values check
    lab_requirements = criteria.get("lab_requirements", {})
    patient_labs = clinical_data.get("lab_values", {})

    for lab_name, lab_range in lab_requirements.items():
        if lab_name in patient_labs:
            value = patient_labs.get(lab_name)
            if isinstance(value, (int, float)):
                min_val = lab_range.get("min", 0)
                max_val = lab_range.get("max", 1000)
                if not (min_val <= value <= max_val):
                    score *= 0.8

    return max(score, 0.1)  # Minimum 0.1


def calculate_similarity(embedding1: list, embedding2: list) -> float:
    """Calculate cosine similarity between embeddings"""
    if not embedding1 or not embedding2:
        return 0.7  # Default

    try:
        arr1 = np.array(embedding1[:50])  # Use first 50 dimensions
        arr2 = np.array(embedding2[:50])

        # Cosine similarity
        dot_product = np.dot(arr1, arr2)
        norm1 = np.linalg.norm(arr1)
        norm2 = np.linalg.norm(arr2)

        if norm1 == 0 or norm2 == 0:
            return 0.7

        similarity = dot_product / (norm1 * norm2)
        # Normalize to 0-1
        return (similarity + 1) / 2

    except:
        return 0.7  # Fallback


def generate_match_reasons(demographics: dict, clinical_data: dict, criteria: dict, pattern: dict) -> list:
    """Generate human-readable match reasons"""
    reasons = []

    age = demographics.get("age")
    if age:
        reasons.append(f"Age {age} fits trial criteria")

    condition = clinical_data.get("primary_condition")
    if condition:
        reasons.append(f"Has {condition} diagnosis")

    enrollment_history = clinical_data.get("enrollment_history", 0)
    if enrollment_history > 0:
        reasons.append(f"Previous trial experience ({enrollment_history} trials)")

    pattern_success = pattern.get("enrollment_success_rate", 0)
    if pattern_success > 0.8:
        reasons.append(f"Similar patients have {pattern_success:.0%} success rate")

    return reasons[:4]  # Top 4 reasons


def generate_risk_factors(demographics: dict, clinical_data: dict, criteria: dict) -> list:
    """Identify potential enrollment risks"""
    risks = []

    age = demographics.get("age", 0)
    age_max = criteria.get("age_range", {}).get("max", 99)
    if age > age_max - 5:
        risks.append("Age near upper limit")

    enrollment_history = clinical_data.get("enrollment_history", 0)
    if enrollment_history == 0:
        risks.append("No previous trial experience")

    medications = clinical_data.get("medications", [])
    if len(medications) > 5:
        risks.append("Multiple medications may affect eligibility")

    return risks[:3]  # Top 3 risks


def calculate_distribution(matches: list) -> dict:
    """Calculate score distribution"""
    if not matches:
        return {"high": 0, "medium": 0, "low": 0, "average": 0.0}

    scores = [m["overall_score"] for m in matches]
    high = sum(1 for s in scores if s >= 0.8)
    medium = sum(1 for s in scores if 0.5 <= s < 0.8)
    low = sum(1 for s in scores if s < 0.5)

    return {
        "high": high,
        "medium": medium,
        "low": low,
        "average": round(np.mean(scores), 3)
    }


@agent.on_message(model=AgentStatus)
async def handle_status(ctx: Context, sender: str, msg: AgentStatus):
    await ctx.send(sender, AgentStatus(
        agent_name="matching_agent",
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
            logger.info(f"💬 Matching Agent received chat message from {sender}: {item.text}")

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
    logger.info(f"✓ Matching received acknowledgement from {sender} for message: {msg.acknowledged_msg_id}")


# Include chat protocol in agent
agent.include(chat_proto, publish_manifest=True)


if __name__ == "__main__":
    agent.run()
