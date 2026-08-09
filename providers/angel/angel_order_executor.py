"""
============================================================

Angel Order Executor

============================================================
"""

from common.logger import get_logger
from execution.broker.broker_result import BrokerResult
logger = get_logger("RUSI")


class AngelOrderExecutor:

    def __init__(self, smartapi_client):

        self._client = smartapi_client

    def place_order(
        self,
        order_request,
    ):
        """
        Execute an order using Angel SmartAPI.

        NOTE:
        This method initially runs in PAPER MODE.
        Replace the implementation with the real
        SmartAPI placeOrder() call when live trading
        is enabled.
        """

        logger.info("")
        logger.info("Paper Order Execution")
        logger.info("----------------------------")

        logger.info(
            "Symbol      : %s",
            order_request.symbol,
        )

        logger.info(
            "Exchange    : %s",
            order_request.exchange,
        )

        logger.info(
            "Transaction : %s",
            order_request.transaction_type,
        )

        logger.info(
            "Quantity    : %d",
            order_request.quantity,
        )

        return BrokerResult(

            success=True,

            order_id="PAPER_ORDER_000001",

            message="Paper trade executed",

            filled_quantity=order_request.quantity,

            average_price=order_request.execution_price,
        )
