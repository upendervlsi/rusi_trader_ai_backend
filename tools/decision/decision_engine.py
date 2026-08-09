"""
============================================================
RUSI Trader AI

Decision Engine

Converts indicator values into trading decisions.
============================================================
"""

from __future__ import annotations

from tools.decision.decision_models import (
    DecisionResult,
    IndicatorSnapshot,
    SignalStrength,
    TradeSignal,
)
from tools.indicators.indicator_engine import IndicatorEngine
from tools.scanner.market_data_models import MarketData


class DecisionEngine:
    """
    Initial rule-based decision engine.
    """

    def __init__(self) -> None:

        self._indicator_engine = IndicatorEngine()

    # ---------------------------------------------------------

    def evaluate(
        self,
        market_data: MarketData,
    ) -> DecisionResult:

        indicators = self._indicator_engine.compute(
            market_data
        )

        ema = indicators.get("ema20")
        sma = indicators.get("sma20")
        rsi = indicators.get("rsi14")

        signal = TradeSignal.HOLD
        confidence = 50.0
        strength = SignalStrength.MEDIUM
        reasons: list[str] = []

        if (
            ema is not None
            and sma is not None
            and rsi is not None
        ):

            if ema > sma and rsi < 70:

                signal = TradeSignal.BUY
                confidence = 80.0
                strength = SignalStrength.STRONG

                reasons.append(
                    "EMA is above SMA."
                )

                reasons.append(
                    "RSI is below overbought level."
                )

            elif ema < sma and rsi > 30:

                signal = TradeSignal.SELL
                confidence = 80.0
                strength = SignalStrength.STRONG

                reasons.append(
                    "EMA is below SMA."
                )

                reasons.append(
                    "RSI is above oversold level."
                )

            else:

                reasons.append(
                    "Indicators do not provide a clear signal."
                )

        result = DecisionResult(
            symbol=market_data.symbol,
            signal=signal,
            confidence=confidence,
            strength=strength,
            indicators=IndicatorSnapshot(
                values=indicators
            ),
        )

        for reason in reasons:
            result.add_reason(reason)

        return result

    # ---------------------------------------------------------

    def __str__(self):

        return "DecisionEngine()"

    def __repr__(self):

        return self.__str__()
