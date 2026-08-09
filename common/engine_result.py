"""
============================================================

Engine Result

Standard output for every intelligence engine.

============================================================
"""

from dataclasses import dataclass, field


@dataclass(slots=True)
class EngineResult:

    engine_name: str

    signal: str

    score: float

    confidence: float

    reasons: list[str] = field(default_factory=list)

    details: dict = field(default_factory=dict)

    warnings: list[str] = field(default_factory=list)
