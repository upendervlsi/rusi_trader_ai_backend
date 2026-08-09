"""
============================================================
RUSI Trader AI

V1.0

Paper Execution Engine Unit Tests
============================================================
"""

from tools.execution.paper_execution_engine import (
    PaperExecutionEngine,
)
from tools.execution.order_models import (
    OrderRequest,
    OrderSide,
    OrderStatus,
)


class TestPaperExecutionEngine:

    def setup_method(self):

        self.engine = PaperExecutionEngine()

    # ---------------------------------------------------------

    def _request(self):

        return OrderRequest(
            symbol="INFY",
            side=OrderSide.BUY,
            quantity=10,
            price=1500.0,
        )

    # ---------------------------------------------------------

    def test_constructor(self):

        assert self.engine.order_count() == 0

    # ---------------------------------------------------------

    def test_submit_order(self):

        order = self.engine.submit_order(
            self._request()
        )

        assert order.status == OrderStatus.FILLED
        assert order.quantity == 10

    # ---------------------------------------------------------

    def test_filled_quantity(self):

        order = self.engine.submit_order(
            self._request()
        )

        assert order.filled_quantity == 10

    # ---------------------------------------------------------

    def test_average_price(self):

        order = self.engine.submit_order(
            self._request()
        )

        assert order.average_price == 1500.0

    # ---------------------------------------------------------

    def test_paper_engine(self):

        assert self.engine.is_paper_engine()

    # ---------------------------------------------------------

    def test_order_count(self):

        self.engine.submit_order(
            self._request()
        )

        assert self.engine.order_count() == 1

    # ---------------------------------------------------------

    def test_string(self):

        assert "PaperExecutionEngine" in str(self.engine)
        assert "PaperExecutionEngine" in repr(self.engine)
