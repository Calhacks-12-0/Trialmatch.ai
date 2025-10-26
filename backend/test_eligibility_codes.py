#!/usr/bin/env python3
"""
Test eligibility agent with code extraction
"""

import json
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.eligibility_agent import extract_criteria

# Load sample trial
with open('trials_sample.json', 'r') as f:
    trials = json.load(f)

print("="*70)
print("Testing Eligibility Agent with Code Extraction")
print("="*70)

for i, trial in enumerate(trials[:3], 1):  # Test first 3 trials
    print(f"\n{'='*70}")
    print(f"Trial {i}: {trial['nct_id']}")
    print(f"{'='*70}")
    print(f"Condition: {trial['condition']}")
    print(f"Title: {trial['title'][:80]}...")

    # Extract criteria with codes
    criteria = extract_criteria(trial)

    print(f"\n--- Demographics ---")
    print(f"Age: {criteria.age_range['min']}-{criteria.age_range['max']} years")
    print(f"Gender: {criteria.gender or 'All'}")

    print(f"\n--- Inclusion Codes ---")
    if criteria.inclusion_codes.get('icd10'):
        print(f"ICD-10: {', '.join(criteria.inclusion_codes['icd10'])}")
    if criteria.inclusion_codes.get('snomed'):
        print(f"SNOMED: {', '.join(criteria.inclusion_codes['snomed'])}")
    if criteria.inclusion_codes.get('loinc'):
        print(f"LOINC: {', '.join(criteria.inclusion_codes['loinc'][:5])}...")  # Show first 5
    if criteria.inclusion_codes.get('rxnorm'):
        print(f"RxNorm: {', '.join(criteria.inclusion_codes['rxnorm'])}")

    print(f"\n--- Exclusion Codes ---")
    if criteria.exclusion_codes.get('icd10'):
        print(f"ICD-10: {', '.join(criteria.exclusion_codes['icd10'])}")
    if criteria.exclusion_codes.get('snomed'):
        print(f"SNOMED: {', '.join(criteria.exclusion_codes['snomed'])}")

    print(f"\n--- Found Terms ---")
    if criteria.found_terms.get('conditions'):
        print(f"Conditions ({len(criteria.found_terms['conditions'])}):")
        for cond in criteria.found_terms['conditions']:
            excl = " [EXCLUSION]" if cond.get('is_exclusion') else ""
            print(f"  - {cond['term']}: {cond.get('display', 'N/A')}{excl}")

    if criteria.found_terms.get('labs'):
        print(f"Labs ({len(criteria.found_terms['labs'])}):")
        for lab in criteria.found_terms['labs'][:3]:  # Show first 3
            print(f"  - {lab['term']}: {lab.get('display', 'N/A')}")

    if criteria.found_terms.get('medications'):
        print(f"Medications ({len(criteria.found_terms['medications'])}):")
        for med in criteria.found_terms['medications']:
            print(f"  - {med['term']}: {med.get('display', 'N/A')}")

print("\n" + "="*70)
print("✓ Eligibility code extraction working!")
print("="*70)
