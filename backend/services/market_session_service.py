"""
============================================================

RUSI Trader AI

Market Session Service

Determines whether a market is currently open based on
config/market_sessions.yaml.

This is the single source of truth for market session state.

============================================================
"""

from __future__ import annotations

from datetime import datetime, time
from pathlib import Path
from zoneinfo import ZoneInfo

import yaml


class MarketSessionService:

    _instance = None

    def __new__(cls):

        if cls._instance is None:

            cls._instance = super().__new__(cls)

            cls._instance._config = (
                cls._instance._load_config()
            )

        return cls._instance

    # ---------------------------------------------------------
    # Configuration
    # ---------------------------------------------------------

    @staticmethod
    def _load_config():

        config_file = (
            Path(__file__).resolve().parents[2]
            / "config"
            / "market_sessions.yaml"
        )

        with config_file.open(
            "r",
            encoding="utf-8",
        ) as fp:

            return yaml.safe_load(fp)

    # ---------------------------------------------------------
    # Public
    # ---------------------------------------------------------

    def is_market_open(
        self,
        exchange: str,
        now: datetime | None = None,
    ) -> bool:

        exchange = exchange.upper()

        market_config = (
            self._config
            .get("markets", {})
            .get(exchange)
        )

        if not market_config:

            return False

        if not market_config.get(
            "enabled",
            False,
        ):

            return False

        timezone_name = market_config.get(
            "timezone",
            "Asia/Kolkata",
        )

        timezone = ZoneInfo(
            timezone_name
        )

        if now is None:

            now = datetime.now(
                timezone
            )

        else:

            if now.tzinfo is None:

                now = now.replace(
                    tzinfo=timezone
                )

            else:

                now = now.astimezone(
                    timezone
                )

        # -----------------------------------------------------
        # Weekend
        # -----------------------------------------------------

        if now.weekday() >= 5:

            return False

        current_time = now.time()

        # -----------------------------------------------------
        # Sessions
        # -----------------------------------------------------

        sessions = market_config.get(
            "sessions",
            [],
        )

        for session in sessions:

            open_time = self._parse_time(
                session["open"]
            )

            close_time = self._parse_time(
                session["close"]
            )

            if (
                open_time
                <= current_time
                <= close_time
            ):

                return True

        return False

    # ---------------------------------------------------------
    # Status
    # ---------------------------------------------------------

    def get_market_status(
        self,
        exchange: str,
        now: datetime | None = None,
    ) -> str:

        if self.is_market_open(
            exchange,
            now,
        ):

            return "OPEN"

        return "CLOSED"

    # ---------------------------------------------------------
    # Time Parser
    # ---------------------------------------------------------

    @staticmethod
    def _parse_time(
        value: str,
    ) -> time:

        hour, minute = (
            int(part)
            for part in value.split(":")
        )

        return time(
            hour=hour,
            minute=minute,
        )
