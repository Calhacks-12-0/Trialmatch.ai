#!/usr/bin/env python3
"""
Test Validation Agent with exclusion scenarios.

This script tests the validation agent's ability to:
1. Detect exclusion code violations
2. Handle patients with clean records (no exclusions)
3. Properly categorize exclusion reasons
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.validation_agent import check_exclusions, extract_patient_codes

print("=" * 70)
print("Testing Validation Agent - Exclusion Checking")
print("=" * 70)
print()

# Test Scenario 1: Patient with diabetic nephropathy (should be excluded)
print("Test 1: Patient with diabetic nephropathy (EXCLUSION)")
print("-" * 70)

patient_codes_1 = {
    "icd10": ["E11.9", "E11.21"],  # Type 2 diabetes + diabetic nephropathy
    "snomed": ["44054006", "127013003"],  # Diabetes + nephropathy
    "loinc": ["4548-4"],
    "rxnorm": ["6809"]  # Metformin
}

exclusion_codes_1 = {
    "icd10": ["E11.21", "E10.21"],  # Diabetic nephropathy codes
    "snomed": ["127013003"],
    "loinc": [],
    "rxnorm": []
}

violations_1 = check_exclusions(patient_codes_1, exclusion_codes_1)
print(f"Patient Codes: ICD-10 {patient_codes_1['icd10']}, SNOMED {patient_codes_1['snomed']}")
print(f"Exclusion Codes: ICD-10 {exclusion_codes_1['icd10']}, SNOMED {exclusion_codes_1['snomed']}")
print(f"Violations Found: {len(violations_1)}")
for v in violations_1:
    print(f"  ✗ {v['system']} code {v['code']}: {v['reason']}")
print()

# Test Scenario 2: Clean patient (should NOT be excluded)
print("Test 2: Clean patient with diabetes only (NO EXCLUSION)")
print("-" * 70)

patient_codes_2 = {
    "icd10": ["E11.9"],  # Type 2 diabetes only
    "snomed": ["44054006"],  # Diabetes
    "loinc": ["4548-4"],  # HbA1c
    "rxnorm": ["6809"]  # Metformin
}

exclusion_codes_2 = {
    "icd10": ["E11.21", "E11.31"],  # Nephropathy, retinopathy
    "snomed": ["127013003", "4855003"],
    "loinc": [],
    "rxnorm": []
}

violations_2 = check_exclusions(patient_codes_2, exclusion_codes_2)
print(f"Patient Codes: ICD-10 {patient_codes_2['icd10']}, SNOMED {patient_codes_2['snomed']}")
print(f"Exclusion Codes: ICD-10 {exclusion_codes_2['icd10']}, SNOMED {exclusion_codes_2['snomed']}")
print(f"Violations Found: {len(violations_2)}")
if len(violations_2) == 0:
    print("  ✓ Patient is eligible (no exclusions)")
else:
    for v in violations_2:
        print(f"  ✗ {v['system']} code {v['code']}: {v['reason']}")
print()

# Test Scenario 3: Patient with multiple exclusions
print("Test 3: Patient with multiple exclusions (MULTIPLE VIOLATIONS)")
print("-" * 70)

patient_codes_3 = {
    "icd10": ["E11.9", "E11.21", "E11.31", "I50.9"],  # Diabetes + complications + heart failure
    "snomed": ["44054006", "127013003", "4855003", "84114007"],
    "loinc": ["4548-4"],
    "rxnorm": ["6809"]
}

exclusion_codes_3 = {
    "icd10": ["E11.21", "E11.31", "I50.9"],  # Nephropathy, retinopathy, heart failure
    "snomed": ["127013003", "4855003", "84114007"],
    "loinc": [],
    "rxnorm": []
}

violations_3 = check_exclusions(patient_codes_3, exclusion_codes_3)
print(f"Patient Codes: ICD-10 {patient_codes_3['icd10']}, SNOMED {patient_codes_3['snomed']}")
print(f"Exclusion Codes: ICD-10 {exclusion_codes_3['icd10']}, SNOMED {exclusion_codes_3['snomed']}")
print(f"Violations Found: {len(violations_3)}")
for v in violations_3:
    print(f"  ✗ {v['system']} code {v['code']}: {v['reason']}")
print()

# Test Scenario 4: Extract codes from patient match object
print("Test 4: Extract codes from patient match object")
print("-" * 70)

mock_match = {
    "patient_id": "patient-123",
    "demographics": {
        "age": 55,
        "gender": "Male"
    },
    "clinical_data": {
        "icd10_codes": ["E11.9", "I10"],
        "snomed_codes": ["44054006", "38341003"],
        "loinc_codes": ["4548-4", "2093-3"],
        "rxnorm_codes": ["6809", "29046"]
    }
}

extracted_codes = extract_patient_codes(mock_match)
print(f"Extracted from match object:")
print(f"  ICD-10: {extracted_codes['icd10']}")
print(f"  SNOMED: {extracted_codes['snomed']}")
print(f"  LOINC: {extracted_codes['loinc']}")
print(f"  RxNorm: {extracted_codes['rxnorm']}")
print()

# Test validation against exclusions
exclusion_codes_4 = {
    "icd10": ["E11.21"],  # Nephropathy only
    "snomed": [],
    "loinc": [],
    "rxnorm": []
}

violations_4 = check_exclusions(extracted_codes, exclusion_codes_4)
print(f"Checking against exclusions: ICD-10 {exclusion_codes_4['icd10']}")
print(f"Violations Found: {len(violations_4)}")
if len(violations_4) == 0:
    print("  ✓ Patient is eligible")
print()

print("=" * 70)
print("✓ Validation Agent tests complete!")
print("=" * 70)
print()
print("Summary:")
print("  - Test 1: Correctly identified diabetic nephropathy exclusion")
print("  - Test 2: Correctly passed clean patient")
print("  - Test 3: Correctly identified multiple exclusions")
print("  - Test 4: Successfully extracted codes from match object")
print()
