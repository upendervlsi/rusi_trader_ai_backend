"""
============================================================
RUSI Trader AI

File    : angel_broker.py

Purpose :
    Angel One SmartAPI broker implementation.

Responsibilities
----------------
1. Login
2. Logout
3. Historical Data
4. Order Placement

Author : RUSI Trader AI
============================================================
"""

from __future__ import annotations

from typing import Any

from SmartApi import SmartConnect

from market.instrument import Instrument


class AngelBroker:
    """
    Angel One SmartAPI implementation.

    Implements the Broker interface.
    """

    def __init__(
        self,
        api_key: str,
        client_id: str,
        password: str,
        totp: str,
    ):

        self._api_key = api_key
        self._client_id = client_id
        self._password = password
        self._totp = totp

        self._smart = SmartConnect(api_key=self._api_key)

        self._logged_in = False
        self._feed_token = None

    ####################################################################
    # Login
    ####################################################################

    def login(self) -> bool:

        response = self._smart.generateSession(
            self._client_id,
            self._password,
            self._totp,
        )

        if not response:
            raise RuntimeError("Empty login response.")

        if not response.get("status", False):
            raise RuntimeError(
                response.get(
                    "message",
                    "Angel login failed.",
                )
            )

        self._feed_token = self._smart.getfeedToken()

        self._logged_in = True

        print("[AngelBroker] Login successful.")

        return True

    ####################################################################
    # Logout
    ####################################################################

    def logout(self) -> None:

        if self._logged_in:

            self._smart.terminateSession(
                self._client_id
            )

        self._logged_in = False

        print("[AngelBroker] Logout.")

    ####################################################################
    # Historical Data
    ####################################################################

    def get_historical_data(
        self,
        instrument: Instrument,
        interval: str,
        lookback: int,
    ) -> Any:

        if not self._logged_in:
            raise RuntimeError(
                "Broker not logged in."
            )

        params = {
            "exchange": instrument.exchange,
            "symboltoken": instrument.token,
            "interval": interval,
            "fromdate": "",
            "todate": "",
        }

        print(
            "[AngelBroker] Historical Request:",
            instrument.display_name(),
        )

        return self._smart.getCandleData(params)

    ####################################################################
    # Order Placement
    ####################################################################

    def place_order(
        self,
        instrument: Instrument,
        side: str,
        quantity: int,
    ) -> Any:

        if not self._logged_in:
            raise RuntimeError(
                "Broker not logged in."
            )

        order = {

            "variety": "NORMAL",

            "tradingsymbol": instrument.symbol,

            "symboltoken": instrument.token,

            "transactiontype": side.upper(),

            "exchange": instrument.exchange,

            "ordertype": "MARKET",

            "producttype": "CARRYFORWARD",

            "duration": "DAY",

            "price": "0",

            "squareoff": "0",

            "stoploss": "0",

            "quantity": quantity,
        }

        order_id = self._smart.placeOrder(order)

        print(
            "[AngelBroker] Order Placed:",
            order_id,
        )

        return order_id
