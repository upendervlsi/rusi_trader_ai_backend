"""
============================================================

Common Enums

============================================================
"""

from enum import Enum


# ============================================================
# Execution
# ============================================================

class ExecutionMode(Enum):
    LIVE = "LIVE"
    PAPER = "PAPER"
    REPLAY = "REPLAY"
    BACKTEST = "BACKTEST"


# ============================================================
# Data Sources
# ============================================================

class DataSourceType(Enum):
    NONE = "NONE"
    ANGEL = "ANGEL"
    ZERODHA = "ZERODHA"
    DHAN = "DHAN"
    CSV = "CSV"
    REPLAY = "REPLAY"


# ============================================================
# Markets
# ============================================================

class MarketType(Enum):
    EQUITY = "EQUITY"
    FUTURES = "FUTURES"
    OPTIONS = "OPTIONS"
    MCX = "MCX"
    CURRENCY = "CURRENCY"


# ============================================================
# Time Frames
# ============================================================

class TimeFrame(Enum):
    M1 = "1m"
    M3 = "3m"
    M5 = "5m"
    M15 = "15m"
    H1 = "1h"
    D1 = "1d"


# ============================================================
# Recommendations
# ============================================================

class Recommendation(Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"
    EXIT = "EXIT"
    WAIT = "WAIT"


# ============================================================
# Trend
# ============================================================

class Trend(Enum):
    BULLISH = "Bullish"
    BEARISH = "Bearish"
    SIDEWAYS = "Sideways"


# ============================================================
# Data Status
# ============================================================

class DataStatus(Enum):
    VERIFIED = "Verified"
    INVALID = "Invalid"
    MISSING = "Missing"
    DELAYED = "Delayed"
