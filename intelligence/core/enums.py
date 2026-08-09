"""
========================================================================

RUSI Trader AI

File:
    intelligence/core/enums.py

Description:
    Common enumerations shared across the entire intelligence framework.

========================================================================
"""

from enum import Enum


class Exchange(str, Enum):
    NSE = "NSE"
    BSE = "BSE"
    NFO = "NFO"
    MCX = "MCX"
    CDS = "CDS"


class InstrumentType(str, Enum):
    EQUITY = "EQUITY"
    FUTURE = "FUTURE"
    OPTION = "OPTION"
    COMMODITY = "COMMODITY"
    ETF = "ETF"
    INDEX = "INDEX"


class OptionType(str, Enum):
    CALL = "CALL"
    PUT = "PUT"


class CandleInterval(str, Enum):
    M1 = "1MIN"
    M3 = "3MIN"
    M5 = "5MIN"
    M10 = "10MIN"
    M15 = "15MIN"
    M30 = "30MIN"
    H1 = "1HOUR"
    H2 = "2HOUR"
    H4 = "4HOUR"
    DAY = "1DAY"


class MarketDirection(str, Enum):
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"


class DecisionAction(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"
    WAIT = "WAIT"
    EXIT = "EXIT"
    ADD_POSITION = "ADD_POSITION"
    REDUCE_POSITION = "REDUCE_POSITION"
    NO_TRADE = "NO_TRADE"


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    EXTREME = "EXTREME"


class QualityGrade(str, Enum):
    A_PLUS = "A+"
    A = "A"
    B = "B"
    C = "C"
    D = "D"
