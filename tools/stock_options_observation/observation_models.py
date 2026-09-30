"""
RUSI Trader AI

Stock Options Observation Models

Stage 9

Purpose
-------
Represent one stock-options paper-trading observation.

This module is isolated from the existing NIFTY V1 trade journal.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class StockOptionObservation:
    """
    One observation of a stock-options candidate or NO_TRADE decision.
    """

    observation_id: str
    observed_at: datetime

    symbol: str
    underlying_price: float

    decision: str
    direction: str

    bullish_score: float
    bearish_score: float
    analysis_reason: str

    option_symbol: str | None = None
    option_type: str | None = None
    strike: float | None = None
    expiry: str | None = None
    token: str | None = None
    lot_size: int | None = None

    option_price: float | None = None
    quality_score: float | None = None
    quality_rank: int | None = None
    spread_percent: float | None = None
    volume: float | None = None
    open_interest: float | None = None
    volume_oi_ratio: float | None = None
    quote_completeness: float | None = None

    stop_loss: float | None = None
    target_price: float | None = None
    risk_reward_ratio: float | None = None
    maximum_loss: float | None = None
    maximum_reward: float | None = None

    metadata: dict[str, Any] = field(default_factory=dict)
