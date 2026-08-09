"""
============================================================

Trading Engine Service

Single entry point for starting the trading engine.

Runs the trading engine continuously in a background thread.

============================================================
"""

from __future__ import annotations

import threading
import time

from common.logger import get_logger

from config.config_manager import ConfigManager
from core.execution_manager import ExecutionManager

logger = get_logger("RUSI")
class TradingEngineService:

    _instance = None

    #
    # Seconds between execution cycles
    #
    REFRESH_INTERVAL = 60

    def __new__(cls):

        if cls._instance is None:

            cls._instance = super().__new__(cls)

            cls._instance._thread = None
            cls._instance._running = False

        return cls._instance

    # ---------------------------------------------------------
    # Start
    # ---------------------------------------------------------

    def start(self):

        if self._running:

            logger.info(
                "Trading Engine already running."
            )

            return

        self._running = True

        self._thread = threading.Thread(

            target=self._run_engine,

            daemon=True,

            name="TradingEngine",

        )

        self._thread.start()

        logger.info(
            "Trading Engine Thread Started"
        )

    # ---------------------------------------------------------
    # Stop
    # ---------------------------------------------------------

    def stop(self):

        self._running = False

    # ---------------------------------------------------------
    # Engine Scheduler
    # ---------------------------------------------------------

    def _run_engine(self):

        logger.info("Loading Configuration")

        config = ConfigManager(
            "config/application.yaml"
        ).load()

        manager = ExecutionManager(config)

        while self._running:

            cycle_start = time.time()

            try:

                logger.info("=" * 60)
                logger.info(
                    "Trading Engine Cycle Started"
                )
                logger.info("=" * 60)

                manager.run()

                logger.info(
                    "Trading Engine Cycle Completed"
                )

            except Exception:

                logger.exception(
                    "Trading Engine Cycle Failed"
                )

            elapsed = time.time() - cycle_start

            sleep_time = max(
                0,
                self.REFRESH_INTERVAL - elapsed,
            )

            logger.info(
                "Next refresh in %.1f seconds",
                sleep_time,
            )

            while (
                self._running
                and
                sleep_time > 0
            ):

                time.sleep(
                    min(1, sleep_time)
                )

                sleep_time -= 1

        logger.info(
            "Trading Engine Scheduler Stopped"
        )
