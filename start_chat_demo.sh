#!/bin/bash

# Quick Start Script for Agent Chat Demo
# This starts the chat router in demo mode (no agents needed)

echo "======================================================================"
echo "  TrialMatch AI - Agent Chat Demo"
echo "======================================================================"
echo ""
echo "Starting services..."
echo ""

# Check if in correct directory
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: python3 not found. Please install Python 3."
    exit 1
fi

# Check npm
if ! command -v npm &> /dev/null; then
    echo "❌ Error: npm not found. Please install Node.js."
    exit 1
fi

# Install backend dependencies
echo "📦 Installing backend dependencies..."
cd backend
pip3 install -q flask flask-cors 2>/dev/null || pip3 install flask flask-cors
cd ..

# Install frontend dependencies if needed
if [ ! -d "frontend/node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
fi

# Start chat router in background
echo "🚀 Starting Chat Router API (Port 5001)..."
cd backend
python3 chat_router.py &
CHAT_PID=$!
cd ..

# Wait for chat router to start
sleep 3

# Start frontend dev server
echo "🚀 Starting Frontend Dev Server (Port 3000)..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "======================================================================"
echo "✅ Services Started!"
echo "======================================================================"
echo ""
echo "  Chat Router:  http://localhost:5001"
echo "  Frontend:     http://localhost:3000"
echo ""
echo "======================================================================"
echo "📖 HOW TO USE:"
echo "======================================================================"
echo ""
echo "  1. Open http://localhost:3000 in your browser"
echo "  2. Click the 'Agent Control' tab (3rd tab)"
echo "  3. Click '💬 Chat' button on any agent hexagon"
echo "  4. Start chatting with the agent!"
echo ""
echo "  Example queries:"
echo "    - 'Find patients with Type 2 Diabetes'"
echo "    - 'Show me the top 10 matches'"
echo "    - 'What patterns have you discovered?'"
echo ""
echo "======================================================================"
echo "⚠️  DEMO MODE:"
echo "======================================================================"
echo ""
echo "  Currently running in DEMO mode with simulated responses."
echo "  To enable real agent communication:"
echo ""
echo "    1. Open 8 new terminals"
echo "    2. Run each agent: python3 backend/agents/<agent>_agent.py"
echo "    3. Chat will then use real agent responses"
echo ""
echo "======================================================================"
echo ""
echo "Press Ctrl+C to stop all services..."
echo ""

# Wait for user interrupt
trap "echo ''; echo 'Stopping services...'; kill $CHAT_PID $FRONTEND_PID 2>/dev/null; echo 'Done!'; exit 0" INT

# Keep script running
wait
