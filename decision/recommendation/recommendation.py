"""
============================================================

Trading Recommendation

============================================================
"""

from dataclasses import dataclass, field


@dataclass(slots=True)
class TradingRecommendation:

    #
    # Decision
    #

    recommendation: str

    #
    # Existing symbol (keep for backward compatibility)
    #

    symbol: str

    #
    # Option Information
    #

    underlying_symbol: str = ""

    option_symbol: str = ""

    exchange: str = ""

    option_token: str = ""

    strike: float = 0.0

    expiry: str = ""

    option_type: str = ""

    #
    # Scores
    #

    confidence: float = 0.0

    score: float = 0.0

    reasons: list[str] = field(default_factory=list)

    #
    # Trade Plan
    #

    entry_price: float = 0.0

    stop_loss: float = 0.0

    target_price: float = 0.0

    risk_reward: float = 0.0
