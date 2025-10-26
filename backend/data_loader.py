import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import json
import requests
from datetime import datetime
import logging
import os
import glob
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ClinicalDataLoader:
    """Load and prepare clinical trial and patient data"""
    
    def __init__(self):
        self.patients_df = None
        self.trials_df = None
        self.base_url = "https://clinicaltrials.gov/api/v2/"
        self.synthea_data_path = os.path.join(os.path.dirname(__file__), 'data', 'fhir')

    def load_synthea_patients(self, max_patients: int = 1000) -> pd.DataFrame:
        """Load real Synthea FHIR patient data"""
        logger.info(f"Loading Synthea FHIR patient data from {self.synthea_data_path}...")

        if not os.path.exists(self.synthea_data_path):
            logger.warning(f"Synthea data not found at {self.synthea_data_path}, falling back to synthetic generation")
            return self.generate_synthetic_patients(max_patients)

        # Get all JSON files in the Synthea directory
        patient_files = glob.glob(os.path.join(self.synthea_data_path, '*.json'))

        # if not patient_files:
        #     logger.warning("No Synthea patient files found, falling back to synthetic generation")
        #     return self.generate_synthetic_patients(max_patients)

        logger.info(f"Found {len(patient_files)} Synthea patient files")

        # Limit the number of files to process
        patient_files = patient_files[:max_patients]

        patients = []

        for idx, file_path in enumerate(patient_files):
            try:
                with open(file_path, 'r') as f:
                    bundle = json.load(f)

                # Extract patient resource and other resources from bundle
                patient_resource = None
                conditions = []
                medications = []
                observations = []

                for entry in bundle.get('entry', []):
                    resource = entry.get('resource', {})
                    resource_type = resource.get('resourceType')

                    if resource_type == 'Patient':
                        patient_resource = resource
                    elif resource_type == 'Condition':
                        conditions.append(resource)
                    elif resource_type == 'MedicationRequest':
                        medications.append(resource)
                    elif resource_type == 'Observation':
                        observations.append(resource)

                if not patient_resource:
                    continue

                # Parse patient data
                patient_data = self._parse_synthea_patient(
                    patient_resource, conditions, medications, observations
                )

                if patient_data:
                    patients.append(patient_data)

                if (idx + 1) % 100 == 0:
                    logger.info(f"Processed {idx + 1}/{len(patient_files)} patients...")

            except Exception as e:
                logger.warning(f"Error processing {file_path}: {e}")
                continue

        logger.info(f"Successfully loaded {len(patients)} Synthea patients")

        self.patients_df = pd.DataFrame(patients)
        return self.patients_df

    def _parse_synthea_patient(self, patient: Dict, conditions: List[Dict],
                               medications: List[Dict], observations: List[Dict]) -> Dict:
        """Parse a Synthea FHIR patient resource into our format"""
        try:
            # Extract basic demographics
            patient_id = patient.get('id', 'unknown')

            # Name
            name = patient.get('name', [{}])[0]
            given_name = ' '.join(name.get('given', ['Unknown']))
            family_name = name.get('family', 'Unknown')

            # Gender
            gender = patient.get('gender', 'unknown')[0].upper() if patient.get('gender') else 'U'

            # Birth date and calculate age
            birth_date = patient.get('birthDate', '1970-01-01')
            birth_year = int(birth_date.split('-')[0])
            current_year = datetime.now().year
            age = current_year - birth_year

            # Address and geolocation
            address = patient.get('address', [{}])[0] if patient.get('address') else {}
            city = address.get('city', 'Unknown')
            state = address.get('state', 'Unknown')

            # Extract lat/long from extension
            latitude = 40.0  # Default
            longitude = -95.0  # Default

            for ext in address.get('extension', []):
                if 'geolocation' in ext.get('url', ''):
                    for geo_ext in ext.get('extension', []):
                        if 'latitude' in geo_ext.get('url', ''):
                            latitude = geo_ext.get('valueDecimal', latitude)
                        elif 'longitude' in geo_ext.get('url', ''):
                            longitude = geo_ext.get('valueDecimal', longitude)

            # Primary condition (most recent active condition)
            primary_condition = 'healthy'
            if conditions:
                # Sort by onset date if available, otherwise use first condition
                active_conditions = [c for c in conditions
                                   if c.get('clinicalStatus', {}).get('coding', [{}])[0].get('code') == 'active']
                if active_conditions:
                    condition = active_conditions[0]
                elif conditions:
                    condition = conditions[0]
                else:
                    condition = None

                if condition and 'code' in condition:
                    coding = condition['code'].get('coding', [{}])[0]
                    primary_condition = coding.get('display', 'unknown')

            # Extract medications
            med_list = []
            for med in medications[:5]:  # Limit to 5 medications
                if 'medicationCodeableConcept' in med:
                    coding = med['medicationCodeableConcept'].get('coding', [{}])[0]
                    med_name = coding.get('display', 'unknown')
                    med_list.append(med_name.lower())

            # Extract lab values from observations
            lab_values = {
                'hba1c': np.random.uniform(5.0, 10.0),  # Default random
                'cholesterol': np.random.uniform(150, 300),
                'blood_pressure': f"{np.random.randint(110, 180)}/{np.random.randint(70, 100)}"
            }

            # Try to find actual lab values
            for obs in observations:
                code = obs.get('code', {})
                coding = code.get('coding', [{}])[0]
                code_display = coding.get('display', '').lower()

                if 'hemoglobin a1c' in code_display or 'hba1c' in code_display:
                    value = obs.get('valueQuantity', {}).get('value')
                    if value:
                        lab_values['hba1c'] = float(value)
                elif 'cholesterol' in code_display:
                    value = obs.get('valueQuantity', {}).get('value')
                    if value:
                        lab_values['cholesterol'] = float(value)

            # Enrollment history (simulated based on conditions)
            enrollment_history = min(len(conditions) // 2, 3)

            return {
                'patient_id': f'SYN{patient_id[:8]}',
                'age': age,
                'gender': gender,
                'primary_condition': primary_condition.lower(),
                'medications': med_list,
                'lab_values': lab_values,
                'latitude': latitude,
                'longitude': longitude,
                'city': city,
                'state': state,
                'enrollment_history': enrollment_history
            }

        except Exception as e:
            logger.warning(f"Error parsing patient: {e}")
            return None

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
    
    def prepare_for_conway(self, use_synthea: bool = True, max_patients: int = 1000) -> Dict:
        """Prepare data in format for Conway pattern discovery"""
        if self.patients_df is None:
            if use_synthea:
                logger.info("Using Synthea FHIR patient data")
                self.load_synthea_patients(max_patients=max_patients)
            else:
                logger.info("Using synthetic patient data")
                self.generate_synthetic_patients(n_patients=max_patients)

        if self.trials_df is None:
            self.fetch_clinical_trials()

        return {
            'patients': self.patients_df.to_dict('records'),
            'trials': self.trials_df.to_dict('records'),
            'metadata': {
                'patient_count': len(self.patients_df),
                'trial_count': len(self.trials_df),
                'timestamp': datetime.now().isoformat(),
                'data_source': 'synthea' if use_synthea else 'synthetic'
            }
        }