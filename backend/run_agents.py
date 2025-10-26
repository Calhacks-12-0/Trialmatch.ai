"""
Agent Bureau Runner: Runs all 8 Fetch.ai agents in a single process.

This script starts all agents using Fetch.ai's Bureau, which manages
multiple agents in one process. This is ideal for development and demos.

For production, each agent should run in a separate process.

Usage:
    python run_agents.py
"""

from uagents import Bureau
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import all agents
try:
    from agents.coordinator_agent import agent as coordinator
    from agents.eligibility_agent import agent as eligibility
    from agents.pattern_agent import agent as pattern
    from agents.discovery_agent import agent as discovery
    from agents.matching_agent import agent as matching
    from agents.site_agent import agent as site
    from agents.prediction_agent import agent as prediction
    from agents.validation_agent import agent as validation
except ImportError as e:
    logger.error(f"Failed to import agents: {e}")
    logger.error("Make sure you're running from the backend/ directory")
    sys.exit(1)


def main():
    """Run all agents in a Bureau"""

    logger.info("=" * 70)
    logger.info("STARTING TRIALMATCH AI AGENT NETWORK")
    logger.info("=" * 70)
    logger.info("")
    logger.info("Initializing 8-agent system:")
    logger.info("  1. Coordinator Agent (Port 8000) - Orchestrates workflow")
    logger.info("  2. Eligibility Agent (Port 8001) - Extracts trial criteria with codes")
    logger.info("  3. Pattern Agent (Port 8002) - Matches Conway patterns")
    logger.info("  4. Discovery Agent (Port 8003) - Finds patient candidates")
    logger.info("  5. Matching Agent (Port 8004) - Scores patients")
    logger.info("  6. Site Agent (Port 8005) - Recommends sites")
    logger.info("  7. Prediction Agent (Port 8006) - Forecasts enrollment")
    logger.info("  8. Validation Agent (Port 8007) - Validates exclusion criteria")
    logger.info("")
    logger.info("=" * 70)
    logger.info("")

    # Create Bureau
    bureau = Bureau(port=8001)  # Bureau control port

    # Add all agents
    bureau.add(coordinator)
    bureau.add(eligibility)
    bureau.add(pattern)
    bureau.add(discovery)
    bureau.add(matching)
    bureau.add(site)
    bureau.add(prediction)
    bureau.add(validation)

    logger.info("✓ All agents registered with Bureau")
    logger.info("")
    logger.info("Starting agents...")
    logger.info("Press Ctrl+C to stop all agents")
    logger.info("=" * 70)
    logger.info("")

    try:
        # Run all agents
        bureau.run()
    except KeyboardInterrupt:
        logger.info("")
        logger.info("=" * 70)
        logger.info("Shutting down agent network...")
        logger.info("=" * 70)
        sys.exit(0)


if __name__ == "__main__":
    main()
