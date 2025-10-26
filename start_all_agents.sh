#!/bin/bash

###################################################################################
# TrialMatch AI - Start All Agents
#
# This script launches all 8 Fetch.AI agents for the TrialMatch AI system:
# - Coordinator (Port 8000) - Orchestrates the workflow
# - Eligibility (Port 8001) - Extracts trial criteria
# - Pattern (Port 8002) - Matches patient patterns
# - Discovery (Port 8003) - Searches patient database
# - Matching (Port 8004) - Scores patient-trial matches
# - Site (Port 8005) - Recommends trial sites
# - Prediction (Port 8006) - Forecasts enrollment timelines
# - Validation (Port 8007) - Validates exclusion criteria
#
# Usage:
#   ./start_all_agents.sh              # Start all agents in background
#   ./start_all_agents.sh foreground   # Start all agents in separate terminals
#   ./start_all_agents.sh stop         # Stop all agents
#
###################################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project paths
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
VENV_PYTHON="$PROJECT_ROOT/venv/bin/python"
PID_DIR="$PROJECT_ROOT/.agent_pids"

# Agent list
AGENTS=(
    "coordinator_agent:8000"
    "eligibility_agent:8001"
    "pattern_agent:8002"
    "discovery_agent:8003"
    "matching_agent:8004"
    "site_agent:8005"
    "prediction_agent:8006"
    "validation_agent:8007"
)

###################################################################################
# Functions
###################################################################################

print_header() {
    echo -e "${BLUE}========================================================================${NC}"
    echo -e "${BLUE}  TrialMatch AI - Multi-Agent System${NC}"
    echo -e "${BLUE}========================================================================${NC}"
}

check_requirements() {
    echo -e "${YELLOW}Checking requirements...${NC}"

    # Check if venv exists
    if [ ! -f "$VENV_PYTHON" ]; then
        echo -e "${RED}❌ Virtual environment not found at: $VENV_PYTHON${NC}"
        echo -e "${YELLOW}   Please create it with: python3 -m venv venv${NC}"
        echo -e "${YELLOW}   Then install requirements: venv/bin/pip install -r backend/requirements.txt${NC}"
        exit 1
    fi

    # Check if backend directory exists
    if [ ! -d "$BACKEND_DIR" ]; then
        echo -e "${RED}❌ Backend directory not found: $BACKEND_DIR${NC}"
        exit 1
    fi

    echo -e "${GREEN}✓ Requirements check passed${NC}"
}

create_pid_dir() {
    mkdir -p "$PID_DIR"
}

start_agent_background() {
    local agent_name=$1
    local port=$2
    local pid_file="$PID_DIR/${agent_name}.pid"

    echo -e "${YELLOW}Starting ${agent_name} on port ${port}...${NC}"

    # Start agent in background
    cd "$BACKEND_DIR"
    nohup "$VENV_PYTHON" -m "agents.${agent_name}" > "$PID_DIR/${agent_name}.log" 2>&1 &
    local pid=$!

    # Save PID
    echo $pid > "$pid_file"

    # Wait a moment and check if still running
    sleep 0.5
    if ps -p $pid > /dev/null 2>&1; then
        echo -e "${GREEN}✓ ${agent_name} started (PID: $pid)${NC}"
        return 0
    else
        echo -e "${RED}❌ ${agent_name} failed to start${NC}"
        return 1
    fi
}

start_agent_foreground() {
    local agent_name=$1
    local port=$2

    echo -e "${YELLOW}Starting ${agent_name} on port ${port} in new terminal...${NC}"

    # Detect OS and open appropriate terminal
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        osascript -e "tell application \"Terminal\" to do script \"cd '$BACKEND_DIR' && '$VENV_PYTHON' -m agents.${agent_name}\""
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux - try various terminal emulators
        if command -v gnome-terminal &> /dev/null; then
            gnome-terminal -- bash -c "cd '$BACKEND_DIR' && '$VENV_PYTHON' -m agents.${agent_name}; exec bash"
        elif command -v xterm &> /dev/null; then
            xterm -e "cd '$BACKEND_DIR' && '$VENV_PYTHON' -m agents.${agent_name}" &
        else
            echo -e "${YELLOW}⚠ No terminal emulator found. Starting in background instead.${NC}"
            start_agent_background "$agent_name" "$port"
        fi
    else
        echo -e "${YELLOW}⚠ Unknown OS. Starting in background instead.${NC}"
        start_agent_background "$agent_name" "$port"
    fi
}

stop_all_agents() {
    print_header
    echo -e "${YELLOW}Stopping all agents...${NC}"
    echo ""

    for agent_port in "${AGENTS[@]}"; do
        agent_name="${agent_port%%:*}"
        pid_file="$PID_DIR/${agent_name}.pid"

        if [ -f "$pid_file" ]; then
            pid=$(cat "$pid_file")
            if ps -p $pid > /dev/null 2>&1; then
                echo -e "${YELLOW}Stopping ${agent_name} (PID: $pid)...${NC}"
                kill $pid
                echo -e "${GREEN}✓ ${agent_name} stopped${NC}"
            else
                echo -e "${YELLOW}⚠ ${agent_name} was not running${NC}"
            fi
            rm "$pid_file"
        else
            echo -e "${YELLOW}⚠ No PID file for ${agent_name}${NC}"
        fi
    done

    echo ""
    echo -e "${GREEN}All agents stopped${NC}"
}

show_status() {
    print_header
    echo -e "${YELLOW}Agent Status:${NC}"
    echo ""

    printf "%-20s %-10s %-15s %-10s\n" "AGENT" "PORT" "STATUS" "PID"
    echo "------------------------------------------------------------------------"

    for agent_port in "${AGENTS[@]}"; do
        agent_name="${agent_port%%:*}"
        port="${agent_port##*:}"
        pid_file="$PID_DIR/${agent_name}.pid"

        if [ -f "$pid_file" ]; then
            pid=$(cat "$pid_file")
            if ps -p $pid > /dev/null 2>&1; then
                printf "%-20s %-10s ${GREEN}%-15s${NC} %-10s\n" "$agent_name" "$port" "RUNNING" "$pid"
            else
                printf "%-20s %-10s ${RED}%-15s${NC} %-10s\n" "$agent_name" "$port" "STOPPED" "N/A"
            fi
        else
            printf "%-20s %-10s ${RED}%-15s${NC} %-10s\n" "$agent_name" "$port" "NOT STARTED" "N/A"
        fi
    done

    echo ""
}

start_all_agents() {
    local mode=$1

    print_header
    check_requirements
    create_pid_dir

    echo ""
    echo -e "${YELLOW}Starting all 8 agents in ${mode} mode...${NC}"
    echo ""

    # Start each agent
    for agent_port in "${AGENTS[@]}"; do
        agent_name="${agent_port%%:*}"
        port="${agent_port##*:}"

        if [ "$mode" == "foreground" ]; then
            start_agent_foreground "$agent_name" "$port"
        else
            start_agent_background "$agent_name" "$port"
        fi

        # Small delay between agents
        sleep 1
    done

    echo ""
    echo -e "${GREEN}========================================================================${NC}"
    echo -e "${GREEN}All agents started successfully!${NC}"
    echo -e "${GREEN}========================================================================${NC}"
    echo ""
    echo -e "${BLUE}Agent Inspector URLs:${NC}"
    echo ""
    echo "  Coordinator: https://agentverse.ai/inspect/?uri=http%3A//127.0.0.1%3A8000"
    echo "  Eligibility: https://agentverse.ai/inspect/?uri=http%3A//127.0.0.1%3A8001"
    echo "  Pattern:     https://agentverse.ai/inspect/?uri=http%3A//127.0.0.1%3A8002"
    echo "  Discovery:   https://agentverse.ai/inspect/?uri=http%3A//127.0.0.1%3A8003"
    echo "  Matching:    https://agentverse.ai/inspect/?uri=http%3A//127.0.0.1%3A8004"
    echo "  Site:        https://agentverse.ai/inspect/?uri=http%3A//127.0.0.1%3A8005"
    echo "  Prediction:  https://agentverse.ai/inspect/?uri=http%3A//127.0.0.1%3A8006"
    echo "  Validation:  https://agentverse.ai/inspect/?uri=http%3A//127.0.0.1%3A8007"
    echo ""
    echo -e "${BLUE}Logs available in: ${PID_DIR}/${NC}"
    echo ""

    if [ "$mode" == "background" ]; then
        echo -e "${YELLOW}To stop all agents: ./start_all_agents.sh stop${NC}"
        echo -e "${YELLOW}To view status:     ./start_all_agents.sh status${NC}"
    fi
    echo ""
}

show_help() {
    print_header
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  (no args)   Start all agents in background mode"
    echo "  foreground  Start all agents in separate terminal windows"
    echo "  stop        Stop all running agents"
    echo "  status      Show status of all agents"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                  # Start in background"
    echo "  $0 foreground       # Start in separate terminals"
    echo "  $0 stop             # Stop all agents"
    echo "  $0 status           # Check status"
    echo ""
}

###################################################################################
# Main
###################################################################################

case "${1:-start}" in
    start)
        start_all_agents "background"
        ;;
    foreground)
        start_all_agents "foreground"
        ;;
    stop)
        stop_all_agents
        ;;
    status)
        show_status
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo -e "${RED}Unknown command: $1${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac
