"""
RUSI Trader AI

Suggestion API Model
"""

from pydantic import BaseModel, Field


class SuggestionModel(BaseModel):

    suggestion_id: str

    category: str
    symbol: str
    exchange: str

    latest_price: float

    signal: str

    entry_price: float
    stop_loss: float
    target_price: float
    risk_reward: float

    confidence: float
    score: float

    status: str

    created_time: str
    updated_time: str

    reasons: list[str] = Field(default_factory=list)

    underlying_symbol: str = ""
    option_symbol: str = ""
    option_token: str = ""
    option_type: str = ""

    strike: float = 0.0
    expiry: str = ""

    entry_reached: bool = False
    profit_booked: bool = False
    exit_reason: str = ""
