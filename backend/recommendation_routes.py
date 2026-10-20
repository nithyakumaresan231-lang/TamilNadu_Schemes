"""FastAPI router for Personalized Scheme Recommendations."""

import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import ValidationError

from recommendations.models import UserProfile, RecommendationResponse
from recommendations.recommender import SchemeRecommender

logger = logging.getLogger("tn_schemes_recommendations_api")

router = APIRouter(prefix="/api", tags=["recommendations"])

# Shared recommender instance initialized on import
_recommender: Optional[SchemeRecommender] = None


def get_recommender() -> SchemeRecommender:
    global _recommender
    if _recommender is None:
        _recommender = SchemeRecommender()
    return _recommender


@router.post(
    "/recommendations",
    response_model=RecommendationResponse,
    status_code=status.HTTP_200_OK,
    summary="Get personalized scheme recommendations and eligibility explanations",
)
def get_recommendations(profile: UserProfile):
    """Evaluates the user profile against Tamil Nadu government schemes.

    Does NOT log sensitive personal information.
    """
    try:
        recommender = get_recommender()
        # Log only that a recommendation request was received, without sensitive fields
        logger.info("Processing scheme recommendation request.")
        response = recommender.recommend(profile)
        logger.info(
            f"Recommendations generated: {response.likely_matches_count} likely matches, "
            f"{response.needs_verification_count} needing verification, "
            f"{response.does_not_match_count} not matching."
        )
        return response
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve),
        )
    except Exception as err:
        logger.error(f"Error generating scheme recommendations: {err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate scheme recommendations. Please try again.",
        )
