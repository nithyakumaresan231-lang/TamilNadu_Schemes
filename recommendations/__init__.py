"""Personalized Government Scheme Recommendation and Explainable Eligibility Matching.

This package evaluates Tamil Nadu Government schemes dynamically against user profiles
with explainable, conservative rule-based matching.
"""

from recommendations.models import (
    UserProfile,
    MatchStatus,
    SchemeRecommendation,
    RecommendationResponse,
)
from recommendations.recommender import SchemeRecommender

__all__ = [
    "UserProfile",
    "MatchStatus",
    "SchemeRecommendation",
    "RecommendationResponse",
    "SchemeRecommender",
]
