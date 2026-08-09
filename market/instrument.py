"""
============================================================
RUSI Trader AI

File    : instrument.py

Purpose :
    Generic trading instrument definition used throughout
    the RUSI trading framework.

Author  : RUSI Trader AI
============================================================
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class Instrument:
    """
    Generic tradable instrument.

    This class represents any instrument supported by RUSI.

    Examples
    --------
    - NSE Equity
    - MCX Commodity
    - NFO Future
    - NFO Option
    - ETF
    - Currency

    This object should remain broker-independent.
    """

    # -----------------------------------------
    # Market Information
    # -----------------------------------------

    exchange: str
    symbol: str
    token: str

    # -----------------------------------------
    # Instrument Type
    # -----------------------------------------

    instrument_type: str

    # Examples:
    # EQUITY
    # FUTURE
    # OPTION
    # COMMODITY
    # ETF

    # -----------------------------------------
    # Trading Configuration
    # -----------------------------------------

    enabled: bool = True

    default_interval: str = "ONE_MINUTE"

    # -----------------------------------------
    # Optional Metadata
    # -----------------------------------------

    lot_size: int = 1

    tick_size: float = 0.05

    expiry: Optional[str] = None

    strike: Optional[float] = None

    option_type: Optional[str] = None

    # CE / PE

    exchange_segment: Optional[str] = None

    # NSE
    # NFO
    # MCX
    # CDS

    currency: str = "INR"

    # -----------------------------------------
    # Utility
    # -----------------------------------------

    def display_name(self) -> str:
        """
        Returns a human-readable instrument name.
        """

        return f"{self.exchange}:{self.symbol}"

    def is_option(self) -> bool:
        return self.instrument_type.upper() == "OPTION"

    def is_future(self) -> bool:
        return self.instrument_type.upper() == "FUTURE"

    def is_equity(self) -> bool:
        return self.instrument_type.upper() == "EQUITY"

    def is_commodity(self) -> bool:
        return self.instrument_type.upper() == "COMMODITY"

    def is_etf(self) -> bool:
        return self.instrument_type.upper() == "ETF"

    def __str__(self) -> str:
        return (
            f"Instrument("
            f"{self.display_name()}, "
            f"type={self.instrument_type}, "
            f"enabled={self.enabled})"
        )
