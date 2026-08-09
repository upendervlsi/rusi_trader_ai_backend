"""
============================================================

Default Order Builder

============================================================
"""

from execution.order_builder.order_builder import OrderBuilder
from execution.order_builder.order_request import OrderRequest


class DefaultOrderBuilder(OrderBuilder):

    def build(
        self,
        context,
    ) -> OrderRequest:

        instrument = context.instrument

        return OrderRequest(
            symbol=instrument.symbol,

            exchange=instrument.exchange,

            transaction_type=context.decision.signal.value,

            quantity=instrument.quantity,

            execution_price=context.recommendation.entry_price,

            order_type=instrument.order_type,

            product_type=instrument.product_type,
        )
