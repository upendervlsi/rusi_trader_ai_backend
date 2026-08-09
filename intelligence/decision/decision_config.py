"""
========================================================================

Decision Configuration

========================================================================
"""

from dataclasses import dataclass
from dataclasses import field

from intelligence.core.feature_id import FeatureId


@dataclass(frozen=True, slots=True)
class DecisionConfig:

    buy_threshold: float = 0.30

    sell_threshold: float = -0.30

    feature_weights: dict = field(
        default_factory=lambda: {

            FeatureId.MACD: 4.0,

            FeatureId.RSI_14: 2.0,

        }
    )
