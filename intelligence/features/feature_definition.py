"""
========================================================================

RUSI Trader AI

Feature Definition

Metadata describing one feature calculator.

========================================================================
"""

from dataclasses import dataclass
from typing import Tuple

from intelligence.core.feature_id import FeatureId


@dataclass(frozen=True, slots=True)
class FeatureDefinition:
    """
    Describes one calculated feature.
    """

    feature_id: FeatureId

    name: str

    category: str

    description: str

    version: str

    dependencies: Tuple[FeatureId, ...] = ()
