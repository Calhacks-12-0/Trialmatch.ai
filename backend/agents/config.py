"""
Configuration for agent addresses and communication.
In production, these would be environment variables or service discovery.
"""

import os
from typing import Dict


class AgentConfig:
    """Central configuration for all agent addresses and ports"""

    # Agent ports (each agent needs a unique port)
    COORDINATOR_PORT = 8000
    ELIGIBILITY_PORT = 8001
    PATTERN_PORT = 8002
    DISCOVERY_PORT = 8003
    MATCHING_PORT = 8004
    SITE_PORT = 8005
    PREDICTION_PORT = 8006

    # Agent seeds (deterministic addresses)
    # These seeds generate consistent addresses across restarts
    COORDINATOR_SEED = "coordinator_trial_match_seed_2024"
    ELIGIBILITY_SEED = "eligibility_checker_seed_2024"
    PATTERN_SEED = "pattern_discovery_seed_2024"
    DISCOVERY_SEED = "patient_discovery_seed_2024"
    MATCHING_SEED = "patient_matching_seed_2024"
    SITE_SEED = "site_recommendation_seed_2024"
    PREDICTION_SEED = "enrollment_prediction_seed_2024"

    # Base URLs for local development
    BASE_HOST = os.getenv("AGENT_HOST", "localhost")

    @classmethod
    def get_endpoint(cls, port: int) -> str:
        """Generate endpoint URL for agent"""
        return f"http://{cls.BASE_HOST}:{port}/submit"

    @classmethod
    def get_agent_config(cls, agent_name: str) -> Dict[str, any]:
        """Get configuration for a specific agent"""
        configs = {
            "coordinator": {
                "name": "trial_coordinator",
                "seed": cls.COORDINATOR_SEED,
                "port": cls.COORDINATOR_PORT,
                "endpoint": [cls.get_endpoint(cls.COORDINATOR_PORT)]
            },
            "eligibility": {
                "name": "eligibility_agent",
                "seed": cls.ELIGIBILITY_SEED,
                "port": cls.ELIGIBILITY_PORT,
                "endpoint": [cls.get_endpoint(cls.ELIGIBILITY_PORT)]
            },
            "pattern": {
                "name": "pattern_agent",
                "seed": cls.PATTERN_SEED,
                "port": cls.PATTERN_PORT,
                "endpoint": [cls.get_endpoint(cls.PATTERN_PORT)]
            },
            "discovery": {
                "name": "discovery_agent",
                "seed": cls.DISCOVERY_SEED,
                "port": cls.DISCOVERY_PORT,
                "endpoint": [cls.get_endpoint(cls.DISCOVERY_PORT)]
            },
            "matching": {
                "name": "matching_agent",
                "seed": cls.MATCHING_SEED,
                "port": cls.MATCHING_PORT,
                "endpoint": [cls.get_endpoint(cls.MATCHING_PORT)]
            },
            "site": {
                "name": "site_agent",
                "seed": cls.SITE_SEED,
                "port": cls.SITE_PORT,
                "endpoint": [cls.get_endpoint(cls.SITE_PORT)]
            },
            "prediction": {
                "name": "prediction_agent",
                "seed": cls.PREDICTION_SEED,
                "port": cls.PREDICTION_PORT,
                "endpoint": [cls.get_endpoint(cls.PREDICTION_PORT)]
            }
        }
        return configs.get(agent_name)

    @classmethod
    def get_all_ports(cls) -> list[int]:
        """Get list of all agent ports"""
        return [
            cls.COORDINATOR_PORT,
            cls.ELIGIBILITY_PORT,
            cls.PATTERN_PORT,
            cls.DISCOVERY_PORT,
            cls.MATCHING_PORT,
            cls.SITE_PORT,
            cls.PREDICTION_PORT
        ]


class AgentRegistry:
    """
    Registry to store and retrieve agent addresses.
    In a real system, this would be replaced by Fetch.ai's Almanac contract.
    """

    _addresses: Dict[str, str] = {}

    @classmethod
    def register(cls, name: str, address: str):
        """Register an agent's address"""
        cls._addresses[name] = address
        print(f"✓ Registered {name}: {address}")

    @classmethod
    def get(cls, name: str) -> str:
        """Get an agent's address"""
        address = cls._addresses.get(name)
        if not address:
            raise ValueError(f"Agent '{name}' not found in registry")
        return address

    @classmethod
    def all(cls) -> Dict[str, str]:
        """Get all registered agents"""
        return cls._addresses.copy()

    @classmethod
    def clear(cls):
        """Clear registry (for testing)"""
        cls._addresses.clear()


# Timeout configurations
QUERY_TIMEOUT = 30.0  # seconds to wait for agent responses
QUICK_TIMEOUT = 5.0   # seconds for health checks
LONG_TIMEOUT = 60.0   # seconds for heavy processing

# Logging configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
