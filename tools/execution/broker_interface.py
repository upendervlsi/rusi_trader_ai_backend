"""
============================================================
RUSI Trader AI

V1.0

Broker Interface
============================================================
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from tools.execution.order_models import (
    OrderRequest,
    OrderResult,
)


class BrokerInterface(ABC):
    """
    Abstract broker interface.

    All broker implementations (Angel One, Zerodha,
    HDFC Securities, SBI Securities, etc.) shall
    inherit from this interface.
    """

    @abstractmethod
    def connect(self) -> bool:
        """Establish broker connection."""
        raise NotImplementedError

    @abstractmethod
    def disconnect(self) -> None:
        """Close broker connection."""
        raise NotImplementedError

    @abstractmethod
    def is_connected(self) -> bool:
        """Return current connection state."""
        raise NotImplementedError

    @abstractmethod
    def place_order(
        self,
        request: OrderRequest,
    ) -> OrderResult:
        """Place an order with the broker."""
        raise NotImplementedError

    @abstractmethod
    def cancel_order(
        self,
        order_id: str,
    ) -> bool:
        """Cancel an existing order."""
        raise NotImplementedError

    @abstractmethod
    def get_order(
        self,
        order_id: str,
    ) -> OrderResult | None:
        """Retrieve an order by ID."""
        raise NotImplementedError

    @abstractmethod
    def get_positions(self):
        """Return current broker positions."""
        raise NotImplementedError

    @abstractmethod
    def get_holdings(self):
        """Return current holdings."""
        raise NotImplementedError

    @abstractmethod
    def get_available_cash(self) -> float:
        """Return available trading cash."""
        raise NotImplementedError

    def __str__(self) -> str:
        return self.__class__.__name__

    __repr__ = __str__
