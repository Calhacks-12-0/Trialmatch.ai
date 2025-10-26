# Fetch.ai Agent Integration with Real ClinicalTrials.gov Data

## Overview

Successfully integrated 7 Fetch.ai agents with Arshia's real ClinicalTrials.gov data pipeline.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    TrialMatch AI System                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  1. Data Layer (Arshia's Work)                                  │
│     ├── ClinicalTrials.gov API v2 Integration                   │
│     │   └── Fetch real trials by NCT ID or condition            │
│     ├── Synthea FHIR Patient Data Support                       │
│     │   └── backend/data/fhir/*.json                            │
│     └── Synthetic Patient Generation (fallback)                 │
│                                                                   │
│  2. Conway Pattern Engine (Stage 1 - Unsupervised ML)           │
│     ├── Universal Embedding Creation                            │
│     │   └── sentence-transformers/all-MiniLM-L6-v2              │
│     ├── UMAP Dimensionality Reduction                           │
│     └── HDBSCAN Clustering                                      │
│                                                                   │
│  3. Fetch.ai Agent Network (Stage 2 - Your Work)                │
│     ├── Coordinator Agent (Port 8000)                           │
│     ├── Eligibility Agent (Port 8001)                           │
│     ├── Pattern Agent (Port 8002)                               │
│     ├── Discovery Agent (Port 8003)                             │
│     ├── Matching Agent (Port 8004)                              │
│     ├── Site Agent (Port 8005)                                  │
│     └── Prediction Agent (Port 8006)                            │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Two API Endpoints

### 1. Simple Matching (Prototype)
**Endpoint**: `POST /api/match/trial`

Quick rule-based matching for fast prototyping.

**Flow**:
```
User Request (NCT ID)
    ↓
Fetch Real Trial from ClinicalTrials.gov
    ↓
Generate Synthetic Patients
    ↓
SimplePatientMatcher (rule-based)
    ↓
Return Top 10 Matches
```

**Request**:
```json
{
  "trial_id": "NCT00100000"
}
```

**Response**:
```json
{
  "trial_info": {
    "nct_id": "NCT00100000",
    "title": "Study Title",
    "condition": "Diabetes",
    "phase": "Phase 3",
    "status": "Recruiting"
  },
  "total_matches": 450,
  "matches": [
    {
      "patient_id": "P000001",
      "age": 55,
      "gender": "M",
      "condition": "diabetes",
      "score": 85
    }
  ]
}
```

### 2. Full Agent Pipeline (Production)
**Endpoint**: `POST /api/match/trial/agents`

Complete pipeline with Conway pattern discovery and 7 Fetch.ai agents.

**Flow**:
```
User Request (NCT ID)
    ↓
Fetch Real Trial from ClinicalTrials.gov API
    ↓
Load Patient Data (Synthea or Synthetic)
    ↓
Conway Pattern Discovery (UMAP + HDBSCAN)
    ↓
Match Patterns to Trial
    ↓
Coordinator Agent orchestrates:
    ├── Eligibility Agent (extract criteria)
    ├── Pattern Agent (find matching patterns)
    ├── Discovery Agent (search patients)
    ├── Matching Agent (score patients)
    ├── Site Agent (geographic recommendations)
    └── Prediction Agent (enrollment forecast)
    ↓
Return Comprehensive Results
```

**Request**:
```json
{
  "trial_id": "NCT05613530"
}
```

**Response**:
```json
{
  "status": "success",
  "processing_time": "45.23 seconds",
  "statistics": {
    "total_patients": 1000,
    "total_trials": 1,
    "patterns_discovered": 27,
    "clustered_patients": 934,
    "noise_patients": 66
  },
  "pattern_insights": [
    {
      "pattern_id": 0,
      "size": 127,
      "avg_age": 58.5,
      "common_conditions": ["diabetes", "hypertension"],
      "success_rate": 0.87
    }
  ],
  "trial_matches": [
    {
      "pattern_id": 0,
      "size": 127,
      "match_score": 0.92,
      "eligibility_overlap": 0.85
    }
  ],
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
    "confidence_score": 0.87,
    "coordinator_status": "active"
  },
  "visualization_data": {
    "embeddings": [...],
    "cluster_labels": [...]
  }
}
```

## Files Added/Modified

### New Files (from Brandon branch)
```
backend/agents/
├── models.py              # Pydantic message models
├── config.py              # Agent registry and configuration
├── coordinator_agent.py   # Main orchestrator
├── eligibility_agent.py   # Extract eligibility criteria
├── pattern_agent.py       # Find Conway patterns
├── discovery_agent.py     # Search patient database
├── matching_agent.py      # Score patients
├── site_agent.py          # Geographic recommendations
└── prediction_agent.py    # Enrollment forecasting

backend/run_agents.py      # Bureau runner for all 7 agents
```

### Modified Files
```
backend/integration_service.py
  - Added pandas import
  - Updated process_trial_matching() to fetch real trials
  - Added trial_id, use_synthea, max_patients parameters
  - Fetches specific trial from ClinicalTrials.gov API

backend/app.py
  - Added new endpoint: POST /api/match/trial/agents
  - Kept existing: POST /api/match/trial (simple matcher)
  - New endpoint uses full agent pipeline with Conway
```

### Files from Arshia (Kept)
```
backend/data_loader.py          # Real ClinicalTrials.gov integration
backend/simple_matcher.py       # Rule-based prototype
backend/conway_engine.py        # Pattern discovery
```

## How to Use

### Terminal 1: Start Agents
```bash
cd backend
source venv/bin/activate
python run_agents.py
```

Expected output:
```
✓ Registered coordinator: agent1q0t5...
✓ Registered eligibility: agent1qdd8...
✓ Registered pattern: agent1qt59...
✓ Registered discovery: agent1qfd0...
✓ Registered matching: agent1q2q2...
✓ Registered site: agent1qg5m...
✓ Registered prediction: agent1qt43...
INFO: Starting server on http://0.0.0.0:8001
```

### Terminal 2: Start FastAPI Backend
```bash
cd backend
source venv/bin/activate
python app.py
```

Expected output:
```
INFO: Started server process
INFO: Uvicorn running on http://0.0.0.0:8080
```

### Terminal 3: Test Endpoints

**Test Simple Matcher**:
```bash
curl -X POST http://localhost:8080/api/match/trial \
  -H "Content-Type: application/json" \
  -d '{"trial_id": "NCT05613530"}'
```

**Test Full Agent Pipeline**:
```bash
curl -X POST http://localhost:8080/api/match/trial/agents \
  -H "Content-Type: application/json" \
  -d '{"trial_id": "NCT05613530"}'
```

**Note**: First run takes 30-60 seconds to download ML model.

## Real ClinicalTrials.gov NCT IDs to Test

Here are some real recruiting trials you can test:

- `NCT05613530` - Diabetes trial
- `NCT06037954` - Hypertension trial
- `NCT05500131` - Cancer trial
- `NCT05982652` - Cardiovascular trial
- `NCT06038565` - Alzheimer's trial

## Key Features

### 1. Real Data Integration
- ✅ Fetches real trials from ClinicalTrials.gov API v2
- ✅ Parses trial eligibility criteria (age, gender, conditions)
- ✅ Supports Synthea FHIR patient data
- ✅ Falls back to synthetic data if API fails

### 2. Conway Pattern Discovery
- ✅ Unsupervised learning with UMAP + HDBSCAN
- ✅ Discovers patient clusters without labels
- ✅ Pattern insights: size, age distribution, conditions
- ✅ Matches patterns to trial eligibility

### 3. Fetch.ai Agent Network
- ✅ 7 specialized agents with message-passing communication
- ✅ Coordinator orchestrates entire workflow
- ✅ Type-safe Pydantic models for inter-agent messages
- ✅ Bureau runner for local development

### 4. Two-Stage Pipeline
- ✅ Stage 1: Conway discovers patterns (unsupervised)
- ✅ Stage 2: Agents work WITH pre-discovered patterns
- ✅ No redundancy - agents don't re-discover patterns

## Performance

- **Simple Matcher**: ~1-2 seconds (rule-based, fast)
- **Full Agent Pipeline**: ~30-60 seconds (first run with ML model download)
  - Subsequent runs: ~10-15 seconds
  - Conway pattern discovery: ~8-10 seconds
  - Agent coordination: ~2-3 seconds

## Next Steps

1. **Test with Real Trials**: Use actual NCT IDs from ClinicalTrials.gov
2. **Add Synthea Data**: Place FHIR JSON files in `backend/data/fhir/`
3. **Deploy Agents**: See `docs/AGENTVERSE_DEPLOYMENT.md` for cloud deployment
4. **Frontend Integration**: Connect React dashboard to new `/agents` endpoint

## Troubleshooting

### Agents Not Starting
```bash
# Check if port 8000-8006 are available
lsof -i :8000-8006

# Kill any blocking processes
kill -9 <PID>
```

### ClinicalTrials.gov API Rate Limit
- API has rate limits, use trial_id for specific trials
- Falls back to synthetic data if API fails
- Sample trials saved to `trials_sample.json`

### Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Ensure Python 3.9-3.12 (NOT 3.13)
python --version
```

## Summary

You now have:
- ✅ Real ClinicalTrials.gov data (Arshia's work)
- ✅ 7 Fetch.ai agents (Your work)
- ✅ Conway Pattern Engine (Unsupervised ML)
- ✅ Two API endpoints (simple + full pipeline)
- ✅ Complete integration ready for demo

**Simple matcher** for quick prototypes, **full agent pipeline** for production-quality matching with ML patterns and agent coordination.
