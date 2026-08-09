"""
============================================================

Analysis Bundle

============================================================
"""

from dataclasses import dataclass
from typing import Any
from common.analysis.feature_bundle import FeatureBundle
from dataclasses import field

@dataclass(slots=True)
class AnalysisBundle:

    market_structure: Any = None

    trend: Any = None

    volume: Any = None

    options: Any = None

    sentiment: Any = None

    risk: Any = None
    features: FeatureBundle = field(
        default_factory=FeatureBundle
    )