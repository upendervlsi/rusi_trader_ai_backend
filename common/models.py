"""
============================================================

rusi_trader_ai

Common Models

============================================================
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from common.enums import Recommendation


# ============================================================
# Candle
# ============================================================

@dataclass(slots=True)
class Candle:
    """
    Represents one OHLCV candle.
    """

    timestamp: datetime

    open: float
    high: float
    low: float
    close: float

    volume: float


# ============================================================
# Engine Result
# ============================================================

@dataclass(slots=True)
class EngineResult:
    """
    Standard output returned by every intelligence engine.
    """

    engine_name: str

    recommendation: Recommendation

    confidence: float

    buy_score: float = 0.0
    sell_score: float = 0.0
    wait_score: float = 0.0

    verified: bool = False

    reason: str = ""

    learning_notes: List[str] = field(default_factory=list)

    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================
# Validation Result
# ============================================================

@dataclass(slots=True)
class ValidationResult:
    """
    Common validation result used across loaders
    and verification modules.
    """

    passed: bool

    message: str = ""

    details: Dict[str, Any] = field(default_factory=dict)
