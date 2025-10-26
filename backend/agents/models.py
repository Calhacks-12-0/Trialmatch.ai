"""
Shared message models for all agents in the TrialMatch system.
All inter-agent communication uses these Pydantic models.
"""

from uagents import Model
from typing import List, Dict, Any, Optional
from pydantic import Field


# ============================================================================
# COORDINATOR AGENT MODELS
# ============================================================================

class UserQuery(Model):
    """Initial user query to coordinator"""
    trial_id: str
    query: str
    filters: Optional[Dict[str, Any]] = None


class CoordinatorResponse(Model):
    """Final response from coordinator to user"""
    trial_id: str
    status: str
    eligible_patients: List[Dict[str, Any]]
    total_matches: int
    recommended_sites: List[Dict[str, Any]]
    enrollment_forecast: Dict[str, Any]
    processing_time: float
    metadata: Optional[Dict[str, Any]] = None


# ============================================================================
# ELIGIBILITY AGENT MODELS
# ============================================================================

class EligibilityRequest(Model):
    """Request to extract and analyze trial eligibility criteria"""
    trial_id: str
    trial_data: Optional[Dict[str, Any]] = None


class EligibilityCriteria(Model):
    """Structured eligibility criteria extracted from trial protocol"""
    trial_id: str
    inclusion_criteria: List[str]
    exclusion_criteria: List[str]
    age_range: Dict[str, int]
    gender: Optional[str] = None
    conditions: List[str]
    lab_requirements: Optional[Dict[str, Any]] = None
    medications: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


# ============================================================================
# PATTERN AGENT MODELS
# ============================================================================

class PatternRequest(Model):
    """Request to find patterns matching eligibility criteria"""
    trial_id: str
    criteria: Dict[str, Any]  # EligibilityCriteria as dict
    min_pattern_size: int = 50


class PatternMatch(Model):
    """Single pattern that matches criteria"""
    pattern_id: str
    size: int
    centroid: List[float]
    confidence: float
    enrollment_success_rate: float
    characteristics: Optional[Dict[str, Any]] = None


class PatternResponse(Model):
    """Response with matching patterns"""
    trial_id: str
    patterns: List[Dict[str, Any]]  # List of PatternMatch dicts
    total_patterns: int
    conway_metadata: Optional[Dict[str, Any]] = None


# ============================================================================
# DISCOVERY AGENT MODELS
# ============================================================================

class DiscoveryRequest(Model):
    """Request to discover patients matching patterns"""
    trial_id: str
    patterns: List[Dict[str, Any]]  # PatternMatch objects
    eligibility_criteria: Dict[str, Any]
    max_results: int = 1000


class PatientCandidate(Model):
    """Single patient candidate"""
    patient_id: str
    pattern_id: str
    embedding: List[float]
    demographics: Dict[str, Any]
    clinical_data: Dict[str, Any]
    location: Dict[str, float]


class DiscoveryResponse(Model):
    """Response with discovered patient candidates"""
    trial_id: str
    candidates: List[Dict[str, Any]]  # List of PatientCandidate dicts
    total_found: int
    search_metadata: Optional[Dict[str, Any]] = None


# ============================================================================
# MATCHING AGENT MODELS
# ============================================================================

class MatchingRequest(Model):
    """Request to score patients against trial criteria"""
    trial_id: str
    candidates: List[Dict[str, Any]]  # PatientCandidate objects
    eligibility_criteria: Dict[str, Any]
    patterns: List[Dict[str, Any]]  # For similarity scoring


class PatientMatch(Model):
    """Single patient with match score"""
    patient_id: str
    pattern_id: str
    overall_score: float
    eligibility_score: float
    similarity_score: float
    enrollment_probability: float
    demographics: Dict[str, Any]
    location: Dict[str, float]
    match_reasons: Optional[List[str]] = None
    risk_factors: Optional[List[str]] = None


class MatchingResponse(Model):
    """Response with scored patient matches"""
    trial_id: str
    matches: List[Dict[str, Any]]  # List of PatientMatch dicts
    total_scored: int
    score_distribution: Optional[Dict[str, int]] = None


# ============================================================================
# SITE AGENT MODELS
# ============================================================================

class SiteRequest(Model):
    """Request to recommend trial sites based on patient geography"""
    trial_id: str
    matches: List[Dict[str, Any]]  # PatientMatch objects with locations
    existing_sites: Optional[List[Dict[str, Any]]] = None
    max_sites: int = 10


class SiteRecommendation(Model):
    """Single site recommendation"""
    site_name: str
    location: Dict[str, Any]
    patient_count: int
    average_distance: float
    capacity: int
    current_trials: int
    priority_score: float
    patient_ids: Optional[List[str]] = None


class SiteResponse(Model):
    """Response with site recommendations"""
    trial_id: str
    recommended_sites: List[Dict[str, Any]]  # List of SiteRecommendation dicts
    total_sites: int
    coverage_percentage: float
    geographic_clusters: Optional[Dict[str, Any]] = None


# ============================================================================
# PREDICTION AGENT MODELS
# ============================================================================

class PredictionRequest(Model):
    """Request to forecast enrollment timeline"""
    trial_id: str
    target_enrollment: int
    matches: List[Dict[str, Any]]  # PatientMatch objects
    patterns: List[Dict[str, Any]]  # Pattern success rates
    sites: List[Dict[str, Any]]  # SiteRecommendation objects


class EnrollmentForecast(Model):
    """Enrollment prediction with timeline"""
    trial_id: str
    target_enrollment: int
    predicted_enrollment: int
    estimated_weeks: float
    confidence: float
    weekly_enrollment_rate: float
    milestones: Optional[List[Dict[str, Any]]] = None
    risk_factors: Optional[List[str]] = None
    recommendations: Optional[List[str]] = None
    pattern_success_analysis: Optional[Dict[str, Any]] = None


# ============================================================================
# INTERNAL AGENT COMMUNICATION
# ============================================================================

class AgentStatus(Model):
    """Health check response from any agent"""
    agent_name: str
    status: str
    address: str
    uptime: float
    requests_processed: int
    metadata: Optional[Dict[str, Any]] = None


class ErrorResponse(Model):
    """Standard error response"""
    agent_name: str
    error_type: str
    error_message: str
    trial_id: Optional[str] = None
    timestamp: float
