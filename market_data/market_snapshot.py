"""
============================================================

Market Snapshot

============================================================
"""

from dataclasses import dataclass, field

from common.candle import Candle

from common.analysis.indicator_bundle import IndicatorBundle
from common.analysis.analysis_bundle import AnalysisBundle


@dataclass(slots=True)
class MarketSnapshot:

    candles: list[Candle]

    latest_candle: Candle

    indicators: IndicatorBundle = field(
        default_factory=IndicatorBundle
    )

    analysis: AnalysisBundle = field(
        default_factory=AnalysisBundle
    )
