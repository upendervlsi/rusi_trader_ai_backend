"""
RUSI Trader AI

Suggestion API
"""

from fastapi import APIRouter

from backend.services.suggestion_service import (
    SuggestionService,
)


router = APIRouter(
    prefix="/api",
    tags=["Suggestions"],
)


service = SuggestionService()


@router.get("/suggestions")
def suggestions():

    return service.get_suggestions()
