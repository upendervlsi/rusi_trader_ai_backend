"""
============================================================
RUSI Trader AI

Stock Options Paper Trading Scheduler

Stage 11

Purpose
-------
Runs the independent Stock Options paper-trading cycle.

The scheduler:

    * monitors an existing Stock Options paper position
    * opens a new paper position only when no position exists
    * uses StockOptionsPaperTradingService for all trading logic
    * keeps the Stock Options paper portfolio isolated
    * does NOT modify the NIFTY V1 paper-trading service

Scheduling model
----------------
When a position is open:

    * monitor the existing option every 60 seconds

When no position is open:

    * run the complete Top-3 discovery and entry scan
      every 600 seconds

This keeps position monitoring responsive without repeatedly
running the complete 210-stock discovery pipeline.

The scheduler itself does not implement trading strategy.
It delegates scanning, selection, fresh quote validation,
risk validation, execution, monitoring and persistence to
StockOptionsPaperTradingService.
============================================================
"""

from __future__ import annotations

import threading
import time
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from common.logger import get_logger

from backend.services.stock_options_paper_trading_service import (
    StockOptionsPaperTradingService,
)
from tools.scanner.stock_movement_screener import (
    StockMovementScreener,
)
from tools.stock_options_observation.observation_runner import (
    StockOptionsObservationRunner,
)


logger = get_logger("RUSI")


class StockOptionsPaperScheduler:

    """
    Background scheduler for Stock Options paper trading.

    Singleton behavior ensures that API startup and future
    callers share one scheduler instance.

    Scheduling:

        OPEN POSITION
            -> monitor every 60 seconds

        NO POSITION
            -> Top-3 discovery / entry scan every 600 seconds
    """

    _instance = None

    #
    # Entry/discovery cycle:
    # ten minutes.
    #
    ENTRY_SCAN_INTERVAL = 600

    #
    # Existing-position monitoring:
    # one minute.
    #
    POSITION_MONITOR_INTERVAL = 60

    #
    # Hard Stock Options daily cutoff.
    # 3:29 PM IST: close any open paper position
    # and prevent any new entry for the remainder
    # of the trading day.
    #
    EOD_CUTOFF_HOUR = 15
    EOD_CUTOFF_MINUTE = 29
    MARKET_TIMEZONE = ZoneInfo("Asia/Kolkata")

    def __new__(cls):

        if cls._instance is None:

            cls._instance = super().__new__(cls)

            cls._instance._thread = None
            cls._instance._running = False
            cls._instance._service = None

        return cls._instance

    # ---------------------------------------------------------
    # Start
    # ---------------------------------------------------------

    def start(self, service=None):

        if self._running:

            logger.info(
                "Stock Options Paper Scheduler already running."
            )

            return

        self._running = True

        #
        # IMPORTANT:
        # This service instance will eventually be shared with
        # the Stock Options API.
        #

        if service is not None:
            self._service = service

        elif self._service is None:
            self._service = (
                StockOptionsPaperTradingService()
            )

        self._thread = threading.Thread(

            target=self._run_scheduler,

            daemon=True,

            name="StockOptionsPaperScheduler",

        )

        self._thread.start()

        logger.info(
            "Stock Options Paper Scheduler Thread Started"
        )

    # ---------------------------------------------------------
    # Stop
    # ---------------------------------------------------------

    def stop(self):

        if not self._running:

            return

        logger.info(
            "Stopping Stock Options Paper Scheduler..."
        )

        self._running = False

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
            "Stock Options Paper Scheduler Stopped"
        )

    # ---------------------------------------------------------
    # Status
    # ---------------------------------------------------------

    @property
    def running(self) -> bool:

        return self._running

    # ---------------------------------------------------------
    # Manual cycle
    # ---------------------------------------------------------

    def run_cycle(self) -> dict:

        """
        Run exactly one Stock Options paper-trading cycle.

        This method is intentionally public so the scheduler
        can be validated manually before automatic startup.
        """

        if self._service is None:

            self._service = (
                StockOptionsPaperTradingService()
            )

        try:

            #
            # HARD DAILY EOD SAFETY BOUNDARY
            #
            # Stock Options must never carry a paper position
            # into the next trading day. Once 3:29 PM IST is
            # reached, close the existing position and block
            # all further entries for the remainder of the day.
            #
            now_ist = datetime.now(
                self.MARKET_TIMEZONE
            )

            eod_reached = (
                now_ist.hour > self.EOD_CUTOFF_HOUR
                or (
                    now_ist.hour == self.EOD_CUTOFF_HOUR
                    and now_ist.minute >= self.EOD_CUTOFF_MINUTE
                )
            )

            status = self._service.status()

            open_positions = int(
                status.get(
                    "open_positions",
                    0,
                )
                or 0
            )

            #
            # EOD CUTOFF:
            # Close any remaining Stock Options paper position
            # and do not permit a new entry today.
            #
            if eod_reached:

                if open_positions > 0:

                    logger.info(
                        "Stock Options EOD cutoff reached: "
                        "closing existing paper position at "
                        "15:29 IST."
                    )

                    close_result = (
                        self._service
                        .close_paper_position_admin()
                    )

                    logger.info(
                        "Stock Options EOD paper close completed: "
                        "success=%s action=%s symbol=%s "
                        "realized_pnl=%s",
                        close_result.get("success"),
                        close_result.get("action"),
                        close_result.get("symbol"),
                        close_result.get("realized_pnl"),
                    )

                    return {
                        "success": bool(
                            close_result.get(
                                "success",
                                False,
                            )
                        ),
                        "action": "EOD_CLOSE",
                        "result": close_result,
                    }

                logger.info(
                    "Stock Options EOD cutoff active: "
                    "no new entries permitted after 15:29 IST."
                )

                return {
                    "success": True,
                    "action": "EOD_CUTOFF",
                    "result": {
                        "message": (
                            "Stock Options trading closed for "
                            "the day after 15:29 IST."
                        ),
                    },
                }

            #
            # Existing position:
            # monitor only. Never open another position.
            #

            if open_positions > 0:

                logger.info(
                    "Stock Options Paper: "
                    "monitoring existing position."
                )

                result = (
                    self._service
                    .monitor_open_position()
                )

                return {
                    "success": bool(
                        result.get(
                            "success",
                            False,
                        )
                    ),
                    "action": "MONITOR",
                    "result": result,
                }

            #
            # No position:
            #
            # Refresh the complete dynamic Stock Options
            # observation universe before considering a new
            # paper entry. This prevents a new position from
            # being opened from stale observations.csv data.
            #
            # Existing-position monitoring above remains
            # isolated and does not trigger this full scan.
            #

            logger.info(
                "Stock Options Paper: refreshing observations "
                "before new entry."
            )

            fresh_scan_started_at = datetime.now(timezone.utc)

            movement_screener = StockMovementScreener(
                top_n=3,
                batch_size=50,
            )

            screen_result = movement_screener.screen()

            top_candidates = getattr(
                screen_result,
                "top_candidates",
                [],
            )

            top_symbols = []

            for candidate in top_candidates:

                if isinstance(candidate, dict):

                    symbol = candidate.get(
                        "symbol"
                    )

                else:

                    symbol = getattr(
                        candidate,
                        "symbol",
                        None,
                    )

                if symbol:

                    top_symbols.append(
                        str(symbol)
                        .strip()
                        .upper()
                    )

            logger.info(
                "Stock Options Top-3 screen completed: "
                "universe=%s quote_requests=%s "
                "successful_quotes=%s failed_quotes=%s "
                "top_symbols=%s",
                getattr(
                    screen_result,
                    "universe_count",
                    0,
                ),
                getattr(
                    screen_result,
                    "quote_requests",
                    0,
                ),
                getattr(
                    screen_result,
                    "successful_quotes",
                    0,
                ),
                getattr(
                    screen_result,
                    "failed_quotes",
                    0,
                ),
                top_symbols,
            )

            if not top_symbols:

                return {
                    "success": True,
                    "action": "NO_TRADE",
                    "result": {
                        "message": (
                            "Top-3 Stock Options screener "
                            "returned no symbols."
                        ),
                        "top_symbols": [],
                    },
                }

            observation_runner = StockOptionsObservationRunner(
                history_days=7,
                interval="FIVE_MINUTE",
                market_request_delay_seconds=3.0,
                option_request_delay_seconds=0.0,
            )

            observation_result = observation_runner.run(
                symbols=top_symbols
            )

            logger.info(
                "Stock Options observation refresh completed: "
                "success=%s scanned=%s successful=%s "
                "candidates=%s no_trade=%s elapsed=%.1fs",
                observation_result.success,
                observation_result.scanned_stocks,
                observation_result.successful_scans,
                observation_result.candidate_count,
                observation_result.no_trade_count,
                observation_result.elapsed_seconds,
            )

            if not observation_result.success:

                return {
                    "success": False,
                    "action": "NO_TRADE",
                    "result": {
                        "message": (
                            "Fresh Stock Options observation "
                            "refresh failed; no new paper "
                            "position will be opened."
                        ),
                        "observation_refresh": {
                            "success": False,
                            "scanned_stocks": (
                                observation_result.scanned_stocks
                            ),
                            "successful_scans": (
                                observation_result.successful_scans
                            ),
                            "failed_scans": (
                                observation_result.failed_scans
                            ),
                            "candidate_count": (
                                observation_result.candidate_count
                            ),
                            "no_trade_count": (
                                observation_result.no_trade_count
                            ),
                            "elapsed_seconds": (
                                observation_result.elapsed_seconds
                            ),
                            "errors": observation_result.errors,
                        },
                    },
                }

            #
            # Fresh observations are now persisted.
            # Reuse the existing entry/risk/quote path.
            #

            result = (
                self._service
                .paper_trade_top(
                    symbols=top_symbols,
                    minimum_observed_at=fresh_scan_started_at,
                )
            )

            return {
                "success": bool(
                    result.get(
                        "success",
                        False,
                    )
                ),
                "action": "ENTRY_SCAN",
                "result": result,
            }

        except Exception as exc:

            logger.exception(
                "Stock Options Paper Scheduler Cycle Failed"
            )

            return {
                "success": False,
                "action": "ERROR",
                "error": str(exc),
            }

    # ---------------------------------------------------------
    # Scheduler loop
    # ---------------------------------------------------------

    def _run_scheduler(self):

        logger.info(
            "Stock Options Paper Scheduler Started"
        )

        while self._running:

            cycle_start = time.time()

            try:

                logger.info(
                    "=============================================="
                )

                logger.info(
                    "Stock Options Paper Scheduled Cycle Starting"
                )

                logger.info(
                    "=============================================="
                )

                result = self.run_cycle()

                action = result.get(
                    "action"
                )

                logger.info(
                    "Stock Options Paper Cycle Completed: %s",
                    action,
                )

            except Exception:

                #
                # A single failure must never permanently
                # terminate the scheduler thread.
                #

                logger.exception(
                    "Stock Options Paper Scheduler Cycle Failed"
                )

                action = "ERROR"

            elapsed = (
                time.time()
                - cycle_start
            )

            #
            # Select the next interval based on what this
            # cycle actually did.
            #
            # MONITOR:
            #     existing position -> 60 seconds
            #
            # ENTRY_SCAN / NO_TRADE / ERROR:
            #     no open position / discovery cycle -> 600 sec
            #

            if action == "MONITOR":

                next_interval = (
                    self.POSITION_MONITOR_INTERVAL
                )

                logger.info(
                    "Stock Options open-position monitoring "
                    "interval: %s seconds",
                    next_interval,
                )

            else:

                next_interval = (
                    self.ENTRY_SCAN_INTERVAL
                )

                logger.info(
                    "Stock Options entry/discovery interval: "
                    "%s seconds",
                    next_interval,
                )

            sleep_time = max(
                0,
                next_interval
                - elapsed,
            )

            #
            # Never allow the scheduler to sleep across the
            # 15:29 IST EOD boundary while a normal trading
            # cycle is still active.
            #
            now_ist = datetime.now(
                self.MARKET_TIMEZONE
            )

            if (
                now_ist.hour < self.EOD_CUTOFF_HOUR
                or (
                    now_ist.hour == self.EOD_CUTOFF_HOUR
                    and now_ist.minute < self.EOD_CUTOFF_MINUTE
                )
            ):

                cutoff = now_ist.replace(
                    hour=self.EOD_CUTOFF_HOUR,
                    minute=self.EOD_CUTOFF_MINUTE,
                    second=0,
                    microsecond=0,
                )

                seconds_to_cutoff = (
                    cutoff - now_ist
                ).total_seconds()

                sleep_time = min(
                    sleep_time,
                    max(
                        1.0,
                        seconds_to_cutoff,
                    ),
                )

            logger.info(
                "Next Stock Options paper cycle in %.1f seconds",
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

                interval = min(
                    1.0,
                    sleep_time,
                )

                time.sleep(
                    interval
                )

                sleep_time -= interval
