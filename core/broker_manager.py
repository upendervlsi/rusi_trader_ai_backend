"""
=============================================================

RUSI Trader AI

Broker Manager

Central broker initialization and datasource creation.

Responsibilities
----------------
- Initialize centralized Angel One session.
- Create SmartAPI client.
- Create market datasource.
- Create order executor.
- Preserve one authentication lifecycle for the
  application process.

Sprint-17
Updated
-------
Centralized token-refresh aware SmartAPI client.

=============================================================
"""

from __future__ import annotations

from providers.angel.angel_datasource import (
    AngelDataSource,
)

from providers.angel.angel_order_executor import (
    AngelOrderExecutor,
)

from providers.angel.smartapi_client import (
    SmartApiClient,
)

from providers.angel.session_manager import (
    SessionManager,
)

from trading.context.trading_context import (
    TradingInstrument,
)


class BrokerManager:
    """
    Broker lifecycle manager.

    Responsibilities
    ----------------
    * Login to broker.
    * Maintain centralized SessionManager.
    * Create SmartAPI client.
    * Create datasource using resolved instrument.
    * Create order executor.
    """

    def __init__(
        self,
        config=None,
    ):

        self._config = config

        self._session_manager = None

        self._smartapi_client = None

        self._datasource = None

        self._order_executor = None

    # ========================================================
    # INITIALIZATION
    # ========================================================

    def initialize(self):

        #
        # One SessionManager object for this BrokerManager.
        #
        # SessionManager itself also maintains process-wide
        # shared state, so other services can safely create
        # their own SessionManager instances.
        #

        self._session_manager = (
            SessionManager()
        )

        #
        # Establish initial authenticated session.
        #

        smart_connect = (
            self._session_manager.connect()
        )

        #
        # Create token-refresh-aware SmartAPI client.
        #

        self._smartapi_client = (
            SmartApiClient(
                smart_connect,
                session_manager=(
                    self._session_manager
                ),
            )
        )

        #
        # Order execution uses the same SmartAPI client.
        #

        self._order_executor = (
            AngelOrderExecutor(
                self._smartapi_client
            )
        )

    # ========================================================
    # DATASOURCE
    # ========================================================

    def create_datasource(
        self,
        instrument: TradingInstrument,
    ):

        if self._smartapi_client is None:

            raise RuntimeError(
                "BrokerManager has not been initialized."
            )

        self._datasource = (
            AngelDataSource(
                client=self._smartapi_client,
                instrument=instrument,
            )
        )

    # ========================================================
    # PROPERTIES
    # ========================================================

    @property
    def datasource(self):

        if self._datasource is None:

            raise RuntimeError(
                "Datasource has not been created."
            )

        return self._datasource

    @property
    def smartapi_client(self):

        if self._smartapi_client is None:

            raise RuntimeError(
                "SmartAPI client has not been initialized."
            )

        return self._smartapi_client

    @property
    def session_manager(self):

        if self._session_manager is None:

            raise RuntimeError(
                "SessionManager has not been initialized."
            )

        return self._session_manager

    @property
    def order_executor(self):

        if self._order_executor is None:

            raise RuntimeError(
                "Order executor has not been initialized."
            )

        return self._order_executor

    # ========================================================
    # ORDER EXECUTION
    # ========================================================

    def place_order(
        self,
        order,
    ):
        """
        Submit an order through the active order executor.
        """

        if self._order_executor is None:

            raise RuntimeError(
                "Order executor has not been initialized."
            )

        return self._order_executor.place_order(
            order
        )

    # ========================================================
    # CLEANUP
    # ========================================================

    def shutdown(self):

        #
        # Datasource is only a wrapper around the active
        # instrument/client, so release it first.
        #

        self._datasource = None

        #
        # Order executor no longer needs to be retained.
        #

        self._order_executor = None

        #
        # SmartAPI client is released locally.
        #

        self._smartapi_client = None

        #
        # Intentionally do NOT disconnect the global
        # SessionManager here.
        #
        # Other backend services may still be using the
        # shared SmartAPI session.
        #

        self._session_manager = None
