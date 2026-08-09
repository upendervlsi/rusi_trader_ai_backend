"""
========================================================================

Feature Store

Central repository for all calculated features.

Every feature calculator writes here.

Every evidence engine reads here.

========================================================================
"""

from __future__ import annotations

from typing import Dict
from typing import List

from intelligence.core.feature_id import FeatureId

from intelligence.models.feature_value import FeatureValue


class FeatureStore:

    """
    Stores calculated market features.
    """

    def __init__(self):

        self._features: Dict[
            FeatureId,
            FeatureValue
        ] = {}

    # -------------------------------------------------

    def add(
        self,
        feature: FeatureValue,
    ) -> None:

        self._features[
            feature.feature_id
        ] = feature

    # -------------------------------------------------

    def get(
        self,
        feature_id: FeatureId,
    ) -> FeatureValue:

        if feature_id not in self._features:

            raise KeyError(
                f"Feature not available: {feature_id}"
            )

        return self._features[
            feature_id
        ]

    # -------------------------------------------------

    def get_value(
        self,
        feature_id: FeatureId,
    ) -> float:

        return self.get(
            feature_id
        ).value

    # -------------------------------------------------

    def exists(
        self,
        feature_id: FeatureId,
    ) -> bool:

        return feature_id in self._features

    # -------------------------------------------------

    def remove(
        self,
        feature_id: FeatureId,
    ) -> None:

        self._features.pop(
            feature_id,
            None,
        )

    # -------------------------------------------------

    def clear(
        self,
    ) -> None:

        self._features.clear()

    # -------------------------------------------------

    def all(
        self,
    ) -> List[FeatureValue]:

        return list(
            self._features.values()
        )

    # -------------------------------------------------

    def count(
        self,
    ) -> int:

        return len(
            self._features
        )
    def try_get(
        self,
        feature_id: FeatureId,
    ) -> FeatureValue | None:
        """
        Return the feature if available,
        otherwise None.
        """

        return self._features.get(
            feature_id
        )
