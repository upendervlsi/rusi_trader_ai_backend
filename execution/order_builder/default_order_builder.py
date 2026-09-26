"""
============================================================

RUSI Trader AI

Default Order Builder

============================================================

RUSI V1 OPTION BUYING POLICY

    Underlying BUY  -> BUY CE
    Underlying SELL -> BUY PE

The decision signal represents the underlying market
direction.

It MUST NOT be used directly as the option transaction side.

For RUSI V1:

    CE transaction = BUY
    PE transaction = BUY

SELL is never sent as the transaction type for an option
buying recommendation.
"""

from execution.order_builder.order_builder import OrderBuilder
from execution.order_builder.order_request import OrderRequest


class DefaultOrderBuilder(OrderBuilder):

    def build(
        self,
        context,
    ) -> OrderRequest:

        #
        # Prefer the recommendation-selected execution
        # instrument when available.
        #
        # Otherwise preserve the existing behaviour.
        #

        instrument = (
            context.metadata.get(
                "execution_instrument"
            )
            or context.instrument
        )

        #
        # -----------------------------------------------------
        # RUSI V1 OPTION BUYING
        # -----------------------------------------------------
        #
        # context.decision.signal represents the UNDERLYING
        # direction:
        #
        #     BUY  -> bullish underlying
        #     SELL -> bearish underlying
        #
        # The recommendation engine converts that direction:
        #
        #     BUY  -> CE
        #     SELL -> PE
        #
        # But the actual option transaction is ALWAYS BUY.
        #
        # Therefore we must NOT use:
        #
        #     context.decision.signal.value
        #
        # as the transaction type.
        #

        transaction_type = "BUY"

        #
        # -----------------------------------------------------
        # Build Order Request
        # -----------------------------------------------------
        #

        return OrderRequest(
            symbol=instrument.symbol,

            exchange=instrument.exchange,

            token=str(instrument.token),

            transaction_type=transaction_type,

            quantity=instrument.quantity,

            execution_price=(
                context.recommendation.entry_price
            ),

            order_type=instrument.order_type,

            product_type=instrument.product_type,
        )
