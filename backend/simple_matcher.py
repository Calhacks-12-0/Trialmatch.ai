"""
Simple Patient-Trial Matching Algorithm (Sanity Check)
This is a prototype matching system before the full Conway/Fetch.ai pipeline is implemented.
"""

import numpy as np
from typing import Dict, List
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SimplePatientMatcher:
    """Simple rule-based matching for prototype/demo purposes"""

    def __init__(self):
        pass

    def match_patients_to_trial(self, trial_info: Dict, patients_data: List[Dict], top_n: int = 10) -> Dict:
        """
        Simple matching algorithm based on basic eligibility criteria

        Args:
            trial_info: Trial details from ClinicalTrials.gov
            patients_data: List of patient records
            top_n: Number of top matches to return

        Returns:
            Dict with trial info, matched patients, and scores
        """
        logger.info(f"Matching {len(patients_data)} patients to trial {trial_info['nct_id']}")

        matched_patients = []

        for patient in patients_data:
            score_breakdown = self._calculate_match_score(trial_info, patient)

            if score_breakdown['overall_score'] > 0:  # Only include patients with some match
                # Format location
                city = patient.get('city', 'Unknown')
                state = patient.get('state', 'Unknown')
                location = f"{city}, {state}"

                matched_patients.append({
                    'patient_id': patient['patient_id'],
                    'age': patient['age'],
                    'gender': patient['gender'],
                    'condition': patient['primary_condition'],
                    'location': location,
                    'score': score_breakdown['overall_score'],
                    'subscores': score_breakdown['subscores']
                })

        # Sort by score descending and take top N
        matched_patients.sort(key=lambda x: x['score'], reverse=True)
        top_matches = matched_patients[:top_n]

        logger.info(f"Found {len(matched_patients)} eligible patients, returning top {len(top_matches)}")

        return {
            'trial_info': {
                'nct_id': trial_info['nct_id'],
                'title': trial_info['title'],
                'condition': trial_info['condition'],
                'phase': trial_info['phase'],
                'status': trial_info['status']
            },
            'date_added': datetime.now().isoformat(),
            'total_matches': len(matched_patients),
            'matches': top_matches
        }

    def _calculate_match_score(self, trial: Dict, patient: Dict) -> Dict:
        """
        Calculate match score with detailed subscores
        Returns dict with overall_score and subscores breakdown
        """
        # Seed random for consistent results per patient
        np.random.seed(hash(patient['patient_id']) % 2**32)

        # 1. Medical Eligibility Fit (25 points)
        medical_score = 0
        medical_details = []

        # Age eligibility
        if trial['min_age'] <= patient['age'] <= trial['max_age']:
            age_points = 10
            medical_score += age_points
            medical_details.append(f"Age {patient['age']} within range ({trial['min_age']}-{trial['max_age']})")
        else:
            medical_details.append(f"Age {patient['age']} outside range ({trial['min_age']}-{trial['max_age']})")

        # Condition matching
        trial_condition = trial['condition'].lower()
        patient_condition = patient['primary_condition'].lower()
        if patient_condition in trial_condition or trial_condition in patient_condition:
            medical_score += 10
            medical_details.append(f"Condition match: {patient['primary_condition']}")
        else:
            medical_details.append(f"Partial condition match")
            medical_score += 5

        # Gender eligibility
        if trial['gender'] == 'All' or (trial['gender'] == 'Male' and patient['gender'] == 'M') or (trial['gender'] == 'Female' and patient['gender'] == 'F'):
            medical_score += 5
            medical_details.append("Gender eligible")

        # 2. Feasibility / Logistics (25 points)
        # Simulate distance, visit frequency, etc.
        distance_score = np.random.randint(15, 26)
        logistics_details = [
            f"Est. distance: {np.random.randint(5, 50)} miles",
            f"Visit frequency: {np.random.choice(['Weekly', 'Bi-weekly', 'Monthly'])}",
            f"Travel readiness: {np.random.choice(['High', 'Medium', 'Low'])}"
        ]

        # 3. Predicted Clinical Value (25 points)
        # Simulate biomarker signal, similar responders
        clinical_value = np.random.randint(15, 26)
        clinical_details = [
            f"Biomarker signal: {np.random.choice(['Strong', 'Moderate', 'Weak'])}",
            f"Similar responders: {np.random.randint(45, 95)}%",
            f"Outcome cluster match: {np.random.choice(['High', 'Medium', 'Low'])}"
        ]

        # 4. Enrollment Success Likelihood (25 points)
        # Based on enrollment history and trial acceptance patterns
        enrollment_base = 10 if patient.get('enrollment_history', 0) > 0 else 5
        enrollment_bonus = np.random.randint(10, 16)
        enrollment_score = enrollment_base + enrollment_bonus
        enrollment_details = [
            f"Prior enrollments: {patient.get('enrollment_history', 0)}",
            f"Trial phase: {trial['phase']}",
            f"Dropout risk: {np.random.choice(['Low', 'Medium', 'High'])}",
            f"Acceptance likelihood: {np.random.randint(60, 95)}%"
        ]

        # Calculate overall score
        overall_score = medical_score + distance_score + clinical_value + enrollment_score
        overall_score = max(0, min(100, overall_score))

        return {
            'overall_score': overall_score,
            'subscores': {
                'medical_eligibility': {
                    'score': medical_score,
                    'max_score': 25,
                    'label': 'Medical Eligibility Fit',
                    'description': 'Hard inclusion/exclusion match',
                    'details': medical_details
                },
                'feasibility': {
                    'score': distance_score,
                    'max_score': 25,
                    'label': 'Feasibility / Logistics',
                    'description': 'Can this patient realistically participate?',
                    'details': logistics_details
                },
                'clinical_value': {
                    'score': clinical_value,
                    'max_score': 25,
                    'label': 'Predicted Clinical Value',
                    'description': 'Will this trial likely help this patient?',
                    'details': clinical_details
                },
                'enrollment_likelihood': {
                    'score': enrollment_score,
                    'max_score': 25,
                    'label': 'Enrollment Success Likelihood',
                    'description': 'Will the trial likely accept them?',
                    'details': enrollment_details
                }
            }
        }
