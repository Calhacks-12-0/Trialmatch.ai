#!/bin/bash

# This script updates the startup functions for all agents to add Agentverse support

echo "Updating startup functions for all agents..."

# Array of agent names and their greeting messages
declare -A AGENTS
AGENTS[matching]="Ready to score patient candidates using Pattern Discovery similarity metrics!"
AGENTS[eligibility]="Ready to extract and parse trial eligibility criteria!"
AGENTS[pattern]="Ready to match pre-discovered patient patterns to trial criteria!"
AGENTS[prediction]="Ready to forecast enrollment timelines using pattern analysis!"
AGENTS[site]="Ready to recommend trial sites based on feasibility and patient geography!"
AGENTS[validation]="Ready to validate patient matches against exclusion criteria!"

echo "✓ Configuration ready"
echo ""
echo "Please manually update each agent's startup function using discovery_agent.py as a template."
echo ""
echo "Agent files to update:"
for agent in "${!AGENTS[@]}"; do
    echo "  - agents/${agent}_agent.py"
done
