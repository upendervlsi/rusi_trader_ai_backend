"""
============================================================

RUSI Trader AI

Engine To Evidence Adapter

Converts EngineResult into Evidence

============================================================
"""

from common.engine_result import EngineResult

from intelligence.evidence.evidence import Evidence

from intelligence.signals.signal_type import SignalType

class EngineToEvidenceAdapter:

    def convert(
        self,
        provider_name: str,
        result: EngineResult,
        weight: float = 1.0,
    ) -> Evidence:

        signal = SignalType.HOLD

        #
        # Map Engine Signal
        #

        if result.signal.upper() == "BULLISH":

            signal = SignalType.BUY

        elif result.signal.upper() == "BEARISH":

            signal = SignalType.SELL

        elif result.signal.upper() == "BUY":

            signal = SignalType.BUY

        elif result.signal.upper() == "SELL":

            signal = SignalType.SELL

        return Evidence(

            provider_name=provider_name,

            feature_id=None,

            signal=signal,

            confidence=result.confidence,

            weight=weight,

            reasons=result.reasons,

            details=result.details,
        )
