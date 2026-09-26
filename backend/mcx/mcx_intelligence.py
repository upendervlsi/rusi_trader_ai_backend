from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Tuple


@dataclass
class McxIntelligenceResult:
    signal: str = "WAIT"
    qualified: int = 0
    confidence: float = 0.0

    trend: str = "NEUTRAL"
    momentum: str = "NEUTRAL"
    structure: str = "MIXED"

    vwap: str = "UNKNOWN"
    ema: str = "UNKNOWN"
    rsi: str = "UNKNOWN"
    macd: str = "UNKNOWN"

    breakout: str = "NONE"
    reversal: str = "NONE"
    volume_state: str = "UNKNOWN"
    price_action: str = "NEUTRAL"

    support: Optional[float] = None
    resistance: Optional[float] = None

    entry: Optional[float] = None
    stop_loss: Optional[float] = None
    target: Optional[float] = None
    risk_reward: Optional[float] = None

    atr: Optional[float] = None
    volume_expansion: Optional[float] = None
    price_momentum: Optional[float] = None

    evidence: List[str] = field(default_factory=list)
    reasons: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "signal": self.signal,
            "qualified": self.qualified,
            "confidence": round(float(self.confidence), 2),
            "trend": self.trend,
            "momentum": self.momentum,
            "structure": self.structure,
            "vwap": self.vwap,
            "ema": self.ema,
            "rsi": self.rsi,
            "macd": self.macd,
            "breakout": self.breakout,
            "reversal": self.reversal,
            "volume_state": self.volume_state,
            "price_action": self.price_action,
            "support": self.support,
            "resistance": self.resistance,
            "entry": self.entry,
            "stop_loss": self.stop_loss,
            "target": self.target,
            "risk_reward": (
                round(float(self.risk_reward), 2)
                if self.risk_reward is not None
                else None
            ),
            "atr": self.atr,
            "volume_expansion": self.volume_expansion,
            "price_momentum": self.price_momentum,
            "evidence": list(self.evidence),
            "reasons": list(self.reasons),
        }


class McxIntelligenceEngine:
    """
    Isolated MCX intelligence engine.

    Responsibilities:
      - Analyze MCX candles + MCX indicators.
      - Determine directional signal.
      - Determine whether that signal is qualified.
      - Calculate structure-aware risk.
      - Produce entry / SL / target / R:R.

    Non-responsibilities:
      - Order execution.
      - Portfolio management.
      - Generic NIFTY/Stock Options/Midcap logic.
      - Option selection.
    """

    MIN_CANDLES = 30

    # Qualification thresholds.
    MIN_DIRECTIONAL_SCORE = 6
    MIN_SCORE_ADVANTAGE = 2
    MIN_RISK_REWARD = 2.0

    # Volume thresholds.
    STRONG_VOLUME = 1.20
    WEAK_VOLUME = 0.80

    # Momentum threshold used by the existing MCX indicator layer.
    MOMENTUM_THRESHOLD = 0.10

    # ATR multiplier for initial protective stop.
    ATR_STOP_MULTIPLIER = 1.50

    # Structural lookbacks.
    STRUCTURE_LOOKBACK = 8
    SUPPORT_RESISTANCE_LOOKBACK = 20
    BREAKOUT_LOOKBACK = 10

    def analyze(
        self,
        candles: Sequence[Any],
        indicators: Dict[str, Any],
    ) -> McxIntelligenceResult:
        normalized = self._normalize_candles(candles)

        result = McxIntelligenceResult()

        if len(normalized) < self.MIN_CANDLES:
            result.reasons.append(
                f"INSUFFICIENT_CANDLES:{len(normalized)}"
            )
            return result

        if not indicators:
            result.reasons.append("INDICATORS_UNAVAILABLE")
            return result

        closes = [c["close"] for c in normalized]
        highs = [c["high"] for c in normalized]
        lows = [c["low"] for c in normalized]
        opens = [c["open"] for c in normalized]
        volumes = [c["volume"] for c in normalized]

        current = closes[-1]
        result.entry = current

        # ---------------------------------------------------------
        # Indicator snapshot compatibility
        # ---------------------------------------------------------
        # McxIndicatorEngine.calculate() returns the existing
        # McxIndicatorSnapshot dataclass.
        #
        # Intelligence V2 also accepts a dictionary so this layer
        # remains tolerant of future API serialization.
        # ---------------------------------------------------------

        if hasattr(indicators, "to_dict"):
            indicator_data = indicators.to_dict()
        elif isinstance(indicators, dict):
            indicator_data = indicators
        else:
            indicator_data = vars(indicators)

        ema20 = self._number(indicator_data.get("ema20"))
        ema50 = self._number(indicator_data.get("ema50"))
        vwap = self._number(indicator_data.get("vwap"))
        rsi = self._number(indicator_data.get("rsi"))
        macd = self._number(indicator_data.get("macd"))
        macd_signal = self._number(
            indicator_data.get(
                "macd_signal",
                indicator_data.get("signal"),
            )
        )
        histogram = self._number(
            indicator_data.get(
                "macd_histogram",
                indicator_data.get("histogram"),
            )
        )
        atr = self._number(indicator_data.get("atr"))
        volume_expansion = self._number(
            indicator_data.get("volume_expansion")
        )
        price_momentum = self._number(
            indicator_data.get("price_momentum")
        )

        result.atr = atr
        result.volume_expansion = volume_expansion
        result.price_momentum = price_momentum

        bullish_score = 0
        bearish_score = 0

        # ---------------------------------------------------------
        # 1. EMA trend
        # ---------------------------------------------------------
        if ema20 is not None and ema50 is not None:
            if ema20 > ema50:
                result.ema = "BULLISH_ALIGNMENT"
                result.trend = "BULLISH"
                bullish_score += 2
                result.evidence.append("EMA20_ABOVE_EMA50")
            elif ema20 < ema50:
                result.ema = "BEARISH_ALIGNMENT"
                result.trend = "BEARISH"
                bearish_score += 2
                result.evidence.append("EMA20_BELOW_EMA50")
            else:
                result.ema = "NEUTRAL_ALIGNMENT"

        # ---------------------------------------------------------
        # 2. VWAP
        # ---------------------------------------------------------
        if vwap is not None:
            if current > vwap:
                result.vwap = "ABOVE"
                bullish_score += 1
                result.evidence.append("PRICE_ABOVE_VWAP")
            elif current < vwap:
                result.vwap = "BELOW"
                bearish_score += 1
                result.evidence.append("PRICE_BELOW_VWAP")
            else:
                result.vwap = "AT_VWAP"

        # ---------------------------------------------------------
        # 3. RSI
        # ---------------------------------------------------------
        if rsi is not None:
            if rsi >= 55:
                result.rsi = "BULLISH"
                bullish_score += 1
                result.evidence.append("RSI_BULLISH")
            elif rsi <= 45:
                result.rsi = "BEARISH"
                bearish_score += 1
                result.evidence.append("RSI_BEARISH")
            else:
                result.rsi = "NEUTRAL"

        # ---------------------------------------------------------
        # 4. MACD
        #
        # Direction is based on MACD vs signal.
        # Histogram is additional confirmation.
        # We deliberately avoid calling MACD "bullish" merely because
        # it is above signal while both remain deeply negative.
        # ---------------------------------------------------------
        if macd is not None and macd_signal is not None:
            if macd > macd_signal:
                result.macd = "BULLISH"
                bullish_score += 1
                result.evidence.append("MACD_ABOVE_SIGNAL")
            elif macd < macd_signal:
                result.macd = "BEARISH"
                bearish_score += 1
                result.evidence.append("MACD_BELOW_SIGNAL")
            else:
                result.macd = "NEUTRAL"

        if histogram is not None:
            if histogram > 0:
                bullish_score += 1
                result.evidence.append("MACD_HISTOGRAM_POSITIVE")
            elif histogram < 0:
                bearish_score += 1
                result.evidence.append("MACD_HISTOGRAM_NEGATIVE")

        # ---------------------------------------------------------
        # 5. Price momentum
        # ---------------------------------------------------------
        if price_momentum is not None:
            if price_momentum >= self.MOMENTUM_THRESHOLD:
                result.momentum = "BULLISH"
                bullish_score += 1
                result.evidence.append("PRICE_MOMENTUM_POSITIVE")
            elif price_momentum <= -self.MOMENTUM_THRESHOLD:
                result.momentum = "BEARISH"
                bearish_score += 1
                result.evidence.append("PRICE_MOMENTUM_NEGATIVE")
            else:
                result.momentum = "NEUTRAL"

        # ---------------------------------------------------------
        # 6. Market structure
        # ---------------------------------------------------------
        structure, structure_score, structure_evidence = (
            self._structure(normalized)
        )

        result.structure = structure
        result.evidence.extend(structure_evidence)

        if structure_score > 0:
            bullish_score += structure_score
        elif structure_score < 0:
            bearish_score += abs(structure_score)

        # ---------------------------------------------------------
        # 7. Support / resistance
        # ---------------------------------------------------------
        support, resistance = self._support_resistance(
            highs,
            lows,
        )

        result.support = support
        result.resistance = resistance

        # ---------------------------------------------------------
        # 8. Breakout
        # ---------------------------------------------------------
        breakout = self._detect_breakout(
            closes,
            highs,
            lows,
            volume_expansion,
        )

        result.breakout = breakout

        if breakout == "BULLISH":
            bullish_score += 2
            result.evidence.append("BULLISH_BREAKOUT")
        elif breakout == "BEARISH":
            bearish_score += 2
            result.evidence.append("BEARISH_BREAKOUT")

        # ---------------------------------------------------------
        # 9. Reversal / rejection
        # ---------------------------------------------------------
        reversal = self._detect_reversal(
            opens[-1],
            highs[-1],
            lows[-1],
            closes[-1],
        )

        result.reversal = reversal

        if reversal == "BULLISH_REJECTION":
            bullish_score += 1
            result.evidence.append("BULLISH_REJECTION")
        elif reversal == "BEARISH_REJECTION":
            bearish_score += 1
            result.evidence.append("BEARISH_REJECTION")

        # ---------------------------------------------------------
        # 10. Candle / price action
        # ---------------------------------------------------------
        price_action = self._price_action(
            opens[-1],
            highs[-1],
            lows[-1],
            closes[-1],
        )

        result.price_action = price_action

        if price_action == "BULLISH_IMPULSE":
            bullish_score += 1
            result.evidence.append("BULLISH_IMPULSE_CANDLE")
        elif price_action == "BEARISH_IMPULSE":
            bearish_score += 1
            result.evidence.append("BEARISH_IMPULSE_CANDLE")

        # ---------------------------------------------------------
        # 11. Volume quality
        # ---------------------------------------------------------
        if volume_expansion is not None:
            if volume_expansion >= self.STRONG_VOLUME:
                result.volume_state = "STRONG"
                result.evidence.append("VOLUME_EXPANSION")
            elif volume_expansion >= self.WEAK_VOLUME:
                result.volume_state = "NORMAL"
                result.evidence.append("VOLUME_NORMAL")
            else:
                result.volume_state = "WEAK"
                result.reasons.append("LOW_VOLUME_CONFIRMATION")

        # ---------------------------------------------------------
        # 12. Determine raw signal
        # ---------------------------------------------------------
        if bullish_score > bearish_score and (
            bullish_score >= self.MIN_DIRECTIONAL_SCORE
        ):
            result.signal = "BUY"
        elif bearish_score > bullish_score and (
            bearish_score >= self.MIN_DIRECTIONAL_SCORE
        ):
            result.signal = "SELL"
        else:
            result.signal = "WAIT"

        dominant_score = max(bullish_score, bearish_score)
        weaker_score = min(bullish_score, bearish_score)
        score_advantage = dominant_score - weaker_score

        # ---------------------------------------------------------
        # 13. Dynamic risk
        # ---------------------------------------------------------
        if atr is not None and atr > 0:
            (
                stop_loss,
                target,
                risk_reward,
            ) = self._calculate_risk(
                signal=result.signal,
                entry=current,
                atr=atr,
                support=support,
                resistance=resistance,
            )

            result.stop_loss = stop_loss
            result.target = target
            result.risk_reward = risk_reward

        # ---------------------------------------------------------
        # 14. Confidence
        # ---------------------------------------------------------
        result.confidence = self._confidence(
            result.signal,
            dominant_score,
            score_advantage,
            result.volume_state,
            result.risk_reward,
        )

        # ---------------------------------------------------------
        # 15. Conservative qualification
        # ---------------------------------------------------------
        qualification_reasons = []

        if result.signal == "WAIT":
            qualification_reasons.append("NO_CLEAR_DIRECTION")

        if dominant_score < self.MIN_DIRECTIONAL_SCORE:
            qualification_reasons.append("DIRECTIONAL_SCORE_TOO_LOW")

        if score_advantage < self.MIN_SCORE_ADVANTAGE:
            qualification_reasons.append("DIRECTIONAL_CONFLICT")

        if atr is None or atr <= 0:
            qualification_reasons.append("ATR_UNAVAILABLE")

        if (
            result.risk_reward is None
            or result.risk_reward < self.MIN_RISK_REWARD
        ):
            qualification_reasons.append("RISK_REWARD_BELOW_2R")

        # Weak volume is now a qualification blocker.
        #
        # This is important for Crude/Silver from the real test:
        # movement alone should not turn into an executable-quality
        # MCX trade when volume confirmation is poor.
        if result.volume_state == "WEAK":
            qualification_reasons.append("WEAK_VOLUME_CONFIRMATION")

        # Require at least neutral volume.
        if result.volume_state == "UNKNOWN":
            qualification_reasons.append("VOLUME_CONFIRMATION_UNKNOWN")

        # Require trend agreement with signal.
        if result.signal == "BUY" and result.trend != "BULLISH":
            qualification_reasons.append("TREND_NOT_ALIGNED")

        if result.signal == "SELL" and result.trend != "BEARISH":
            qualification_reasons.append("TREND_NOT_ALIGNED")

        if qualification_reasons:
            result.qualified = 0
            result.reasons.extend(qualification_reasons)
        else:
            result.qualified = 1
            result.reasons.append(
                "MULTI_FACTOR_DIRECTIONAL_ALIGNMENT"
            )
            result.reasons.append("RISK_CONTROLS_PASSED")

            if result.volume_state == "STRONG":
                result.reasons.append("VOLUME_SUPPORTS_MOVE")

        return result

    # =================================================================
    # Candle normalization
    # =================================================================

    def _normalize_candles(
        self,
        candles: Sequence[Any],
    ) -> List[Dict[str, float]]:
        normalized: List[Dict[str, float]] = []

        for candle in candles or []:
            try:
                if isinstance(candle, (list, tuple)):
                    if len(candle) < 6:
                        continue

                    normalized.append(
                        {
                            "open": float(candle[1]),
                            "high": float(candle[2]),
                            "low": float(candle[3]),
                            "close": float(candle[4]),
                            "volume": float(candle[5]),
                        }
                    )
                    continue

                if isinstance(candle, dict):
                    normalized.append(
                        {
                            "open": float(candle["open"]),
                            "high": float(candle["high"]),
                            "low": float(candle["low"]),
                            "close": float(candle["close"]),
                            "volume": float(
                                candle.get("volume", 0.0)
                            ),
                        }
                    )
                    continue

                normalized.append(
                    {
                        "open": float(candle.open),
                        "high": float(candle.high),
                        "low": float(candle.low),
                        "close": float(candle.close),
                        "volume": float(
                            getattr(candle, "volume", 0.0)
                        ),
                    }
                )

            except (KeyError, TypeError, ValueError, AttributeError):
                continue

        return normalized

    # =================================================================
    # Structure
    # =================================================================

    def _structure(
        self,
        candles: Sequence[Dict[str, float]],
    ) -> Tuple[str, int, List[str]]:
        if len(candles) < self.STRUCTURE_LOOKBACK:
            return "MIXED", 0, []

        recent = candles[-self.STRUCTURE_LOOKBACK:]

        midpoint = len(recent) // 2

        first = recent[:midpoint]
        second = recent[midpoint:]

        first_high = max(c["high"] for c in first)
        second_high = max(c["high"] for c in second)

        first_low = min(c["low"] for c in first)
        second_low = min(c["low"] for c in second)

        evidence: List[str] = []

        if second_high > first_high and second_low > first_low:
            return "HH_HL", 2, ["HIGHER_HIGH_HIGHER_LOW"]

        if second_high < first_high and second_low < first_low:
            return "LH_LL", -2, ["LOWER_HIGH_LOWER_LOW"]

        # Partial directional structures are useful but weaker.
        if second_high > first_high:
            evidence.append("HIGHER_HIGH")

        if second_low > first_low:
            evidence.append("HIGHER_LOW")

        if second_high < first_high:
            evidence.append("LOWER_HIGH")

        if second_low < first_low:
            evidence.append("LOWER_LOW")

        return "MIXED", 0, evidence

    # =================================================================
    # Support / resistance
    # =================================================================

    def _support_resistance(
        self,
        highs: Sequence[float],
        lows: Sequence[float],
    ) -> Tuple[Optional[float], Optional[float]]:
        lookback = min(
            self.SUPPORT_RESISTANCE_LOOKBACK,
            len(highs),
        )

        if lookback < 2:
            return None, None

        recent_highs = highs[-lookback:]
        recent_lows = lows[-lookback:]

        return (
            min(recent_lows),
            max(recent_highs),
        )

    # =================================================================
    # Breakout
    # =================================================================

    def _detect_breakout(
        self,
        closes: Sequence[float],
        highs: Sequence[float],
        lows: Sequence[float],
        volume_expansion: Optional[float],
    ) -> str:
        if len(closes) <= self.BREAKOUT_LOOKBACK:
            return "NONE"

        previous_high = max(
            highs[-self.BREAKOUT_LOOKBACK - 1:-1]
        )
        previous_low = min(
            lows[-self.BREAKOUT_LOOKBACK - 1:-1]
        )

        current_close = closes[-1]

        volume_confirmed = (
            volume_expansion is not None
            and volume_expansion >= self.STRONG_VOLUME
        )

        if current_close > previous_high and volume_confirmed:
            return "BULLISH"

        if current_close < previous_low and volume_confirmed:
            return "BEARISH"

        return "NONE"

    # =================================================================
    # Reversal / rejection
    # =================================================================

    def _detect_reversal(
        self,
        open_price: float,
        high: float,
        low: float,
        close: float,
    ) -> str:
        candle_range = high - low

        if candle_range <= 0:
            return "NONE"

        body = abs(close - open_price)

        upper_wick = high - max(open_price, close)
        lower_wick = min(open_price, close) - low

        # Bullish rejection: large lower wick, close in upper part.
        if (
            lower_wick >= body * 1.5
            and close >= low + candle_range * 0.60
        ):
            return "BULLISH_REJECTION"

        # Bearish rejection: large upper wick, close in lower part.
        if (
            upper_wick >= body * 1.5
            and close <= low + candle_range * 0.40
        ):
            return "BEARISH_REJECTION"

        return "NONE"

    # =================================================================
    # Price action
    # =================================================================

    def _price_action(
        self,
        open_price: float,
        high: float,
        low: float,
        close: float,
    ) -> str:
        candle_range = high - low

        if candle_range <= 0:
            return "NEUTRAL"

        body = abs(close - open_price)
        body_ratio = body / candle_range

        if body_ratio < 0.60:
            return "NEUTRAL"

        if close > open_price:
            return "BULLISH_IMPULSE"

        if close < open_price:
            return "BEARISH_IMPULSE"

        return "NEUTRAL"

    # =================================================================
    # Risk
    # =================================================================

    def _calculate_risk(
        self,
        signal: str,
        entry: float,
        atr: float,
        support: Optional[float],
        resistance: Optional[float],
    ) -> Tuple[Optional[float], Optional[float], Optional[float]]:
        if signal not in ("BUY", "SELL") or atr <= 0:
            return None, None, None

        atr_distance = atr * self.ATR_STOP_MULTIPLIER

        if signal == "BUY":
            atr_stop = entry - atr_distance

            if support is not None and support < entry:
                stop_loss = max(
                    support - atr * 0.25,
                    entry - atr_distance,
                )
            else:
                stop_loss = atr_stop

            risk = entry - stop_loss

            if risk <= 0:
                return None, None, None

            structural_target = (
                resistance
                if resistance is not None and resistance > entry
                else None
            )

            two_r_target = entry + (2.0 * risk)

            if structural_target is not None:
                target = max(
                    two_r_target,
                    structural_target,
                )
            else:
                target = two_r_target

            reward = target - entry

        else:
            atr_stop = entry + atr_distance

            if resistance is not None and resistance > entry:
                stop_loss = min(
                    resistance + atr * 0.25,
                    entry + atr_distance,
                )
            else:
                stop_loss = atr_stop

            risk = stop_loss - entry

            if risk <= 0:
                return None, None, None

            structural_target = (
                support
                if support is not None and support < entry
                else None
            )

            two_r_target = entry - (2.0 * risk)

            if structural_target is not None:
                target = min(
                    two_r_target,
                    structural_target,
                )
            else:
                target = two_r_target

            reward = entry - target

        if reward <= 0:
            return (
                round(stop_loss, 4),
                round(target, 4),
                None,
            )

        risk_reward = reward / risk

        return (
            round(stop_loss, 4),
            round(target, 4),
            round(risk_reward, 4),
        )

    # =================================================================
    # Confidence
    # =================================================================

    def _confidence(
        self,
        signal: str,
        dominant_score: int,
        score_advantage: int,
        volume_state: str,
        risk_reward: Optional[float],
    ) -> float:
        if signal == "WAIT":
            return 0.0

        # Directional evidence contributes most.
        score_component = min(
            60.0,
            dominant_score * 6.0,
        )

        # Agreement between factors.
        agreement_component = min(
            20.0,
            score_advantage * 5.0,
        )

        # Volume quality.
        if volume_state == "STRONG":
            volume_component = 15.0
        elif volume_state == "NORMAL":
            volume_component = 8.0
        else:
            volume_component = 0.0

        # Risk quality.
        if risk_reward is not None:
            if risk_reward >= 3.0:
                risk_component = 10.0
            elif risk_reward >= 2.0:
                risk_component = 5.0
            else:
                risk_component = 0.0
        else:
            risk_component = 0.0

        confidence = (
            score_component
            + agreement_component
            + volume_component
            + risk_component
        )

        return min(100.0, confidence)

    # =================================================================
    # Helpers
    # =================================================================

    @staticmethod
    def _number(value: Any) -> Optional[float]:
        if value is None:
            return None

        try:
            return float(value)
        except (TypeError, ValueError):
            return None
