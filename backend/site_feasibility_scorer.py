"""
Site Feasibility Scorer - Calculate site feasibility based on medical codes.

Scores sites on 4 dimensions:
1. CAPABILITY: Can the site perform required LOINC lab tests?
2. EXPERIENCE: Has the site run trials in this ICD-10 chapter before?
3. POPULATION: Does the site's EHR have patients with the required condition codes?
4. CAPACITY: Does the site have bandwidth for another trial?

This addresses the advisor's requirement for "trial and site feasibility based
on controlled terminology sets" using Epic EHR standards.
"""

import json
import logging
from typing import Dict, List, Optional
from pathlib import Path
from collections import defaultdict

logger = logging.getLogger(__name__)


class SiteFeasibilityScorer:
    """Calculate multi-dimensional feasibility scores for trial sites"""

    def __init__(self, site_database_path: str = "site_capabilities.json"):
        """
        Initialize scorer with site capability database.

        Args:
            site_database_path: Path to site_capabilities.json
        """
        self.site_db_path = Path(site_database_path)
        self.sites = self._load_sites()

    def _load_sites(self) -> List[Dict]:
        """Load site capability database"""
        try:
            with open(self.site_db_path, 'r') as f:
                data = json.load(f)
                return data.get("sites", [])
        except Exception as e:
            logger.error(f"Failed to load site database: {e}")
            return []

    def get_icd10_chapter(self, icd10_code: str) -> str:
        """
        Map ICD-10 code to its chapter.

        Args:
            icd10_code: ICD-10 code like "E11.9"

        Returns:
            Chapter range like "E10-E14" (Diabetes)
        """
        # Extract first character and first two digits
        if not icd10_code:
            return "Unknown"

        letter = icd10_code[0]

        # Extract numeric part
        numeric_part = ""
        for char in icd10_code[1:]:
            if char.isdigit():
                numeric_part += char
            else:
                break

        if not numeric_part:
            return "Unknown"

        number = int(numeric_part)

        # Map to chapters
        chapter_map = {
            "E": [(10, 14, "E10-E14")],  # Diabetes
            "I": [(0, 99, "I00-I99")],   # Circulatory
            "C": [(0, 97, "C00-C97")],   # Cancer
            "J": [(0, 99, "J00-J99")],   # Respiratory
            "F": [(0, 99, "F00-F99")],   # Mental/Behavioral
            "N": [(0, 99, "N00-N99")]    # Genitourinary
        }

        if letter in chapter_map:
            for min_code, max_code, chapter in chapter_map[letter]:
                if min_code <= number <= max_code:
                    return chapter

        return "Unknown"

    def score_capability(self, site: Dict, required_loinc_codes: List[str]) -> Dict:
        """
        Score site's LOINC lab capability.

        Args:
            site: Site dictionary from database
            required_loinc_codes: List of LOINC codes trial needs

        Returns:
            {
                "score": 0.0-1.0,
                "has_codes": [...],
                "missing_codes": [...],
                "coverage": 0.85
            }
        """
        if not required_loinc_codes:
            return {"score": 1.0, "has_codes": [], "missing_codes": [], "coverage": 1.0}

        site_loinc = set(site.get("capabilities", {}).get("loinc_codes", []))
        required_set = set(required_loinc_codes)

        has_codes = list(site_loinc.intersection(required_set))
        missing_codes = list(required_set - site_loinc)

        coverage = len(has_codes) / len(required_set) if required_set else 1.0

        # Score calculation:
        # - 100% coverage = 1.0
        # - 80%+ coverage = 0.8-1.0 (good)
        # - 50-80% coverage = 0.5-0.8 (acceptable)
        # - <50% coverage = 0.0-0.5 (poor)
        score = coverage

        return {
            "score": score,
            "has_codes": has_codes,
            "missing_codes": missing_codes,
            "coverage": coverage
        }

    def score_experience(self, site: Dict, trial_icd10_codes: List[str]) -> Dict:
        """
        Score site's experience with trial's disease area (ICD-10 chapter).

        Args:
            site: Site dictionary from database
            trial_icd10_codes: ICD-10 codes from trial inclusion criteria

        Returns:
            {
                "score": 0.0-1.0,
                "relevant_chapters": {...},
                "total_trials": 42,
                "success_rate": 0.87
            }
        """
        if not trial_icd10_codes:
            return {"score": 0.5, "relevant_chapters": {}, "total_trials": 0, "success_rate": 0.0}

        # Determine which ICD-10 chapters this trial belongs to
        trial_chapters = defaultdict(int)
        for code in trial_icd10_codes:
            chapter = self.get_icd10_chapter(code)
            if chapter != "Unknown":
                trial_chapters[chapter] += 1

        # Get site's experience in those chapters
        site_experience = site.get("experience", {}).get("by_icd10_chapter", {})

        relevant_trials = 0
        for chapter in trial_chapters:
            relevant_trials += site_experience.get(chapter, 0)

        total_site_trials = site.get("experience", {}).get("total_trials", 0)
        success_rate = site.get("experience", {}).get("success_rate", 0.0)

        # Score calculation:
        # - Experience in relevant chapters is most important
        # - More trials = higher score
        # - Success rate acts as multiplier

        if total_site_trials == 0:
            experience_score = 0.0
        else:
            # Normalize: 50+ trials in relevant area = 1.0
            experience_score = min(relevant_trials / 50.0, 1.0)

        # Apply success rate multiplier
        score = experience_score * success_rate

        return {
            "score": score,
            "relevant_chapters": dict(trial_chapters),
            "relevant_trials": relevant_trials,
            "total_trials": total_site_trials,
            "success_rate": success_rate
        }

    def score_population(self, site: Dict, trial_icd10_codes: List[str],
                        target_enrollment: int = 100) -> Dict:
        """
        Score site's patient population matching trial codes.

        Args:
            site: Site dictionary from database
            trial_icd10_codes: ICD-10 codes from trial inclusion criteria
            target_enrollment: Trial enrollment target

        Returns:
            {
                "score": 0.0-1.0,
                "matching_patients": 8500,
                "target_enrollment": 100,
                "ratio": 85.0
            }
        """
        if not trial_icd10_codes:
            return {"score": 0.5, "matching_patients": 0, "target_enrollment": target_enrollment, "ratio": 0.0}

        # Count patients with any of the trial's inclusion codes
        site_population = site.get("population", {}).get("by_condition", {})

        matching_patients = 0
        for code in trial_icd10_codes:
            matching_patients += site_population.get(code, 0)

        # Calculate ratio of available patients to target enrollment
        if target_enrollment == 0:
            ratio = 0.0
        else:
            ratio = matching_patients / target_enrollment

        # Score calculation:
        # - Need at least 10x target for good score (accounting for screening failures)
        # - 20x target = 1.0 (excellent)
        # - 10x target = 0.8 (good)
        # - 5x target = 0.6 (acceptable)
        # - 1x target = 0.3 (poor)
        # - <1x target = 0.0-0.3 (very poor)

        if ratio >= 20:
            score = 1.0
        elif ratio >= 10:
            score = 0.8 + (ratio - 10) * 0.02  # 0.8 to 1.0
        elif ratio >= 5:
            score = 0.6 + (ratio - 5) * 0.04   # 0.6 to 0.8
        elif ratio >= 1:
            score = 0.3 + (ratio - 1) * 0.075  # 0.3 to 0.6
        else:
            score = ratio * 0.3                # 0.0 to 0.3

        return {
            "score": score,
            "matching_patients": matching_patients,
            "target_enrollment": target_enrollment,
            "ratio": ratio
        }

    def score_capacity(self, site: Dict) -> Dict:
        """
        Score site's capacity for new trials.

        Args:
            site: Site dictionary from database

        Returns:
            {
                "score": 0.0-1.0,
                "available_slots": 12,
                "current_trials": 38,
                "max_trials": 50,
                "utilization": 0.76
            }
        """
        capacity_data = site.get("capacity", {})

        current_trials = capacity_data.get("current_trials", 0)
        max_trials = capacity_data.get("max_concurrent_trials", 0)
        available_slots = capacity_data.get("available_slots", 0)

        if max_trials == 0:
            utilization = 1.0
            score = 0.0
        else:
            utilization = current_trials / max_trials

            # Score calculation:
            # - <50% utilization = 1.0 (plenty of capacity)
            # - 50-70% = 0.8-1.0 (good capacity)
            # - 70-85% = 0.5-0.8 (acceptable)
            # - 85-95% = 0.2-0.5 (tight)
            # - >95% = 0.0-0.2 (overloaded)

            if utilization < 0.5:
                score = 1.0
            elif utilization < 0.7:
                score = 0.8 + (0.7 - utilization) * 1.0  # 0.8 to 1.0
            elif utilization < 0.85:
                score = 0.5 + (0.85 - utilization) * 2.0  # 0.5 to 0.8
            elif utilization < 0.95:
                score = 0.2 + (0.95 - utilization) * 3.0  # 0.2 to 0.5
            else:
                score = max(0.0, (1.0 - utilization) * 2.0)  # 0.0 to 0.2

        return {
            "score": score,
            "available_slots": available_slots,
            "current_trials": current_trials,
            "max_trials": max_trials,
            "utilization": utilization
        }

    def calculate_feasibility(self, site: Dict, trial_criteria: Dict,
                             target_enrollment: int = 100) -> Dict:
        """
        Calculate overall feasibility score for a site.

        Args:
            site: Site dictionary from database
            trial_criteria: Trial eligibility criteria with medical codes
            target_enrollment: Trial enrollment target

        Returns:
            {
                "site_id": "SITE001",
                "site_name": "Johns Hopkins Hospital",
                "overall_score": 0.85,
                "capability": {...},
                "experience": {...},
                "population": {...},
                "capacity": {...}
            }
        """
        # Extract required codes from trial criteria
        inclusion_codes = trial_criteria.get("inclusion_codes", {})
        required_loinc = inclusion_codes.get("loinc", [])
        required_icd10 = inclusion_codes.get("icd10", [])

        # Calculate component scores
        capability = self.score_capability(site, required_loinc)
        experience = self.score_experience(site, required_icd10)
        population = self.score_population(site, required_icd10, target_enrollment)
        capacity = self.score_capacity(site)

        # Overall score: weighted average
        # Capability: 30% (must have labs)
        # Experience: 25% (domain expertise)
        # Population: 30% (patient availability)
        # Capacity: 15% (bandwidth)

        overall_score = (
            capability["score"] * 0.30 +
            experience["score"] * 0.25 +
            population["score"] * 0.30 +
            capacity["score"] * 0.15
        )

        return {
            "site_id": site.get("site_id"),
            "site_name": site.get("site_name"),
            "location": site.get("location"),
            "overall_score": round(overall_score, 3),
            "capability": capability,
            "experience": experience,
            "population": population,
            "capacity": capacity
        }

    def rank_sites(self, trial_criteria: Dict, target_enrollment: int = 100,
                   top_n: int = 10) -> List[Dict]:
        """
        Rank all sites by feasibility for a trial.

        Args:
            trial_criteria: Trial eligibility criteria with medical codes
            target_enrollment: Trial enrollment target
            top_n: Number of top sites to return

        Returns:
            List of site feasibility scores, sorted by overall_score descending
        """
        site_scores = []

        for site in self.sites:
            score = self.calculate_feasibility(site, trial_criteria, target_enrollment)
            site_scores.append(score)

        # Sort by overall score descending
        site_scores.sort(key=lambda x: x["overall_score"], reverse=True)

        return site_scores[:top_n]


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    scorer = SiteFeasibilityScorer()

    # Example trial: Diabetes trial requiring HbA1c testing
    example_trial = {
        "inclusion_codes": {
            "icd10": ["E11.9", "E11.65"],  # Type 2 diabetes
            "loinc": ["4548-4", "17856-6", "2339-0"],  # HbA1c, Glucose
            "snomed": ["44054006"],
            "rxnorm": []
        },
        "exclusion_codes": {
            "icd10": ["E11.21", "E11.31"],  # Nephropathy, retinopathy
            "snomed": [],
            "loinc": [],
            "rxnorm": []
        }
    }

    print("=" * 70)
    print("Site Feasibility Scoring - Diabetes Trial Example")
    print("=" * 70)
    print()

    ranked_sites = scorer.rank_sites(example_trial, target_enrollment=150, top_n=5)

    for i, site_score in enumerate(ranked_sites, 1):
        print(f"{i}. {site_score['site_name']} ({site_score['site_id']})")
        print(f"   Overall Score: {site_score['overall_score']:.3f}")
        print(f"   - Capability: {site_score['capability']['score']:.3f} "
              f"({site_score['capability']['coverage']*100:.0f}% LOINC coverage)")
        print(f"   - Experience: {site_score['experience']['score']:.3f} "
              f"({site_score['experience']['relevant_trials']} relevant trials)")
        print(f"   - Population: {site_score['population']['score']:.3f} "
              f"({site_score['population']['matching_patients']} patients, "
              f"{site_score['population']['ratio']:.1f}x target)")
        print(f"   - Capacity: {site_score['capacity']['score']:.3f} "
              f"({site_score['capacity']['available_slots']} slots available)")
        print()

    print("=" * 70)
