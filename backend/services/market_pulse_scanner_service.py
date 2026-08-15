"""
============================================================
RUSI Trader AI

Market Pulse Scanner Service

Purpose
-------
Runs the independent Market Pulse Analyzer continuously in
a background thread.

IMPORTANT
---------
This service is completely separate from the trading engine.

It:

    * starts automatically with FastAPI
    * runs the existing MarketPulseAnalyzer
    * publishes results into MarketPulseRuntime
    * keeps the seven-market dashboard updated
    * does NOT place orders
    * does NOT select the execution market
    * does NOT modify TradingEngineService
    * does NOT modify RuntimeManager
    * does NOT modify portfolio positions

Scheduling
----------
A complete Market Pulse scan runs every 5 minutes.

The first scan starts immediately after the service starts.

CRUDE OIL remains WAITING because the current analyzer
deliberately does not use an MCX futures fallback.
============================================================
"""

from __future__ import annotations

import threading
import time

from common.logger import get_logger

from backend.services.market_pulse_analyzer import (
    MarketPulseAnalyzer,
)


logger = get_logger("RUSI")


class MarketPulseScannerService:

    """
    Background scheduler for Market Pulse analysis.

    Singleton behavior ensures FastAPI startup and any future
    callers cannot accidentally create multiple scanner threads.
    """

    _instance = None

    #
    # Five-minute Market Pulse refresh.
    #
    REFRESH_INTERVAL = 300

    def __new__(cls):

        if cls._instance is None:

            cls._instance = super().__new__(cls)

            cls._instance._thread = None

            cls._instance._running = False

            cls._instance._analyzer = None

        return cls._instance

    # ---------------------------------------------------------
    # Start
    # ---------------------------------------------------------

    def start(self):

        if self._running:

            logger.info(
                "Market Pulse Scanner already running."
            )

            return

        self._running = True

        #
        # Create the analyzer once.
        #
        # The analyzer itself reuses its broker session and
        # instrument master across scans.
        #

        self._analyzer = MarketPulseAnalyzer()

        self._thread = threading.Thread(

            target=self._run_scanner,

            daemon=True,

            name="MarketPulseScanner",

        )

        self._thread.start()

        logger.info(
            "Market Pulse Scanner Thread Started"
        )

    # ---------------------------------------------------------
    # Stop
    # ---------------------------------------------------------

    def stop(self):

        if not self._running:

            return

        logger.info(
            "Stopping Market Pulse Scanner..."
        )

        self._running = False

        #
        # Do not block FastAPI shutdown waiting for a broker
        # request to finish.
        #

        thread = self._thread

        if (
            thread is not None
            and thread.is_alive()
            and thread is not threading.current_thread()
        ):

            thread.join(
                timeout=2.0
            )

        self._thread = None

        logger.info(
            "Market Pulse Scanner Stopped"
        )

    # ---------------------------------------------------------
    # Status
    # ---------------------------------------------------------

    @property
    def running(self) -> bool:

        return self._running

    # ---------------------------------------------------------
    # Scanner scheduler
    # ---------------------------------------------------------

    def _run_scanner(self):

        logger.info(
            "Market Pulse Scanner Scheduler Started"
        )

        #
        # First scan happens immediately.
        #

        while self._running:

            cycle_start = time.time()

            try:

                logger.info(
                    "=============================================="
                )

                logger.info(
                    "Market Pulse Scheduled Scan Starting"
                )

                logger.info(
                    "=============================================="
                )

                if self._analyzer is None:

                    self._analyzer = (
                        MarketPulseAnalyzer()
                    )

                self._analyzer.scan()

                logger.info(
                    "Market Pulse Scheduled Scan Completed"
                )

            except Exception:

                #
                # A scanner failure must never kill the
                # background thread permanently.
                #

                logger.exception(
                    "Market Pulse Scanner Cycle Failed"
                )

            elapsed = (
                time.time()
                - cycle_start
            )

            sleep_time = max(
                0,
                self.REFRESH_INTERVAL
                - elapsed,
            )

            logger.info(
                "Next Market Pulse scan in %.1f seconds",
                sleep_time,
            )

            #
            # Sleep in one-second increments so stop()
            # remains responsive.
            #

            while (
                self._running
                and sleep_time > 0
            ):

                time.sleep(
                    min(
                        1.0,
                        sleep_time,
                    )
                )

                sleep_time -= 1.0

        logger.info(
            "Market Pulse Scanner Scheduler Stopped"
        )
