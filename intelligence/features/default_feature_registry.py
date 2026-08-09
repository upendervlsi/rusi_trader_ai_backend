"""
========================================================================

RUSI Trader AI

Default Feature Registry

Creates the default FeatureRegistry used by runtime.

========================================================================
"""

from intelligence.core.feature_id import FeatureId

from intelligence.features.feature_registry import FeatureRegistry

from intelligence.features.atr.atr_calculator import ATRCalculator
from intelligence.features.rsi.rsi_calculator import RSICalculator
from intelligence.features.sma.sma_calculator import SMACalculator
from intelligence.features.ema.ema_calculator import EMACalculator
from intelligence.features.macd.macd_calculator import MACDCalculator
from intelligence.features.price_change.price_change_calculator import (
    PriceChangeCalculator,
)
from intelligence.features.gain_loss.gain_loss_calculator import (
    GainLossCalculator,
)
from intelligence.features.true_range.true_range_calculator import (
    TrueRangeCalculator,
)


def create_default_feature_registry() -> FeatureRegistry:
    registry = FeatureRegistry()

    # SMA
    registry.register(SMACalculator(20, FeatureId.SMA_20))
    registry.register(SMACalculator(50, FeatureId.SMA_50))
    registry.register(SMACalculator(200, FeatureId.SMA_200))

    # EMA
    registry.register(EMACalculator(5, FeatureId.EMA_5))
    registry.register(EMACalculator(9, FeatureId.EMA_9))
    registry.register(EMACalculator(20, FeatureId.EMA_20))
    registry.register(EMACalculator(50, FeatureId.EMA_50))
    registry.register(EMACalculator(100, FeatureId.EMA_100))
    registry.register(EMACalculator(200, FeatureId.EMA_200))

    # RSI
    registry.register(RSICalculator())

    # ATR
    registry.register(ATRCalculator())

    # MACD
    registry.register(MACDCalculator())

    # Other Features
    registry.register(TrueRangeCalculator())
    #registry.register(PriceChangeCalculator())
    #registry.register(GainLossCalculator())

    return registry
