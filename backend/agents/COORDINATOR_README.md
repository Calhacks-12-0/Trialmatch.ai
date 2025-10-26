# Coordinator Agent - The Orchestrator

## Overview

The **Coordinator Agent** is the central orchestrator of the TrialMatch AI multi-agent system. It acts as the "conductor of an orchestra," coordinating 7 specialized AI agents to match patients with clinical trials using machine learning and pattern discovery.

**Agent Address**: `agent1q0t5trykueswlfvskzezq5avpwkuvrh7rws58t9mka3fsngueef96ej7w7c`
**Port**: 8000
**Technology**: Fetch.AI uAgents Framework
**Mode**: Agentverse-enabled (can run locally or on Fetch.AI Agentverse)

---

## Role in the Multi-Agent System

The Coordinator Agent is responsible for:

1. **Receiving user queries** with trial matching requests
2. **Orchestrating a sequential workflow** through 7 specialized agents
3. **Aggregating results** from all agents into a unified response
4. **Managing inter-agent communication** using Fetch.AI's chat protocol
5. **Tracking performance metrics** (timing, success rates, etc.)

---

## The Multi-Agent Ecosystem

The Coordinator Agent connects to and orchestrates **7 specialized agents**, each with a specific expertise:

### 1. Eligibility Agent (Port 8001)
**Address**: `agent1qdd8ytcnfm6uuhtr647wchelc2x7musj62xf8xa7qf9nusrl8hnvke0skte`

**What It Does**:
- Fetches clinical trial details from ClinicalTrials.gov API
- Extracts inclusion/exclusion criteria from trial protocols
- Converts medical terms to standardized codes (ICD-10, SNOMED-CT)
- Parses complex eligibility requirements (age, gender, conditions, labs)

**Example Input**: Trial ID `NCT04567890`
**Example Output**:
```json
{
  "age_min": 18,
  "age_max": 65,
  "conditions_required": ["E11", "I10"],
  "conditions_excluded": ["N18.5"]
}
```

**Connection to Coordinator**: Receives `EligibilityRequest` → Returns `EligibilityCriteria`

---

### 2. Pattern Agent (Port 8002)
**Address**: `agent1qt59qwanc0ur9cxu83gruz8l7upyyx4vwuwctklyl8msfdh60kyuur87r5n`

**What It Does**:
- Matches trial eligibility criteria to **pre-discovered patient patterns**
- Uses the Pattern Discovery Engine's UMAP+HDBSCAN clustering
- Identifies which patient clusters align with trial requirements
- Returns pattern IDs and similarity scores

**Example Input**: Eligibility criteria from Step 1
**Example Output**:
```json
{
  "matching_patterns": [
    {"pattern_id": 42, "similarity": 0.92, "patient_count": 87}
  ]
}
```

**Connection to Coordinator**: Receives `PatternRequest` → Returns `PatternResponse`

---

### 3. Discovery Agent (Port 8003)
**Address**: `agent1qfd0tuljxdfvx74heq47ksdafjvschrkjn6kppllr2d7kjrhml9eyta49wj`

**What It Does**:
- Loads **1000 real FHIR patient records** from Synthea synthetic data
- Searches patient database using patterns from Step 2
- Retrieves candidate patients who match trial criteria
- Returns patient IDs with medical codes and demographics

**Data Sources**:
- Synthea FHIR patient data (5378 total patients, loads 1000)
- ClinicalTrials.gov API (100 diabetes trials cached)

**Example Output**:
```json
{
  "candidates": [
    {
      "patient_id": "patient-001",
      "age": 45,
      "conditions": ["E11.9", "I10"],
      "pattern_id": 42
    }
  ]
}
```

**Connection to Coordinator**: Receives `DiscoveryRequest` → Returns `DiscoveryResponse`

---

### 4. Matching Agent (Port 8004)
**Address**: `agent1q2q2ywhxvj9lt3tm862mzgre4n2f7st8ddnp5j862uzqq0neqzpvwm7y09u`

**What It Does**:
- Scores each patient-trial match using **similarity metrics**
- Calculates match scores based on:
  - Medical code overlap
  - Age/gender compatibility
  - Pattern similarity from UMAP embeddings
- Ranks patients by match quality (0.0 - 1.0 scale)

**Example Output**:
```json
{
  "matches": [
    {
      "patient_id": "patient-001",
      "trial_id": "NCT04567890",
      "match_score": 0.89,
      "reasons": ["Diabetes + Hypertension match", "Age compatible"]
    }
  ]
}
```

**Connection to Coordinator**: Receives `MatchingRequest` → Returns `MatchingResponse`

---

### 5. Validation Agent (Port 8007)
**Address**: `agent1qdvp3zpu6y8vnsnzwghc7zfmdvfyssyk5ac83h886ptqsu2yyzvnq7evglv`

**What It Does**:
- Validates patient matches against **exclusion criteria**
- Checks for disqualifying conditions
- Flags patients who don't meet requirements
- Prevents false positives from reaching recruitment

**Example Output**:
```json
{
  "validated_matches": [
    {"patient_id": "patient-001", "valid": true}
  ],
  "excluded_matches": [
    {
      "patient_id": "patient-002",
      "reason": "Has kidney disease (exclusion)"
    }
  ]
}
```

**Connection to Coordinator**: Receives `ValidationRequest` → Returns `ValidationResponse`

---

### 6. Site Agent (Port 8005)
**Address**: `agent1qg5m40mncw5d06770gc6tfl0hr8hlze3fpwa93t8q24lzgfx60nv5pj3man`

**What It Does**:
- Recommends **optimal trial sites** for recruitment
- Scores sites based on:
  - Geographic proximity to patients
  - Site capacity and enrollment history
  - Therapeutic area expertise
- Returns ranked site recommendations

**Example Output**:
```json
{
  "recommended_sites": [
    {
      "site_id": "UCLA-001",
      "location": "Los Angeles, CA",
      "feasibility_score": 0.87,
      "patient_proximity": 12.3,
      "capacity": "High"
    }
  ]
}
```

**Connection to Coordinator**: Receives `SiteRequest` → Returns `SiteResponse`

---

### 7. Prediction Agent (Port 8006)
**Address**: `agent1qt437ghfkwm5gusr9xgxm9tc8pgca04ffsqwctqvz3l5qxfaxsunqw7eny2`

**What It Does**:
- Forecasts **enrollment timelines** for the trial
- Predicts when target enrollment will be reached
- Uses pattern analysis and historical data
- Generates milestone predictions

**Example Output**:
```json
{
  "forecast": {
    "target_enrollment": 100,
    "predicted_completion": "2025-03-15",
    "milestones": [
      {"date": "2025-01-15", "enrolled": 25},
      {"date": "2025-02-15", "enrolled": 50}
    ]
  }
}
```

**Connection to Coordinator**: Receives `PredictionRequest` → Returns `EnrollmentForecast`

---

## The Workflow: How It All Connects

```
User Query
    ↓
┌─────────────────────────────────────────────────┐
│         COORDINATOR AGENT (Port 8000)           │
│  "The Orchestra Conductor"                      │
└─────────────────────────────────────────────────┘
    ↓
    ↓ Step 1: Get Trial Criteria
    ↓
┌─────────────────────────────────────────────────┐
│       ELIGIBILITY AGENT (Port 8001)             │
│  "The Trial Requirements Expert"                │
│  • Fetches trial from ClinicalTrials.gov        │
│  • Extracts inclusion/exclusion criteria        │
│  • Converts to medical codes                    │
└─────────────────────────────────────────────────┘
    ↓
    ↓ Step 2: Find Matching Patterns
    ↓
┌─────────────────────────────────────────────────┐
│         PATTERN AGENT (Port 8002)               │
│  "The Pattern Matcher"                          │
│  • Matches criteria to patient clusters         │
│  • Uses UMAP+HDBSCAN pattern library            │
│  • Returns pattern IDs                          │
└─────────────────────────────────────────────────┘
    ↓
    ↓ Step 3: Search Patient Database
    ↓
┌─────────────────────────────────────────────────┐
│        DISCOVERY AGENT (Port 8003)              │
│  "The Patient Database Searcher"                │
│  • Searches 1000 FHIR patients                  │
│  • Filters by patterns                          │
│  • Returns candidate patients                   │
└─────────────────────────────────────────────────┘
    ↓
    ↓ Step 4: Score Matches
    ↓
┌─────────────────────────────────────────────────┐
│         MATCHING AGENT (Port 8004)              │
│  "The Scoring Specialist"                       │
│  • Calculates match scores                      │
│  • Uses similarity metrics                      │
│  • Ranks patients                               │
└─────────────────────────────────────────────────┘
    ↓
    ↓ Step 5: Validate Matches
    ↓
┌─────────────────────────────────────────────────┐
│        VALIDATION AGENT (Port 8007)             │
│  "The Quality Control Inspector"                │
│  • Checks exclusion criteria                    │
│  • Flags disqualified patients                  │
│  • Ensures compliance                           │
└─────────────────────────────────────────────────┘
    ↓
    ↓ Step 6: Recommend Sites
    ↓
┌─────────────────────────────────────────────────┐
│          SITE AGENT (Port 8005)                 │
│  "The Geographic Optimizer"                     │
│  • Scores trial sites                           │
│  • Considers patient proximity                  │
│  • Evaluates site capacity                      │
└─────────────────────────────────────────────────┘
    ↓
    ↓ Step 7: Forecast Enrollment
    ↓
┌─────────────────────────────────────────────────┐
│       PREDICTION AGENT (Port 8006)              │
│  "The Timeline Forecaster"                      │
│  • Predicts enrollment timeline                 │
│  • Generates milestones                         │
│  • Estimates completion date                    │
└─────────────────────────────────────────────────┘
    ↓
    ↓ Final Aggregated Response
    ↓
┌─────────────────────────────────────────────────┐
│         COORDINATOR AGENT (Port 8000)           │
│  Returns comprehensive results to user          │
└─────────────────────────────────────────────────┘
```

---

## Communication Protocol

The Coordinator uses **Fetch.AI's official ChatProtocol** for agent-to-agent messaging:

### Message Flow
1. **Coordinator sends** → `ChatMessage` with work request
2. **Agent processes** → Performs specialized task
3. **Agent responds** → `ChatMessage` with results
4. **Coordinator aggregates** → Combines all results

### Key Features
- **Asynchronous messaging** using Fetch.AI's uAgents framework
- **Agentverse-compatible** for deployment to Fetch.AI's decentralized network
- **Local mode fallback** using AgentRegistry for development
- **Message acknowledgments** to track delivery

---

## Configuration Files

### 1. `agentverse_config.py`
Contains all agent addresses and communication mappings:

```python
AGENTVERSE_ADDRESSES = {
    "coordinator": "agent1q0t5...",
    "eligibility": "agent1qdd8...",
    "pattern": "agent1qt59...",
    # ... etc
}

AGENT_COMMUNICATION_MAP = {
    "coordinator": {
        "talks_to": ["eligibility", "pattern", "discovery", ...]
    }
}
```

### 2. `agents/config.py`
Defines ports, endpoints, and agent configurations.

### 3. `agents/models.py`
Defines all message types exchanged between agents:
- `UserQuery`
- `EligibilityRequest/Response`
- `PatternRequest/Response`
- `DiscoveryRequest/Response`
- `MatchingRequest/Response`
- `ValidationRequest/Response`
- `SiteRequest/Response`
- `PredictionRequest`
- `CoordinatorResponse`

---

## Running the Coordinator Agent

### Start Coordinator Alone
```bash
cd backend
../venv/bin/python -m agents.coordinator_agent
```

### Start All Agents (Recommended)
```bash
# Terminal 1: Coordinator
../venv/bin/python -m agents.coordinator_agent

# Terminal 2: Eligibility
../venv/bin/python -m agents.eligibility_agent

# Terminal 3: Pattern
../venv/bin/python -m agents.pattern_agent

# Terminal 4: Discovery
../venv/bin/python -m agents.discovery_agent

# Terminal 5: Matching
../venv/bin/python -m agents.matching_agent

# Terminal 6: Validation
../venv/bin/python -m agents.validation_agent

# Terminal 7: Site
../venv/bin/python -m agents.site_agent

# Terminal 8: Prediction
../venv/bin/python -m agents.prediction_agent
```

### Send a Test Query
```bash
curl -X POST http://localhost:8000/submit \
  -H "Content-Type: application/json" \
  -d '{
    "trial_id": "NCT04567890",
    "query": "Find patients with diabetes and hypertension"
  }'
```

---

## Agent Modes

### Local Mode
- Agents run on localhost (127.0.0.1)
- Uses `AgentRegistry` for agent discovery
- Best for development and testing

### Agentverse Mode
- Agents registered on Fetch.AI Almanac
- Uses agent addresses from `agentverse_config.py`
- Enables decentralized deployment
- Can run agents on different machines/clouds

---

## Monitoring & Debugging

### View Agent Inspector
Each agent has a real-time inspector URL:
```
https://agentverse.ai/inspect/?uri=http%3A//127.0.0.1%3A8000&address=agent1q0t5...
```

### Check Logs
The Coordinator logs:
- Which agents it's contacting
- Timing for each step
- Errors and warnings
- Final aggregated results

### Metrics Tracked
- `requests_processed`: Total queries handled
- `timing`: Per-agent execution time
- `agents_called`: Which agents were invoked
- `start_time`: Agent uptime

---

## Key Dependencies

```python
from uagents import Agent, Context, Protocol
from uagents_core.contrib.protocols.chat import ChatMessage, ChatProtocol
from sentence_transformers import SentenceTransformer  # For embeddings
import numpy as np
import pandas as pd
```

---

## Architecture Highlights

### Why Multi-Agent?
1. **Separation of Concerns** - Each agent has a single, well-defined responsibility
2. **Scalability** - Agents can run on different machines/processes
3. **Maintainability** - Easy to update/replace individual agents
4. **Parallel Processing** - Agents can work concurrently (future enhancement)
5. **Reusability** - Agents can be used by other systems

### Pattern Discovery Integration
The system uses a **Pattern Discovery Engine** that:
- Pre-clusters patients using UMAP (dimensionality reduction)
- Identifies natural patient groups with HDBSCAN
- Creates a "pattern library" for fast matching
- Reduces search space from 1000s to 10s of patients

### Real-World Data
- **Synthea FHIR**: Realistic synthetic patient records
- **ClinicalTrials.gov API**: Real clinical trial data
- **ICD-10/SNOMED-CT**: Standard medical code systems

---

## Future Enhancements

1. **Parallel Agent Execution** - Run agents concurrently instead of sequentially
2. **Caching Layer** - Cache eligibility criteria and patterns
3. **Machine Learning** - Train models on historical match success
4. **Real Patient Data** - Integrate with EHR systems (HIPAA-compliant)
5. **Agent Marketplace** - Deploy to Fetch.AI Agentverse for decentralized access

---

## Related Files

| File | Purpose |
|------|---------|
| `coordinator_agent.py` | Main Coordinator Agent implementation |
| `eligibility_agent.py` | Eligibility criteria extraction |
| `pattern_agent.py` | Pattern matching logic |
| `discovery_agent.py` | Patient database search |
| `matching_agent.py` | Match scoring algorithm |
| `validation_agent.py` | Validation and exclusion checks |
| `site_agent.py` | Site selection and feasibility |
| `prediction_agent.py` | Enrollment forecasting |
| `models.py` | Message type definitions |
| `config.py` | Agent configuration |
| `agentverse_config.py` | Agentverse addresses |
| `pattern_discovery_engine.py` | UMAP+HDBSCAN clustering |

---

## Support & Contact

- **Project**: TrialMatch AI - Healthcare Clinical Trial Matching Dashboard
- **Technology**: Fetch.AI uAgents, React, Python, FastAPI
- **Documentation**: See `/backend/agents/` for individual agent READMEs

---

**The Coordinator Agent is the heart of TrialMatch AI** - orchestrating 7 specialized AI agents to revolutionize clinical trial recruitment through machine learning and pattern discovery! 🚀
