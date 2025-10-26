"""
Helper script to add chat protocol to all agents.
Run this once to update all agent files with chat capabilities.
"""

import os
import re

AGENTS_DIR = "agents"

# Agents to update (excluding discovery and matching which are already done)
AGENTS_TO_UPDATE = [
    ("pattern", "pattern_agent"),
    ("coordinator", "coordinator_agent"),
    ("eligibility", "eligibility_agent"),
    ("site", "site_agent"),
    ("prediction", "prediction_agent"),
    ("validation", "validation_agent")
]

IMPORT_CODE = """from chat_protocol import AgentChatProtocol
from chat_utils import format_agent_response, parse_user_query"""

CHAT_INIT_TEMPLATE = """chat = AgentChatProtocol(agent_name="{agent_key}")"""

CHAT_HANDLER_TEMPLATE = '''

# ============================================================================
# CHAT PROTOCOL HANDLER
# ============================================================================

@chat.on_chat_message
async def handle_chat_message(ctx: Context, sender: str, message: str, msg_id: str):
    """Handle natural language chat queries"""
    logger.info(f"  💬 {agent_display} received chat: '{{message}}' from {{sender}}")

    try:
        response_text = f"{agent_display} received your message: {{message}}\\n\\nThis agent is ready to process queries!"

        # Send chat response
        await chat.send_response(ctx, sender, response_text)

        if "agent_state" in globals() and "requests_processed" in agent_state:
            agent_state["requests_processed"] += 1

    except Exception as e:
        logger.error(f"Error handling chat message: {{e}}")
        await chat.send_response(ctx, sender, f"❌ Error: {{str(e)}}")


# Include chat protocol in agent
agent.include(chat.get_protocol(), publish_manifest=True)
'''

def add_chat_to_agent(agent_key, agent_file_name):
    """Add chat protocol to a single agent file"""
    file_path = os.path.join(AGENTS_DIR, f"{agent_file_name}.py")

    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False

    with open(file_path, 'r') as f:
        content = f.read()

    # Check if already has chat
    if "chat_protocol import" in content:
        print(f"✓ {agent_file_name} already has chat protocol")
        return True

    # 1. Add imports after existing imports
    import_pattern = r'(from agents\.config import.*?\n)'
    if re.search(import_pattern, content):
        content = re.sub(
            import_pattern,
            r'\1' + IMPORT_CODE + '\n',
            content,
            count=1
        )
    else:
        print(f"⚠️  Could not find import location in {agent_file_name}")
        return False

    # 2. Add chat initialization after agent creation
    agent_pattern = r'(agent = Agent\(\*\*config\))'
    chat_init = CHAT_INIT_TEMPLATE.format(agent_key=agent_key)
    if re.search(agent_pattern, content):
        content = re.sub(
            agent_pattern,
            r'\1\n' + chat_init,
            content,
            count=1
        )

    # 3. Add chat handler before if __name__ == "__main__"
    agent_display = agent_file_name.replace('_', ' ').title()
    chat_handler = CHAT_HANDLER_TEMPLATE.format(agent_display=agent_display)

    main_pattern = r'(\n\nif __name__ == "__main__":)'
    if re.search(main_pattern, content):
        content = re.sub(
            main_pattern,
            chat_handler + r'\1',
            content,
            count=1
        )
    else:
        # If no main block, add at end
        content += chat_handler

    # Write back
    with open(file_path, 'w') as f:
        f.write(content)

    print(f"✓ Added chat protocol to {agent_file_name}")
    return True


def main():
    print("=" * 60)
    print("Adding Chat Protocol to All Agents")
    print("=" * 60)

    success_count = 0
    for agent_key, agent_file in AGENTS_TO_UPDATE:
        if add_chat_to_agent(agent_key, agent_file):
            success_count += 1

    print("=" * 60)
    print(f"✓ Successfully updated {success_count}/{len(AGENTS_TO_UPDATE)} agents")
    print("=" * 60)


if __name__ == "__main__":
    main()
