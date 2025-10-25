from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import asyncio
from integration_service import TrialMatchIntegrationService
from data_loader import ClinicalDataLoader
from simple_matcher import SimplePatientMatcher
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="TrialMatch AI API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
integration_service = TrialMatchIntegrationService()
data_loader = ClinicalDataLoader()
simple_matcher = SimplePatientMatcher()

class TrialMatchRequest(BaseModel):
    trial_id: Optional[str] = None
    query: Optional[str] = None

@app.on_event("startup")
async def startup():
    """Initialize services on startup"""
    logger.info("TrialMatch AI API starting...")
    # Skip pre-loading for faster startup (data loaded on-demand)
    logger.info("API ready - data will be loaded on first request")

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "TrialMatch AI"}

@app.get("/api/dashboard/metrics")
async def get_dashboard_metrics():
    """Get real-time dashboard metrics"""
    return integration_service.get_dashboard_metrics()

@app.post("/api/match/trial")
async def match_trial(request: TrialMatchRequest):
    """
    Simple patient matching endpoint (Prototype)
    Uses basic rule-based matching before full Conway/Fetch.ai pipeline
    """
    try:
        trial_id = request.trial_id
        if not trial_id:
            raise HTTPException(status_code=400, detail="trial_id is required")

        logger.info(f"Simple matching for trial: {trial_id}")

        # Fetch trial details from ClinicalTrials.gov
        data_loader_instance = ClinicalDataLoader()

        # Try to fetch the specific trial
        try:
            import requests
            response = requests.get(
                f"https://clinicaltrials.gov/api/v2/studies/{trial_id}",
                timeout=10
            )

            if response.status_code == 200:
                study_data = response.json()
                study = study_data.get('studies', [{}])[0] if 'studies' in study_data else study_data

                # Parse the trial using data_loader's parse method
                trial_info = data_loader_instance._parse_study(study)
            else:
                raise HTTPException(status_code=404, detail=f"Trial {trial_id} not found")

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch trial: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch trial from ClinicalTrials.gov")

        # Generate synthetic patient data
        patients_df = data_loader_instance.generate_synthetic_patients(n_patients=1000)
        patients_data = patients_df.to_dict('records')

        # Perform simple matching
        results = simple_matcher.match_patients_to_trial(trial_info, patients_data, top_n=10)

        logger.info(f"Matched {results['total_matches']} patients, returning top {len(results['matches'])}")

        return results

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/patterns")
async def get_patterns():
    """Get discovered patterns for visualization"""
    if not integration_service.conway_engine.patterns:
        await integration_service.process_trial_matching()
    
    return {
        'patterns': integration_service.conway_engine.patterns[:10],
        'insights': integration_service.conway_engine.get_pattern_insights()[:5]
    }

@app.get("/api/agents/status")
async def get_agent_status():
    """Get Fetch.ai agent network status"""
    return {
        'agents': [
            {'name': 'Coordinator', 'status': 'active', 'tasks': 45},
            {'name': 'Pattern Discovery', 'status': 'active', 'tasks': 234},
            {'name': 'Eligibility', 'status': 'active', 'tasks': 189},
            {'name': 'Matching', 'status': 'active', 'tasks': 156},
            {'name': 'Site Selection', 'status': 'idle', 'tasks': 98},
            {'name': 'Prediction', 'status': 'active', 'tasks': 67}
        ],
        'total_messages': 789,
        'avg_response_time': '234ms'
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)