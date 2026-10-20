"""Explainable eligibility rule extraction and condition evaluation engine.

Extracts and evaluates explicit, unambiguous eligibility rules from scheme records
against a UserProfile. Adheres to conservative evaluation principles:
- Evaluates conditions only when explicitly present in the scheme record.
- Flags ambiguous or unstated criteria as requiring verification.
- Never assumes missing user data satisfies a mandatory requirement.
"""

import re
from typing import Any, Dict, List, Optional, Tuple
from recommendations.models import UserProfile, MatchStatus, SchemeRecommendation


def _clean_text(val: Any) -> str:
    if val is None:
        return ""
    if isinstance(val, list):
        return " ".join(str(x) for x in val)
    return str(val)


class SchemeEligibilityEvaluator:
    """Evaluates a single scheme's eligibility against a user profile."""

    def __init__(self, scheme: Dict[str, Any]):
        self.scheme = scheme
        self.scheme_id = scheme.get("scheme_id", "")
        self.scheme_name = scheme.get("scheme_name", "")
        self.eligibility_text = _clean_text(scheme.get("eligibility"))
        self.target_text = _clean_text(scheme.get("target_beneficiaries"))
        self.objective_text = _clean_text(scheme.get("objective"))
        self.category_text = _clean_text(scheme.get("category"))
        self.department_text = _clean_text(scheme.get("department"))
        self.verification_level = scheme.get("verification_level", "PARTIAL")
        self.combined_text = f"{self.eligibility_text} {self.target_text} {self.objective_text} {self.category_text}".lower()

    def evaluate(self, profile: UserProfile) -> SchemeRecommendation:
        matched: List[str] = []
        failed: List[str] = []
        unknown: List[str] = []

        # 1. Age Evaluation
        self._eval_age(profile, matched, failed, unknown)

        # 2. Income Evaluation
        self._eval_income(profile, matched, failed, unknown)

        # 3. Gender Evaluation
        self._eval_gender(profile, matched, failed, unknown)

        # 4. Government School Evaluation
        self._eval_govt_school(profile, matched, failed, unknown)

        # 5. Student / Education Enrolment Evaluation
        self._eval_student_status(profile, matched, failed, unknown)

        # 6. Social Category (SC/ST/BC/MBC) Evaluation
        self._eval_social_category(profile, matched, failed, unknown)

        # 7. Farmer / Agriculture Evaluation
        self._eval_farmer_status(profile, matched, failed, unknown)

        # 8. Disability Status Evaluation
        self._eval_disability(profile, matched, failed, unknown)

        # 9. Marital Status Evaluation
        self._eval_marital_status(profile, matched, failed, unknown)

        # 10. Specialized Occupation (Handloom / Construction / Driver)
        self._eval_occupation(profile, matched, failed, unknown)

        # 11. Record Completeness & Dataset Verification Check
        has_evaluated_rules = len(matched) > 0 or len(failed) > 0 or len(unknown) > 0
        if not has_evaluated_rules:
            unknown.append(
                "Eligibility criteria in the official record are descriptive or general; departmental verification is required"
            )

        # Check for vague phrases in eligibility
        vague_markers = [
            ("as per guidelines", "Specific eligibility guidelines are not detailed in the record"),
            ("as per rules", "Detailed rules are governed by external government orders"),
            ("subject to applicable guidelines", "Subject to specific departmental circulars"),
        ]
        for marker, expl in vague_markers:
            if marker in self.combined_text:
                if expl not in unknown:
                    unknown.append(expl)

        # Verification level notice: insufficiently verified records require departmental verification
        if self.verification_level not in ("VERIFIED", "CORRECTED"):
            status_desc = self.verification_level or "PARTIAL"
            unknown.append(
                f"Scheme record has '{status_desc}' verification status in the dataset and requires official departmental verification before final eligibility can be confirmed"
            )

        # Determine overall match status
        if len(failed) > 0:
            status = MatchStatus.DOES_NOT_MATCH
        elif len(unknown) > 0 or len(matched) == 0:
            status = MatchStatus.NEEDS_VERIFICATION
        else:
            status = MatchStatus.LIKELY_MATCH

        # Calculate an explainable score for ranking
        score = (len(matched) * 10) - (len(unknown) * 2)

        return SchemeRecommendation(
            scheme_id=self.scheme_id,
            scheme_name=self.scheme_name,
            department=self.department_text,
            category=self.category_text,
            status=status,
            matched_conditions=matched,
            failed_conditions=failed,
            unknown_conditions=unknown,
            eligibility=self.eligibility_text,
            verification_level=self.verification_level,
            official_source_url=self.scheme.get("official_source_url") or self.scheme.get("official_application_url"),
            score=score,
        )

    # -------------------------------------------------------------
    # Rule Evaluation Methods
    # -------------------------------------------------------------

    def _eval_age(self, profile: UserProfile, matched: List[str], failed: List[str], unknown: List[str]):
        text = self.combined_text
        # Range patterns like 'age 18-35', 'age limit 18-45', 'aged 18–55 years'
        m_range = re.search(r'\b(?:age|aged)\s*(?:limit)?\s*(\d{1,2})\s*[-–—to]\s*(\d{1,2})\b', text)
        # Min age patterns like 'aged 18+', 'age 60+'
        m_plus = re.search(r'\b(?:age|aged)\s*(\d{1,2})\s*\+', text)
        # Explicit 'below 10,000' is population, but 'aged 0-18' is range

        min_age, max_age = None, None
        if m_range:
            min_age = int(m_range.group(1))
            max_age = int(m_range.group(2))
        elif m_plus:
            min_age = int(m_plus.group(1))

        if min_age is not None:
            if profile.age is not None:
                if max_age is not None:
                    if min_age <= profile.age <= max_age:
                        matched.append(f"Age {profile.age} meets the required age range of {min_age}–{max_age} years")
                    else:
                        failed.append(f"Age {profile.age} is outside the required age range of {min_age}–{max_age} years")
                else:
                    if profile.age >= min_age:
                        matched.append(f"Age {profile.age} satisfies the minimum age requirement of {min_age}+ years")
                    else:
                        failed.append(f"Age {profile.age} is below the minimum required age of {min_age} years")
            else:
                range_desc = f"{min_age}–{max_age}" if max_age else f"{min_age}+"
                unknown.append(f"Age is required to verify the {range_desc} years eligibility criteria")
        elif "age condition" in text or "age conditions" in text or "age-related" in text:
            unknown.append("Specific age conditions apply under department guidelines and require verification")

    def _eval_income(self, profile: UserProfile, matched: List[str], failed: List[str], unknown: List[str]):
        text = self.combined_text
        if "without an income condition" in text:
            matched.append("Scheme is provided without an income ceiling")
            return

        # Check for explicit numbers
        # e.g., 'income below ₹2,00,000', 'income up to ₹3 lakh', 'not exceed ₹2.5 lakh'
        threshold = None
        if "2,00,000" in text or "200000" in text:
            threshold = 200000.0
        elif "1,50,000" in text or "150000" in text:
            threshold = 150000.0
        elif "2,40,000" in text or "240000" in text:
            threshold = 240000.0
        elif "3,00,000" in text or "300000" in text or "3 lakh" in text:
            threshold = 300000.0
        elif "4,00,000" in text or "400000" in text or "4 lakh" in text:
            threshold = 400000.0
        elif "5,00,000" in text or "500000" in text or "5 lakh" in text:
            threshold = 500000.0
        elif "6,00,000" in text or "600000" in text or "6 lakh" in text:
            threshold = 600000.0
        elif "2.5 lakh" in text or "not exceed ₹2" in text:
            threshold = 250000.0

        if threshold is not None:
            if profile.annual_income is not None:
                if profile.annual_income <= threshold:
                    matched.append(
                        f"Annual family income ₹{int(profile.annual_income):,} is within the limit (max ₹{int(threshold):,})"
                    )
                else:
                    failed.append(
                        f"Annual family income ₹{int(profile.annual_income):,} exceeds the explicit limit of ₹{int(threshold):,}"
                    )
            else:
                unknown.append(f"Annual family income is required to verify the threshold of ₹{int(threshold):,}")
        elif (
            "income criteria as per guidelines" in text
            or "income below specified limit" in text
            or "family income below specified limit" in text
            or "income criteria" in text
        ):
            unknown.append("The income threshold is not specified in the record and requires departmental verification")

    def _eval_gender(self, profile: UserProfile, matched: List[str], failed: List[str], unknown: List[str]):
        text = self.combined_text
        requires_female = any(w in text for w in ["girl student", "girl students", "women aged", "women entrepreneurs", "pregnant women", "eligible female", "women household heads", "destitute women"])
        requires_male = any(w in text for w in ["boy student", "boy students", "eligible male students"])

        if requires_female and not requires_male:
            if profile.gender:
                g = profile.gender.strip().lower()
                if g in ("female", "woman", "girl"):
                    matched.append("Gender (Female) matches the target group for this scheme")
                elif g in ("male", "boy", "man"):
                    failed.append("Scheme is explicitly intended for female / girl beneficiaries")
                else:
                    unknown.append("Gender eligibility requires verification against scheme guidelines")
            else:
                unknown.append("Gender is not specified; scheme requires female applicant")
        elif requires_male and not requires_female:
            if profile.gender:
                g = profile.gender.strip().lower()
                if g in ("male", "boy", "man"):
                    matched.append("Gender (Male) matches the target group for this scheme")
                elif g in ("female", "woman", "girl"):
                    failed.append("Scheme is explicitly intended for male / boy beneficiaries")
                else:
                    unknown.append("Gender eligibility requires verification against scheme guidelines")
            else:
                unknown.append("Gender is not specified; scheme requires male applicant")

    def _eval_govt_school(self, profile: UserProfile, matched: List[str], failed: List[str], unknown: List[str]):
        text = self.combined_text
        if "government school" in text or "govt school" in text or "government schools" in text:
            if profile.government_school == "yes":
                matched.append("Attended a government school as required")
            elif profile.government_school == "no":
                failed.append("Scheme explicitly requires education in a government school")
            else:
                unknown.append("Government-school attendance has not been confirmed")

    def _eval_student_status(self, profile: UserProfile, matched: List[str], failed: List[str], unknown: List[str]):
        text = self.combined_text
        student_keywords = ["pursuing higher education", "students enrolled in colleges", "college students", "school students", "post-matric"]
        if any(kw in text for kw in student_keywords):
            is_student = (profile.current_student_status == "yes") or (profile.occupation and "student" in profile.occupation.lower())
            is_non_student = (profile.current_student_status == "no") and (profile.occupation and "student" not in profile.occupation.lower())

            if is_student:
                matched.append("Current student enrolment status matches the educational requirement")
            elif is_non_student:
                failed.append("Scheme requires currently enrolled student status")
            else:
                unknown.append("Student enrolment status has not been specified and requires verification")

    def _eval_social_category(self, profile: UserProfile, matched: List[str], failed: List[str], unknown: List[str]):
        text = self.combined_text
        # SC/ST explicit requirement
        sc_st_exclusive = ("sc/st categories" in text or "sc/st students" in text or "sc/st farmers" in text or "sc/st beneficiaries" in text)
        bc_mbc_exclusive = ("bc/mbc students" in text or "bc/mbc categories" in text or "bc/mbc/dnc" in text)

        if sc_st_exclusive:
            if profile.category:
                cat = profile.category.strip().upper()
                if "SC" in cat or "ST" in cat:
                    matched.append(f"Social category ({profile.category}) matches the scheme target group (SC/ST)")
                elif cat in ("BC", "MBC", "DNC", "GENERAL", "OC"):
                    failed.append(f"Scheme explicitly targets SC/ST categories (provided: {profile.category})")
                else:
                    unknown.append(f"Social category ({profile.category}) requires verification against SC/ST criteria")
            else:
                unknown.append("Social category is required to verify the SC/ST eligibility requirement")
        elif bc_mbc_exclusive:
            if profile.category:
                cat = profile.category.strip().upper()
                if any(c in cat for c in ["BC", "MBC", "DNC"]):
                    matched.append(f"Social category ({profile.category}) matches the scheme target group (BC/MBC/DNC)")
                elif cat in ("SC", "ST", "GENERAL", "OC"):
                    failed.append(f"Scheme explicitly targets BC/MBC/DNC categories (provided: {profile.category})")
                else:
                    unknown.append(f"Social category ({profile.category}) requires verification against BC/MBC criteria")
            else:
                unknown.append("Social category is required to verify the BC/MBC eligibility requirement")

    def _eval_farmer_status(self, profile: UserProfile, matched: List[str], failed: List[str], unknown: List[str]):
        text = self.combined_text
        farmer_indicators = ["land-holding farmers", "registered agricultural workers", "farmers and agricultural", "small and marginal farmers", "engaged in agriculture"]
        if any(ind in text for ind in farmer_indicators):
            is_farmer = (profile.farmer_status == "yes") or (profile.occupation and "farmer" in profile.occupation.lower())
            is_non_farmer = (profile.farmer_status == "no") and (profile.occupation and "farmer" not in profile.occupation.lower())

            if is_farmer:
                matched.append("Farmer / agricultural background matches scheme criteria")
            elif is_non_farmer:
                failed.append("Scheme specifically requires farmer or agricultural worker status")
            else:
                unknown.append("Farmer or agricultural land-holding status requires verification")

    def _eval_disability(self, profile: UserProfile, matched: List[str], failed: List[str], unknown: List[str]):
        text = self.combined_text
        if "intellectually disabled" in text or "differently abled" in text or "disability must be" in text:
            if profile.disability_status == "yes":
                matched.append("Disability status matches the scheme target group")
            elif profile.disability_status == "no":
                failed.append("Scheme is specifically for differently abled / disabled beneficiaries")
            else:
                unknown.append("Disability status is required to verify this scheme")

    def _eval_marital_status(self, profile: UserProfile, matched: List[str], failed: List[str], unknown: List[str]):
        text = self.combined_text
        requires_widow_destitute = any(w in text for w in ["widow/divorced/abandoned", "widow re-marriage", "destitute widow", "widow pension"])
        if requires_widow_destitute:
            if profile.marital_status:
                ms = profile.marital_status.strip().lower()
                if ms in ("widow", "divorced", "destitute", "abandoned", "deserted"):
                    matched.append(f"Marital status ({profile.marital_status}) matches scheme criteria")
                elif ms in ("married", "unmarried", "single"):
                    failed.append("Scheme explicitly requires widow, divorced, or destitute status")
                else:
                    unknown.append("Marital status requires verification against widow/destitute criteria")
            else:
                unknown.append("Marital / destitute status is required to verify eligibility")

    def _eval_occupation(self, profile: UserProfile, matched: List[str], failed: List[str], unknown: List[str]):
        text = self.combined_text
        if "handloom weaver" in text or "co-operative handloom" in text:
            if profile.occupation:
                occ = profile.occupation.strip().lower()
                if "weaver" in occ or "handloom" in occ:
                    matched.append("Occupation as handloom weaver matches scheme requirement")
                else:
                    failed.append("Scheme is specifically for registered handloom weavers")
            else:
                unknown.append("Registered handloom weaver status requires verification")
        elif "construction worker" in text or "construction workers" in text:
            if profile.occupation:
                occ = profile.occupation.strip().lower()
                if "construction" in occ:
                    matched.append("Registered construction worker occupation matches scheme requirement")
                else:
                    failed.append("Scheme is specifically for registered construction workers")
            else:
                unknown.append("Registered construction worker status requires verification")
        elif "driver welfare" in text or "driver-board" in text:
            if profile.occupation:
                occ = profile.occupation.strip().lower()
                if "driver" in occ:
                    matched.append("Registered driver occupation matches scheme requirement")
                else:
                    failed.append("Scheme is specifically for registered driver board workers")
            else:
                unknown.append("Registered driver board status requires verification")
