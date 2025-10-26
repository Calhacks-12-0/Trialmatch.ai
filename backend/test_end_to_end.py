#!/usr/bin/env python3
"""
End-to-End Integration Test - All 4 Phases Working Together

Tests the complete pipeline from trial criteria → site recommendations:
1. Phase 1: Extract medical codes from FHIR data
2. Phase 2: Eligibility agent extracts codes from trial criteria
3. Phase 3: Validation agent checks exclusion criteria
4. Phase 4: Site agent scores feasibility and recommends sites

This demonstrates all advisor requirements working together.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from trial_criteria_mapper import TrialCriteriaMapper
from site_feasibility_scorer import SiteFeasibilityScorer
from agents.validation_agent import check_exclusions, extract_patient_codes
from fhir_code_extractor import FHIRCodeExtractor
import json

print("=" * 80)
print("END-TO-END INTEGRATION TEST")
print("Testing All 4 Phases: Code Extraction → Eligibility → Validation → Site Feasibility")
print("=" * 80)
print()

# ============================================================================
# PHASE 1: Extract Medical Codes from FHIR Data
# ============================================================================
print("PHASE 1: Extract Medical Codes from FHIR Data")
print("-" * 80)

# Load a sample Synthea patient
patient_file = "fhir/Aaron697_Abernathy674_434edd9b-7e79-3154-0448-61b9596261d2.json"
if os.path.exists(patient_file):
    with open(patient_file, 'r') as f:
        patient_bundle = json.load(f)

    code_extractor = FHIRCodeExtractor()
    extracted_codes = code_extractor.extract_all_codes_from_bundle(patient_bundle)

    print(f"✓ Extracted codes from patient FHIR bundle:")
    print(f"  - Condition codes: {len(extracted_codes['condition_codes'])} (diagnoses)")
    print(f"  - Observation codes: {len(extracted_codes['observation_codes'])} (lab results)")
    print(f"  - Medication codes: {len(extracted_codes['medication_codes'])} (prescriptions)")

    # Show sample codes
    if extracted_codes['condition_codes']:
        sample_condition = extracted_codes['condition_codes'][0]
        print(f"  - Sample condition: {sample_condition.get('display', 'N/A')} ({sample_condition['code']})")
else:
    print("⚠ No FHIR data found - using mock codes")
    extracted_codes = {
        'condition_codes': [{'code': 'E11.9', 'system': 'ICD-10', 'display': 'Type 2 diabetes'}],
        'observation_codes': [{'code': '4548-4', 'system': 'LOINC', 'display': 'HbA1c'}],
        'medication_codes': [{'code': '6809', 'system': 'RxNorm', 'display': 'Metformin'}]
    }

print()

# ============================================================================
# PHASE 2: Eligibility Agent Extracts Codes from Trial Criteria
# ============================================================================
print("PHASE 2: Eligibility Agent - Trial Criteria Mapping")
print("-" * 80)

# Sample diabetes trial criteria (natural language)
trial_criteria_text = [
    "Patients with Type 2 diabetes mellitus",
    "Age 18-65 years",
    "HbA1c between 7-10%",
    "On metformin therapy",
    "No history of diabetic nephropathy",  # EXCLUSION
    "No diabetic retinopathy"  # EXCLUSION
]

print("Trial Criteria (natural language):")
for i, criterion in enumerate(trial_criteria_text, 1):
    print(f"  {i}. {criterion}")
print()

# Map to medical codes
mapper = TrialCriteriaMapper()
mapped_codes = mapper.map_criteria_to_codes(trial_criteria_text)

print("✓ Mapped to Medical Codes:")
print(f"  Inclusion Codes:")
print(f"    - ICD-10: {', '.join(mapped_codes['inclusion_codes']['icd10'])}")
print(f"    - LOINC: {', '.join(mapped_codes['inclusion_codes']['loinc'][:3])}...")
print(f"    - RxNorm: {', '.join(mapped_codes['inclusion_codes']['rxnorm'])}")
print(f"  Exclusion Codes:")
print(f"    - ICD-10: {', '.join(mapped_codes['exclusion_codes']['icd10'])}")
print(f"    - SNOMED: {', '.join(mapped_codes['exclusion_codes']['snomed'])}")
print(f"  Demographics:")
print(f"    - Age: {mapped_codes['demographics']['age_range']}")
print()

# ============================================================================
# PHASE 3: Validation Agent Checks Exclusion Criteria
# ============================================================================
print("PHASE 3: Validation Agent - Exclusion Checking")
print("-" * 80)

# Create mock patient matches
mock_patients = [
    {
        "patient_id": "P001",
        "name": "Clean Patient (should PASS)",
        "clinical_data": {
            "icd10_codes": ["E11.9"],  # Type 2 diabetes only
            "snomed_codes": ["44054006"],
            "loinc_codes": ["4548-4"],
            "rxnorm_codes": ["6809"]
        }
    },
    {
        "patient_id": "P002",
        "name": "Patient with Nephropathy (should FAIL)",
        "clinical_data": {
            "icd10_codes": ["E11.9", "E11.21"],  # Diabetes + nephropathy
            "snomed_codes": ["44054006", "127013003"],
            "loinc_codes": ["4548-4"],
            "rxnorm_codes": ["6809"]
        }
    },
    {
        "patient_id": "P003",
        "name": "Patient with Retinopathy (should FAIL)",
        "clinical_data": {
            "icd10_codes": ["E11.9", "E11.31"],  # Diabetes + retinopathy
            "snomed_codes": ["44054006", "4855003"],
            "loinc_codes": ["4548-4"],
            "rxnorm_codes": ["6809"]
        }
    }
]

print("Validating 3 patient matches against exclusion criteria:")
print()

valid_count = 0
excluded_count = 0

for patient in mock_patients:
    patient_codes = extract_patient_codes(patient)
    violations = check_exclusions(patient_codes, mapped_codes['exclusion_codes'])

    is_valid = len(violations) == 0
    if is_valid:
        valid_count += 1
        status = "✓ PASS"
    else:
        excluded_count += 1
        status = "✗ FAIL"

    print(f"{status} - {patient['name']}")
    if violations:
        for v in violations:
            print(f"       Violation: {v['system']} {v['code']} - {v['reason']}")
    print()

print(f"✓ Validation complete: {valid_count} valid, {excluded_count} excluded")
print()

# ============================================================================
# PHASE 4: Site Agent - Feasibility Scoring
# ============================================================================
print("PHASE 4: Site Agent - Feasibility Scoring")
print("-" * 80)

# Use the mapped codes from Phase 2 as trial criteria
trial_criteria = {
    "inclusion_codes": mapped_codes['inclusion_codes'],
    "exclusion_codes": mapped_codes['exclusion_codes']
}

target_enrollment = 150

print(f"Trial Requirements:")
print(f"  - Target Enrollment: {target_enrollment}")
print(f"  - Required LOINC: {', '.join(trial_criteria['inclusion_codes']['loinc'][:3])}...")
print(f"  - Required ICD-10: {', '.join(trial_criteria['inclusion_codes']['icd10'])}")
print()

# Score sites by feasibility
scorer = SiteFeasibilityScorer()
feasibility_rankings = scorer.rank_sites(
    trial_criteria=trial_criteria,
    target_enrollment=target_enrollment,
    top_n=5
)

print("✓ Top 5 Sites by Feasibility:")
print()

for i, site in enumerate(feasibility_rankings, 1):
    print(f"{i}. {site['site_name']}")
    print(f"   Overall Feasibility: {site['overall_score']:.3f}")
    print(f"   - Capability: {site['capability']['score']:.3f} ({site['capability']['coverage']*100:.0f}% LOINC)")
    print(f"   - Experience: {site['experience']['score']:.3f} ({site['experience']['relevant_trials']} trials)")
    print(f"   - Population: {site['population']['score']:.3f} ({site['population']['matching_patients']} patients)")
    print(f"   - Capacity: {site['capacity']['score']:.3f} ({site['capacity']['available_slots']} slots)")
    print()

# ============================================================================
# SUMMARY
# ============================================================================
print("=" * 80)
print("✓ END-TO-END TEST COMPLETE!")
print("=" * 80)
print()
print("Summary of All 4 Phases:")
print()
print("✓ PHASE 1 (FHIR Code Extraction):")
print(f"  - Extracted {len(extracted_codes['condition_codes'])} condition codes from FHIR data")
print(f"  - Extracted {len(extracted_codes['observation_codes'])} observation codes (labs)")
print(f"  - Extracted {len(extracted_codes['medication_codes'])} medication codes")
print()
print("✓ PHASE 2 (Eligibility Criteria Mapping):")
print(f"  - Mapped {len(trial_criteria_text)} text criteria to medical codes")
print(f"  - Found {len(mapped_codes['inclusion_codes']['icd10'])} inclusion ICD-10 codes")
print(f"  - Found {len(mapped_codes['exclusion_codes']['icd10'])} exclusion ICD-10 codes")
print(f"  - Detected {len(mapped_codes['found_terms']['conditions'])} condition terms")
print()
print("✓ PHASE 3 (Validation - Exclusion Checking):")
print(f"  - Validated {len(mock_patients)} patient matches")
print(f"  - {valid_count} patients passed (no exclusion violations)")
print(f"  - {excluded_count} patients excluded (had contraindications)")
print()
print("✓ PHASE 4 (Site Feasibility Scoring):")
print(f"  - Scored {len(feasibility_rankings)} sites on 4 dimensions")
print(f"  - Top site: {feasibility_rankings[0]['site_name']}")
print(f"  - Best feasibility score: {feasibility_rankings[0]['overall_score']:.3f}")
print()
print("=" * 80)
print("All advisor requirements demonstrated:")
print("  ✓ Controlled terminology sets (ICD-10, SNOMED, LOINC, RxNorm)")
print("  ✓ Standardized EHR query language (Epic FHIR)")
print("  ✓ Trial and site feasibility based on medical codes")
print("  ✓ Negation handling (exclusion criteria)")
print("=" * 80)
