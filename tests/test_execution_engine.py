"""
============================================================
RUSI Trader AI

V1.0

Execution Engine Unit Tests
============================================================
"""

from tools.execution.execution_engine import ExecutionEngine
from tools.execution.order_models import (
    OrderRequest,
    OrderSide,
    OrderStatus,
)


class TestExecutionEngine:

    def setup_method(self):

        self.engine = ExecutionEngine()

    # ---------------------------------------------------------

    def _request(self):

        return OrderRequest(
            symbol="INFY",
            side=OrderSide.BUY,
            quantity=10,
        )

    # ---------------------------------------------------------

    def test_constructor(self):

        assert self.engine.order_count() == 0

    # ---------------------------------------------------------

    def test_submit_order(self):

        order = self.engine.submit_order(
            self._request()
        )

        assert order is not None
        assert order.symbol == "INFY"
        assert self.engine.order_count() == 1

    # ---------------------------------------------------------

    def test_get_order(self):

        order = self.engine.submit_order(
            self._request()
        )

        result = self.engine.get_order(order.order_id)

        assert result == order

    # ---------------------------------------------------------

    def test_cancel_order(self):

        order = self.engine.submit_order(
            self._request()
        )

        assert self.engine.cancel_order(
            order.order_id
        )

        assert order.status == OrderStatus.CANCELLED

    # ---------------------------------------------------------

    def test_cancel_filled_order(self):

        order = self.engine.submit_order(
            self._request()
        )

        self.engine.update_order_status(
            order.order_id,
            OrderStatus.FILLED,
        )

        assert not self.engine.cancel_order(
            order.order_id
        )

    # ---------------------------------------------------------

    def test_update_status(self):

        order = self.engine.submit_order(
            self._request()
        )

        assert self.engine.update_order_status(
            order.order_id,
            OrderStatus.OPEN,
        )

        assert order.status == OrderStatus.OPEN

    # ---------------------------------------------------------

    def test_clear(self):

        self.engine.submit_order(
            self._request()
        )

        self.engine.clear()

        assert self.engine.order_count() == 0

    # ---------------------------------------------------------

    def test_string(self):

        assert "ExecutionEngine" in str(self.engine)
        assert "ExecutionEngine" in repr(self.engine)
