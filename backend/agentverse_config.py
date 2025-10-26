"""
Agentverse Agent Address Configuration

IMPORTANT: After deploying each agent to Agentverse, update the addresses below
with the actual Agentverse addresses from the deployment logs.

Example Agentverse address format:
"agent1qf8n9q8ndlfvphmnwjzj9p077yq0m6kqc22se9g89y5en22sc38ck4p4e8d"

How to get addresses:
1. Deploy agent to Agentverse
2. Copy address from startup logs: "My address is agent1q..."
3. Paste address below
4. Redeploy all agents that need to communicate with updated addresses
"""

# ============================================================================
# AGENTVERSE AGENT ADDRESSES - UPDATE THESE AFTER DEPLOYMENT
# ============================================================================

AGENTVERSE_ADDRESSES = {
    "coordinator": "agent1q0t5trykueswlfvskzezq5avpwkuvrh7rws58t9mka3fsngueef96ej7w7c",  # Get from Inspector
    "eligibility": "agent1qdd8ytcnfm6uuhtr647wchelc2x7musj62xf8xa7qf9nusrl8hnvke0skte",  # Get from Inspector
    "pattern": "agent1qt59qwanc0ur9cxu83gruz8l7upyyx4vwuwctklyl8msfdh60kyuur87r5n",      # Get from Inspector
    "discovery": "agent1qfd0tuljxdfvx74heq47ksdafjvschrkjn6kppllr2d7kjrhml9eyta49wj",    # Get from Inspector
    "matching": "agent1q2q2ywhxvj9lt3tm862mzgre4n2f7st8ddnp5j862uzqq0neqzpvwm7y09u",     # Get from Inspector
    "validation": "agent1qdvp3zpu6y8vnsnzwghc7zfmdvfyssyk5ac83h886ptqsu2yyzvnq7evglv",   # Get from Inspector
    "site": "agent1qg5m40mncw5d06770gc6tfl0hr8hlze3fpwa93t8q24lzgfx60nv5pj3man",         # Get from Inspector
    "prediction": "agent1qt437ghfkwm5gusr9xgxm9tc8pgca04ffsqwctqvz3l5qxfaxsunqw7eny2"    # Get from Inspector
}

# ============================================================================
# AGENT COMMUNICATION MAP
# ============================================================================
# Defines which agents need to communicate with which other agents

AGENT_COMMUNICATION_MAP = {
    "coordinator": {
        # Coordinator needs to talk to all agents
        "talks_to": ["eligibility", "pattern", "discovery", "matching", "validation", "site", "prediction"],
        "receives_from": ["eligibility", "pattern", "discovery", "matching", "validation", "site", "prediction"]
    },
    "eligibility": {
        "talks_to": ["coordinator"],
        "receives_from": ["coordinator"]
    },
    "pattern": {
        "talks_to": ["coordinator"],
        "receives_from": ["coordinator"]
    },
    "discovery": {
        "talks_to": ["coordinator"],
        "receives_from": ["coordinator"]
    },
    "matching": {
        "talks_to": ["coordinator"],
        "receives_from": ["coordinator"]
    },
    "validation": {
        "talks_to": ["coordinator"],
        "receives_from": ["coordinator"]
    },
    "site": {
        "talks_to": ["coordinator"],
        "receives_from": ["coordinator"]
    },
    "prediction": {
        "talks_to": ["coordinator"],
        "receives_from": ["coordinator"]
    }
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_agent_address(agent_name: str) -> str:
    """
    Get Agentverse address for an agent.

    Args:
        agent_name: Name of the agent (e.g., "coordinator", "discovery")

    Returns:
        Agentverse address string or empty string if not configured
    """
    return AGENTVERSE_ADDRESSES.get(agent_name, "")

def is_agentverse_mode() -> bool:
    """
    Check if any Agentverse addresses are configured.

    Returns:
        True if at least one agent address is configured
    """
    return any(addr != "" for addr in AGENTVERSE_ADDRESSES.values())

def get_agents_to_talk_to(agent_name: str) -> list[str]:
    """
    Get list of agent names this agent should talk to.

    Args:
        agent_name: Name of the agent

    Returns:
        List of agent names
    """
    return AGENT_COMMUNICATION_MAP.get(agent_name, {}).get("talks_to", [])

def validate_configuration(agent_name: str) -> tuple[bool, str]:
    """
    Validate that required addresses are configured for an agent.

    Args:
        agent_name: Name of the agent to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not is_agentverse_mode():
        return True, "Running in local mode (no Agentverse addresses configured)"

    agents_needed = get_agents_to_talk_to(agent_name)
    missing = []

    for needed_agent in agents_needed:
        if not get_agent_address(needed_agent):
            missing.append(needed_agent)

    if missing:
        return False, f"Missing Agentverse addresses for: {', '.join(missing)}"

    return True, "Configuration valid"
