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
            score = self._calculate_match_score(trial_info, patient)

            if score > 0:  # Only include patients with some match
                matched_patients.append({
                    'patient_id': patient['patient_id'],
                    'age': patient['age'],
                    'gender': patient['gender'],
                    'condition': patient['primary_condition'],
                    'score': score
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

    def _calculate_match_score(self, trial: Dict, patient: Dict) -> int:
        """
        Calculate match score based on simple eligibility rules
        Score ranges from 0-100
        """
        score = 0

        # Age eligibility (30 points)
        if trial['min_age'] <= patient['age'] <= trial['max_age']:
            score += 30
            # Bonus for being in ideal age range (middle of trial range)
            ideal_age = (trial['min_age'] + trial['max_age']) / 2
            age_diff = abs(patient['age'] - ideal_age)
            age_range = trial['max_age'] - trial['min_age']
            if age_range > 0:
                age_bonus = int(10 * (1 - age_diff / age_range))
                score += max(0, age_bonus)

        # Gender eligibility (20 points)
        if trial['gender'] == 'All':
            score += 20
        elif trial['gender'] == 'Male' and patient['gender'] == 'M':
            score += 20
        elif trial['gender'] == 'Female' and patient['gender'] == 'F':
            score += 20

        # Condition matching (30 points)
        trial_condition = trial['condition'].lower()
        patient_condition = patient['primary_condition'].lower()

        # Check for exact or partial condition match
        if patient_condition in trial_condition or trial_condition in patient_condition:
            score += 30
        elif any(keyword in trial_condition for keyword in ['diabetes', 'cancer', 'cardiovascular', 'hypertension', 'alzheimer']):
            # Partial match for common conditions
            if any(keyword in patient_condition for keyword in ['diabetes', 'cancer', 'cardiovascular', 'hypertension', 'alzheimer']):
                score += 15

        # Enrollment history bonus (10 points)
        # Patients with previous successful enrollments get bonus points
        if patient.get('enrollment_history', 0) > 0:
            score += min(10, patient['enrollment_history'] * 3)

        # Add some randomness for demonstration (±5 points)
        np.random.seed(hash(patient['patient_id']) % 2**32)
        random_bonus = np.random.randint(-5, 6)
        score += random_bonus

        # Ensure score is between 0 and 100
        score = max(0, min(100, score))

        return score
