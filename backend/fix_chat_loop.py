#!/usr/bin/env python3
"""
Fix the chat message loop in all agents by preventing them from responding
to incoming ChatMessages (they should only send acknowledgements).
"""

import re
import os

AGENTS = [
    "eligibility_agent.py",
    "pattern_agent.py",
    "discovery_agent.py",
    "matching_agent.py",
    "validation_agent.py",
    "site_agent.py",
    "prediction_agent.py"
]

def fix_agent_chat_handler(filepath):
    """Fix the chat handler in an agent file"""
    with open(filepath, 'r') as f:
        content = f.read()

    # Pattern to match the chat message handler
    # We need to remove the response ChatMessage sending
    pattern = r'(@chat_proto\.on_message\(ChatMessage\).*?)(await ctx\.send\(sender, ack\))(.*?)(# Update stats|@chat_proto\.on_message\(ChatAcknowledgement\))'

    def replacement(match):
        handler_start = match.group(1)
        ack_send = match.group(2)
        middle_content = match.group(3)
        next_section = match.group(4)

        # Check if this handler already has the fix
        if "NOTE: We don't send a response ChatMessage" in middle_content:
            print(f"  Already fixed: {filepath}")
            return match.group(0)

        # Create fixed handler
        fixed_middle = '''

            # NOTE: We don't send a response ChatMessage to avoid infinite loops.
            # Actual work requests should use specific message types (EligibilityRequest, etc.),
            # not ChatMessage.


'''
        return handler_start + ack_send + fixed_middle + next_section

    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    if new_content != content:
        with open(filepath, 'w') as f:
            f.write(new_content)
        print(f"✓ Fixed: {filepath}")
        return True
    else:
        print(f"  No changes needed: {filepath}")
        return False

def main():
    print("Fixing chat loop in all agents...")
    print("=" * 60)

    agents_dir = os.path.join(os.path.dirname(__file__), "agents")
    fixed_count = 0

    for agent_file in AGENTS:
        filepath = os.path.join(agents_dir, agent_file)
        if os.path.exists(filepath):
            if fix_agent_chat_handler(filepath):
                fixed_count += 1
        else:
            print(f"  Not found: {filepath}")

    print("=" * 60)
    print(f"Fixed {fixed_count} agents")
    print("\nRestart all agents to apply the fix!")

if __name__ == "__main__":
    main()
