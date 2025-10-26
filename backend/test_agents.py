"""
Test script to verify Fetch.ai agents are working correctly.

This script tests:
1. Agent imports
2. Agent initialization
3. Message model validation
4. Agent registry
5. Basic agent startup

Usage:
    python test_agents.py
"""

import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_imports():
    """Test that all required packages can be imported"""
    logger.info("Testing imports...")

    try:
        import uagents
        logger.info("✓ uagents imported successfully")
    except ImportError as e:
        logger.error(f"✗ Failed to import uagents: {e}")
        logger.error("  Fix: pip install uagents==0.11.0")
        return False

    try:
        import pydantic
        version = pydantic.VERSION
        logger.info(f"✓ pydantic {version} imported successfully")

        if version.startswith("2."):
            logger.warning("⚠ Warning: Pydantic 2.x detected. uagents requires 1.x")
            logger.warning("  Fix: pip install pydantic==1.10.9")
    except ImportError as e:
        logger.error(f"✗ Failed to import pydantic: {e}")
        return False

    try:
        import numpy
        logger.info("✓ numpy imported successfully")
    except ImportError:
        logger.error("✗ Failed to import numpy")
        return False

    try:
        import pandas
        logger.info("✓ pandas imported successfully")
    except ImportError:
        logger.error("✗ Failed to import pandas")
        return False

    logger.info("")
    return True


def test_agent_modules():
    """Test that all agent modules can be imported"""
    logger.info("Testing agent modules...")

    modules = [
        "agents.models",
        "agents.config",
        "agents.coordinator_agent",
        "agents.eligibility_agent",
        "agents.pattern_agent",
        "agents.discovery_agent",
        "agents.matching_agent",
        "agents.site_agent",
        "agents.prediction_agent"
    ]

    for module in modules:
        try:
            __import__(module)
            logger.info(f"✓ {module} imported successfully")
        except ImportError as e:
            logger.error(f"✗ Failed to import {module}: {e}")
            return False

    logger.info("")
    return True


def test_message_models():
    """Test that message models can be instantiated"""
    logger.info("Testing message models...")

    try:
        from agents.models import (
            UserQuery,
            EligibilityRequest,
            PatternRequest,
            DiscoveryRequest,
            MatchingRequest,
            SiteRequest,
            PredictionRequest
        )

        # Test UserQuery
        query = UserQuery(
            trial_id="NCT00123456",
            query="Find patients for diabetes trial",
            filters={}
        )
        logger.info(f"✓ UserQuery created: {query.trial_id}")

        # Test EligibilityRequest
        req = EligibilityRequest(trial_id="NCT00123456")
        logger.info(f"✓ EligibilityRequest created: {req.trial_id}")

        # Test PatternRequest
        pattern_req = PatternRequest(
            trial_id="NCT00123456",
            criteria={"age_range": {"min": 18, "max": 65}},
            min_pattern_size=50
        )
        logger.info(f"✓ PatternRequest created: {pattern_req.trial_id}")

        logger.info("✓ All message models validated")
        logger.info("")
        return True

    except Exception as e:
        logger.error(f"✗ Message model error: {e}")
        return False


def test_agent_config():
    """Test agent configuration"""
    logger.info("Testing agent configuration...")

    try:
        from agents.config import AgentConfig, AgentRegistry

        # Test config loading
        coordinator_config = AgentConfig.get_agent_config("coordinator")
        logger.info(f"✓ Coordinator config loaded: port {coordinator_config['port']}")

        eligibility_config = AgentConfig.get_agent_config("eligibility")
        logger.info(f"✓ Eligibility config loaded: port {eligibility_config['port']}")

        # Test all ports are unique
        all_ports = AgentConfig.get_all_ports()
        if len(all_ports) == len(set(all_ports)):
            logger.info(f"✓ All {len(all_ports)} ports are unique")
        else:
            logger.error("✗ Duplicate ports detected!")
            return False

        logger.info(f"  Ports in use: {all_ports}")
        logger.info("")
        return True

    except Exception as e:
        logger.error(f"✗ Agent config error: {e}")
        return False


def test_data_loader():
    """Test data loader functionality"""
    logger.info("Testing data loader...")

    try:
        from data_loader import ClinicalDataLoader

        loader = ClinicalDataLoader()
        logger.info("✓ ClinicalDataLoader instantiated")

        # Generate small test dataset
        patients = loader.generate_synthetic_patients(n_patients=10)
        logger.info(f"✓ Generated {len(patients)} synthetic patients")

        trials = loader.fetch_clinical_trials(condition="diabetes", max_trials=5)
        logger.info(f"✓ Generated {len(trials)} synthetic trials")

        logger.info("")
        return True

    except Exception as e:
        logger.error(f"✗ Data loader error: {e}")
        return False


def test_conway_engine():
    """Test patient pattern engine"""
    logger.info("Testing Pattern Discovery engine...")

    try:
        from conway_engine import Pattern DiscoveryPatternEngine
        from data_loader import ClinicalDataLoader

        engine = Pattern DiscoveryPatternEngine()
        logger.info("✓ Pattern DiscoveryPatternEngine instantiated")

        # Generate small test dataset
        loader = ClinicalDataLoader()
        # Generate small datasets first
        loader.generate_synthetic_patients(n_patients=100)
        loader.fetch_clinical_trials(condition="diabetes", max_trials=10)
        data = loader.prepare_for_conway()
        logger.info(f"✓ Test data prepared: {data['metadata']['patient_count']} patients")

        # Create embeddings (this will take a moment)
        logger.info("  Creating embeddings (this may take 10-20 seconds)...")
        embeddings = engine.create_universal_embedding(data)
        logger.info(f"✓ Embeddings created: shape {embeddings.shape}")

        logger.info("")
        return True

    except Exception as e:
        logger.error(f"✗ Pattern Discovery engine error: {e}")
        return False


def print_summary(results):
    """Print test summary"""
    logger.info("=" * 60)
    logger.info("TEST SUMMARY")
    logger.info("=" * 60)

    all_passed = all(results.values())

    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        logger.info(f"{status} - {test_name}")

    logger.info("=" * 60)

    if all_passed:
        logger.info("✓ ALL TESTS PASSED!")
        logger.info("")
        logger.info("You're ready to run the agent network:")
        logger.info("  python run_agents.py")
        logger.info("")
    else:
        logger.info("✗ SOME TESTS FAILED")
        logger.info("")
        logger.info("Please fix the errors above before running agents.")
        logger.info("")

    return all_passed


def main():
    """Run all tests"""
    logger.info("=" * 60)
    logger.info("TRIALMATCH AI - AGENT SYSTEM TEST")
    logger.info("=" * 60)
    logger.info("")

    results = {
        "Imports": test_imports(),
        "Agent Modules": test_agent_modules(),
        "Message Models": test_message_models(),
        "Agent Config": test_agent_config(),
        "Data Loader": test_data_loader(),
        "Pattern Discovery Engine": test_conway_engine()
    }

    all_passed = print_summary(results)

    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
