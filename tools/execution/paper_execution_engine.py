"""
============================================================
RUSI Trader AI

V1.0

Paper Execution Engine
============================================================
"""

from __future__ import annotations

from tools.execution.execution_engine import ExecutionEngine
from tools.execution.order_models import (
    OrderRequest,
    OrderStatus,
)


class PaperExecutionEngine(ExecutionEngine):
    """
    Simulates broker execution for paper trading.
    """

    def submit_order(self, request: OrderRequest):
        """
        Submit and immediately execute a paper order.
        """

        order = super().submit_order(request)

        order.status = OrderStatus.FILLED
        order.filled_quantity = request.quantity

        if request.price is not None:
            order.average_price = request.price

        return order

    # ---------------------------------------------------------

    def is_paper_engine(self) -> bool:
        return True

    # ---------------------------------------------------------

    def __str__(self):

        return (
            f"PaperExecutionEngine("
            f"orders={self.order_count()})"
        )

    __repr__ = __str__
