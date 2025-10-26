#!/bin/bash
# TrialMatch AI - Agent Network Launcher
# This script starts all 8 Fetch.ai agents for clinical trial matching

echo "======================================================================"
echo "  TrialMatch AI - Starting Agent Network"
echo "======================================================================"
echo ""
echo "This will start 8 Fetch.ai agents:"
echo "  1. Coordinator Agent (Port 8000) - Orchestrates workflow"
echo "  2. Eligibility Agent (Port 8001) - Extracts trial criteria"
echo "  3. Pattern Agent (Port 8002) - Matches patient patterns"
echo "  4. Discovery Agent (Port 8003) - Finds patient candidates"
echo "  5. Matching Agent (Port 8004) - Scores patients"
echo "  6. Site Agent (Port 8005) - Recommends trial sites"
echo "  7. Prediction Agent (Port 8006) - Forecasts enrollment"
echo "  8. Validation Agent (Port 8007) - Validates criteria"
echo ""
echo "======================================================================"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: python3 not found"
    echo "Please install Python 3.9 or higher"
    exit 1
fi

# Check if uagents is installed
python3 -c "import uagents" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Warning: uagents not installed"
    echo "Installing dependencies..."
    pip3 install uagents
fi

# Run the agents
echo "🚀 Starting agents..."
echo ""
python3 run_agents.py

# If the script exits, show message
echo ""
echo "======================================================================"
echo "  Agent network stopped"
echo "======================================================================"
