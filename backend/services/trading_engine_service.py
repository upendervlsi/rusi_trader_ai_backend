"""
============================================================

Trading Engine Service

Single entry point for starting the trading engine.

Runs the trading engine continuously in a background thread.

Multi-market orchestration:
    - NIFTY_FNO
    - MIDCPNIFTY_FNO

IMPORTANT:
    Existing NIFTY execution logic is preserved.
    MIDCAP runs through a separate ExecutionManager instance.

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

    #
    # Markets owned by the scheduler.
    #
    # NIFTY is kept as the existing/default path.
    # MIDCAP is an isolated sibling execution path.
    #
    ENGINE_MARKETS = (
        "NIFTY_FNO",
        "MIDCPNIFTY_FNO",
    )

    def __new__(cls):

        if cls._instance is None:

            cls._instance = super().__new__(cls)

            cls._instance._thread = None
            cls._instance._running = False

            #
            # Existing NIFTY manager reference.
            #
            # Keep this attribute for backward compatibility with
            # existing API/runtime code.
            #
            cls._instance._manager = None

            #
            # New isolated multi-market manager registry.
            #
            cls._instance._managers = {}

            #
            # Existing runtime market selection compatibility.
            #
            cls._instance._selected_market = None

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
    # NIFTY Real Trading Manager Access
    # ---------------------------------------------------------

    def get_nifty_manager(self):
        """
        Return the existing NIFTY ExecutionManager.

        This accessor never creates a new manager.
        """

        return self._manager

    # ---------------------------------------------------------
    # Runtime Market Selection
    # ---------------------------------------------------------

    def select_market(
        self,
        market_name: str,
    ):
        """
        Select the logical market for the requested market path.

        Backward compatibility:
            - NIFTY selection continues to use the existing
              _manager reference.
            - MIDCAP selection is routed only to the isolated
              MIDCAP ExecutionManager.

        This method does NOT change trading strategy logic.
        """

        if not market_name:
            raise ValueError(
                "Market name cannot be empty."
            )

        self._selected_market = market_name

        logger.info(
            "Runtime Market Selection : %s",
            market_name,
        )

        #
        # If the requested market manager already exists,
        # synchronize only that manager.
        #
        manager = self._managers.get(market_name)

        if manager is not None:

            instrument = manager.select_market(
                market_name
            )

            #
            # Preserve the historical _manager reference for NIFTY.
            #
            if market_name == "NIFTY_FNO":
                self._manager = manager

            return instrument

        #
        # Engine may not have initialized yet.
        #
        # Store the selection and let the engine apply it when
        # the corresponding manager is created.
        #
        from config.watchlist.watchlist_manager import (
            WatchlistManager,
        )

        watchlist = WatchlistManager()

        return watchlist.get(
            market_name
        )

    # ---------------------------------------------------------
    # Manager Creation
    # ---------------------------------------------------------

    def _create_manager(
        self,
        config,
        market_name: str,
    ):
        """
        Create one isolated ExecutionManager for one logical market.

        Each market receives its own ExecutionManager instance.

        NIFTY and MIDCAP therefore do not share:
            - Watchlist selection
            - Broker manager
            - Position manager
            - execution pipeline state

        Shared singleton services, where already designed as
        singletons by the existing architecture, remain untouched.
        """

        logger.info(
            "Creating ExecutionManager : %s",
            market_name,
        )

        manager = ExecutionManager(
            config,
            logical_market_name=market_name,
        )

        manager.select_market(
            market_name
        )

        self._managers[market_name] = manager

        #
        # Preserve existing _manager behavior.
        #
        if market_name == "NIFTY_FNO":
            self._manager = manager

        logger.info(
            "ExecutionManager Ready : %s",
            market_name,
        )

        return manager

    # ---------------------------------------------------------
    # Engine Scheduler
    # ---------------------------------------------------------

    def _run_engine(self):

        logger.info(
            "Loading Configuration"
        )

        config = ConfigManager(
            "config/application.yaml"
        ).load()

        #
        # -----------------------------------------------------
        # NIFTY
        # -----------------------------------------------------
        #
        # This is the existing/default execution manager.
        #
        # Do not alter its internal execution path.
        #

        try:

            nifty_manager = self._create_manager(
                config,
                "NIFTY_FNO",
            )

        except Exception:

            logger.exception(
                "Failed to initialize NIFTY ExecutionManager"
            )

            nifty_manager = None

        #
        # -----------------------------------------------------
        # MIDCAP
        # -----------------------------------------------------
        #
        # Completely separate ExecutionManager instance.
        #

        try:

            midcap_manager = self._create_manager(
                config,
                "MIDCPNIFTY_FNO",
            )

        except Exception:

            logger.exception(
                "Failed to initialize MIDCAP ExecutionManager"
            )

            midcap_manager = None

        #
        # Apply an explicitly requested runtime selection only
        # to its corresponding manager.
        #
        # Normally the managers above are already correctly
        # initialized with their fixed markets.
        #

        if self._selected_market:

            selected_manager = self._managers.get(
                self._selected_market
            )

            if selected_manager is not None:

                logger.info(
                    "Applying Runtime Market Selection : %s",
                    self._selected_market,
                )

                selected_manager.select_market(
                    self._selected_market
                )

        #
        # -----------------------------------------------------
        # Continuous Multi-Market Scheduler
        # -----------------------------------------------------
        #

        while self._running:

            cycle_start = time.time()

            logger.info("=" * 60)

            logger.info(
                "Trading Engine Multi-Market Cycle Started"
            )

            logger.info("=" * 60)

            #
            # -------------------------------------------------
            # NIFTY CYCLE
            # -------------------------------------------------
            #
            # Existing NIFTY manager is run exactly as before.
            #

            if nifty_manager is not None:

                try:

                    logger.info(
                        "Starting Market Cycle : NIFTY_FNO"
                    )

                    nifty_manager.run()

                    logger.info(
                        "Market Cycle Completed : NIFTY_FNO"
                    )

                except Exception:

                    #
                    # IMPORTANT:
                    # NIFTY failure must not prevent MIDCAP from
                    # getting its own cycle.
                    #

                    logger.exception(
                        "NIFTY Market Cycle Failed"
                    )

            #
            # -------------------------------------------------
            # MIDCAP CYCLE
            # -------------------------------------------------
            #
            # Separate manager.
            #

            if midcap_manager is not None:

                try:

                    logger.info(
                        "Starting Market Cycle : MIDCPNIFTY_FNO"
                    )

                    midcap_manager.run()

                    logger.info(
                        "Market Cycle Completed : MIDCPNIFTY_FNO"
                    )

                except Exception:

                    #
                    # IMPORTANT:
                    # MIDCAP failure must not stop NIFTY.
                    #

                    logger.exception(
                        "MIDCAP Market Cycle Failed"
                    )

            logger.info(
                "Trading Engine Multi-Market Cycle Completed"
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
                and sleep_time > 0
            ):

                time.sleep(
                    min(1, sleep_time)
                )

                sleep_time -= 1

        logger.info(
            "Trading Engine Scheduler Stopped"
        )
