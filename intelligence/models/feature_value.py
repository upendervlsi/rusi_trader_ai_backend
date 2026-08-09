"""
========================================================================

Feature Value

Represents one calculated feature.

========================================================================
"""

from dataclasses import dataclass
from datetime import datetime

from intelligence.core.feature_id import FeatureId


@dataclass(frozen=True, slots=True)
class FeatureValue:

    feature_id: FeatureId

    value: float

    timestamp: datetime

    calculator: str

    version: str

    valid: bool = True
