"""
============================================================
RUSI Trader AI

V1.0

Order Manager Unit Tests
============================================================
"""

from tools.execution.execution_engine import ExecutionEngine
from tools.execution.order_manager import OrderManager
from tools.execution.order_models import (
    OrderRequest,
    OrderSide,
)


class TestOrderManager:

    def setup_method(self):

        self.engine = ExecutionEngine()
        self.manager = OrderManager(self.engine)

    # ---------------------------------------------------------

    def _request(self):

        return OrderRequest(
            symbol="INFY",
            side=OrderSide.BUY,
            quantity=10,
        )

    # ---------------------------------------------------------

    def test_constructor(self):

        assert self.manager.total_orders() == 0

    # ---------------------------------------------------------

    def test_submit(self):

        order = self.manager.submit(
            self._request()
        )

        assert order.symbol == "INFY"
        assert self.manager.total_orders() == 1

    # ---------------------------------------------------------

    def test_get(self):

        order = self.manager.submit(
            self._request()
        )

        result = self.manager.get(order.order_id)

        assert result == order

    # ---------------------------------------------------------

    def test_cancel(self):

        order = self.manager.submit(
            self._request()
        )

        assert self.manager.cancel(order.order_id)

    # ---------------------------------------------------------

    def test_clear(self):

        self.manager.submit(
            self._request()
        )

        self.manager.clear()

        assert self.manager.total_orders() == 0

    # ---------------------------------------------------------

    def test_string(self):

        assert "OrderManager" in str(self.manager)
        assert "OrderManager" in repr(self.manager)
