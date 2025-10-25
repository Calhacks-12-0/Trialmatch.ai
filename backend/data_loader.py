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
        """Fetch real clinical trials from ClinicalTrials.gov API v2"""
        logger.info(f"Fetching trials for condition: {condition} from ClinicalTrials.gov API")

        trials = []
        page_token = None
        fetched_count = 0

        try:
            # ClinicalTrials.gov API v2 endpoint
            endpoint = f"{self.base_url}studies"

            while fetched_count < max_trials:
                # Build query parameters
                params = {
                    'query.cond': condition,
                    'pageSize': min(100, max_trials - fetched_count),  # Max 100 per request
                    'filter.overallStatus': 'RECRUITING',  # Only recruiting trials
                    'format': 'json'
                }

                if page_token:
                    params['pageToken'] = page_token

                logger.info(f"Requesting {params['pageSize']} trials (total so far: {fetched_count})")

                # Make API request with timeout
                response = requests.get(endpoint, params=params, timeout=30)
                response.raise_for_status()

                data = response.json()
                studies = data.get('studies', [])

                if not studies:
                    logger.info("No more studies available")
                    break

                # Parse each study
                for study in studies:
                    try:
                        trial = self._parse_study(study)
                        trials.append(trial)
                        fetched_count += 1

                        if fetched_count >= max_trials:
                            break
                    except Exception as e:
                        logger.warning(f"Error parsing study: {e}")
                        continue

                # Check for next page
                page_token = data.get('nextPageToken')
                if not page_token:
                    break

            logger.info(f"Successfully fetched {len(trials)} trials from ClinicalTrials.gov")

        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            logger.warning("Falling back to synthetic data generation")
            return self._generate_synthetic_trials(condition, max_trials)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            logger.warning("Falling back to synthetic data generation")
            return self._generate_synthetic_trials(condition, max_trials)

        if not trials:
            logger.warning("No trials fetched, generating synthetic data")
            return self._generate_synthetic_trials(condition, max_trials)

        self.trials_df = pd.DataFrame(trials)

        # Save sample for sanity check
        self._save_sample_trials(trials[:10])

        logger.info(f"Loaded {len(self.trials_df)} trials")
        return self.trials_df

    def _parse_study(self, study: Dict) -> Dict:
        """Parse a study from ClinicalTrials.gov API response"""
        protocol = study.get('protocolSection', {})
        identification = protocol.get('identificationModule', {})
        description = protocol.get('descriptionModule', {})
        design = protocol.get('designModule', {})
        eligibility = protocol.get('eligibilityModule', {})
        status = protocol.get('statusModule', {})

        # Extract phase
        phases = design.get('phases', [])
        phase = phases[0] if phases else 'Not Specified'

        # Extract enrollment
        enrollment_info = design.get('enrollmentInfo', {})
        enrollment_target = enrollment_info.get('count', np.random.randint(50, 500))

        # Extract age eligibility
        min_age_str = eligibility.get('minimumAge', '18 Years')
        max_age_str = eligibility.get('maximumAge', '90 Years')

        # Parse age strings (e.g., "18 Years" -> 18)
        try:
            min_age = int(''.join(filter(str.isdigit, min_age_str))) if min_age_str else 18
        except:
            min_age = 18

        try:
            max_age = int(''.join(filter(str.isdigit, max_age_str))) if max_age_str else 90
        except:
            max_age = 90

        # Extract gender
        sex = eligibility.get('sex', 'ALL')
        gender_map = {'MALE': 'Male', 'FEMALE': 'Female', 'ALL': 'All'}
        gender = gender_map.get(sex, 'All')

        # Extract criteria
        criteria_text = eligibility.get('eligibilityCriteria', '')
        inclusion_criteria = self._extract_criteria_list(criteria_text)

        # Extract locations (sites count)
        locations = protocol.get('contactsLocationsModule', {}).get('locations', [])
        sites_count = len(locations) if locations else np.random.randint(1, 10)

        # Extract conditions
        conditions = protocol.get('conditionsModule', {}).get('conditions', [])
        primary_condition = conditions[0] if conditions else 'Not Specified'

        return {
            'nct_id': identification.get('nctId', 'NCT00000000'),
            'title': identification.get('briefTitle', 'No title available'),
            'condition': primary_condition,
            'phase': phase,
            'enrollment_target': enrollment_target,
            'min_age': min_age,
            'max_age': max_age,
            'gender': gender,
            'inclusion_criteria': inclusion_criteria,
            'sites': sites_count,
            'status': status.get('overallStatus', 'Unknown')
        }

    def _extract_criteria_list(self, criteria_text: str) -> List[str]:
        """Extract criteria from eligibility criteria text"""
        if not criteria_text:
            return self._generate_criteria()

        # Split by common delimiters and take first few meaningful lines
        lines = [line.strip() for line in criteria_text.split('\n') if line.strip()]
        criteria = [line for line in lines if len(line) > 10 and not line.startswith('Exclusion')][:5]

        return criteria if criteria else self._generate_criteria()

    def _generate_synthetic_trials(self, condition: str, max_trials: int) -> pd.DataFrame:
        """Generate synthetic trials as fallback"""
        logger.info(f"Generating {max_trials} synthetic trials for {condition}")
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
        return pd.DataFrame(trials)

    def _save_sample_trials(self, trials: List[Dict]):
        """Save a sample of trials for sanity checking"""
        try:
            sample_file = 'trials_sample.json'
            with open(sample_file, 'w') as f:
                json.dump(trials, f, indent=2)
            logger.info(f"Saved sample trials to {sample_file} for sanity check")
        except Exception as e:
            logger.warning(f"Could not save sample file: {e}")
    
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