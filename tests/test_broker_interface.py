"""
============================================================
RUSI Trader AI

V1.0

Broker Interface Unit Tests
============================================================
"""

import pytest

from tools.execution.broker_interface import BrokerInterface
from tools.execution.order_models import (
    OrderRequest,
    OrderResult,
    OrderSide,
)


class MockBroker(BrokerInterface):

    def __init__(self):
        self.connected = False

    def connect(self) -> bool:
        self.connected = True
        return True

    def disconnect(self) -> None:
        self.connected = False

    def is_connected(self) -> bool:
        return self.connected

    def place_order(
        self,
        request: OrderRequest,
    ) -> OrderResult:

        return OrderResult(
            order_id="TEST001",
            symbol=request.symbol,
            side=request.side,
            quantity=request.quantity,
        )

    def cancel_order(
        self,
        order_id: str,
    ) -> bool:
        return True

    def get_order(
        self,
        order_id: str,
    ) -> OrderResult | None:
        return None

    def get_positions(self):
        return []

    def get_holdings(self):
        return []

    def get_available_cash(self) -> float:
        return 100000.0


class TestBrokerInterface:

    def setup_method(self):
        self.broker = MockBroker()

    # ---------------------------------------------------------

    def test_connect(self):

        assert self.broker.connect()
        assert self.broker.is_connected()

    # ---------------------------------------------------------

    def test_disconnect(self):

        self.broker.connect()
        self.broker.disconnect()

        assert not self.broker.is_connected()

    # ---------------------------------------------------------

    def test_place_order(self):

        request = OrderRequest(
            symbol="INFY",
            side=OrderSide.BUY,
            quantity=10,
        )

        order = self.broker.place_order(request)

        assert order.order_id == "TEST001"
        assert order.symbol == "INFY"

    # ---------------------------------------------------------

    def test_cash(self):

        assert self.broker.get_available_cash() == 100000.0

    # ---------------------------------------------------------

    def test_string(self):

        assert "MockBroker" in str(self.broker)
        assert "MockBroker" in repr(self.broker)

    # ---------------------------------------------------------

    def test_abstract_class(self):

        with pytest.raises(TypeError):
            BrokerInterface()
