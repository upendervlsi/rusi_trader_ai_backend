"""
============================================================
RUSI Trader AI

V1.0

Order Manager
============================================================
"""

from __future__ import annotations

from tools.execution.execution_engine import ExecutionEngine
from tools.execution.order_models import (
    OrderRequest,
    OrderResult,
)


class OrderManager:
    """
    Coordinates order lifecycle using the execution engine.
    """

    def __init__(
        self,
        execution_engine: ExecutionEngine,
    ) -> None:

        self._execution_engine = execution_engine

    # ---------------------------------------------------------

    def submit(
        self,
        request: OrderRequest,
    ) -> OrderResult:
        """
        Submit an order.
        """
        return self._execution_engine.submit_order(request)

    # ---------------------------------------------------------

    def cancel(
        self,
        order_id: str,
    ) -> bool:
        """
        Cancel an existing order.
        """
        return self._execution_engine.cancel_order(order_id)

    # ---------------------------------------------------------

    def get(
        self,
        order_id: str,
    ) -> OrderResult | None:
        """
        Retrieve an order.
        """
        return self._execution_engine.get_order(order_id)

    # ---------------------------------------------------------

    def total_orders(self) -> int:
        """
        Return total tracked orders.
        """
        return self._execution_engine.order_count()

    # ---------------------------------------------------------

    def clear(self) -> None:
        """
        Remove all tracked orders.
        """
        self._execution_engine.clear()

    # ---------------------------------------------------------

    def __str__(self) -> str:
        return (
            f"OrderManager("
            f"orders={self.total_orders()})"
        )

    __repr__ = __str__
