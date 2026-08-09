"""
============================================================
RUSI Trader AI

V1.0

Execution Engine
============================================================
"""

from __future__ import annotations

from uuid import uuid4

from tools.execution.order_models import (
    OrderRequest,
    OrderResult,
    OrderStatus,
)


class ExecutionEngine:
    """
    Broker-independent execution engine.
    """

    def __init__(self) -> None:
        self._orders: dict[str, OrderResult] = {}

    # ---------------------------------------------------------

    def submit_order(
        self,
        request: OrderRequest,
    ) -> OrderResult:
        """
        Submit a new order.
        """

        order = OrderResult(
            order_id=str(uuid4()),
            symbol=request.symbol,
            side=request.side,
            quantity=request.quantity,
            status=OrderStatus.NEW,
        )

        self._orders[order.order_id] = order

        return order

    # ---------------------------------------------------------

    def get_order(
        self,
        order_id: str,
    ) -> OrderResult | None:

        return self._orders.get(order_id)

    # ---------------------------------------------------------

    def cancel_order(
        self,
        order_id: str,
    ) -> bool:

        order = self.get_order(order_id)

        if order is None:
            return False

        if order.status == OrderStatus.FILLED:
            return False

        order.status = OrderStatus.CANCELLED

        return True

    # ---------------------------------------------------------

    def update_order_status(
        self,
        order_id: str,
        status: OrderStatus,
    ) -> bool:

        order = self.get_order(order_id)

        if order is None:
            return False

        order.status = status

        return True

    # ---------------------------------------------------------

    def order_count(self) -> int:

        return len(self._orders)

    # ---------------------------------------------------------

    def clear(self) -> None:

        self._orders.clear()

    # ---------------------------------------------------------

    def __str__(self) -> str:

        return (
            f"ExecutionEngine("
            f"orders={len(self._orders)})"
        )

    __repr__ = __str__
