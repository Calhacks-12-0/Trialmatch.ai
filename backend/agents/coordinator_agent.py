from uagents import Agent, Context, Model, Protocol
from typing import List, Dict, Any
import json
import asyncio
import logging

logger = logging.getLogger(__name__)

# Define message models for agent communication
class PatternDiscoveryRequest(Model):
    patient_data: Dict
    trial_id: str

class PatternDiscoveryResponse(Model):
    patterns: List[Dict]
    embeddings: List[List[float]]
    metadata: Dict

class TrialMatchRequest(Model):
    trial_id: str
    patterns: List[Dict]

class MatchResults(Model):
    trial_id: str
    matches: List[Dict]
    total_eligible: int
    sites: List[Dict]

# Initialize coordinator agent
coordinator = Agent(
    name="trial_coordinator",
    seed="coordinator_seed_main",
    port=8000,
    endpoint=["http://localhost:8000/submit"]
)

# Store for inter-agent communication
agent_store = {}

@coordinator.on_event("startup")
async def startup(ctx: Context):
    """Initialize coordinator on startup"""
    logger.info(f"Coordinator agent started with address: {coordinator.address}")
    agent_store['active_queries'] = {}
    agent_store['pattern_cache'] = {}

@coordinator.on_query(model=TrialMatchRequest)
async def handle_trial_match(ctx: Context, sender: str, msg: TrialMatchRequest):
    """Main entry point for trial matching queries"""
    logger.info(f"Received trial match request for: {msg.trial_id}")
    
    # Check if patterns are cached
    if msg.trial_id in agent_store.get('pattern_cache', {}):
        patterns = agent_store['pattern_cache'][msg.trial_id]
        logger.info("Using cached patterns")
    else:
        # Request pattern discovery from pattern agent
        pattern_response = await ctx.send(
            "agent1qf7t4q4h8lxwnjxhgvy3nwgfx0t3q8xn9c3sm8c",  # Pattern agent address
            PatternDiscoveryRequest(
                patient_data=msg.patterns,
                trial_id=msg.trial_id
            )
        )
        patterns = pattern_response.patterns if pattern_response else msg.patterns
    
    # Process matches
    eligible_patients = []
    for pattern in patterns:
        if pattern.get('enrollment_success_rate', 0) > 0.6:
            eligible_patients.extend([
                {
                    'patient_id': f"P{i:06d}",
                    'pattern_id': pattern['pattern_id'],
                    'match_score': pattern.get('enrollment_success_rate', 0.75)
                }
                for i in range(pattern.get('size', 0))[:10]  # Limit for demo
            ])
    
    # Generate site recommendations
    sites = [
        {'name': 'Memorial Hospital', 'location': 'New York, NY', 'capacity': 85, 'trials': 12},
        {'name': 'City Medical Center', 'location': 'Los Angeles, CA', 'capacity': 92, 'trials': 8},
        {'name': 'Regional Clinic', 'location': 'Chicago, IL', 'capacity': 78, 'trials': 6}
    ]
    
    result = MatchResults(
        trial_id=msg.trial_id,
        matches=eligible_patients[:100],  # Top 100 matches
        total_eligible=len(eligible_patients),
        sites=sites
    )
    
    logger.info(f"Found {result.total_eligible} eligible patients")
    return result

# Run the agent
if __name__ == "__main__":
    coordinator.run()