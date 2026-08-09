"""
=============================================================
Market Universe Constants
=============================================================
"""

from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent

PROJECT_ROOT = PACKAGE_DIR.parent.parent

CONFIG_DIR = PROJECT_ROOT / "config"

UNIVERSE_DIR = CONFIG_DIR / "universe"

CACHE_DIR = PROJECT_ROOT / "cache"

MASTER_DIR = CACHE_DIR / "instrument_master"

MASTER_FILE = MASTER_DIR / "master.json"

MASTER_TIMESTAMP = MASTER_DIR / "timestamp.txt"

MASTER_REFRESH_HOURS = 24

EQUITY_FILE = UNIVERSE_DIR / "equity_nifty100.json"

FUTURE_FILE = UNIVERSE_DIR / "futures.json"

OPTION_FILE = UNIVERSE_DIR / "options.json"

COMMODITY_FILE = UNIVERSE_DIR / "commodities.json"

ALL_MARKET_FILE = UNIVERSE_DIR / "all_markets.json"

SUPPORTED_EXCHANGES = (
    "NSE",
    "BSE",
    "NFO",
    "MCX",
)

SUPPORTED_SEGMENTS = (
    "EQ",
    "FUT",
    "OPT",
    "COM",
)
