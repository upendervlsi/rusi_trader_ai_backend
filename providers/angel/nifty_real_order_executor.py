"""
============================================================

NIFTY Real Order Executor

Dedicated real-order execution path for NIFTY F&O.

IMPORTANT:
- This executor is NOT used by Paper Trading.
- This executor is NOT used by MIDCAP, MCX, or Stock Options.
- Actual broker execution occurs only when this class is
  explicitly called by the NIFTY Real Trading path.

============================================================
"""

import time

from common.logger import get_logger
from execution.broker.broker_result import BrokerResult

logger = get_logger("RUSI")


class NiftyRealOrderExecutor:

    ORDER_DETAIL_ATTEMPTS = 5
    ORDER_DETAIL_INTERVAL_SECONDS = 1.0

    def __init__(self, smartapi_client):
        self._client = smartapi_client

    @staticmethod
    def _extract_order_data(response):
        """
        Extract the order-detail data dictionary from the
        different response shapes that SmartAPI may return.
        """
        if not isinstance(response, dict):
            return None

        data = response.get("data")

        if isinstance(data, dict):
            return data

        if isinstance(data, list):
            if len(data) == 1 and isinstance(data[0], dict):
                return data[0]

        return None

    @staticmethod
    def _get_value(data, *keys):
        """
        Return the first non-empty value for the supplied keys.
        """
        if not isinstance(data, dict):
            return None

        for key in keys:
            value = data.get(key)

            if value is not None and str(value).strip() != "":
                return value

        return None

    @classmethod
    def _parse_order_details(cls, response):
        """
        Parse broker order details into:

            status
            filled_quantity
            average_price

        Angel One field naming can vary between API responses,
        so the parser accepts the known casing variants without
        inventing missing values.
        """
        data = cls._extract_order_data(response)

        if data is None:
            return {
                "status": "",
                "filled_quantity": 0,
                "average_price": None,
                "data": None,
            }

        status = cls._get_value(
            data,
            "orderstatus",
            "orderStatus",
            "status",
        )

        filled_raw = cls._get_value(
            data,
            "filledshares",
            "filledShares",
            "filledquantity",
            "filledQuantity",
        )

        average_raw = cls._get_value(
            data,
            "averageprice",
            "averagePrice",
            "average_price",
        )

        try:
            filled_quantity = int(float(filled_raw or 0))
        except (TypeError, ValueError):
            filled_quantity = 0

        try:
            average_price = (
                float(average_raw)
                if average_raw is not None
                else None
            )
        except (TypeError, ValueError):
            average_price = None

        return {
            "status": str(status or "").strip().lower(),
            "filled_quantity": filled_quantity,
            "average_price": average_price,
            "data": data,
        }

    def _resolve_fill(
        self,
        broker_order_id: str,
    ):
        """
        Poll broker-side order details until the order reaches
        a terminal state or the bounded polling window expires.

        Returns:
            {
                "status": str,
                "filled_quantity": int,
                "average_price": float | None,
                "data": dict | None,
            }
        """
        last_result = {
            "status": "",
            "filled_quantity": 0,
            "average_price": None,
            "data": None,
        }

        for attempt in range(
            1,
            self.ORDER_DETAIL_ATTEMPTS + 1,
        ):
            try:
                response = self._client.get_order_details(
                    broker_order_id
                )
            except Exception as exc:
                logger.exception(
                    "NIFTY order detail query failed "
                    "(attempt %d/%d): %s",
                    attempt,
                    self.ORDER_DETAIL_ATTEMPTS,
                    exc,
                )
                response = None

            parsed = self._parse_order_details(response)
            last_result = parsed

            logger.info(
                "NIFTY Real Order Status : %s | "
                "Filled Qty : %d | Avg Price : %s | "
                "Attempt : %d/%d",
                parsed["status"],
                parsed["filled_quantity"],
                parsed["average_price"],
                attempt,
                self.ORDER_DETAIL_ATTEMPTS,
            )

            status = parsed["status"]

            if status in {
                "complete",
                "completed",
                "filled",
                "executed",
            }:
                return parsed

            if status in {
                "rejected",
                "cancelled",
                "canceled",
                "failed",
                "expired",
            }:
                return parsed

            if attempt < self.ORDER_DETAIL_ATTEMPTS:
                time.sleep(
                    self.ORDER_DETAIL_INTERVAL_SECONDS
                )

        return last_result

    def check_existing_order(
        self,
        broker_order_id: str,
    ):
        """
        Check the current broker-side status of an already-submitted
        NIFTY real order.

        This method NEVER places a new order.

        It is used by the NIFTY Real pending-order recovery path
        to reconcile an order that was previously accepted by the
        broker but whose fill status was not resolved locally.

        Returns:
            {
                "status": str,
                "filled_quantity": int,
                "average_price": float | None,
                "data": dict | None,
            }
        """
        broker_order_id = str(broker_order_id or "").strip()

        if not broker_order_id:
            logger.error(
                "NIFTY pending-order reconciliation failed: "
                "broker order ID is empty"
            )
            return {
                "status": "",
                "filled_quantity": 0,
                "average_price": None,
                "data": None,
            }

        try:
            response = self._client.get_order_details(
                broker_order_id
            )
        except Exception as exc:
            logger.exception(
                "NIFTY pending-order reconciliation failed | "
                "Order ID : %s | Error : %s",
                broker_order_id,
                exc,
            )
            return {
                "status": "",
                "filled_quantity": 0,
                "average_price": None,
                "data": None,
            }

        parsed = self._parse_order_details(response)

        # --------------------------------------------------------
        # Angel One reconciliation fallback
        #
        # individual_order_details() can return:
        #
        #     AB1007 / Order not found
        #
        # even when the same completed order is still available
        # through orderBook().
        #
        # This fallback is READ-ONLY. It never places, modifies,
        # or cancels an order.
        # --------------------------------------------------------

        error_code = str(
            response.get("errorcode", "")
            if isinstance(response, dict)
            else ""
        ).upper()

        message = str(
            response.get("message", "")
            if isinstance(response, dict)
            else ""
        ).strip().lower()

        order_not_found = (
            error_code == "AB1007"
            or message == "order not found"
            or "order not found" in message
        )

        if order_not_found:
            logger.warning(
                "NIFTY Pending Order Reconciliation : "
                "Order Details returned Order Not Found | "
                "Order ID : %s | "
                "Falling back to broker Order Book",
                broker_order_id,
            )

            try:
                order_book_response = (
                    self._client.get_order_book()
                )
            except Exception as exc:
                logger.exception(
                    "NIFTY pending-order Order Book fallback "
                    "failed | Order ID : %s | Error : %s",
                    broker_order_id,
                    exc,
                )
                order_book_response = None

            matched_order = None

            if isinstance(order_book_response, dict):
                order_book_data = order_book_response.get(
                    "data"
                )

                if isinstance(order_book_data, list):
                    for order in order_book_data:
                        if not isinstance(order, dict):
                            continue

                        order_id = str(
                            order.get("orderid", "")
                            or order.get("orderId", "")
                        ).strip()

                        if order_id == broker_order_id:
                            matched_order = order
                            break

            if matched_order is not None:
                parsed = self._parse_order_details(
                    {"data": matched_order}
                )

                logger.info(
                    "NIFTY Pending Order Reconciliation : "
                    "Order Book Match | "
                    "Order ID : %s | Status : %s | "
                    "Filled Qty : %d | Avg Price : %s",
                    broker_order_id,
                    parsed["status"] or "UNKNOWN",
                    parsed["filled_quantity"],
                    parsed["average_price"],
                )
            else:
                logger.warning(
                    "NIFTY Pending Order Reconciliation : "
                    "Order Book Match Not Found | "
                    "Order ID : %s | Remaining UNKNOWN",
                    broker_order_id,
                )

                # Order details and Order Book both failed to resolve the
                # broker order. Do NOT reuse the original Order Details
                # response because it may contain a stale/terminal status
                # that is not authoritative after AB1007 / Order Not Found.
                # Keep the order unresolved so ExecutionManager continues
                # blocking duplicate entries.
                parsed = {
                    "status": "",
                    "filled_quantity": 0,
                    "average_price": None,
                    "data": None,
                }

        logger.info(
            "NIFTY Pending Order Reconciliation : "
            "Order ID : %s | Status : %s | "
            "Filled Qty : %d | Avg Price : %s",
            broker_order_id,
            parsed["status"] or "UNKNOWN",
            parsed["filled_quantity"],
            parsed["average_price"],
        )

        return parsed

    def place_order(
        self,
        order_request,
    ) -> BrokerResult:
        """
        Place a NIFTY F&O real order through SmartAPI.

        A successful BrokerResult is returned only after broker-side
        fill information has been obtained. No fill price or quantity
        is fabricated.
        """

        if order_request is None:
            return BrokerResult(
                success=False,
                order_id="",
                message="Order request is required",
                filled_quantity=0,
                average_price=None,
            )

        symbol = str(
            order_request.symbol or ""
        ).strip()

        exchange = str(
            order_request.exchange or ""
        ).strip().upper()

        transaction_type = str(
            order_request.transaction_type or ""
        ).strip().upper()

        token = str(
            order_request.token or ""
        ).strip()

        order_type = str(
            order_request.order_type or "MARKET"
        ).strip().upper()

        product_type = str(
            order_request.product_type or "INTRADAY"
        ).strip().upper()

        quantity = int(
            order_request.quantity
        )

        if not symbol:
            return BrokerResult(
                success=False,
                order_id="",
                message="NIFTY real order rejected: symbol is empty",
                filled_quantity=0,
                average_price=None,
            )

        if not symbol.startswith("NIFTY"):
            return BrokerResult(
                success=False,
                order_id="",
                message=(
                    "NIFTY real order rejected: "
                    f"symbol '{symbol}' is not a NIFTY instrument"
                ),
                filled_quantity=0,
                average_price=None,
            )

        if symbol.startswith("MIDCPNIFTY"):
            return BrokerResult(
                success=False,
                order_id="",
                message=(
                    "NIFTY real order rejected: "
                    "MIDCPNIFTY is not allowed"
                ),
                filled_quantity=0,
                average_price=None,
            )

        if exchange != "NFO":
            return BrokerResult(
                success=False,
                order_id="",
                message=(
                    "NIFTY real order rejected: "
                    f"exchange must be NFO, got '{exchange}'"
                ),
                filled_quantity=0,
                average_price=None,
            )

        if transaction_type not in ("BUY", "SELL"):
            return BrokerResult(
                success=False,
                order_id="",
                message=(
                    "NIFTY real order rejected: "
                    f"invalid transaction type '{transaction_type}'"
                ),
                filled_quantity=0,
                average_price=None,
            )

        if not token:
            return BrokerResult(
                success=False,
                order_id="",
                message="NIFTY real order rejected: token is empty",
                filled_quantity=0,
                average_price=None,
            )

        if quantity <= 0:
            return BrokerResult(
                success=False,
                order_id="",
                message=(
                    "NIFTY real order rejected: "
                    "quantity must be greater than zero"
                ),
                filled_quantity=0,
                average_price=None,
            )

        angel_order = {
            "variety": "NORMAL",
            "tradingsymbol": symbol,
            "symboltoken": token,
            "transactiontype": transaction_type,
            "exchange": exchange,
            "ordertype": order_type,
            "producttype": product_type,
            "duration": "DAY",
            "price": "0",
            "squareoff": "0",
            "stoploss": "0",
            "quantity": quantity,
        }

        logger.info("")
        logger.info("NIFTY REAL ORDER EXECUTION")
        logger.info("----------------------------")
        logger.info("Symbol      : %s", symbol)
        logger.info("Exchange    : %s", exchange)
        logger.info("Transaction : %s", transaction_type)
        logger.info("Quantity    : %d", quantity)
        logger.info("Order Type  : %s", order_type)
        logger.info("Product     : %s", product_type)

        try:
            broker_order_id = self._client.place_order(
                angel_order
            )
        except Exception as exc:
            logger.exception(
                "NIFTY Real Order failed: %s",
                exc,
            )

            return BrokerResult(
                success=False,
                order_id="",
                message=f"Broker order placement failed: {exc}",
                filled_quantity=0,
                average_price=None,
            )

        if not broker_order_id:
            logger.error(
                "NIFTY Real Order rejected: "
                "SmartAPI returned no order ID"
            )

            return BrokerResult(
                success=False,
                order_id="",
                message=(
                    "SmartAPI rejected order or returned "
                    "no order ID"
                ),
                filled_quantity=0,
                average_price=None,
            )

        broker_order_id = str(
            broker_order_id
        ).strip()

        logger.info(
            "NIFTY Real Order accepted by broker. "
            "Order ID: %s",
            broker_order_id,
        )

        fill = self._resolve_fill(
            broker_order_id
        )

        status = fill["status"]
        filled_quantity = fill["filled_quantity"]
        average_price = fill["average_price"]

        if status in {
            "complete",
            "completed",
            "filled",
            "executed",
        }:
            if (
                filled_quantity > 0
                and average_price is not None
                and average_price > 0
            ):
                logger.info(
                    "NIFTY Real Order FILLED | "
                    "Order ID : %s | Qty : %d | "
                    "Avg Price : %.4f",
                    broker_order_id,
                    filled_quantity,
                    average_price,
                )

                return BrokerResult(
                    success=True,
                    order_id=broker_order_id,
                    message="NIFTY real order filled by broker",
                    filled_quantity=filled_quantity,
                    average_price=average_price,
                )

            logger.error(
                "NIFTY Real Order reported FILLED but "
                "fill quantity/average price is invalid | "
                "Order ID : %s | Qty : %d | Avg Price : %s",
                broker_order_id,
                filled_quantity,
                average_price,
            )

            return BrokerResult(
                success=False,
                order_id=broker_order_id,
                message=(
                    "Broker reported filled order but "
                    "valid fill quantity/average price "
                    "was not available"
                ),
                filled_quantity=filled_quantity,
                average_price=average_price,
            )

        if status in {
            "rejected",
            "cancelled",
            "canceled",
            "failed",
            "expired",
        }:
            logger.warning(
                "NIFTY Real Order NOT FILLED | "
                "Order ID : %s | Status : %s",
                broker_order_id,
                status,
            )

            return BrokerResult(
                success=False,
                order_id=broker_order_id,
                message=(
                    "NIFTY real order not filled. "
                    f"Broker status: {status}"
                ),
                filled_quantity=filled_quantity,
                average_price=average_price,
            )

        logger.warning(
            "NIFTY Real Order fill status unresolved within "
            "bounded polling window | Order ID : %s | "
            "Status : %s",
            broker_order_id,
            status or "UNKNOWN",
        )

        return BrokerResult(
            success=False,
            order_id=broker_order_id,
            message=(
                "NIFTY real order accepted but fill status "
                "was not resolved within the bounded polling window"
            ),
            filled_quantity=filled_quantity,
            average_price=average_price,
        )
