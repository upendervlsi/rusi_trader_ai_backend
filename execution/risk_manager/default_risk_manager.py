"""
========================================================================

RUSI Trader AI

Default Risk Manager

========================================================================
"""

from execution.order_builder.order_request import OrderRequest
from execution.risk_manager.risk_manager import RiskManager
from execution.risk_manager.risk_result import RiskResult


class DefaultRiskManager(RiskManager):

    MAX_ORDER_QTY = 100

    def evaluate(
        self,
        order: OrderRequest,
    ) -> RiskResult:

        #
        # Order existence validation
        #
        if order is None:

            return RiskResult(
                trade_allowed=False,
                reason="No order generated. Trade rejected before risk evaluation.",
                approved_quantity=0,
                warnings=[
                    "Order Builder was skipped."
                ],
            )

        #
        # Quantity validation
        #
        if order.quantity <= 0:

            return RiskResult(
                trade_allowed=False,
                reason="Invalid order quantity",
                approved_quantity=0,
            )

        #
        # Maximum order quantity
        #
        approved_qty = min(
            order.quantity,
            self.MAX_ORDER_QTY,
        )

        warnings = []

        if approved_qty != order.quantity:

            warnings.append(
                f"Quantity reduced from {order.quantity} to {approved_qty}"
            )

        return RiskResult(
            trade_allowed=True,
            reason="Risk checks passed",
            approved_quantity=approved_qty,
            warnings=warnings,
        )
