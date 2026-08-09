"""
========================================================================

RUSI Trader AI

Angel One Order Mapper

========================================================================
"""

from __future__ import annotations

from broker.angel_one.angel_order_request import (
    AngelOrderRequest,
)
from broker.base.broker_order import (
    BrokerOrder,
)


class AngelOrderMapper:

    DEFAULT_VARIETY = "NORMAL"

    DEFAULT_EXCHANGE = "NSE"

    DEFAULT_DURATION = "DAY"

    def map(
        self,
        broker_order: BrokerOrder,
        symbol_token: str,
    ) -> AngelOrderRequest:

        return AngelOrderRequest(
            variety=self.DEFAULT_VARIETY,
            tradingsymbol=broker_order.symbol,
            symboltoken=symbol_token,
            transactiontype=broker_order.signal.value,
            exchange=self.DEFAULT_EXCHANGE,
            ordertype=broker_order.order_type,
            producttype=broker_order.product_type,
            duration=self.DEFAULT_DURATION,
            quantity=broker_order.quantity,
            price=broker_order.price,
        )
