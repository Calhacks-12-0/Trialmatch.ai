"""
Script to add Agentverse startup logic to all remaining agent files.
"""

AGENTS = {
    "matching": "Ready to score patient candidates using Pattern Discovery similarity metrics!",
    "eligibility": "Ready to extract and parse trial eligibility criteria!",
    "pattern": "Ready to match pre-discovered patient patterns to trial criteria!",
    "prediction": "Ready to forecast enrollment timelines using pattern analysis!",
    "site": "Ready to recommend trial sites based on feasibility and patient geography!",
    "validation": "Ready to validate patient matches against exclusion criteria!"
}

STARTUP_TEMPLATE = '''@agent.on_event("startup")
async def startup(ctx: Context):
    logger.info(f"✓ {agent_name_cap} Agent started: {{ctx.agent.address}}")
    AgentRegistry.register("{agent_name}", ctx.agent.address)
    {original_content}

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
                        text="Hello from {agent_name_cap} Agent! {greeting}"
                    )]
                )
                await ctx.send(coordinator_addr, greeting)
                logger.info(f"  ✓ Sent greeting to coordinator")
            except Exception as e:
                logger.error(f"  ❌ Failed to send greeting to coordinator: {{e}}")
        else:
            logger.warning(f"  ⚠ Missing coordinator address - update agentverse_config.py")
    else:
        logger.info("🏠 Running in LOCAL MODE")
'''

# Original content for each agent's startup
ORIGINAL_CONTENT = {
    "matching": "",
    "eligibility": '''agent_state["data_loader"] = ClinicalDataLoader()
    agent_state["criteria_mapper"] = TrialCriteriaMapper()''',
    "pattern": '''# Patterns will be loaded from context storage when needed''',
    "prediction": "",
    "site": '''# Initialize feasibility scorer
    agent_state["feasibility_scorer"] = SiteFeasibilityScorer()''',
    "validation": ""
}

def update_agent(agent_name, greeting):
    """Update an agent's startup function."""
    filepath = f"agents/{agent_name}_agent.py"

    try:
        with open(filepath, 'r') as f:
            content = f.read()

        # Find and extract original startup content (lines between startup def and next @)
        import re

        # Find the startup function
        pattern = r'@agent\.on_event\("startup"\)\s+async def startup\(ctx: Context\):\s+(.*?)(?=\n\n@|\nif __name__|$)'
        match = re.search(pattern, content, re.DOTALL)

        if match:
            original = ORIGINAL_CONTENT.get(agent_name, "")

            new_startup = STARTUP_TEMPLATE.format(
                agent_name=agent_name,
                agent_name_cap=agent_name.capitalize(),
                greeting=greeting,
                original_content=original
            )

            # Replace the old startup with new one
            updated_content = re.sub(
                pattern,
                new_startup.rstrip(),
                content,
                flags=re.DOTALL
            )

            # Ensure proper address logging
            updated_content = updated_content.replace(
                f'logger.info(f"✓ {agent_name.capitalize()} Agent started: {{agent.address}}")',
                f'logger.info(f"✓ {agent_name.capitalize()} Agent started: {{ctx.agent.address}}")'
            )

            with open(filepath, 'w') as f:
                f.write(updated_content)

            print(f"✓ Updated {agent_name}_agent.py startup function")
            return True
        else:
            print(f"⚠ Could not find startup function in {agent_name}_agent.py")
            return False

    except Exception as e:
        print(f"❌ Error updating {agent_name}_agent.py: {e}")
        return False

if __name__ == "__main__":
    print("Finalizing agent startup functions...")
    print("=" * 60)

    success_count = 0
    for agent_name, greeting in AGENTS.items():
        if update_agent(agent_name, greeting):
            success_count += 1

    print("=" * 60)
    print(f"✓ Updated {success_count}/{len(AGENTS)} agent startup functions")

    if success_count == len(AGENTS):
        print("\n🎉 All agents are now ready for Agentverse deployment!")
        print("\nNext steps:")
        print("1. Test locally: python agents/coordinator_agent.py")
        print("2. Deploy to Agentverse following AGENTVERSE_DEPLOYMENT_GUIDE.md")
    else:
        print("\n⚠ Some agents need manual review")
