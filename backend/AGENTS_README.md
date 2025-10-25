# TrialMatch AI - Fetch.ai Agent System

Multi-agent system for clinical trial patient matching using Fetch.ai's uagents framework.

## Architecture Overview

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Conway Engine  │────>│  Pattern Storage │────>│  Fetch.ai Agents│
│  (Stage 1)      │     │                  │     │  (Stage 2)      │
└─────────────────┘     └──────────────────┘     └─────────────────┘
  Unsupervised ML         Pre-discovered           Agent Coordination
  UMAP + HDBSCAN          Patterns                 Message Passing
```

### Two-Stage Pipeline

1. **Stage 1: Conway Pattern Engine** (Unsupervised Learning)
   - Discovers patterns in patient/trial data using UMAP + HDBSCAN
   - Creates universal embeddings from clinical features
   - Identifies patient clusters without supervision
   - Runs FIRST, before agents

2. **Stage 2: Fetch.ai Agents** (Coordination)
   - Work WITH pre-discovered patterns from Conway
   - Orchestrate matching workflow across 7 specialized agents
   - Handle eligibility, discovery, matching, site selection, and prediction

## Agent System

### 7 Specialized Agents

1. **Coordinator Agent** (Port 8000)
   - Orchestrates the entire multi-agent workflow
   - Sequences requests to all 6 specialized agents
   - Returns unified response

2. **Eligibility Agent** (Port 8001)
   - Extracts structured eligibility criteria from trials
   - Returns age ranges, conditions, gender, lab requirements

3. **Pattern Agent** (Port 8002)
   - Finds matching Conway patterns for trial criteria
   - Scores patterns: success rate (40%) + confidence (30%) + size (20%) + diversity (10%)

4. **Discovery Agent** (Port 8003)
   - Searches patient database using Conway patterns
   - Filters by basic eligibility (age, gender, condition)

5. **Matching Agent** (Port 8004)
   - Scores patients using Conway similarity metrics
   - Components: eligibility (40%) + similarity (30%) + enrollment probability (30%)

6. **Site Agent** (Port 8005)
   - Geographic site recommendations using clustering
   - Assigns patients to nearest major cities

7. **Prediction Agent** (Port 8006)
   - Forecasts enrollment timeline using pattern success rates
   - Generates milestones and risk factors

## Quick Start

### Prerequisites

- Python 3.9-3.12 (NOT 3.13 - uagents incompatibility)
- Virtual environment recommended

### Setup

```bash
# 1. Create virtual environment with Python 3.12
python3.12 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start agents (Terminal 1)
python run_agents.py

# 4. Start FastAPI backend (Terminal 2)
python app.py

# 5. Test the endpoint
curl -X POST http://localhost:8080/api/match/trial \
  -H "Content-Type: application/json" \
  -d '{"trial_id": "NCT00100000"}'
```

### Expected Output

The system will:
1. Load clinical trial data
2. Run Conway pattern discovery (30-60 seconds first run)
3. Send patterns to Fetch.ai agent network
4. Return comprehensive matching results with:
   - Pattern statistics
   - Top 5 pattern insights
   - Trial matches
   - Agent coordination status

## File Structure

```
backend/
├── agents/                    # Fetch.ai agent system
│   ├── __init__.py
│   ├── config.py             # Agent addresses, ports, seeds
│   ├── models.py             # Pydantic message models
│   ├── coordinator_agent.py  # Main orchestrator
│   ├── eligibility_agent.py  # Extract eligibility criteria
│   ├── pattern_agent.py      # Find Conway patterns
│   ├── discovery_agent.py    # Search patient database
│   ├── matching_agent.py     # Score patients
│   ├── site_agent.py         # Geographic recommendations
│   └── prediction_agent.py   # Enrollment forecasts
│
├── run_agents.py             # Bureau runner (all 7 agents)
├── app.py                    # FastAPI backend
├── integration_service.py    # Pipeline coordinator
├── conway_engine.py          # Pattern discovery (Stage 1)
├── data_loader.py            # Clinical data loading
├── requirements.txt          # Python dependencies
│
└── docs/                     # Documentation
    ├── QUICKSTART_AGENTS.md  # 5-minute setup guide
    ├── AGENTS_COMPLETE.md    # Full implementation details
    ├── SETUP.md              # Python 3.12 setup
    ├── AGENTVERSE_DEPLOYMENT.md
    └── AGENTVERSE_QUICKSTART.md
```

## Key Technologies

- **Fetch.ai uagents**: Multi-agent framework
- **FastAPI**: REST API backend
- **Pydantic**: Type-safe message models
- **sentence-transformers**: Clinical text embeddings
- **UMAP + HDBSCAN**: Conway pattern discovery
- **NumPy/scikit-learn**: ML operations

## API Endpoints

### POST /api/match/trial
Main trial matching endpoint.

**Request:**
```json
{
  "trial_id": "NCT00100000"  // Optional, defaults to first trial
}
```

**Response:**
```json
{
  "status": "success",
  "processing_time": "45.23 seconds",
  "statistics": {
    "total_patients": 1000,
    "total_trials": 50,
    "patterns_discovered": 27,
    "clustered_patients": 934,
    "noise_patients": 66
  },
  "pattern_insights": [...],
  "trial_matches": [...],
  "agent_results": {
    "agents_activated": [
      "coordinator_agent",
      "eligibility_agent",
      "pattern_agent",
      "discovery_agent",
      "matching_agent",
      "site_agent",
      "prediction_agent"
    ],
    "messages_processed": 189,
    "eligible_patients_found": 127,
    "recommended_sites": 10,
    "predicted_enrollment_timeline": "8-12 weeks",
    "confidence_score": 0.87
  }
}
```

## Agent Communication Flow

```
User Request
    ↓
Coordinator Agent (8000)
    ↓
Eligibility Agent (8001) → Extract trial criteria
    ↓
Pattern Agent (8002) → Find Conway patterns
    ↓
Discovery Agent (8003) → Search patients
    ↓
Matching Agent (8004) → Score patients
    ↓
Site Agent (8005) → Geographic recommendations
    ↓
Prediction Agent (8006) → Enrollment forecast
    ↓
Final Response
```

## Troubleshooting

### Python Version Issues
- Error: `ModuleNotFoundError: No module named 'uagents'`
- Solution: Use Python 3.9-3.12 (NOT 3.13)
```bash
brew install python@3.12
/opt/homebrew/bin/python3.12 -m venv venv
```

### Pydantic Compatibility
- Error: `ForwardRef._evaluate() missing argument`
- Solution: Ensure Pydantic 1.10.24 (NOT 2.x)
```bash
pip install "pydantic>=1.10.24,<2.0"
```

### First Run Slow
- First run takes 30-60 seconds to download sentence-transformers model
- Subsequent runs are fast (~10-15 seconds)

### Agent Connection Issues
- Ensure all 7 agents are running in Terminal 1
- Check ports 8000-8006 are not in use
- Verify `run_agents.py` shows "Starting agent..." for all 7 agents

## Integration with Frontend

The backend exposes a REST API that the frontend can call:

```javascript
// Example frontend integration
const response = await fetch('http://localhost:8080/api/match/trial', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ trial_id: 'NCT00100000' })
});

const results = await response.json();
console.log(results.agent_results);
```

## Next Steps

1. **For Development**: See [docs/QUICKSTART_AGENTS.md](docs/QUICKSTART_AGENTS.md)
2. **For Deployment**: See [docs/AGENTVERSE_DEPLOYMENT.md](docs/AGENTVERSE_DEPLOYMENT.md)
3. **For Full Details**: See [docs/AGENTS_COMPLETE.md](docs/AGENTS_COMPLETE.md)

## Notes for Teammates

- **Your responsibility**: Agents only (this folder)
- **Other team's responsibility**: Real data integration
- **Integration point**: `integration_service.py` coordinates Conway → Agents
- **Data flow**: `data_loader.py` → `conway_engine.py` → `agents/`

All agents are fully implemented and tested. The system is ready for integration with real clinical trial data from your teammates' work.

## Credits

Built with Fetch.ai's uagents framework for CalHacks 12.
