"""
Script to apply Agentverse support to all remaining agents.

This script adds the necessary imports, state variables, and startup logic
to enable agents to work with Agentverse.
"""

import re

# Agent names and their descriptions for greeting messages
AGENTS = {
    "matching": "Ready to score patient candidates using Pattern Discovery similarity metrics!",
    "eligibility": "Ready to extract and parse trial eligibility criteria!",
    "pattern": "Ready to match pre-discovered patient patterns to trial criteria!",
    "prediction": "Ready to forecast enrollment timelines using pattern analysis!",
    "site": "Ready to recommend trial sites based on feasibility and patient geography!",
    "validation": "Ready to validate patient matches against exclusion criteria!"
}

def add_imports(agent_content):
    """Add Agentverse imports after existing imports."""
    # Find the last import statement
    import_pattern = r'(from agents\.config import.*?\n)'

    imports_to_add = '''from agentverse_config import (
    get_agent_address,
    is_agentverse_mode,
    get_agents_to_talk_to,
    validate_configuration
)
'''

    # Add after the config import
    agent_content = re.sub(
        import_pattern,
        r'\1' + imports_to_add + '\n',
        agent_content,
        count=1
    )

    return agent_content

def update_agent_state(agent_content):
    """Add Agentverse fields to agent_state."""
    # Find agent_state dictionary
    state_pattern = r'(agent_state = \{[^}]+)(\})'

    additions = ''',
    "agentverse_addresses": {},
    "is_agentverse": False,
    "coordinator_address": None'''

    agent_content = re.sub(
        state_pattern,
        r'\1' + additions + r'\2',
        agent_content
    )

    return agent_content

def update_startup_function(agent_content, agent_name, greeting_message):
    """Update startup function to add Agentverse support."""

    # Find the startup function
    startup_pattern = r'(@agent\.on_event\("startup"\)\s+async def startup\(ctx: Context\):\s+)(.*?)(\n\n@)'

    # Build the new startup content
    new_startup = r'''\1logger.info(f"✓ {agent_name} Agent started: {{ctx.agent.address}}")
    AgentRegistry.register("{agent_name}", ctx.agent.address)
    \2

    # Check if running in Agentverse mode
    agent_state["is_agentverse"] = is_agentverse_mode()

    if agent_state["is_agentverse"]:
        logger.info("🌐 Running in AGENTVERSE MODE")

        # Get coordinator address
        coordinator_addr = get_agent_address("coordinator")
        if coordinator_addr:
            agent_state["coordinator_address"] = coordinator_addr
            logger.info(f"  ✓ Loaded coordinator address: {{coordinator_addr[:20]}}...")

            # Send greeting to coordinator
            try:
                greeting = ChatMessage(
                    timestamp=datetime.utcnow(),
                    msg_id=uuid4(),
                    content=[TextContent(
                        type="text",
                        text="Hello from {agent_name_cap} Agent! {greeting_msg}"
                    )]
                )
                await ctx.send(coordinator_addr, greeting)
                logger.info(f"  ✓ Sent greeting to coordinator")
            except Exception as e:
                logger.error(f"  ❌ Failed to send greeting to coordinator: {{e}}")
        else:
            logger.warning(f"  ⚠ Missing coordinator address - update agentverse_config.py")
    else:
        logger.info("🏠 Running in LOCAL MODE")\3'''.format(
        agent_name=agent_name,
        agent_name_cap=agent_name.capitalize(),
        greeting_msg=greeting_message
    )

    agent_content = re.sub(
        startup_pattern,
        new_startup,
        agent_content,
        flags=re.DOTALL
    )

    return agent_content

def process_agent(agent_name, greeting_message):
    """Process a single agent file."""
    file_path = f"agents/{agent_name}_agent.py"

    try:
        with open(file_path, 'r') as f:
            content = f.read()

        # Apply transformations
        content = add_imports(content)
        content = update_agent_state(content)
        # Note: startup function is more complex, will do manually

        # Write back
        with open(file_path, 'w') as f:
            f.write(content)

        print(f"✓ Updated {agent_name}_agent.py")

    except Exception as e:
        print(f"❌ Error updating {agent_name}_agent.py: {e}")

if __name__ == "__main__":
    print("Applying Agentverse support to agents...")
    print("=" * 60)

    for agent_name, greeting in AGENTS.items():
        process_agent(agent_name, greeting)

    print("=" * 60)
    print("✓ All agents updated!")
    print("\nNote: Startup functions need manual verification.")
