"""
============================================================
RUSI Trader AI

File    : commodity_loader.py

Purpose :
    Loads commodity definitions from YAML configuration and
    converts them into Instrument objects.

Author  : RUSI Trader AI
============================================================
"""

from pathlib import Path
from typing import Dict

import yaml

from market.instrument import Instrument


class CommodityLoader:
    """
    Loads commodity configuration.
    """

    REQUIRED_FIELDS = (
        "exchange",
        "symbol",
        "token",
        "instrument_type",
    )

    def __init__(self, config_file: str = "config/commodities.yaml"):

        self.config_file = Path(config_file)

    def load(self) -> Dict[str, Instrument]:
        """
        Load all commodities.

        Returns
        -------
        Dict[str, Instrument]
        """

        if not self.config_file.exists():
            raise FileNotFoundError(
                f"Commodity configuration not found: {self.config_file}"
            )

        with self.config_file.open("r", encoding="utf-8") as fp:
            data = yaml.safe_load(fp) or {}

        commodities = data.get("commodities", {})

        instruments: Dict[str, Instrument] = {}

        for name, cfg in commodities.items():

            self._validate(name, cfg)

            instruments[name] = Instrument(
                exchange=cfg["exchange"],
                symbol=cfg["symbol"],
                token=str(cfg["token"]),
                instrument_type=cfg["instrument_type"],
                enabled=cfg.get("enabled", True),
                default_interval=cfg.get(
                    "default_interval",
                    "ONE_MINUTE",
                ),
                lot_size=cfg.get("lot_size", 1),
                tick_size=cfg.get("tick_size", 0.05),
                expiry=cfg.get("expiry"),
                strike=cfg.get("strike"),
                option_type=cfg.get("option_type"),
                exchange_segment=cfg.get(
                    "exchange_segment",
                    cfg["exchange"],
                ),
                currency=cfg.get("currency", "INR"),
            )

        return instruments

    def _validate(self, name: str, cfg: dict) -> None:
        """
        Validate one commodity definition.
        """

        missing = []

        for field in self.REQUIRED_FIELDS:

            if field not in cfg:
                missing.append(field)

        if missing:
            raise ValueError(
                f"{name} missing required fields: "
                f"{', '.join(missing)}"
            )
