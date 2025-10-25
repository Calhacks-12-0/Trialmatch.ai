import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import json
import requests
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ClinicalDataLoader:
    """Load and prepare clinical trial and patient data"""
    
    def __init__(self):
        self.patients_df = None
        self.trials_df = None
        self.base_url = "https://clinicaltrials.gov/api/v2/"
        
    def generate_synthetic_patients(self, n_patients: int = 5000) -> pd.DataFrame:
        """Generate synthetic patient data for demo"""
        logger.info(f"Generating {n_patients} synthetic patients...")
        
        np.random.seed(42)
        
        conditions = ['diabetes', 'hypertension', 'cancer', 'alzheimers', 'cardiovascular']
        medications = ['metformin', 'insulin', 'statins', 'aspirin', 'beta-blockers']
        
        patients = {
            'patient_id': [f'P{str(i).zfill(6)}' for i in range(n_patients)],
            'age': np.random.normal(55, 15, n_patients).clip(18, 90).astype(int),
            'gender': np.random.choice(['M', 'F'], n_patients),
            'primary_condition': np.random.choice(conditions, n_patients),
            'medications': [np.random.choice(medications, np.random.randint(0, 4)).tolist() 
                          for _ in range(n_patients)],
            'lab_values': [{
                'hba1c': np.random.uniform(5.0, 10.0),
                'blood_pressure': f"{np.random.randint(110, 180)}/{np.random.randint(70, 100)}",
                'cholesterol': np.random.uniform(150, 300)
            } for _ in range(n_patients)],
            'latitude': np.random.uniform(25, 48, n_patients),  # US latitude range
            'longitude': np.random.uniform(-125, -65, n_patients),  # US longitude range
            'enrollment_history': np.random.choice([0, 1, 2, 3], n_patients, p=[0.5, 0.3, 0.15, 0.05])
        }
        
        self.patients_df = pd.DataFrame(patients)
        logger.info(f"Generated {len(self.patients_df)} patients")
        return self.patients_df
    
    def fetch_clinical_trials(self, condition: str = "diabetes", max_trials: int = 100) -> pd.DataFrame:
        """Fetch real clinical trials from ClinicalTrials.gov API"""
        logger.info(f"Fetching {max_trials} trials for condition: {condition}")
        
        # For hackathon demo, generate synthetic trials instead of API call
        # (API might be slow/down during hackathon)
        trials = []
        for i in range(max_trials):
            trial = {
                'nct_id': f'NCT{str(100000 + i).zfill(8)}',
                'title': f'Study of {condition} Treatment {i}',
                'condition': condition,
                'phase': np.random.choice(['Phase 1', 'Phase 2', 'Phase 3', 'Phase 4']),
                'enrollment_target': np.random.randint(50, 500),
                'min_age': np.random.randint(18, 45),
                'max_age': np.random.randint(60, 90),
                'gender': np.random.choice(['All', 'Male', 'Female']),
                'inclusion_criteria': self._generate_criteria(),
                'sites': np.random.randint(1, 20),
                'status': 'Recruiting'
            }
            trials.append(trial)
        
        self.trials_df = pd.DataFrame(trials)
        logger.info(f"Loaded {len(self.trials_df)} trials")
        return self.trials_df
    
    def _generate_criteria(self) -> List[str]:
        """Generate sample inclusion/exclusion criteria"""
        criteria = [
            "Age between specified range",
            "Confirmed diagnosis of condition",
            "No recent surgery",
            "Willing to comply with study protocol",
            "Not pregnant or nursing"
        ]
        return np.random.choice(criteria, np.random.randint(3, 6), replace=False).tolist()
    
    def prepare_for_conway(self) -> Dict:
        """Prepare data in format for Conway pattern discovery"""
        if self.patients_df is None:
            self.generate_synthetic_patients()
        if self.trials_df is None:
            self.fetch_clinical_trials()
            
        return {
            'patients': self.patients_df.to_dict('records'),
            'trials': self.trials_df.to_dict('records'),
            'metadata': {
                'patient_count': len(self.patients_df),
                'trial_count': len(self.trials_df),
                'timestamp': datetime.now().isoformat()
            }
        }