"""
============================================================
RUSI Trader AI

Scanner Configuration

Central configuration used by all scanner implementations.
============================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class ScannerConfig:
    """
    Global scanner configuration.
    """

    enabled: bool = True

    max_candidates: int = 100

    confidence_threshold: float = 0.60

    score_threshold: float = 0.50

    parallel_scanners: bool = True

    enable_multi_timeframe: bool = True

    enable_evidence_collection: bool = True

    enable_ai_ranking: bool = True

    allow_partial_results: bool = False

    scan_timeout_seconds: int = 30

    metadata: dict[str, object] = field(default_factory=dict)
