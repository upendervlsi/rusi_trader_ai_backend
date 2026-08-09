"""
============================================================

Recommendation Model

============================================================
"""

from pydantic import BaseModel


class RecommendationModel(BaseModel):

    recommendation: str | None

    confidence: float | None

    score: float | None

    option_symbol: str | None

    exchange: str | None

    strike: float | None

    expiry: str | None

    option_type: str | None

    entry_price: float | None

    stop_loss: float | None

    target_price: float | None

    risk_reward: float | None

    reasons: list[str]

    updated_time: str
