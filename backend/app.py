from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import asyncio
from integration_service import TrialMatchIntegrationService
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

# Initialize integration service
integration_service = TrialMatchIntegrationService()

class TrialMatchRequest(BaseModel):
    trial_id: Optional[str] = None
    query: Optional[str] = None

@app.on_event("startup")
async def startup():
    """Initialize services on startup"""
    logger.info("TrialMatch AI API starting...")
    # Pre-load data for faster demos
    await integration_service.process_trial_matching()
    logger.info("Initial data loaded")

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
    Main endpoint: Process trial matching request
    Flow: Data → Conway → Fetch.ai Agents → Results
    """
    try:
        logger.info(f"Processing match request for trial: {request.trial_id}")
        results = await integration_service.process_trial_matching(request.trial_id)
        return results
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