"""
Trial Criteria Mapper - Convert trial text criteria to medical codes.

Maps natural language trial eligibility criteria to structured medical codes
(ICD-10, SNOMED, LOINC, RxNorm) using a medical terminology database.
"""

import json
import re
import logging
from typing import Dict, List, Optional, Tuple, Union
from pathlib import Path

logger = logging.getLogger(__name__)


class TrialCriteriaMapper:
    """Maps trial text criteria to standard medical codes"""

    def __init__(self, terminology_path: str = "medical_terminology.json"):
        """
        Initialize mapper with medical terminology database.

        Args:
            terminology_path: Path to medical terminology JSON file
        """
        self.terminology_path = Path(terminology_path)
        self.terminology = self._load_terminology()

    def _load_terminology(self) -> Dict:
        """Load medical terminology database from JSON"""
        try:
            with open(self.terminology_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load terminology database: {e}")
            return {"conditions": {}, "lab_tests": {}, "medications": {}, "exclusion_keywords": []}

    def detect_exclusion(self, text: str) -> bool:
        """
        Detect if text contains exclusion/negation keywords.

        Args:
            text: Criteria text to check

        Returns:
            True if text indicates exclusion/negation
        """
        text_lower = text.lower()
        exclusion_keywords = self.terminology.get("exclusion_keywords", [])

        for keyword in exclusion_keywords:
            if keyword in text_lower:
                return True

        return False

    def find_conditions(self, text: str) -> List[Dict]:
        """
        Find condition mentions in text and map to codes.

        Args:
            text: Criteria text to search

        Returns:
            List of matched conditions with codes
        """
        text_lower = text.lower()
        matched_conditions = []
        conditions_db = self.terminology.get("conditions", {})

        for condition_name, condition_info in conditions_db.items():
            # Check main name
            if condition_name in text_lower:
                matched_conditions.append({
                    "term": condition_name,
                    "matched_text": condition_name,
                    **condition_info
                })
                continue

            # Check variants
            variants = condition_info.get("variants", [])
            for variant in variants:
                if variant.lower() in text_lower:
                    matched_conditions.append({
                        "term": variant,
                        "matched_text": variant.lower(),
                        **condition_info
                    })
                    break

        # Sort by length (longest first) to prioritize specific matches
        matched_conditions.sort(key=lambda x: len(x.get("matched_text", "")), reverse=True)

        # Filter out generic matches that are substrings of more specific matches
        filtered_conditions = []
        used_positions = set()

        for condition in matched_conditions:
            matched_text = condition.get("matched_text", "")
            # Find position in text
            pos = text_lower.find(matched_text)
            if pos == -1:
                continue

            # Check if this match overlaps with already used positions
            match_range = set(range(pos, pos + len(matched_text)))
            if not match_range.intersection(used_positions):
                filtered_conditions.append(condition)
                used_positions.update(match_range)

        # Remove matched_text before returning
        for condition in filtered_conditions:
            condition.pop("matched_text", None)

        return filtered_conditions

    def find_lab_tests(self, text: str) -> List[Dict]:
        """
        Find lab test mentions in text and map to LOINC codes.

        Args:
            text: Criteria text to search

        Returns:
            List of matched lab tests with LOINC codes
        """
        text_lower = text.lower()
        matched_labs = []
        labs_db = self.terminology.get("lab_tests", {})

        for lab_name, lab_info in labs_db.items():
            # Check main name
            if lab_name in text_lower:
                matched_labs.append({
                    "term": lab_name,
                    **lab_info
                })
                continue

            # Check variants
            variants = lab_info.get("variants", [])
            for variant in variants:
                if variant.lower() in text_lower:
                    matched_labs.append({
                        "term": variant,
                        **lab_info
                    })
                    break

        return matched_labs

    def find_medications(self, text: str) -> List[Dict]:
        """
        Find medication mentions in text and map to RxNorm codes.

        Args:
            text: Criteria text to search

        Returns:
            List of matched medications with RxNorm codes
        """
        text_lower = text.lower()
        matched_meds = []
        meds_db = self.terminology.get("medications", {})

        for med_name, med_info in meds_db.items():
            # Check main name
            if med_name in text_lower:
                matched_meds.append({
                    "term": med_name,
                    **med_info
                })
                continue

            # Check variants
            variants = med_info.get("variants", [])
            for variant in variants:
                if variant.lower() in text_lower:
                    matched_meds.append({
                        "term": variant,
                        **med_info
                    })
                    break

        return matched_meds

    def extract_age_range(self, text: str) -> Optional[Dict[str, int]]:
        """
        Extract age range from criteria text.

        Examples:
            "18-65 years" → {"min": 18, "max": 65}
            "over 18" → {"min": 18, "max": 999}
            "adults" → {"min": 18, "max": 65}

        Args:
            text: Criteria text

        Returns:
            Dict with min/max age or None
        """
        text_lower = text.lower()

        # Pattern: "18-65 years", "age 18 to 65", etc.
        age_range_pattern = r'(\d+)\s*[-to]+\s*(\d+)\s*(?:years?|y\.?o\.?)?'
        match = re.search(age_range_pattern, text_lower)
        if match:
            return {"min": int(match.group(1)), "max": int(match.group(2))}

        # Pattern: "over 18", "18 and older", ">= 18"
        min_age_pattern = r'(?:over|above|>=|≥|older than)\s*(\d+)'
        match = re.search(min_age_pattern, text_lower)
        if match:
            return {"min": int(match.group(1)), "max": 999}

        # Pattern: "under 65", "< 65"
        max_age_pattern = r'(?:under|below|<|≤|younger than)\s*(\d+)'
        match = re.search(max_age_pattern, text_lower)
        if match:
            return {"min": 0, "max": int(match.group(1))}

        # Check demographic terms
        age_terms = self.terminology.get("demographics", {}).get("age_terms", {})
        for term, age_range in age_terms.items():
            if term in text_lower:
                return age_range

        return None

    def extract_gender(self, text: str) -> Optional[str]:
        """
        Extract gender from criteria text.

        Args:
            text: Criteria text

        Returns:
            "Male", "Female", or "All", or None
        """
        text_lower = text.lower()
        gender_terms = self.terminology.get("demographics", {}).get("gender_terms", {})

        if any(term in text_lower for term in gender_terms.get("male", [])):
            return "Male"
        elif any(term in text_lower for term in gender_terms.get("female", [])):
            return "Female"
        elif any(term in text_lower for term in gender_terms.get("all", [])):
            return "All"

        return None

    def map_criteria_to_codes(self, criteria_text: Union[str, List[str]]) -> Dict:
        """
        Main method: Map trial criteria text to medical codes.

        Args:
            criteria_text: String or list of criteria strings

        Returns:
            Structured criteria with medical codes:
            {
                "inclusion_codes": {
                    "icd10": [...],
                    "snomed": [...],
                    "loinc": [...],
                    "rxnorm": [...]
                },
                "exclusion_codes": {
                    "icd10": [...],
                    "snomed": [...],
                    "loinc": [...],
                    "rxnorm": [...]
                },
                "demographics": {
                    "age_range": {"min": 18, "max": 65},
                    "gender": "All"
                },
                "found_terms": {
                    "conditions": [...],
                    "labs": [...],
                    "medications": [...]
                }
            }
        """
        # Convert to list if string
        if isinstance(criteria_text, str):
            criteria_list = [criteria_text]
        else:
            criteria_list = criteria_text

        # Join all criteria
        full_text = " ".join(criteria_list)

        # Initialize result structure
        result = {
            "inclusion_codes": {
                "icd10": [],
                "snomed": [],
                "loinc": [],
                "rxnorm": []
            },
            "exclusion_codes": {
                "icd10": [],
                "snomed": [],
                "loinc": [],
                "rxnorm": []
            },
            "demographics": {
                "age_range": None,
                "gender": None
            },
            "found_terms": {
                "conditions": [],
                "labs": [],
                "medications": []
            }
        }

        # Extract demographics
        result["demographics"]["age_range"] = self.extract_age_range(full_text)
        result["demographics"]["gender"] = self.extract_gender(full_text)

        # Process each criterion separately to handle exclusions
        for criterion in criteria_list:
            is_exclusion = self.detect_exclusion(criterion)

            # Find conditions
            conditions = self.find_conditions(criterion)
            for cond in conditions:
                # Check if this is marked as an exclusion condition
                is_exclusion_cond = cond.get("exclusion", False)

                if is_exclusion or is_exclusion_cond:
                    # Add to exclusion codes
                    if "icd10" in cond:
                        result["exclusion_codes"]["icd10"].extend(cond["icd10"])
                    if "snomed" in cond:
                        result["exclusion_codes"]["snomed"].extend(cond["snomed"])
                else:
                    # Add to inclusion codes
                    if "icd10" in cond:
                        result["inclusion_codes"]["icd10"].extend(cond["icd10"])
                    if "snomed" in cond:
                        result["inclusion_codes"]["snomed"].extend(cond["snomed"])

                result["found_terms"]["conditions"].append({
                    "term": cond["term"],
                    "display": cond.get("display"),
                    "is_exclusion": is_exclusion or is_exclusion_cond
                })

            # Find lab tests
            labs = self.find_lab_tests(criterion)
            for lab in labs:
                if "loinc" in lab:
                    if is_exclusion:
                        result["exclusion_codes"]["loinc"].extend(lab["loinc"])
                    else:
                        result["inclusion_codes"]["loinc"].extend(lab["loinc"])

                result["found_terms"]["labs"].append({
                    "term": lab["term"],
                    "display": lab.get("display"),
                    "is_exclusion": is_exclusion
                })

            # Find medications
            medications = self.find_medications(criterion)
            for med in medications:
                if "rxnorm" in med:
                    if is_exclusion:
                        result["exclusion_codes"]["rxnorm"].extend(med["rxnorm"])
                    else:
                        result["inclusion_codes"]["rxnorm"].extend(med["rxnorm"])

                result["found_terms"]["medications"].append({
                    "term": med["term"],
                    "display": med.get("display"),
                    "is_exclusion": is_exclusion
                })

        # Remove duplicates
        for code_type in ["inclusion_codes", "exclusion_codes"]:
            for system in ["icd10", "snomed", "loinc", "rxnorm"]:
                result[code_type][system] = list(set(result[code_type][system]))

        return result


# Example usage
if __name__ == "__main__":
    import sys
    from typing import Union

    logging.basicConfig(level=logging.INFO)

    mapper = TrialCriteriaMapper()

    # Test criteria
    test_criteria = [
        "Patients with Type 2 diabetes mellitus",
        "Age 18-65 years",
        "HbA1c between 7-10%",
        "No history of diabetic nephropathy",
        "On metformin therapy"
    ]

    print("="*70)
    print("Trial Criteria Mapper - Test")
    print("="*70)
    print("\nInput Criteria:")
    for i, criterion in enumerate(test_criteria, 1):
        print(f"{i}. {criterion}")

    result = mapper.map_criteria_to_codes(test_criteria)

    print("\n" + "="*70)
    print("Mapped to Medical Codes")
    print("="*70)

    print("\n--- Demographics ---")
    print(f"Age Range: {result['demographics']['age_range']}")
    print(f"Gender: {result['demographics']['gender']}")

    print("\n--- Inclusion Codes ---")
    if result['inclusion_codes']['icd10']:
        print(f"ICD-10: {', '.join(result['inclusion_codes']['icd10'])}")
    if result['inclusion_codes']['snomed']:
        print(f"SNOMED: {', '.join(result['inclusion_codes']['snomed'])}")
    if result['inclusion_codes']['loinc']:
        print(f"LOINC: {', '.join(result['inclusion_codes']['loinc'])}")
    if result['inclusion_codes']['rxnorm']:
        print(f"RxNorm: {', '.join(result['inclusion_codes']['rxnorm'])}")

    print("\n--- Exclusion Codes ---")
    if result['exclusion_codes']['icd10']:
        print(f"ICD-10: {', '.join(result['exclusion_codes']['icd10'])}")
    if result['exclusion_codes']['snomed']:
        print(f"SNOMED: {', '.join(result['exclusion_codes']['snomed'])}")

    print("\n--- Found Terms ---")
    print(f"Conditions: {len(result['found_terms']['conditions'])}")
    for cond in result['found_terms']['conditions']:
        excl_marker = " [EXCLUSION]" if cond['is_exclusion'] else ""
        print(f"  - {cond['term']}: {cond['display']}{excl_marker}")

    print(f"\nLabs: {len(result['found_terms']['labs'])}")
    for lab in result['found_terms']['labs']:
        print(f"  - {lab['term']}: {lab['display']}")

    print(f"\nMedications: {len(result['found_terms']['medications'])}")
    for med in result['found_terms']['medications']:
        print(f"  - {med['term']}: {med['display']}")

    print("\n" + "="*70)
