"""
========================================================================

RUSI Trader AI

Order Mapper

========================================================================
"""

from __future__ import annotations

from broker.base.broker_order import BrokerOrder
from intelligence.pipeline.trading_pipeline_result import (
    TradingPipelineResult,
)


class OrderMapper:
    """
    Converts a TradingPipelineResult into a generic BrokerOrder.
    """

    DEFAULT_ORDER_TYPE = "MARKET"
    DEFAULT_PRODUCT_TYPE = "INTRADAY"

    def map(
        self,
        result: TradingPipelineResult,
        symbol: str,
    ) -> BrokerOrder:

        plan = result.trade_plan
        risk = result.risk_result

        return BrokerOrder(
            symbol=symbol,
            signal=plan.signal,
            quantity=risk.position_size,
            order_type=self.DEFAULT_ORDER_TYPE,
            product_type=self.DEFAULT_PRODUCT_TYPE,
            price=plan.entry_price,
            stop_loss=plan.stop_loss,
            target_price=plan.target_price,
        )
