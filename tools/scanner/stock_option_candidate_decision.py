"""
========================================================================

RUSI Trader AI

Stock Option Candidate Decision

Stage 6
-------
Combines:

    StockBullBearAnalysis
            ↓
    BULLISH / BEARISH / NO_TRADE
            ↓
    StockOptionQualitySelector
            ↓
    Final stock-option candidate

This module is isolated from the NIFTY V1 runtime.

It does not:
    - modify NIFTY logic
    - fetch market data
    - place orders
    - hardcode stocks
    - hardcode strikes
    - hardcode expiries
    - impose profitability thresholds

========================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field

from tools.scanner.stock_bull_bear_analyzer import (
    StockBullBearAnalysis,
)
from tools.market_universe.stock_option_quality_selector import (
    StockOptionQualityCandidate,
)


@dataclass(slots=True)
class StockOptionCandidateDecision:
    """
    Final stock-option candidate decision.
    """

    symbol: str
    decision: str
    direction: str
    underlying_price: float

    bullish_score: float
    bearish_score: float
    analysis_reason: str

    candidate: StockOptionQualityCandidate | None = None

    metadata: dict = field(default_factory=dict)


class StockOptionCandidateDecisionEngine:
    """
    Stage-6 final candidate decision layer.

    The engine joins stock-level directional analysis with
    direction-specific option quality selection.
    """

    def __init__(
        self,
        quality_selector,
    ) -> None:

        if quality_selector is None:
            raise ValueError(
                "StockOptionQualitySelector is required."
            )

        self._quality_selector = quality_selector

    def decide(
        self,
        analysis: StockBullBearAnalysis,
        underlying_price: float,
        quotes: dict[str, dict],
    ) -> StockOptionCandidateDecision:

        if analysis is None:
            raise ValueError(
                "Stock bull/bear analysis is required."
            )

        if not analysis.symbol:
            raise ValueError(
                "Stock symbol is required."
            )

        if underlying_price <= 0:
            raise ValueError(
                "Underlying price must be positive."
            )

        if quotes is None:
            quotes = {}

        direction = analysis.direction

        # ------------------------------------------------------------
        # No directional setup
        # ------------------------------------------------------------

        if direction == "NO_TRADE":

            return StockOptionCandidateDecision(
                symbol=analysis.symbol,
                decision="NO_TRADE",
                direction=direction,
                underlying_price=float(
                    underlying_price
                ),
                bullish_score=analysis.bullish_score,
                bearish_score=analysis.bearish_score,
                analysis_reason=analysis.reason,
                candidate=None,
                metadata={
                    "reason": analysis.reason,
                    "quote_count": len(quotes),
                },
            )

        # ------------------------------------------------------------
        # Direction-specific option selection
        #
        # BULLISH -> CE
        # BEARISH -> PE
        #
        # The quality selector already owns this mapping through
        # StockOptionSelector.
        # ------------------------------------------------------------

        selected = self._quality_selector.select_best(
            symbol=analysis.symbol,
            direction=direction,
            underlying_price=float(
                underlying_price
            ),
            quotes=quotes,
        )

        # ------------------------------------------------------------
        # Directional setup exists, but no usable option quote
        # ------------------------------------------------------------

        if selected is None:

            return StockOptionCandidateDecision(
                symbol=analysis.symbol,
                decision="NO_TRADE",
                direction=direction,
                underlying_price=float(
                    underlying_price
                ),
                bullish_score=analysis.bullish_score,
                bearish_score=analysis.bearish_score,
                analysis_reason=analysis.reason,
                candidate=None,
                metadata={
                    "reason": (
                        "No valid option candidate with "
                        "available quote data"
                    ),
                    "quote_count": len(quotes),
                },
            )

        # ------------------------------------------------------------
        # Valid stock-option candidate
        # ------------------------------------------------------------

        candidate = selected.candidate
        quality = selected.quality

        return StockOptionCandidateDecision(
            symbol=analysis.symbol,
            decision="CANDIDATE",
            direction=direction,
            underlying_price=float(
                underlying_price
            ),
            bullish_score=analysis.bullish_score,
            bearish_score=analysis.bearish_score,
            analysis_reason=analysis.reason,
            candidate=selected,
            metadata={
                "option_symbol": candidate.option_symbol,
                "token": candidate.token,
                "exchange": candidate.exchange,
                "strike": candidate.strike,
                "expiry": candidate.expiry,
                "option_type": candidate.option_type,
                "lot_size": candidate.lot_size,
                "distance_percent": candidate.distance_percent,
                "quality_score": quality.quality_score,
                "quality_rank": quality.rank,
                "spread_percent": quality.spread_percent,
                "volume": quality.volume,
                "open_interest": quality.open_interest,
                "volume_oi_ratio": quality.volume_oi_ratio,
                "quote_completeness": quality.quote_completeness,
                "quote_components": quality.components,
            },
        )
