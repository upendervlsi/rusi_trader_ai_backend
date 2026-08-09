"""
============================================================

Position Status

============================================================
"""

from enum import Enum


class PositionStatus(Enum):

    OPEN = "OPEN"

    CLOSED = "CLOSED"

    CANCELLED = "CANCELLED"
