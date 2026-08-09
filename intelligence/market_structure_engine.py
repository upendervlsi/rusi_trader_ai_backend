"""
============================================================

Market Structure Engine

============================================================
"""

from common.engine_result import EngineResult
import inspect

print("=" * 60)
print("EngineResult Class :", EngineResult)
print("Module             :", EngineResult.__module__)
print("File               :", inspect.getfile(EngineResult))
print("Annotations        :", EngineResult.__annotations__)
print("=" * 60)

from common.market_structure import MarketStructure

from intelligence.base_engine import BaseEngine


class MarketStructureEngine(BaseEngine):

    def verify(self, snapshot):

        return len(snapshot.candles) >= 4

    def analyze(self, snapshot):

        if not self.verify(snapshot):

            return EngineResult(
                engine_name="Market Structure",
                signal="UNKNOWN",
                score=0.0,
                confidence=0.0,
                reasons=["Not enough candles"],
            )

        candles = snapshot.candles

        c1 = candles[-4]
        c2 = candles[-3]
        c3 = candles[-2]
        c4 = candles[-1]

        structure = MarketStructure()

        structure.higher_high = c4.high > c3.high
        structure.higher_low = c4.low > c3.low

        structure.lower_high = c4.high < c3.high
        structure.lower_low = c4.low < c3.low

        if structure.higher_high and structure.higher_low:

            structure.trend = "BULLISH"

        elif structure.lower_high and structure.lower_low:

            structure.trend = "BEARISH"

        else:

            structure.trend = "SIDEWAYS"

        return EngineResult(

            engine_name="Market Structure",

            signal=structure.trend,

            score=100.0,

            confidence=100.0,

            reasons=[

                f"Higher High : {structure.higher_high}",

                f"Higher Low  : {structure.higher_low}",

                f"Lower High  : {structure.lower_high}",

                f"Lower Low   : {structure.lower_low}",

            ],

            details={
                "structure": structure,
            },
        )
