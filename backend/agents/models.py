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
    query: str = Field(description="Natural language query")
    filters: Optional[Dict[str, Any]] = Field(default_factory=dict)


class CoordinatorResponse(Model):
    """Final response from coordinator to user"""
    trial_id: str
    status: str
    eligible_patients: List[Dict[str, Any]]
    total_matches: int
    recommended_sites: List[Dict[str, Any]]
    enrollment_forecast: Dict[str, Any]
    processing_time: float
    metadata: Dict[str, Any] = Field(default_factory=dict)


# ============================================================================
# ELIGIBILITY AGENT MODELS
# ============================================================================

class EligibilityRequest(Model):
    """Request to extract and analyze trial eligibility criteria"""
    trial_id: str
    trial_data: Optional[Dict[str, Any]] = Field(default=None)


class EligibilityCriteria(Model):
    """Structured eligibility criteria extracted from trial protocol"""
    trial_id: str
    inclusion_criteria: List[str]
    exclusion_criteria: List[str]
    age_range: Dict[str, int] = Field(description="{'min': 18, 'max': 65}")
    gender: Optional[str] = None
    conditions: List[str]
    lab_requirements: Dict[str, Any] = Field(
        default_factory=dict,
        description="e.g., {'HbA1c': {'max': 8.0}, 'cholesterol': {'min': 100}}"
    )
    medications: List[str] = Field(default_factory=list)

    # NEW: Medical codes for code-based matching
    inclusion_codes: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="Medical codes for inclusion: {'icd10': [...], 'snomed': [...], 'loinc': [...], 'rxnorm': [...]}"
    )
    exclusion_codes: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="Medical codes for exclusion: {'icd10': [...], 'snomed': [...], 'loinc': [...], 'rxnorm': [...]}"
    )
    found_terms: Dict[str, List[Dict]] = Field(
        default_factory=dict,
        description="Terms found in criteria text with their mappings"
    )

    metadata: Dict[str, Any] = Field(default_factory=dict)


# ============================================================================
# PATTERN AGENT MODELS
# ============================================================================

class PatternRequest(Model):
    """Request to find patterns matching eligibility criteria"""
    trial_id: str
    criteria: Dict[str, Any]  # EligibilityCriteria as dict
    min_pattern_size: int = Field(default=50)


class PatternMatch(Model):
    """Single pattern that matches criteria"""
    pattern_id: str
    size: int
    centroid: List[float]
    confidence: float
    enrollment_success_rate: float
    characteristics: Dict[str, Any] = Field(
        default_factory=dict,
        description="Average characteristics of patients in this pattern"
    )


class PatternResponse(Model):
    """Response with matching patterns"""
    trial_id: str
    patterns: List[Dict[str, Any]]  # List of PatternMatch dicts
    total_patterns: int
    conway_metadata: Dict[str, Any] = Field(default_factory=dict)


# ============================================================================
# DISCOVERY AGENT MODELS
# ============================================================================

class DiscoveryRequest(Model):
    """Request to discover patients matching patterns"""
    trial_id: str
    patterns: List[Dict[str, Any]]  # PatternMatch objects
    eligibility_criteria: Dict[str, Any]
    max_results: int = Field(default=1000)


class PatientCandidate(Model):
    """Single patient candidate"""
    patient_id: str
    pattern_id: str
    embedding: List[float]
    demographics: Dict[str, Any]
    clinical_data: Dict[str, Any]
    location: Dict[str, float] = Field(description="{'lat': 40.7, 'lon': -74.0}")


class DiscoveryResponse(Model):
    """Response with discovered patient candidates"""
    trial_id: str
    candidates: List[Dict[str, Any]]  # List of PatientCandidate dicts
    total_found: int
    search_metadata: Dict[str, Any] = Field(default_factory=dict)


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
    match_reasons: List[str] = Field(
        default_factory=list,
        description="Human-readable reasons for match"
    )
    risk_factors: List[str] = Field(
        default_factory=list,
        description="Potential issues that could affect enrollment"
    )


class MatchingResponse(Model):
    """Response with scored patient matches"""
    trial_id: str
    matches: List[Dict[str, Any]]  # List of PatientMatch dicts
    total_scored: int
    score_distribution: Dict[str, int] = Field(
        default_factory=dict,
        description="Distribution of scores (e.g., high/medium/low)"
    )


# ============================================================================
# SITE AGENT MODELS
# ============================================================================

class SiteRequest(Model):
    """Request to recommend trial sites based on feasibility and patient geography"""
    trial_id: str
    matches: List[Dict[str, Any]]  # PatientMatch objects with locations
    eligibility_criteria: Dict[str, Any] = Field(
        default_factory=dict,
        description="Trial eligibility criteria with medical codes for feasibility scoring"
    )
    target_enrollment: int = Field(default=100)
    existing_sites: Optional[List[Dict[str, Any]]] = Field(default=None)
    max_sites: int = Field(default=10)


class SiteRecommendation(Model):
    """Single site recommendation"""
    site_name: str
    location: Dict[str, Any] = Field(description="{'city': 'NYC', 'state': 'NY', 'lat': 40.7, 'lon': -74.0}")
    patient_count: int
    average_distance: float = Field(description="Average distance to patients in km")
    capacity: int = Field(description="Estimated capacity for this trial")
    current_trials: int = Field(default=0)
    priority_score: float = Field(description="Overall priority score (0-1)")
    patient_ids: List[str] = Field(default_factory=list)

    # NEW: Feasibility scores
    feasibility_score: float = Field(default=0.0, description="Overall feasibility score (0-1)")
    capability_score: float = Field(default=0.0, description="LOINC lab capability score")
    experience_score: float = Field(default=0.0, description="ICD-10 chapter experience score")
    population_score: float = Field(default=0.0, description="Patient population score")
    capacity_score: float = Field(default=0.0, description="Trial capacity score")


class SiteResponse(Model):
    """Response with site recommendations"""
    trial_id: str
    recommended_sites: List[Dict[str, Any]]  # List of SiteRecommendation dicts
    total_sites: int
    coverage_percentage: float = Field(
        description="Percentage of patients covered by recommended sites"
    )
    geographic_clusters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Geographic clustering information"
    )


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
    milestones: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="[{'week': 4, 'enrollment': 100, 'percentage': 25}, ...]"
    )
    risk_factors: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(
        default_factory=list,
        description="Actionable recommendations to improve enrollment"
    )
    pattern_success_analysis: Dict[str, Any] = Field(default_factory=dict)


# ============================================================================
# VALIDATION AGENT MODELS
# ============================================================================

class ValidationRequest(Model):
    """Request to validate patient matches against exclusion criteria"""
    trial_id: str
    matches: List[Dict[str, Any]]  # PatientMatch objects with patient codes
    exclusion_codes: Dict[str, List[str]] = Field(
        description="Trial exclusion codes: {'icd10': [...], 'snomed': [...], 'loinc': [...], 'rxnorm': [...]}"
    )


class PatientValidation(Model):
    """Validation result for a single patient"""
    patient_id: str
    is_valid: bool
    exclusion_violations: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of codes that triggered exclusion: [{'code': 'E11.21', 'system': 'ICD-10', 'reason': 'diabetic nephropathy'}, ...]"
    )
    validation_score: float = Field(
        description="0.0 (excluded) to 1.0 (fully valid)"
    )


class ValidationResponse(Model):
    """Response with validated patient matches"""
    trial_id: str
    validations: List[Dict[str, Any]]  # List of PatientValidation dicts
    total_validated: int
    total_excluded: int
    exclusion_reasons: Dict[str, int] = Field(
        default_factory=dict,
        description="Count of each exclusion reason: {'diabetic nephropathy': 5, ...}"
    )


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
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ErrorResponse(Model):
    """Standard error response"""
    agent_name: str
    error_type: str
    error_message: str
    trial_id: Optional[str] = None
    timestamp: float
