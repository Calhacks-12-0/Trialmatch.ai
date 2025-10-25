# TrialMatch AI - Fetch.ai Multi-Agent System

## 🏗️ Architecture Overview

This system implements a **7-agent network** using Fetch.ai's uagents framework to intelligently match patients to clinical trials.

### **The Two-Stage Pipeline**

```
┌─────────────────────────────────────────────────────────────┐
│  STAGE 1: CONWAY PATTERN ENGINE (Unsupervised Discovery)   │
│  --------------------------------------------------------   │
│  • Processes 50,000+ patients & 450,000+ trials           │
│  • Creates multi-modal embeddings (text + numeric + geo)   │
│  • Discovers natural clusters using UMAP + HDBSCAN        │
│  • NO LABELS NEEDED - pure unsupervised learning           │
│  • Output: Pattern clusters with similarity metrics        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  STAGE 2: FETCH.AI AGENT NETWORK (Orchestration)          │
│  --------------------------------------------------------   │
│  • Receives pre-discovered Conway patterns                 │
│  • 7 specialized agents work collaboratively               │
│  • Sequential pipeline with inter-agent messaging          │
│  • Output: Ranked patients + sites + enrollment forecast   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🤖 The 7 Agents

### **1. Coordinator Agent** (Port 8000)
**Role:** Orchestrates the entire multi-agent workflow

**Responsibilities:**
- Receives user queries
- Calls all 6 specialized agents sequentially
- Aggregates results
- Returns comprehensive response

**Key Features:**
- Sequential orchestration with error handling
- Timing metrics for each agent
- Centralized logging and monitoring

**Message Flow:**
```
User Query → Coordinator → [6 agents in sequence] → Coordinator → Response
```

---

### **2. Eligibility Agent** (Port 8001)
**Role:** Extracts structured eligibility criteria from trial protocols

**Responsibilities:**
- Fetches trial data from ClinicalTrials.gov or database
- Parses inclusion/exclusion criteria
- Extracts age range, gender, conditions, lab requirements
- Returns machine-readable criteria

**Input:** `EligibilityRequest` with trial_id
**Output:** `EligibilityCriteria` with structured requirements

**Example Output:**
```json
{
  "trial_id": "NCT00123456",
  "age_range": {"min": 18, "max": 65},
  "conditions": ["diabetes"],
  "lab_requirements": {
    "HbA1c": {"min": 6.5, "max": 10.0}
  }
}
```

**Future Enhancement:** Use LLM (GPT-4/Claude) to parse natural language criteria

---

### **3. Pattern Agent** (Port 8002)
**Role:** Finds matching Conway patterns based on trial criteria

**Responsibilities:**
- Receives pre-discovered Conway patterns from integration service
- Matches patterns to trial eligibility criteria
- Ranks patterns by match score
- Returns top matching patterns

**Key Point:** **Does NOT discover patterns** - works with Conway's pre-discovered clusters

**Matching Algorithm:**
- Enrollment success rate (40% weight)
- Pattern confidence (30% weight)
- Pattern size (20% weight)
- Diversity factor (10% weight)

**Input:** `PatternRequest` with trial criteria
**Output:** `PatternResponse` with ranked patterns

---

### **4. Discovery Agent** (Port 8003)
**Role:** Searches patient database for candidates matching patterns

**Responsibilities:**
- Receives matching patterns from Pattern Agent
- Searches patient database efficiently
- Filters by basic eligibility (age, gender, condition)
- Returns patient candidates with embeddings

**Strategy:**
- Uses Conway pattern membership for efficient search
- Samples patients from each pattern
- Applies basic eligibility filtering
- Returns candidates with associated pattern ID

**Input:** `DiscoveryRequest` with patterns + criteria
**Output:** `DiscoveryResponse` with patient candidates

---

### **5. Matching Agent** (Port 8004)
**Role:** Scores patients using Conway's similarity metrics

**Responsibilities:**
- Receives patient candidates from Discovery Agent
- Scores using Conway embedding similarity
- Calculates eligibility score
- Estimates enrollment probability
- Generates match reasons and risk factors

**Scoring Components:**
1. **Eligibility Score** (40%): How well patient meets criteria
2. **Similarity Score** (30%): Conway embedding distance to pattern centroid
3. **Enrollment Probability** (30%): Based on pattern historical success

**Input:** `MatchingRequest` with candidates + criteria + patterns
**Output:** `MatchingResponse` with scored matches

**Example Match:**
```json
{
  "patient_id": "P001234",
  "overall_score": 0.87,
  "eligibility_score": 0.92,
  "similarity_score": 0.85,
  "enrollment_probability": 0.78,
  "match_reasons": [
    "Age 55 fits trial criteria",
    "Has diabetes diagnosis",
    "Similar patients have 78% success rate"
  ],
  "risk_factors": [
    "No previous trial experience"
  ]
}
```

---

### **6. Site Agent** (Port 8005)
**Role:** Recommends trial sites based on patient geography

**Responsibilities:**
- Receives scored patient matches with locations
- Clusters patients geographically
- Recommends optimal trial sites
- Calculates site capacity and coverage

**Algorithm:**
- Assigns patients to nearest major city
- Counts patients per city
- Ranks cities by patient concentration
- Returns top N site recommendations

**Input:** `SiteRequest` with patient matches + locations
**Output:** `SiteResponse` with site recommendations

**Example Site:**
```json
{
  "site_name": "New York Medical Center",
  "location": {"city": "New York", "state": "NY"},
  "patient_count": 87,
  "average_distance": 15.3,
  "capacity": 150,
  "priority_score": 0.87,
  "patient_ids": ["P001234", "P001567", ...]
}
```

---

### **7. Prediction Agent** (Port 8006)
**Role:** Forecasts enrollment timeline using pattern analysis

**Responsibilities:**
- Receives matched patients + site recommendations
- Uses Conway pattern success rates
- Forecasts enrollment timeline
- Generates milestones (25%, 50%, 75%, 100%)
- Identifies risks and recommendations

**Methodology:**
1. Calculate average enrollment probability from patterns
2. Estimate weekly enrollment rate based on site capacity
3. Calculate timeline to reach target
4. Generate milestone predictions
5. Identify risks and optimization opportunities

**Input:** `PredictionRequest` with target, matches, patterns, sites
**Output:** `EnrollmentForecast` with timeline + confidence

**Example Forecast:**
```json
{
  "target_enrollment": 300,
  "predicted_enrollment": 285,
  "estimated_weeks": 12.5,
  "confidence": 0.85,
  "weekly_enrollment_rate": 22.8,
  "milestones": [
    {"week": 3.1, "enrollment": 75, "percentage": 25},
    {"week": 6.3, "enrollment": 150, "percentage": 50},
    {"week": 9.4, "enrollment": 225, "percentage": 75},
    {"week": 12.5, "enrollment": 300, "percentage": 100}
  ],
  "risk_factors": [
    "Limited patient pool: 285 eligible vs 300 target"
  ],
  "recommendations": [
    "Focus outreach on high-scoring patients (>0.8) first",
    "Use pattern insights to optimize recruitment messaging"
  ]
}
```

---

## 🚀 Running the Agent Network

### **Prerequisites**

Install dependencies:
```bash
pip install -r requirements.txt
```

Required packages:
- `uagents==0.11.0` - Fetch.ai agent framework
- `pydantic==1.10.9` - Data validation (must be 1.x for uagents)
- All other dependencies from requirements.txt

### **Option 1: Run All Agents Together (Bureau)**

**Best for development and demos:**

```bash
cd backend
python run_agents.py
```

This starts all 7 agents in a single process using Fetch.ai's Bureau.

**Ports used:**
- 8000: Coordinator Agent
- 8001: Eligibility Agent
- 8002: Pattern Agent
- 8003: Discovery Agent
- 8004: Matching Agent
- 8005: Site Agent
- 8006: Prediction Agent

### **Option 2: Run Agents Separately**

**Best for production:**

```bash
# Terminal 1
python agents/coordinator_agent.py

# Terminal 2
python agents/eligibility_agent.py

# Terminal 3
python agents/pattern_agent.py

# Terminal 4
python agents/discovery_agent.py

# Terminal 5
python agents/matching_agent.py

# Terminal 6
python agents/site_agent.py

# Terminal 7
python agents/prediction_agent.py
```

### **Running the Full System**

1. **Start agents:**
   ```bash
   python run_agents.py
   ```

2. **Start FastAPI backend** (in another terminal):
   ```bash
   python app.py
   ```

3. **Test the system:**
   ```bash
   curl http://localhost:8080/api/health
   curl -X POST http://localhost:8080/api/match/trial -H "Content-Type: application/json" -d '{"trial_id": "NCT00100000"}'
   ```

---

## 📊 Agent Communication

### **Message Models**

All agents use Pydantic models defined in `agents/models.py`:

- `UserQuery` - Initial query to coordinator
- `EligibilityRequest` / `EligibilityCriteria`
- `PatternRequest` / `PatternResponse`
- `DiscoveryRequest` / `DiscoveryResponse`
- `MatchingRequest` / `MatchingResponse`
- `SiteRequest` / `SiteResponse`
- `PredictionRequest` / `EnrollmentForecast`
- `CoordinatorResponse` - Final aggregated response
- `AgentStatus` - Health check

### **Inter-Agent Communication**

Agents communicate using Fetch.ai's message passing:

```python
# Sending a query
response = await ctx.send(
    destination=agent_address,
    message=RequestModel(...),
    timeout=30.0
)

# Handling a query
@agent.on_query(model=RequestModel, replies={ResponseModel})
async def handle_query(ctx: Context, sender: str, msg: RequestModel) -> ResponseModel:
    # Process request
    result = process(msg)
    # Return response
    return ResponseModel(result=result)
```

### **Agent Registry**

Agents register their addresses on startup:

```python
from agents.config import AgentRegistry

# Register (in agent startup)
AgentRegistry.register("coordinator", agent.address)

# Lookup (when sending messages)
coordinator_addr = AgentRegistry.get("coordinator")
```

---

## 🔧 Configuration

### **Agent Configuration** (`agents/config.py`)

- Agent ports (8000-8006)
- Agent seeds (deterministic addresses)
- Timeout settings
- Logging configuration

### **Timeouts**

- `QUERY_TIMEOUT = 30.0` seconds - Normal agent queries
- `QUICK_TIMEOUT = 5.0` seconds - Health checks
- `LONG_TIMEOUT = 60.0` seconds - Heavy processing

---

## 📈 Monitoring & Debugging

### **Logging**

All agents log to console with structured format:

```
2024-01-15 10:30:15 - coordinator_agent - INFO - STEP 1: Calling Eligibility Agent...
2024-01-15 10:30:15 - eligibility_agent - INFO -   → Eligibility Agent processing: NCT00100000
2024-01-15 10:30:16 - eligibility_agent - INFO -   ✓ Extracted criteria: age {'min': 18, 'max': 65}
```

### **Health Checks**

Query any agent's status:

```python
from agents.models import AgentStatus

status = await ctx.send(agent_address, AgentStatus(...))
# Returns: agent_name, status, uptime, requests_processed
```

### **Debugging Tips**

1. **Check agent addresses:**
   ```python
   from agents.config import AgentRegistry
   print(AgentRegistry.all())
   ```

2. **Test individual agents:**
   - Run just one agent
   - Send test queries directly
   - Check logs for errors

3. **Common issues:**
   - **Port conflicts:** Make sure ports 8000-8006 are free
   - **Import errors:** Run from `backend/` directory
   - **Pydantic version:** Must be 1.x (not 2.x) for uagents compatibility

---

## 🎯 Integration with Conway Engine

### **How It Works**

1. **Integration Service runs Conway first:**
   ```python
   # In integration_service.py
   embeddings = self.conway_engine.create_universal_embedding(data)
   pattern_results = self.conway_engine.discover_patterns(embeddings)
   ```

2. **Patterns are stored for agents:**
   ```python
   # Patterns available to agents via context storage
   ctx.storage.set("conway_patterns", pattern_results['patterns'])
   ```

3. **Pattern Agent retrieves patterns:**
   ```python
   # In pattern_agent.py
   conway_patterns = ctx.storage.get("conway_patterns")
   ```

4. **Agents work WITH patterns, not discovering them**

---

## 🚧 Future Enhancements

### **High Priority**

1. **Full HTTP Integration**
   - Currently: Agents can communicate, but integration_service uses simulation
   - TODO: Implement HTTP client to call Coordinator Agent from FastAPI

2. **LLM Integration for Eligibility Agent**
   - Use GPT-4 or Claude to parse natural language criteria
   - Extract structured requirements from trial protocols

3. **Real ClinicalTrials.gov API**
   - Fetch actual trial data
   - Parse real eligibility criteria

### **Medium Priority**

4. **Database Persistence**
   - Store agent results
   - Cache patterns and embeddings
   - Patient/trial database

5. **Advanced Similarity Metrics**
   - Use actual Conway embedding distances
   - Implement more sophisticated scoring

6. **Error Recovery**
   - Retry logic for failed agents
   - Fallback strategies
   - Circuit breakers

### **Nice to Have**

7. **Agent Dashboard**
   - Real-time agent status visualization
   - Message flow diagram
   - Performance metrics

8. **A/B Testing**
   - Compare different agent strategies
   - Optimize orchestration flow

9. **Agentverse Deployment**
   - Deploy agents to Fetch.ai cloud
   - Public agent addresses
   - Decentralized coordination

---

## 📝 Quick Reference

### **File Structure**

```
backend/
├── agents/
│   ├── __init__.py
│   ├── models.py                  # All message models
│   ├── config.py                  # Agent configuration
│   ├── coordinator_agent.py       # Main orchestrator
│   ├── eligibility_agent.py       # Trial criteria extraction
│   ├── pattern_agent.py           # Pattern matching
│   ├── discovery_agent.py         # Patient search
│   ├── matching_agent.py          # Patient scoring
│   ├── site_agent.py              # Geographic recommendations
│   └── prediction_agent.py        # Enrollment forecast
├── run_agents.py                  # Bureau runner (all agents)
├── integration_service.py         # Conway → Agents bridge
├── conway_engine.py               # Pattern discovery ML
├── data_loader.py                 # Data generation
└── app.py                         # FastAPI server
```

### **Agent Addresses**

With deterministic seeds, agent addresses are consistent:
- Coordinator: `agent1q...` (derived from seed)
- Eligibility: `agent1q...`
- Pattern: `agent1q...`
- etc.

To get actual addresses, check logs on startup or use `AgentRegistry.all()`

---

## 🎓 Learn More

- **Fetch.ai Docs:** https://docs.fetch.ai/
- **uagents Documentation:** https://github.com/fetchai/uAgents
- **Conway Pattern Engine:** See `conway_engine.py`
- **Project Spec:** See main project README

---

## ✅ Implementation Checklist

- [x] 7 agents implemented
- [x] Message models defined
- [x] Agent registry system
- [x] Bureau runner created
- [x] Logging and monitoring
- [x] Error handling
- [ ] Full HTTP integration with integration_service
- [ ] LLM integration for eligibility parsing
- [ ] Database persistence
- [ ] Production deployment configuration

---

**Built for CalHacks 12.0 - TrialMatch AI Team**

*Intelligent patient-trial matching using unsupervised pattern discovery + multi-agent orchestration*
