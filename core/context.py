"""
============================================================

Execution Context

============================================================
"""

from dataclasses import dataclass
from datetime import datetime, UTC


@dataclass(slots=True)
class ExecutionContext:

    started_at: datetime

    mode: str

    datasource: str

    market: str
