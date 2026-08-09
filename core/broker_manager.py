"""
=============================================================
RUSI Trader AI

Broker Manager

Central broker initialization and datasource creation.

Sprint-17
=============================================================
"""

from __future__ import annotations

from providers.angel.angel_datasource import AngelDataSource
from providers.angel.angel_order_executor import AngelOrderExecutor
from providers.angel.smartapi_client import SmartApiClient
from providers.angel.session_manager import SessionManager

from trading.context.trading_context import TradingInstrument


class BrokerManager:
    """
    Broker lifecycle manager.

    Responsibilities
    ----------------
    * Login to broker
    * Create SmartAPI client
    * Create datasource using resolved instrument
    * Create order executor
    """

    def __init__(self, config=None):

        self._config = config

        self._session_manager = None
        self._smartapi_client = None
        self._datasource = None
        self._order_executor = None

    # ---------------------------------------------------------
    # Initialization
    # ---------------------------------------------------------

    def initialize(self):

        self._session_manager = SessionManager()

        smart_connect = self._session_manager.connect()

        self._smartapi_client = SmartApiClient(
            smart_connect
        )

        self._order_executor = AngelOrderExecutor(
            self._smartapi_client
        )

    # ---------------------------------------------------------
    # Datasource
    # ---------------------------------------------------------

    def create_datasource(
        self,
        instrument: TradingInstrument,
    ):

        self._datasource = AngelDataSource(
            client=self._smartapi_client,
            instrument=instrument,
        )

    # ---------------------------------------------------------
    # Properties
    # ---------------------------------------------------------

    @property
    def datasource(self):

        if self._datasource is None:

            raise RuntimeError(
                "Datasource has not been created."
            )

        return self._datasource

    @property
    def smartapi_client(self):

        return self._smartapi_client

    @property
    def order_executor(self):

        return self._order_executor

    # ---------------------------------------------------------
    # Cleanup
    # ---------------------------------------------------------

    def shutdown(self):

        self._datasource = None
    # ---------------------------------------------------------
    # Order Execution
    # ---------------------------------------------------------

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
