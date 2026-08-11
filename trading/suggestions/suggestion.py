"""
RUSI Trader AI

Trading Suggestion

Represents an AI-generated market opportunity shown to
the Flutter application.

IMPORTANT:
This object is informational/trading guidance only.
It does NOT execute broker orders.
"""

from dataclasses import dataclass, field


@dataclass
class TradingSuggestion:

    # ---------------------------------------------------------
    # Identity
    # ---------------------------------------------------------

    suggestion_id: str = ""

    category: str = ""

    symbol: str = ""

    exchange: str = ""

    # ---------------------------------------------------------
    # Market
    # ---------------------------------------------------------

    latest_price: float = 0.0

    # ---------------------------------------------------------
    # Trade direction
    # ---------------------------------------------------------

    signal: str = "IGNORE"

    # ---------------------------------------------------------
    # Trade plan
    # ---------------------------------------------------------

    entry_price: float = 0.0

    stop_loss: float = 0.0

    target_price: float = 0.0

    risk_reward: float = 0.0

    # ---------------------------------------------------------
    # Confidence
    # ---------------------------------------------------------

    confidence: float = 0.0

    score: float = 0.0

    # ---------------------------------------------------------
    # Lifecycle
    # ---------------------------------------------------------

    status: str = "WATCHING"

    created_time: str = ""

    updated_time: str = ""

    # ---------------------------------------------------------
    # Reasoning
    # ---------------------------------------------------------

    reasons: list[str] = field(
        default_factory=list
    )

    # ---------------------------------------------------------
    # Instrument information
    # ---------------------------------------------------------

    underlying_symbol: str = ""

    option_symbol: str = ""

    option_token: str = ""

    option_type: str = ""

    strike: float = 0.0

    expiry: str = ""

    # ---------------------------------------------------------
    # Execution / lifecycle tracking
    # ---------------------------------------------------------

    entry_reached: bool = False

    profit_booked: bool = False

    exit_reason: str = ""

    # ---------------------------------------------------------
    # Lifecycle prices
    # ---------------------------------------------------------

    entry_reached_price: float = 0.0

    exit_price: float = 0.0

    # ---------------------------------------------------------
    # Reversal tracking
    # ---------------------------------------------------------

    reversal_warning: bool = False

    reversal_count: int = 0

    reversal_started_time: str = ""

    # ---------------------------------------------------------
    # Monitoring
    # ---------------------------------------------------------

    last_checked_price: float = 0.0

    last_checked_time: str = ""
