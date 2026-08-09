"""
============================================================

Recommendation API

============================================================
"""

from fastapi import APIRouter

from backend.services.recommendation_service import (
    RecommendationService,
)

router = APIRouter(
    prefix="/api",
    tags=["Recommendation"],
)

service = RecommendationService()


@router.get("/recommendation")
def recommendation():

    return service.get_recommendation()
