"""
========================================================================

RUSI Trader AI

Angel One Configuration Loader

Description
-----------
Loads Angel One configuration from YAML.

========================================================================
"""

from __future__ import annotations

from pathlib import Path

import yaml

from broker.angel_one.angel_credentials import AngelCredentials


class ConfigLoader:
    """
    Loads broker configuration.
    """

    def __init__(
        self,
        config_file: str = "config/broker.yaml",
    ) -> None:

        self._config_file = Path(config_file)

    def load_credentials(
        self,
    ) -> AngelCredentials:

        if not self._config_file.exists():

            raise FileNotFoundError(
                f"Configuration file not found : {self._config_file}"
            )

        with open(
            self._config_file,
            "r",
            encoding="utf-8",
        ) as fp:

            config = yaml.safe_load(fp)

        angel = config["angel_one"]

        return AngelCredentials(
            api_key=angel["api_key"],
            client_id=angel["client_id"],
            pin=angel["pin"],
            totp_secret=angel["totp_secret"],
            vendor_code=angel.get("vendor_code", ""),
            imei=angel.get("imei", ""),
        )
