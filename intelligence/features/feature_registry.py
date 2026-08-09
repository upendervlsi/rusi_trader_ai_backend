"""
========================================================================

Feature Registry

========================================================================
"""

from __future__ import annotations

from typing import Dict
from typing import List

from intelligence.core.feature_id import FeatureId
from intelligence.features.base_feature_calculator import (
    BaseFeatureCalculator,
)


class FeatureRegistry:
    """
    Registers feature calculators.
    """

    def __init__(self):

        self._calculators: Dict[
            FeatureId,
            BaseFeatureCalculator,
        ] = {}

    def register(
        self,
        calculator: BaseFeatureCalculator,
    ) -> None:

        feature = calculator.definition.feature_id

        if feature in self._calculators:
            raise ValueError(
                f"{feature} already registered."
            )

        self._calculators[feature] = calculator

    def get(
        self,
        feature: FeatureId,
    ) -> BaseFeatureCalculator:

        return self._calculators[feature]

    def exists(
        self,
        feature: FeatureId,
    ) -> bool:

        return feature in self._calculators

    def all(self) -> List[BaseFeatureCalculator]:

        return list(self._calculators.values())

    def count(self) -> int:

        return len(self._calculators)
