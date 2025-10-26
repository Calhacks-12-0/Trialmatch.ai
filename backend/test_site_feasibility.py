#!/usr/bin/env python3
"""
Test Site Feasibility Scoring with Site Agent logic.

Demonstrates how the site agent now selects sites based on:
1. CAPABILITY (LOINC lab codes)
2. EXPERIENCE (ICD-10 chapter history)
3. POPULATION (EHR patient counts)
4. CAPACITY (trial load)
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from site_feasibility_scorer import SiteFeasibilityScorer
from agents.site_agent import assign_patients_to_sites
import numpy as np

print("=" * 70)
print("Testing Site Feasibility - Diabetes Trial Example")
print("=" * 70)
print()

# Initialize feasibility scorer
scorer = SiteFeasibilityScorer()

# Example diabetes trial with medical codes
diabetes_trial_criteria = {
    "inclusion_codes": {
        "icd10": ["E11.9", "E11.65"],  # Type 2 diabetes
        "snomed": ["44054006"],
        "loinc": ["4548-4", "17856-6", "2339-0"],  # HbA1c, Glucose
        "rxnorm": []
    },
    "exclusion_codes": {
        "icd10": ["E11.21", "E11.31"],  # Nephropathy, retinopathy
        "snomed": ["127013003", "4855003"],
        "loinc": [],
        "rxnorm": []
    }
}

target_enrollment = 150

print("Trial Requirements:")
print(f"  Target Enrollment: {target_enrollment}")
print(f"  Required LOINC codes: {diabetes_trial_criteria['inclusion_codes']['loinc']}")
print(f"  Required ICD-10: {diabetes_trial_criteria['inclusion_codes']['icd10']}")
print()

# Rank sites by feasibility
print("Step 1: Ranking Sites by Feasibility")
print("-" * 70)

feasibility_rankings = scorer.rank_sites(
    trial_criteria=diabetes_trial_criteria,
    target_enrollment=target_enrollment,
    top_n=10
)

for i, site in enumerate(feasibility_rankings[:5], 1):
    print(f"{i}. {site['site_name']}")
    print(f"   Overall Feasibility: {site['overall_score']:.3f}")
    print(f"   - Capability (LOINC): {site['capability']['score']:.3f} "
          f"({site['capability']['coverage']*100:.0f}% coverage)")
    print(f"   - Experience (ICD-10): {site['experience']['score']:.3f} "
          f"({site['experience']['relevant_trials']} diabetes trials)")
    print(f"   - Population: {site['population']['score']:.3f} "
          f"({site['population']['matching_patients']} diabetic patients)")
    print(f"   - Capacity: {site['capacity']['score']:.3f} "
          f"({site['capacity']['available_slots']} slots available)")
    print()

# Generate mock patient matches with geographic locations
print("Step 2: Assigning Patients to Sites")
print("-" * 70)

# Create 200 mock patients distributed across US
np.random.seed(42)

mock_patients = []
us_cities = [
    {"city": "New York", "lat": 40.7128, "lon": -74.0060},
    {"city": "Los Angeles", "lat": 34.0522, "lon": -118.2437},
    {"city": "Chicago", "lat": 41.8781, "lon": -87.6298},
    {"city": "Boston", "lat": 42.3601, "lon": -71.0589},
    {"city": "San Francisco", "lat": 37.7749, "lon": -122.4194},
    {"city": "Baltimore", "lat": 39.2904, "lon": -76.6122},
    {"city": "Rochester", "lat": 44.0225, "lon": -92.4699},
    {"city": "Cleveland", "lat": 41.5034, "lon": -81.6217}
]

for i in range(200):
    # Randomly select a city and add some noise
    base_city = us_cities[np.random.randint(0, len(us_cities))]
    lat = base_city["lat"] + np.random.uniform(-2, 2)
    lon = base_city["lon"] + np.random.uniform(-2, 2)

    mock_patients.append({
        "patient_id": f"P{i+1:04d}",
        "location": {"lat": lat, "lon": lon},
        "overall_score": np.random.uniform(0.7, 1.0)
    })

print(f"Generated {len(mock_patients)} mock patient matches")
print()

# Assign patients to sites
recommendations = assign_patients_to_sites(
    feasibility_rankings=feasibility_rankings,
    matches=mock_patients,
    max_sites=5
)

print("Final Site Recommendations (Feasibility + Geography):")
print("-" * 70)

for i, site in enumerate(recommendations, 1):
    print(f"{i}. {site['site_name']}")
    print(f"   Priority Score: {site['priority_score']:.3f} "
          f"(60% feasibility + 40% patient count)")
    print(f"   - Feasibility: {site['feasibility_score']:.3f}")
    print(f"   - Assigned Patients: {site['patient_count']}")
    print(f"   - Average Distance: {site['average_distance']:.1f} km")
    print(f"   - Capability: {site['capability_score']:.3f} | "
          f"Experience: {site['experience_score']:.3f} | "
          f"Population: {site['population_score']:.3f} | "
          f"Capacity: {site['capacity_score']:.3f}")
    print()

# Calculate coverage
total_patients = len(mock_patients)
assigned_patients = sum(site['patient_count'] for site in recommendations)
coverage = (assigned_patients / total_patients) * 100

print("=" * 70)
print(f"✓ Site Feasibility Test Complete!")
print(f"  - {len(recommendations)} sites recommended")
print(f"  - {assigned_patients}/{total_patients} patients assigned ({coverage:.1f}% coverage)")
print(f"  - Top site: {recommendations[0]['site_name']} (priority: {recommendations[0]['priority_score']:.3f})")
print("=" * 70)
print()

print("Key Improvements Over Geography-Only Approach:")
print("  1. LOINC capability matching ensures sites can perform required labs")
print("  2. ICD-10 experience scoring prioritizes sites with domain expertise")
print("  3. EHR population data validates patient availability")
print("  4. Capacity scoring prevents site overload")
print("  5. Combined with geographic optimization for patient convenience")
print()
