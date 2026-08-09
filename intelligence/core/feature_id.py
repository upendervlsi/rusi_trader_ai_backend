"""
========================================================================

RUSI Trader AI

Feature Identifiers

Description:
    Defines all supported feature identifiers used throughout
    the intelligence framework.

========================================================================
"""

from enum import Enum


class FeatureId(str, Enum):

    # -------------------------------------------------
    # Raw Price
    # -------------------------------------------------

    OPEN = "OPEN"
    HIGH = "HIGH"
    LOW = "LOW"
    CLOSE = "CLOSE"
    LTP = "LTP"

    # -------------------------------------------------
    # Moving Averages
    # -------------------------------------------------

    EMA_5 = "EMA_5"
    EMA_9 = "EMA_9"
    EMA_20 = "EMA_20"
    EMA_50 = "EMA_50"
    EMA_100 = "EMA_100"
    EMA_200 = "EMA_200"

    SMA_20 = "SMA_20"
    SMA_50 = "SMA_50"
    SMA_200 = "SMA_200"

    VWAP = "VWAP"

    # -------------------------------------------------
    # Momentum
    # -------------------------------------------------

    RSI_14 = "RSI_14"

    MACD = "MACD"
    MACD_SIGNAL = "MACD_SIGNAL"
    MACD_HISTOGRAM = "MACD_HISTOGRAM"

    STOCHASTIC_K = "STOCHASTIC_K"
    STOCHASTIC_D = "STOCHASTIC_D"

    ROC = "ROC"

    CCI = "CCI"

    MFI = "MFI"

    # -------------------------------------------------
    # Trend
    # -------------------------------------------------

    ADX_14 = "ADX_14"

    PLUS_DI = "PLUS_DI"

    MINUS_DI = "MINUS_DI"

    # -------------------------------------------------
    # Volatility
    # -------------------------------------------------
    TRUE_RANGE = "TRUE_RANGE"
    ATR_14 = "ATR_14"

    BOLLINGER_UPPER = "BOLLINGER_UPPER"

    BOLLINGER_MIDDLE = "BOLLINGER_MIDDLE"

    BOLLINGER_LOWER = "BOLLINGER_LOWER"

    # -------------------------------------------------
    # Volume
    # -------------------------------------------------

    VOLUME = "VOLUME"
    AVG_VOLUME_20 = "AVG_VOLUME_20"
    OBV = "OBV"

    VOLUME_RATIO = "VOLUME_RATIO"

    # -------------------------------------------------
    # Open Interest
    # -------------------------------------------------

    OPEN_INTEREST = "OPEN_INTEREST"

    OI_CHANGE = "OI_CHANGE"

    PCR = "PCR"

    MAX_PAIN = "MAX_PAIN"

    CLOSE_PRICE = "CLOSE_PRICE"

