"""
Validation Agent: Validates patient matches against trial exclusion criteria using medical codes.

Responsibilities:
- Receive patient match candidates with their medical codes (ICD-10, SNOMED, LOINC, RxNorm)
- Receive trial exclusion codes from eligibility criteria
- Check if any patient codes appear in exclusion codes
- Flag matches that violate exclusion criteria
- Return validation results with specific violation reasons

This solves the negation problem: distinguishing between "has diabetes" (E11.9)
and "no history of diabetes" (exclusion code E11.9).
"""

from uagents import Agent, Context
import logging
import time
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.models import ValidationRequest, ValidationResponse, PatientValidation, AgentStatus
from agents.config import AgentConfig, AgentRegistry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

config = AgentConfig.get_agent_config("validation")
agent = Agent(**config)

agent_state = {
    "requests_processed": 0,
    "start_time": time.time(),
    "total_validated": 0,
    "total_excluded": 0
}


@agent.on_event("startup")
async def startup(ctx: Context):
    logger.info(f"✓ Validation Agent started: {agent.address}")
    AgentRegistry.register("validation", agent.address)


@agent.on_message(model=ValidationRequest)
async def handle_validation_request(ctx: Context, sender: str, msg: ValidationRequest):
    """Validate patient matches against exclusion codes"""
    logger.info(f"  → Validation Agent processing: {msg.trial_id} ({len(msg.matches)} candidates)")

    try:
        validations = []
        excluded_count = 0
        exclusion_reason_counts = {}

        for match in msg.matches:
            # Extract patient codes from match
            patient_id = match.get("patient_id", "UNKNOWN")

            # Get patient medical codes (from demographics or clinical_data)
            patient_codes = extract_patient_codes(match)

            # Check for exclusion violations
            violations = check_exclusions(patient_codes, msg.exclusion_codes)

            # Calculate validation score
            is_valid = len(violations) == 0
            validation_score = 1.0 if is_valid else 0.0

            # Count exclusion reasons
            for violation in violations:
                reason = violation.get("reason", "Unknown")
                exclusion_reason_counts[reason] = exclusion_reason_counts.get(reason, 0) + 1

            if not is_valid:
                excluded_count += 1

            validations.append({
                "patient_id": patient_id,
                "is_valid": is_valid,
                "exclusion_violations": violations,
                "validation_score": validation_score
            })

        agent_state["requests_processed"] += 1
        agent_state["total_validated"] += len(msg.matches)
        agent_state["total_excluded"] += excluded_count

        logger.info(f"  ✓ Validated {len(validations)} patients, excluded {excluded_count}")

        response = ValidationResponse(
            trial_id=msg.trial_id,
            validations=validations,
            total_validated=len(validations),
            total_excluded=excluded_count,
            exclusion_reasons=exclusion_reason_counts
        )

        await ctx.send(sender, response)

    except Exception as e:
        logger.error(f"Error in validation: {e}")
        error_response = ValidationResponse(
            trial_id=msg.trial_id,
            validations=[],
            total_validated=0,
            total_excluded=0,
            exclusion_reasons={"error": str(e)}
        )
        await ctx.send(sender, error_response)


def extract_patient_codes(match: dict) -> dict:
    """
    Extract medical codes from patient match data.

    Args:
        match: Patient match dictionary containing demographics and clinical_data

    Returns:
        Dict with code lists: {"icd10": [...], "snomed": [...], "loinc": [...], "rxnorm": [...]}
    """
    patient_codes = {
        "icd10": [],
        "snomed": [],
        "loinc": [],
        "rxnorm": []
    }

    # Check demographics for code fields
    demographics = match.get("demographics", {})
    if "icd10_codes" in demographics:
        patient_codes["icd10"] = demographics["icd10_codes"]
    if "snomed_codes" in demographics:
        patient_codes["snomed"] = demographics["snomed_codes"]

    # Check clinical_data for code fields
    clinical_data = match.get("clinical_data", {})
    if "icd10_codes" in clinical_data:
        patient_codes["icd10"].extend(clinical_data.get("icd10_codes", []))
    if "snomed_codes" in clinical_data:
        patient_codes["snomed"].extend(clinical_data.get("snomed_codes", []))
    if "loinc_codes" in clinical_data:
        patient_codes["loinc"] = clinical_data.get("loinc_codes", [])
    if "rxnorm_codes" in clinical_data:
        patient_codes["rxnorm"] = clinical_data.get("rxnorm_codes", [])

    # Remove duplicates
    for system in patient_codes:
        patient_codes[system] = list(set(patient_codes[system]))

    return patient_codes


def check_exclusions(patient_codes: dict, exclusion_codes: dict) -> list:
    """
    Check if patient codes violate any exclusion criteria.

    Args:
        patient_codes: Patient's medical codes by system
        exclusion_codes: Trial exclusion codes by system

    Returns:
        List of violation dictionaries with code, system, and reason
    """
    violations = []

    # Define human-readable reasons for common exclusion codes
    exclusion_reasons = {
        # Diabetic complications
        "E11.21": "diabetic nephropathy",
        "E10.21": "diabetic kidney disease (Type 1)",
        "E11.31": "diabetic retinopathy",
        "E10.31": "diabetic retinopathy (Type 1)",
        "E11.22": "diabetic chronic kidney disease",
        "E11.42": "diabetic neuropathy",

        # Cardiovascular exclusions
        "I50.9": "heart failure",
        "I21.9": "recent myocardial infarction",

        # Renal exclusions
        "N18.6": "end-stage renal disease",
        "N18.5": "chronic kidney disease stage 5",

        # Cancer exclusions
        "C50.9": "breast cancer",
        "C34.9": "lung cancer",

        # SNOMED codes
        "127013003": "diabetic nephropathy",
        "4855003": "diabetic retinopathy"
    }

    # Check each code system
    for system in ["icd10", "snomed", "loinc", "rxnorm"]:
        patient_system_codes = set(patient_codes.get(system, []))
        exclusion_system_codes = set(exclusion_codes.get(system, []))

        # Find intersections (violations)
        violated_codes = patient_system_codes.intersection(exclusion_system_codes)

        for code in violated_codes:
            reason = exclusion_reasons.get(code, f"excluded {system.upper()} code")
            violations.append({
                "code": code,
                "system": system.upper(),
                "reason": reason
            })

    return violations


@agent.on_message(model=AgentStatus)
async def handle_status(ctx: Context, sender: str, msg: AgentStatus):
    await ctx.send(sender, AgentStatus(
        agent_name="validation_agent",
        status="healthy",
        address=agent.address,
        uptime=time.time() - agent_state["start_time"],
        requests_processed=agent_state["requests_processed"],
        metadata={
            "total_validated": agent_state["total_validated"],
            "total_excluded": agent_state["total_excluded"]
        }
    ))


if __name__ == "__main__":
    agent.run()
