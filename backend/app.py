from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import asyncio
from integration_service import TrialMatchIntegrationService
from data_loader import ClinicalDataLoader
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
    Patient matching endpoint using Conway pattern discovery
    Uses the same pipeline as the full agent version but returns simpler results
    """
    try:
        trial_id = request.trial_id
        if not trial_id:
            raise HTTPException(status_code=400, detail="trial_id is required")

        logger.info(f"Pattern-based matching for trial: {trial_id}")

        # Use the integration service to perform matching with Conway patterns
        results = await integration_service.process_trial_matching(
            trial_id=trial_id,
            use_synthea=False,
            max_patients=1000
        )

        # Simplify results for this endpoint
        simplified_results = {
            'trial_id': trial_id,
            'total_matches': results['statistics']['clustered_patients'],
            'patterns_discovered': results['statistics']['patterns_discovered'],
            'top_insights': results['pattern_insights'][:5],
            'processing_time': results['processing_time']
        }

        logger.info(f"Matched {simplified_results['total_matches']} patients using {simplified_results['patterns_discovered']} patterns")

        return simplified_results

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/match/trial/agents")
async def match_trial_with_agents(request: TrialMatchRequest):
    """
    Full agent pipeline with Conway pattern discovery
    Uses real ClinicalTrials.gov data + Fetch.ai agents

    Flow: Real Trial Data → Conway Pattern Discovery → 7 Fetch.ai Agents → Results
    """
    try:
        trial_id = request.trial_id
        if not trial_id:
            raise HTTPException(status_code=400, detail="trial_id is required")

        logger.info(f"Full agent pipeline for trial: {trial_id}")
        logger.info("Pipeline: ClinicalTrials.gov → Conway → Fetch.ai Agents")

        # Run full pipeline with real data and agents
        results = await integration_service.process_trial_matching(
            trial_id=trial_id,
            use_synthea=False,  # Use synthetic patients (can change to True if Synthea data available)
            max_patients=1000
        )

        logger.info(f"Agent pipeline completed in {results['processing_time']}")

        return results

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Agent pipeline failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/patterns")
async def get_patterns():
    """Get discovered patterns for visualization"""
    if not integration_service.conway_engine.patterns:
        await integration_service.process_trial_matching()

    # Get patient data for insights
    patient_data = integration_service.data_loader.patients_df.to_dict('records') if integration_service.data_loader.patients_df is not None else None

    # Get 3D embeddings and cluster labels for visualization
    embeddings_3d = []
    cluster_labels = []
    if hasattr(integration_service.conway_engine, 'reduced_embeddings_3d') and hasattr(integration_service.conway_engine, 'cluster_labels'):
        embeddings_3d = integration_service.conway_engine.reduced_embeddings_3d[:1000].tolist()
        cluster_labels = integration_service.conway_engine.cluster_labels[:1000].tolist()

    return {
        'patterns': integration_service.conway_engine.patterns[:10],
        'insights': integration_service.conway_engine.get_pattern_insights(patient_data=patient_data)[:10],
        'embeddings_3d': embeddings_3d,
        'cluster_labels': cluster_labels
    }

@app.get("/api/agents/status")
async def get_agent_status():
    """Get Fetch.ai agent network status by checking if Bureau is running"""
    from agents.config import AgentConfig
    import socket

    def check_port(port: int) -> bool:
        """Check if a port is open (agent is running)"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            return result == 0
        except:
            return False

    # Check if Bureau is running on port 8001 (all agents run through Bureau)
    bureau_active = check_port(8001)

    agent_info = [
        {'name': 'Coordinator Agent', 'port': AgentConfig.COORDINATOR_PORT},
        {'name': 'Eligibility Agent', 'port': AgentConfig.ELIGIBILITY_PORT},
        {'name': 'Pattern Agent', 'port': AgentConfig.PATTERN_PORT},
        {'name': 'Discovery Agent', 'port': AgentConfig.DISCOVERY_PORT},
        {'name': 'Matching Agent', 'port': AgentConfig.MATCHING_PORT},
        {'name': 'Site Agent', 'port': AgentConfig.SITE_PORT},
        {'name': 'Prediction Agent', 'port': AgentConfig.PREDICTION_PORT}
    ]

    agents_status = []

    # If Bureau is active, all agents are active
    for agent in agent_info:
        agents_status.append({
            'name': agent['name'],
            'status': 'active' if bureau_active else 'offline',
            'port': agent['port']
        })

    return {
        'agents': agents_status,
        'active_count': len(agent_info) if bureau_active else 0,
        'total_count': len(agent_info),
        'bureau_active': bureau_active
    }

@app.get("/api/patients/geographic")
async def get_patient_geographic_distribution():
    """
    Get patient geographic distribution and recommended trial sites
    Returns patient locations and clustered site recommendations
    """
    try:
        import numpy as np
        from sklearn.cluster import KMeans

        logger.info("Fetching patient geographic distribution...")

        # Load patient data
        data_loader_instance = ClinicalDataLoader()
        patients_df = data_loader_instance.generate_synthetic_patients(n_patients=2000)

        # Extract geographic coordinates
        patients_data = patients_df.to_dict('records')
        patient_locations = []

        for patient in patients_data:
            patient_locations.append({
                'patient_id': patient['patient_id'],
                'latitude': float(patient['latitude']),
                'longitude': float(patient['longitude']),
                'age': patient['age'],
                'condition': patient['primary_condition']
            })

        # Perform geographic clustering to identify optimal site locations
        coordinates = np.array([[p['latitude'], p['longitude']] for p in patient_locations])

        # Use k-means to find 8 optimal site locations
        n_sites = 8
        kmeans = KMeans(n_clusters=n_sites, random_state=42, n_init=10)
        kmeans.fit(coordinates)

        # Calculate cluster assignments and densities
        cluster_labels = kmeans.labels_
        cluster_centers = kmeans.cluster_centers_

        # Build recommended sites with patient counts
        recommended_sites = []
        site_names = [
            "Memorial Medical Center",
            "University Hospital",
            "Regional Research Institute",
            "City Health Center",
            "Coastal Medical Campus",
            "Metro Clinical Research",
            "Valley Healthcare System",
            "Northside Medical Complex"
        ]

        for i, center in enumerate(cluster_centers):
            cluster_patients = np.sum(cluster_labels == i)
            cluster_patient_data = [p for j, p in enumerate(patient_locations) if cluster_labels[j] == i]

            # Calculate average age and condition distribution for cluster
            avg_age = np.mean([p['age'] for p in cluster_patient_data])
            conditions = [p['condition'] for p in cluster_patient_data]
            condition_counts = {}
            for cond in conditions:
                condition_counts[cond] = condition_counts.get(cond, 0) + 1

            primary_condition = max(condition_counts.items(), key=lambda x: x[1])[0] if condition_counts else 'unknown'

            # Estimate capacity based on patient density
            capacity = min(95, 60 + (cluster_patients // 30))

            recommended_sites.append({
                'id': i + 1,
                'name': site_names[i],
                'latitude': float(center[0]),
                'longitude': float(center[1]),
                'patient_count': int(cluster_patients),
                'avg_age': round(float(avg_age), 1),
                'primary_condition': primary_condition,
                'capacity': int(capacity),
                'cluster_id': i
            })

        # Sort by patient count (highest density first)
        recommended_sites.sort(key=lambda x: x['patient_count'], reverse=True)

        # Assign cluster_id to each patient for visualization
        for i, patient in enumerate(patient_locations):
            patient['cluster_id'] = int(cluster_labels[i])

        logger.info(f"Analyzed {len(patient_locations)} patients across {n_sites} geographic clusters")

        return {
            'patients': patient_locations,
            'recommended_sites': recommended_sites,
            'total_patients': len(patient_locations),
            'total_sites': len(recommended_sites),
            'metadata': {
                'clustering_method': 'k-means',
                'n_clusters': n_sites
            }
        }

    except Exception as e:
        logger.error(f"Geographic analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)