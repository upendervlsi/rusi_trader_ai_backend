"""
============================================================

Intelligence Result

============================================================
"""

from dataclasses import dataclass, field

from common.engine_result import EngineResult


@dataclass(slots=True)
class IntelligenceResult:

    #
    # Results from all intelligence engines
    #
    results: list[EngineResult] = field(default_factory=list)

    #
    # Statistics
    #
    successful_engines: int = 0
    failed_engines: int = 0

    #
    # Performance
    #
    execution_time_ms: float = 0.0
