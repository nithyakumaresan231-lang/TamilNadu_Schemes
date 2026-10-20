"""Unit tests for the Scheme Recommendation and Eligibility Matching Engine.

Validates the 14 mandatory test scenarios outlined in Section 11 of the requirements:
1. Profile satisfying explicit age range.
2. Profile outside explicit age range.
3. Income below explicit threshold.
4. Income above explicit threshold.
5. Missing income where threshold is required.
6. Unknown or missing age.
7. Ambiguous eligibility statement.
8. Incomplete scheme record.
9. Scheme with PARTIAL verification.
10. Scheme with VERIFIED verification.
11. Invalid age and income inputs.
12. Scheme with no interpretable eligibility rules.
13. Mandatory condition fails while another condition is unknown.
14. Correct scheme IDs and source metadata in responses.
"""

import unittest
from recommendations.models import UserProfile, MatchStatus
from recommendations.eligibility import SchemeEligibilityEvaluator
from recommendations.recommender import SchemeRecommender


class TestRecommendationEngine(unittest.TestCase):

    def setUp(self):
        # Sample synthetic scheme records for controlled unit tests
        self.age_scheme = {
            "scheme_id": "TEST001",
            "scheme_name": "Youth Skill Support",
            "department": "Labour Welfare",
            "category": "Employment",
            "eligibility": "Youth aged 18-35 years; resident of Tamil Nadu",
            "target_beneficiaries": "Unemployed youth",
            "verification_level": "VERIFIED",
            "official_source_url": "https://tn.gov.in/youth",
        }

        self.income_scheme = {
            "scheme_id": "TEST002",
            "scheme_name": "Low Income Housing Grant",
            "department": "Housing",
            "category": "Housing",
            "eligibility": "Annual family income below ₹2,00,000 per annum",
            "target_beneficiaries": "Low income families",
            "verification_level": "PARTIAL",
            "official_source_url": "https://tn.gov.in/housing",
        }

        self.complex_scheme = {
            "scheme_id": "TEST003",
            "scheme_name": "Special Women Higher Education",
            "department": "Social Welfare",
            "category": "Education",
            "eligibility": "Girl students who studied in government schools; age 18-30; income below ₹2,00,000",
            "target_beneficiaries": "Eligible girl students",
            "verification_level": "PARTIAL",
            "official_source_url": "https://tn.gov.in/women",
        }

    # 1. Profile satisfying explicit age range
    def test_01_satisfying_age_range(self):
        profile = UserProfile(age=25)
        evaluator = SchemeEligibilityEvaluator(self.age_scheme)
        rec = evaluator.evaluate(profile)
        self.assertTrue(any("meets the required age range" in m for m in rec.matched_conditions))
        self.assertEqual(len(rec.failed_conditions), 0)

    # 2. Profile outside explicit age range
    def test_02_outside_age_range(self):
        profile = UserProfile(age=42)
        evaluator = SchemeEligibilityEvaluator(self.age_scheme)
        rec = evaluator.evaluate(profile)
        self.assertEqual(rec.status, MatchStatus.DOES_NOT_MATCH)
        self.assertTrue(any("is outside the required age range" in f for f in rec.failed_conditions))

    # 3. Income below explicit threshold
    def test_03_income_below_threshold(self):
        profile = UserProfile(annual_income=150000.0)
        evaluator = SchemeEligibilityEvaluator(self.income_scheme)
        rec = evaluator.evaluate(profile)
        self.assertTrue(any("is within the limit" in m for m in rec.matched_conditions))
        self.assertEqual(len(rec.failed_conditions), 0)

    # 4. Income above explicit threshold
    def test_04_income_above_threshold(self):
        profile = UserProfile(annual_income=250000.0)
        evaluator = SchemeEligibilityEvaluator(self.income_scheme)
        rec = evaluator.evaluate(profile)
        self.assertEqual(rec.status, MatchStatus.DOES_NOT_MATCH)
        self.assertTrue(any("exceeds the explicit limit" in f for f in rec.failed_conditions))

    # 5. Missing income where threshold is required
    def test_05_missing_income_where_required(self):
        profile = UserProfile(annual_income=None)
        evaluator = SchemeEligibilityEvaluator(self.income_scheme)
        rec = evaluator.evaluate(profile)
        self.assertEqual(rec.status, MatchStatus.NEEDS_VERIFICATION)
        self.assertTrue(any("Annual family income is required" in u for u in rec.unknown_conditions))

    # 6. Unknown or missing age
    def test_06_missing_age_where_required(self):
        profile = UserProfile(age=None)
        evaluator = SchemeEligibilityEvaluator(self.age_scheme)
        rec = evaluator.evaluate(profile)
        self.assertEqual(rec.status, MatchStatus.NEEDS_VERIFICATION)
        self.assertTrue(any("Age is required" in u for u in rec.unknown_conditions))

    # 7. Ambiguous eligibility statement
    def test_07_ambiguous_eligibility(self):
        ambiguous_scheme = {
            "scheme_id": "TEST004",
            "scheme_name": "General Welfare Fund",
            "eligibility": "Eligible citizens as per guidelines; income criteria as per guidelines",
            "target_beneficiaries": "General public",
            "verification_level": "PARTIAL",
        }
        profile = UserProfile(age=30, annual_income=100000.0)
        evaluator = SchemeEligibilityEvaluator(ambiguous_scheme)
        rec = evaluator.evaluate(profile)
        self.assertEqual(rec.status, MatchStatus.NEEDS_VERIFICATION)
        self.assertTrue(any("income threshold is not specified" in u for u in rec.unknown_conditions))

    # 8. Incomplete scheme record
    def test_08_incomplete_scheme_record(self):
        incomplete_scheme = {
            "scheme_id": "TEST005",
            "scheme_name": "Incomplete Record Scheme",
            "eligibility": None,
            "target_beneficiaries": None,
            "verification_level": "PARTIAL",
        }
        profile = UserProfile(age=25)
        evaluator = SchemeEligibilityEvaluator(incomplete_scheme)
        rec = evaluator.evaluate(profile)
        self.assertEqual(rec.status, MatchStatus.NEEDS_VERIFICATION)
        self.assertTrue(any("descriptive or general" in u for u in rec.unknown_conditions))

    # 9. Scheme with PARTIAL verification
    def test_09_partial_verification_scheme(self):
        evaluator = SchemeEligibilityEvaluator(self.income_scheme)
        # Even with matching income, PARTIAL verification level forces NEEDS_VERIFICATION
        rec = evaluator.evaluate(UserProfile(annual_income=150000.0))
        self.assertEqual(rec.verification_level, "PARTIAL")
        self.assertEqual(rec.status, MatchStatus.NEEDS_VERIFICATION)
        self.assertTrue(any("requires official departmental verification" in u for u in rec.unknown_conditions))

        # But a definitive failure on a mandatory condition still triggers DOES_NOT_MATCH
        rec_failed = evaluator.evaluate(UserProfile(annual_income=300000.0))
        self.assertEqual(rec_failed.status, MatchStatus.DOES_NOT_MATCH)

    # 10. Scheme with VERIFIED verification
    def test_10_verified_scheme(self):
        evaluator = SchemeEligibilityEvaluator(self.age_scheme)
        rec = evaluator.evaluate(UserProfile(age=25))
        self.assertEqual(rec.verification_level, "VERIFIED")
        self.assertEqual(rec.status, MatchStatus.LIKELY_MATCH)

    # 11. Invalid age and income inputs
    def test_11_input_validation(self):
        with self.assertRaises(ValueError):
            UserProfile(age=-5)
        with self.assertRaises(ValueError):
            UserProfile(age=150)
        with self.assertRaises(ValueError):
            UserProfile(annual_income=-1000.0)

    # 12. Scheme with no interpretable eligibility rules
    def test_12_no_interpretable_rules(self):
        vague_scheme = {
            "scheme_id": "TEST006",
            "scheme_name": "Broad Community Scheme",
            "eligibility": "Support for social welfare across the district",
            "target_beneficiaries": "Local community",
            "verification_level": "PARTIAL",
        }
        rec = SchemeEligibilityEvaluator(vague_scheme).evaluate(UserProfile(age=30))
        self.assertEqual(rec.status, MatchStatus.NEEDS_VERIFICATION)

    # 13. Mandatory condition fails while another condition is unknown
    def test_13_failed_condition_with_unknown_condition(self):
        # Male user, age=25 (matches age), income=None (unknown), but gender is female only (fails)
        profile = UserProfile(age=25, gender="male", annual_income=None)
        evaluator = SchemeEligibilityEvaluator(self.complex_scheme)
        rec = evaluator.evaluate(profile)
        # Even though income is unknown, the explicit gender failure forces DOES_NOT_MATCH
        self.assertEqual(rec.status, MatchStatus.DOES_NOT_MATCH)
        self.assertTrue(any("explicitly intended for female" in f for f in rec.failed_conditions))

    # 14. Correct scheme IDs and source metadata in responses
    def test_14_metadata_integrity(self):
        schemes = [self.age_scheme, self.income_scheme]
        recommender = SchemeRecommender(schemes=schemes)
        resp = recommender.recommend(UserProfile(age=25))
        self.assertEqual(resp.total_schemes_evaluated, 2)
        rec0 = resp.recommendations[0]
        self.assertIn(rec0.scheme_id, ["TEST001", "TEST002"])
        self.assertTrue(rec0.official_source_url.startswith("https://tn.gov.in/"))


if __name__ == "__main__":
    unittest.main()
