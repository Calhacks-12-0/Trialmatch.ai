"""
FHIR Code Extractor - Extract standard medical codes from FHIR resources.

Extracts ICD-10, SNOMED, LOINC, and RxNorm codes from Synthea FHIR bundles.
This is the foundation for using controlled medical terminology instead of free text.
"""

import logging
from typing import Dict, List, Optional
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class FHIRCodeExtractor:
    """Extract and classify medical codes from FHIR resources"""

    # Mapping of FHIR code system URLs to standard names
    CODE_SYSTEM_MAP = {
        # ICD-10
        "http://hl7.org/fhir/sid/icd-10": "ICD-10",
        "http://hl7.org/fhir/sid/icd-10-cm": "ICD-10",

        # SNOMED CT
        "http://snomed.info/sct": "SNOMED",

        # LOINC
        "http://loinc.org": "LOINC",

        # RxNorm
        "http://www.nlm.nih.gov/research/umls/rxnorm": "RxNorm",

        # Other common systems
        "http://terminology.hl7.org/CodeSystem/v3-ActCode": "HL7-ActCode",
        "http://terminology.hl7.org/CodeSystem/condition-clinical": "HL7-ConditionClinical",
        "http://terminology.hl7.org/CodeSystem/v3-MaritalStatus": "HL7-MaritalStatus",
    }

    @classmethod
    def extract_codes_from_coding(cls, coding: Dict) -> Optional[Dict]:
        """
        Extract a single code from a FHIR coding element.

        Args:
            coding: FHIR coding object with system, code, display

        Returns:
            Dict with {system, code, display} or None if not a recognized system
        """
        if not isinstance(coding, dict):
            return None

        system_url = coding.get("system", "")
        code = coding.get("code")
        display = coding.get("display", "")

        if not code:
            return None

        # Map system URL to standard name
        system_name = cls.CODE_SYSTEM_MAP.get(system_url)

        if not system_name:
            # Try partial match for systems we might not have exact URL for
            for url_pattern, name in cls.CODE_SYSTEM_MAP.items():
                if url_pattern in system_url:
                    system_name = name
                    break

        if not system_name:
            # Unknown system - log but still return it
            logger.debug(f"Unknown code system: {system_url}")
            return None

        return {
            "system": system_name,
            "code": code,
            "display": display,
            "system_url": system_url
        }

    @classmethod
    def extract_codes_from_codeable_concept(cls, codeable_concept: Dict) -> List[Dict]:
        """
        Extract all codes from a FHIR CodeableConcept.

        CodeableConcept can have multiple codings (e.g., SNOMED + ICD-10 for same condition).

        Args:
            codeable_concept: FHIR CodeableConcept with "coding" array

        Returns:
            List of extracted codes
        """
        if not isinstance(codeable_concept, dict):
            return []

        codings = codeable_concept.get("coding", [])
        if not isinstance(codings, list):
            return []

        extracted_codes = []
        for coding in codings:
            code_info = cls.extract_codes_from_coding(coding)
            if code_info:
                extracted_codes.append(code_info)

        return extracted_codes

    @classmethod
    def extract_condition_codes(cls, condition_resource: Dict) -> List[Dict]:
        """
        Extract diagnosis/condition codes from a FHIR Condition resource.

        Returns ICD-10 and/or SNOMED codes for the condition.
        """
        if condition_resource.get("resourceType") != "Condition":
            return []

        code = condition_resource.get("code", {})
        return cls.extract_codes_from_codeable_concept(code)

    @classmethod
    def extract_observation_codes(cls, observation_resource: Dict) -> List[Dict]:
        """
        Extract lab/observation codes from a FHIR Observation resource.

        Returns LOINC codes for lab tests and measurements.
        """
        if observation_resource.get("resourceType") != "Observation":
            return []

        code = observation_resource.get("code", {})
        return cls.extract_codes_from_codeable_concept(code)

    @classmethod
    def extract_medication_codes(cls, medication_resource: Dict) -> List[Dict]:
        """
        Extract medication codes from FHIR MedicationRequest resource.

        Returns RxNorm codes for medications.
        """
        resource_type = medication_resource.get("resourceType")
        if resource_type not in ["MedicationRequest", "Medication"]:
            return []

        # Check medicationCodeableConcept
        med_concept = medication_resource.get("medicationCodeableConcept", {})
        if med_concept:
            return cls.extract_codes_from_codeable_concept(med_concept)

        # Some resources might have medication.code instead
        med_code = medication_resource.get("medication", {}).get("code", {})
        if med_code:
            return cls.extract_codes_from_codeable_concept(med_code)

        return []

    @classmethod
    def extract_all_codes_from_bundle(cls, fhir_bundle: Dict) -> Dict[str, List[Dict]]:
        """
        Extract all medical codes from a FHIR bundle.

        Args:
            fhir_bundle: Complete FHIR bundle (entire patient file)

        Returns:
            Dict with categorized codes:
            {
                "condition_codes": [...],  # ICD-10, SNOMED diagnoses
                "observation_codes": [...], # LOINC lab tests
                "medication_codes": [...],  # RxNorm medications
                "procedure_codes": [...]    # Procedure codes (future)
            }
        """
        if fhir_bundle.get("resourceType") != "Bundle":
            logger.warning("Not a FHIR bundle")
            return {"condition_codes": [], "observation_codes": [], "medication_codes": []}

        condition_codes = []
        observation_codes = []
        medication_codes = []

        entries = fhir_bundle.get("entry", [])

        for entry in entries:
            resource = entry.get("resource", {})
            resource_type = resource.get("resourceType")

            if resource_type == "Condition":
                codes = cls.extract_condition_codes(resource)
                condition_codes.extend(codes)

            elif resource_type == "Observation":
                codes = cls.extract_observation_codes(resource)
                observation_codes.extend(codes)

            elif resource_type in ["MedicationRequest", "Medication"]:
                codes = cls.extract_medication_codes(resource)
                medication_codes.extend(codes)

        return {
            "condition_codes": condition_codes,
            "observation_codes": observation_codes,
            "medication_codes": medication_codes,
        }

    @classmethod
    def get_codes_by_system(cls, extracted_codes: Dict[str, List[Dict]], system: str) -> List[str]:
        """
        Get just the code strings for a specific system.

        Args:
            extracted_codes: Output from extract_all_codes_from_bundle()
            system: "ICD-10", "SNOMED", "LOINC", or "RxNorm"

        Returns:
            List of code strings (e.g., ["E11.9", "E11.65"])
        """
        all_codes = []

        # Check all code categories
        for code_list in extracted_codes.values():
            for code_info in code_list:
                if code_info.get("system") == system:
                    all_codes.append(code_info["code"])

        return list(set(all_codes))  # Remove duplicates

    @classmethod
    def summarize_codes(cls, extracted_codes: Dict[str, List[Dict]]) -> Dict:
        """
        Create a summary of extracted codes for logging/debugging.

        Returns:
            {
                "icd10_count": 5,
                "snomed_count": 12,
                "loinc_count": 20,
                "rxnorm_count": 3,
                "total_codes": 40,
                "icd10_codes": ["E11.9", "I10"],
                "snomed_codes": ["314529007", ...],
                ...
            }
        """
        summary = {
            "icd10_count": 0,
            "snomed_count": 0,
            "loinc_count": 0,
            "rxnorm_count": 0,
            "icd10_codes": [],
            "snomed_codes": [],
            "loinc_codes": [],
            "rxnorm_codes": [],
        }

        for code_list in extracted_codes.values():
            for code_info in code_list:
                system = code_info.get("system")
                code = code_info.get("code")

                if system == "ICD-10":
                    summary["icd10_count"] += 1
                    summary["icd10_codes"].append(code)
                elif system == "SNOMED":
                    summary["snomed_count"] += 1
                    summary["snomed_codes"].append(code)
                elif system == "LOINC":
                    summary["loinc_count"] += 1
                    summary["loinc_codes"].append(code)
                elif system == "RxNorm":
                    summary["rxnorm_count"] += 1
                    summary["rxnorm_codes"].append(code)

        # Remove duplicates
        for key in ["icd10_codes", "snomed_codes", "loinc_codes", "rxnorm_codes"]:
            summary[key] = list(set(summary[key]))

        summary["total_codes"] = sum([
            summary["icd10_count"],
            summary["snomed_count"],
            summary["loinc_count"],
            summary["rxnorm_count"]
        ])

        return summary


# Example usage:
if __name__ == "__main__":
    import json
    import sys

    logging.basicConfig(level=logging.INFO)

    if len(sys.argv) > 1:
        fhir_file = sys.argv[1]

        with open(fhir_file, 'r') as f:
            bundle = json.load(f)

        extractor = FHIRCodeExtractor()
        codes = extractor.extract_all_codes_from_bundle(bundle)
        summary = extractor.summarize_codes(codes)

        print("\n" + "="*70)
        print(f"FHIR Code Extraction Summary for {fhir_file}")
        print("="*70)
        print(f"Total codes extracted: {summary['total_codes']}")
        print(f"  ICD-10: {summary['icd10_count']} codes")
        print(f"  SNOMED: {summary['snomed_count']} codes")
        print(f"  LOINC:  {summary['loinc_count']} codes")
        print(f"  RxNorm: {summary['rxnorm_count']} codes")

        if summary['icd10_codes']:
            print(f"\nICD-10 Codes: {', '.join(summary['icd10_codes'][:10])}")
        if summary['snomed_codes']:
            print(f"SNOMED Codes: {', '.join(summary['snomed_codes'][:10])}")
        if summary['loinc_codes']:
            print(f"LOINC Codes: {', '.join(summary['loinc_codes'][:10])}")
        if summary['rxnorm_codes']:
            print(f"RxNorm Codes: {', '.join(summary['rxnorm_codes'][:10])}")

        print("\n" + "="*70)
    else:
        print("Usage: python fhir_code_extractor.py <path_to_fhir_bundle.json>")
