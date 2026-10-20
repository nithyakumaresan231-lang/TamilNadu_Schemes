"""Recommendation service coordinating scheme dataset loading, evaluation, and ranking."""

import json
import logging
import os
from typing import Any, Dict, List, Optional

from recommendations.eligibility import SchemeEligibilityEvaluator
from recommendations.models import (
    MatchStatus,
    RecommendationResponse,
    SchemeRecommendation,
    UserProfile,
)

logger = logging.getLogger("tn_schemes_recommender")


class SchemeRecommender:
    """Evaluates all schemes in data/schemes.json against a user profile."""

    def __init__(self, data_path: Optional[str] = None, schemes: Optional[List[Dict[str, Any]]] = None):
        if schemes is not None:
            self.schemes = schemes
        else:
            if data_path is None:
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                data_path = os.path.join(base_dir, "data", "schemes.json")
            with open(data_path, "r", encoding="utf-8") as f:
                self.schemes = json.load(f)
        logger.info(f"SchemeRecommender loaded {len(self.schemes)} schemes.")

    def recommend(self, profile: UserProfile) -> RecommendationResponse:
        evaluated: List[SchemeRecommendation] = []

        for s in self.schemes:
            evaluator = SchemeEligibilityEvaluator(s)
            rec = evaluator.evaluate(profile)
            evaluated.append(rec)

        # Partition by match status
        likely_matches: List[SchemeRecommendation] = []
        needs_verification: List[SchemeRecommendation] = []
        does_not_match: List[SchemeRecommendation] = []

        for r in evaluated:
            if r.status == MatchStatus.LIKELY_MATCH:
                likely_matches.append(r)
            elif r.status == MatchStatus.NEEDS_VERIFICATION:
                needs_verification.append(r)
            else:
                does_not_match.append(r)

        # Ranking logic:
        # Within LIKELY_MATCH: score desc, len(matched_conditions) desc
        likely_matches.sort(
            key=lambda x: (x.score, len(x.matched_conditions)),
            reverse=True,
        )

        # Within NEEDS_VERIFICATION: prioritize schemes where some conditions matched, then fewer unknowns
        needs_verification.sort(
            key=lambda x: (len(x.matched_conditions), x.score, -len(x.unknown_conditions)),
            reverse=True,
        )

        # Within DOES_NOT_MATCH: order by matched conditions count
        does_not_match.sort(
            key=lambda x: (len(x.matched_conditions), -len(x.failed_conditions)),
            reverse=True,
        )

        ranked = likely_matches + needs_verification + does_not_match

        return RecommendationResponse(
            total_schemes_evaluated=len(self.schemes),
            likely_matches_count=len(likely_matches),
            needs_verification_count=len(needs_verification),
            does_not_match_count=len(does_not_match),
            recommendations=ranked,
        )
