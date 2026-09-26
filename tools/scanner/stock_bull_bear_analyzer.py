"""
========================================================================

RUSI Trader AI

Stock Bull/Bear Analyzer

Stage 5
-------
Analyzes an individual stock underlying using the existing feature
engine and compatible evidence providers.

This module is isolated from the NIFTY V1 runtime.

========================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field

from intelligence.evidence.evidence import Evidence
from intelligence.evidence.evidence_context import EvidenceContext
from intelligence.evidence.providers.ema_evidence_provider import (
    EMAEvidenceProvider,
)
from intelligence.evidence.providers.macd_evidence_provider import (
    MACDEvidenceProvider,
)
from intelligence.evidence.providers.rsi_evidence_provider import (
    RSIEvidenceProvider,
)
from intelligence.features.feature_registry import FeatureRegistry
from intelligence.features.ema.ema_calculator import EMACalculator
from intelligence.features.macd.macd_calculator import MACDCalculator
from intelligence.features.rsi.rsi_calculator import RSICalculator
from intelligence.features.feature_engine import FeatureEngine
from intelligence.core.feature_id import FeatureId
from intelligence.models.market_series import MarketSeries
from intelligence.signals.signal_type import SignalType


@dataclass(slots=True)
class StockBullBearAnalysis:
    """
    Result of stock-level bullish/bearish analysis.
    """

    symbol: str
    direction: str
    bullish_score: float
    bearish_score: float
    evidence_count: int
    bullish_evidence: list[Evidence] = field(default_factory=list)
    bearish_evidence: list[Evidence] = field(default_factory=list)
    neutral_evidence: list[Evidence] = field(default_factory=list)
    features: dict[str, float] = field(default_factory=dict)
    reason: str = ""


class StockBullBearAnalyzer:
    """
    Stage-5 stock underlying analyzer.

    Uses the existing FeatureEngine and the existing EMA, MACD and RSI
    evidence providers without modifying them.
    """

    def __init__(
        self,
        feature_engine: FeatureEngine | None = None,
    ) -> None:

        if feature_engine is not None:

            self._feature_engine = feature_engine

        else:

            registry = FeatureRegistry()

            registry.register(
                EMACalculator(
                    20,
                    FeatureId.EMA_20,
                )
            )

            registry.register(
                EMACalculator(
                    50,
                    FeatureId.EMA_50,
                )
            )

            registry.register(
                RSICalculator()
            )

            registry.register(
                MACDCalculator()
            )

            self._feature_engine = FeatureEngine(
                registry
            )

        self._providers = (
            EMAEvidenceProvider(),
            MACDEvidenceProvider(),
            RSIEvidenceProvider(),
        )

    def analyze(
        self,
        symbol: str,
        series: MarketSeries,
    ) -> StockBullBearAnalysis:
        """
        Analyze one stock underlying.
        """

        if not symbol:
            raise ValueError(
                "Stock symbol is required."
            )

        if series is None or series.is_empty():
            raise ValueError(
                f"MarketSeries is empty for {symbol}."
            )

        series.validate()

        feature_store = (
            self._feature_engine.calculate(
                series
            )
        )

        context = EvidenceContext()

        for provider in self._providers:

            try:
                provider.generate(
                    feature_store,
                    context,
                )
            except KeyError:
                # A provider may require a feature that is unavailable
                # because there is insufficient historical data.
                continue

        bullish = [
            evidence
            for evidence in context.evidences
            if evidence.signal
            in (
                SignalType.BUY,
                SignalType.STRONG_BUY,
            )
        ]

        bearish = [
            evidence
            for evidence in context.evidences
            if evidence.signal
            in (
                SignalType.SELL,
                SignalType.STRONG_SELL,
            )
        ]

        neutral = [
            evidence
            for evidence in context.evidences
            if evidence.signal == SignalType.HOLD
        ]

        bullish_score = self._score(
            bullish
        )

        bearish_score = self._score(
            bearish
        )

        direction, reason = (
            self._determine_direction(
                bullish_score=bullish_score,
                bearish_score=bearish_score,
                evidence_count=context.count,
            )
        )

        features = {
            feature.feature_id.value: float(
                feature.value
            )
            for feature in feature_store.all()
            if feature.valid
        }

        return StockBullBearAnalysis(
            symbol=symbol,
            direction=direction,
            bullish_score=bullish_score,
            bearish_score=bearish_score,
            evidence_count=context.count,
            bullish_evidence=bullish,
            bearish_evidence=bearish,
            neutral_evidence=neutral,
            features=features,
            reason=reason,
        )

    @staticmethod
    def _score(
        evidences: list[Evidence],
    ) -> float:
        """
        Convert provider confidence values into a normalized
        aggregate score.

        Existing providers currently express confidence on a
        0-100 scale, despite the Evidence documentation describing
        a 0-1 range. Normalize without changing the providers.
        """

        total = 0.0

        for evidence in evidences:

            confidence = float(
                evidence.confidence
            )

            if confidence > 1.0:
                confidence /= 100.0

            confidence = max(
                0.0,
                min(
                    confidence,
                    1.0,
                ),
            )

            total += confidence

        return round(
            total,
            4,
        )

    @staticmethod
    def _determine_direction(
        bullish_score: float,
        bearish_score: float,
        evidence_count: int,
    ) -> tuple[str, str]:

        if evidence_count == 0:

            return (
                "NO_TRADE",
                "Insufficient analytical evidence",
            )

        if bullish_score > bearish_score:

            return (
                "BULLISH",
                "Bullish evidence is stronger than bearish evidence",
            )

        if bearish_score > bullish_score:

            return (
                "BEARISH",
                "Bearish evidence is stronger than bullish evidence",
            )

        return (
            "NO_TRADE",
            "Bullish and bearish evidence are balanced",
        )
