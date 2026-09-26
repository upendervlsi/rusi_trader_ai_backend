"""
RUSI Trader AI

Stock Option Quality Selector

Stage 6B

Purpose
-------
Combine the existing dynamic StockOptionSelector with the
independent StockOptionQualityAnalyzer.

The selector supplies direction-specific contracts:
    BULLISH -> CE
    BEARISH -> PE

Quality ranking is therefore performed within the supplied
direction only.

This module does not modify the existing NIFTY option path.
"""

from __future__ import annotations

from dataclasses import dataclass

from tools.market_universe.stock_option_selector import (
    StockOptionCandidate,
)
from tools.market_universe.stock_option_quality import (
    StockOptionQuality,
    StockOptionQualityAnalyzer,
)


@dataclass(slots=True)
class StockOptionQualityCandidate:
    candidate: StockOptionCandidate
    quality: StockOptionQuality


class StockOptionQualitySelector:

    def __init__(
        self,
        option_selector,
        quality_analyzer: StockOptionQualityAnalyzer | None = None,
    ):
        self._option_selector = option_selector
        self._quality_analyzer = (
            quality_analyzer
            if quality_analyzer is not None
            else StockOptionQualityAnalyzer()
        )

    def rank_candidates(
        self,
        candidates: list[StockOptionCandidate],
        quotes: dict[str, dict],
    ) -> list[StockOptionQualityCandidate]:

        if not candidates:
            return []

        qualities = []
        candidate_by_symbol = {}

        for candidate in candidates:

            raw_quote = quotes.get(candidate.option_symbol)

            if raw_quote is None:
                continue

            quality = self._quality_analyzer.analyze(
                raw_quote,
                candidate.option_symbol,
                candidate.token,
            )

            qualities.append(quality)
            candidate_by_symbol[candidate.option_symbol] = candidate

        if not qualities:
            return []

        # IMPORTANT:
        # rank() receives only the supplied direction's candidates.
        ranked = self._quality_analyzer.rank(qualities)

        return [
            StockOptionQualityCandidate(
                candidate=candidate_by_symbol[item.option_symbol],
                quality=item,
            )
            for item in ranked
            if item.option_symbol in candidate_by_symbol
        ]

    def select_best(
        self,
        symbol: str,
        direction: str,
        underlying_price: float,
        quotes: dict[str, dict],
    ) -> StockOptionQualityCandidate | None:

        candidates = self._option_selector.select(
            symbol=symbol,
            direction=direction,
            underlying_price=underlying_price,
        )

        ranked = self.rank_candidates(
            candidates=candidates,
            quotes=quotes,
        )

        if not ranked:
            return None

        return ranked[0]
