"""
============================================================
RUSI Trader AI

Confidence Engine

Computes confidence score from technical indicators.
============================================================
"""

from __future__ import annotations


class ConfidenceEngine:
    """
    Computes weighted confidence scores.
    """

    def __init__(self) -> None:

        self.weights = {
            "ema_sma": 25.0,
            "rsi": 15.0,
            "macd": 20.0,
            "adx": 15.0,
            "supertrend": 15.0,
            "vwap": 10.0,
        }

    # ---------------------------------------------------------

    def calculate(
        self,
        indicators: dict[str, object],
    ) -> tuple[float, dict[str, float]]:

        score = 0.0

        breakdown: dict[str, float] = {
            "ema_sma": 0.0,
            "rsi": 0.0,
            "macd": 0.0,
            "adx": 0.0,
            "supertrend": 0.0,
            "vwap": 0.0,
        }

        ema = indicators.get("ema20")
        sma = indicators.get("sma20")
        rsi = indicators.get("rsi14")
        adx = indicators.get("adx14")
        vwap = indicators.get("vwap")
        macd = indicators.get("macd")
        supertrend = indicators.get("supertrend")

        # EMA / SMA
        if (
            ema is not None
            and sma is not None
            and ema > sma
        ):
            breakdown["ema_sma"] = self.weights["ema_sma"]

        # RSI
        if (
            rsi is not None
            and 40 <= rsi <= 65
        ):
            breakdown["rsi"] = self.weights["rsi"]

        # MACD
        if (
            isinstance(macd, dict)
            and macd.get("macd") is not None
            and macd.get("signal") is not None
            and macd["macd"] > macd["signal"]
        ):
            breakdown["macd"] = self.weights["macd"]

        # ADX
        if (
            adx is not None
            and adx >= 25
        ):
            breakdown["adx"] = self.weights["adx"]

        # SuperTrend
        if (
            isinstance(supertrend, dict)
            and supertrend.get("trend") == "UP"
        ):
            breakdown["supertrend"] = self.weights["supertrend"]

        # VWAP
        if (
            ema is not None
            and vwap is not None
            and ema >= vwap
        ):
            breakdown["vwap"] = self.weights["vwap"]

        score = sum(breakdown.values())

        return score, breakdown

    # ---------------------------------------------------------

    def __str__(self):

        return "ConfidenceEngine()"

    def __repr__(self):

        return self.__str__()
