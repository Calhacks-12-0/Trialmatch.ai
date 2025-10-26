"""
Template for adding Agentverse support to agents.

This shows the pattern to follow for all non-coordinator agents.
They receive chat messages from the coordinator and can respond.
"""

# ============================================================================
# 1. ADD THESE IMPORTS AT THE TOP OF YOUR AGENT FILE
# ============================================================================

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agentverse_config import (
    get_agent_address,
    is_agentverse_mode,
    get_agents_to_talk_to,
    validate_configuration
)

# ============================================================================
# 2. ADD TO AGENT STATE
# ============================================================================

agent_state = {
    # ... existing fields ...
    "agentverse_addresses": {},  # Store Agentverse addresses
    "is_agentverse": False,
    "coordinator_address": None  # Store coordinator address
}

# ============================================================================
# 3. UPDATE STARTUP HANDLER
# ============================================================================

@agent.on_event("startup")
async def startup(ctx: Context):
    """Initialize agent on startup"""
    logger.info(f"✓ Agent started: {ctx.agent.address}")
    AgentRegistry.register("agent_name", ctx.agent.address)  # Replace with actual agent name

    # Check if running in Agentverse mode
    agent_state["is_agentverse"] = is_agentverse_mode()

    if agent_state["is_agentverse"]:
        logger.info("🌐 Running in AGENTVERSE MODE")

        # Get coordinator address (most agents talk back to coordinator)
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
                        text=f"Hello from [Agent Name]! Ready to process requests."
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

# ============================================================================
# 4. CHAT MESSAGE HANDLER ALREADY EXISTS (from previous updates)
# ============================================================================

# The chat protocol handlers are already in place from the previous updates.
# They will automatically handle messages from the coordinator and send
# acknowledgements and responses.

@chat_proto.on_message(ChatMessage)
async def handle_chat_message(ctx: Context, sender: str, msg: ChatMessage):
    """Handle incoming chat messages using official Fetch.AI protocol"""
    for item in msg.content:
        if isinstance(item, TextContent):
            logger.info(f"💬 Agent received chat message from {sender}: {item.text}")

            # Send acknowledgment
            ack = ChatAcknowledgement(
                timestamp=datetime.utcnow(),
                acknowledged_msg_id=msg.msg_id
            )
            await ctx.send(sender, ack)

            # Process and respond
            response_text = f"Agent received: {item.text}\\n\\nAgent is ready!"

            response = ChatMessage(
                timestamp=datetime.utcnow(),
                msg_id=uuid4(),
                content=[TextContent(type="text", text=response_text)]
            )
            await ctx.send(sender, response)

            agent_state["requests_processed"] += 1

@chat_proto.on_message(ChatAcknowledgement)
async def handle_acknowledgement(ctx: Context, sender: str, msg: ChatAcknowledgement):
    """Handle chat acknowledgements"""
    logger.info(f"✓ Agent received acknowledgement from {sender}")
