"""
============================================================
RUSI Trader AI

File    : broker_manager.py

Purpose :
    Central broker manager.

Responsibilities
----------------
1. Register broker implementations.
2. Select the active broker.
3. Delegate broker operations.
4. Keep the trading framework broker-independent.

Author : RUSI Trader AI
============================================================
"""

from typing import Dict, Protocol

from market.instrument import Instrument


class Broker(Protocol):
    """
    Interface implemented by all brokers.
    """

    def login(self) -> bool:
        ...

    def logout(self) -> None:
        ...

    def get_historical_data(
        self,
        instrument: Instrument,
        interval: str,
        lookback: int,
    ):
        ...

    def place_order(
        self,
        instrument: Instrument,
        side: str,
        quantity: int,
    ):
        ...


class BrokerManager:

    def __init__(self):

        self._brokers: Dict[str, Broker] = {}

        self._active_broker: Broker | None = None

    def register(
        self,
        name: str,
        broker: Broker,
    ) -> None:

        self._brokers[name.upper()] = broker

    def activate(
        self,
        name: str,
    ) -> None:

        key = name.upper()

        if key not in self._brokers:
            raise KeyError(f"Broker '{name}' not registered.")

        self._active_broker = self._brokers[key]

    def active(self) -> Broker:

        if self._active_broker is None:
            raise RuntimeError("No active broker selected.")

        return self._active_broker

    def login(self):

        return self.active().login()

    def logout(self):

        return self.active().logout()

    def historical_data(
        self,
        instrument: Instrument,
        interval: str,
        lookback: int,
    ):

        return self.active().get_historical_data(
            instrument,
            interval,
            lookback,
        )

    def place_order(
        self,
        instrument: Instrument,
        side: str,
        quantity: int,
    ):

        return self.active().place_order(
            instrument,
            side,
            quantity,
        )
