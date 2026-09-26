"""
============================================================

RUSI Trader AI

Smart API Client

Encapsulates all SmartAPI communication.

Responsibilities
----------------
- Historical candles
- Live LTP
- Full market quotes
- Centralized expired-token recovery

Authentication
--------------
This client does NOT perform broker login.

SessionManager owns authentication and token refresh.

When SmartAPI returns:

    Invalid Token
    AG8001

the client requests a token refresh from SessionManager
and retries the original request exactly once.

============================================================
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Callable

logger = logging.getLogger(__name__)

from SmartApi import SmartConnect

from providers.angel.session_manager import (
    SessionManager,
)


class SmartApiClient:
    """
    Wrapper around Angel One SmartAPI.

    Higher-level application layers should communicate
    through this class rather than directly calling
    SmartConnect.
    """

    def __init__(
        self,
        smart_api: SmartConnect,
        session_manager: SessionManager | None = None,
    ):

        self._api = smart_api

        #
        # Keep a SessionManager reference so token refresh
        # can update the same process-wide SmartConnect.
        #

        self._session_manager = (
            session_manager
            or SessionManager()
        )

    # ========================================================
    # PROPERTIES
    # ========================================================

    @property
    def api(self) -> SmartConnect:
        return self._api

    # ========================================================
    # TOKEN ERROR DETECTION
    # ========================================================

    @staticmethod
    def _is_invalid_token_response(
        response: Any,
    ) -> bool:
        """
        Detect Angel One invalid-token responses.

        Known Angel response:

            {
                "success": False,
                "message": "Invalid Token",
                "errorCode": "AG8001",
                "data": ""
            }

        Some SmartAPI versions may use slightly different
        keys, so the detection intentionally checks the
        relevant fields without being overly broad.
        """

        if not isinstance(
            response,
            dict,
        ):

            return False

        error_code = str(
            response.get(
                "errorCode",
                "",
            )
        ).upper()

        message = str(
            response.get(
                "message",
                "",
            )
        ).lower()

        error_type = str(
            response.get(
                "error_type",
                "",
            )
        ).lower()

        if error_code == "AG8001":

            return True

        if "invalid token" in message:

            return True

        if "tokenexception" in error_type:

            return True

        return False

    # ========================================================
    # TOKEN RECOVERY
    # ========================================================

    def _refresh_and_update_client(
        self,
    ) -> None:
        """
        Refresh the access token and make sure this client
        points to the authenticated SmartConnect instance.
        """

        refreshed_api = (
            self._session_manager.refresh()
        )

        #
        # SessionManager intentionally returns the same
        # SmartConnect instance after refresh.
        #

        self._api = refreshed_api

    # ========================================================
    # REQUEST WITH TOKEN RECOVERY
    # ========================================================

    def _execute_with_token_recovery(
        self,
        operation: Callable[[], Any],
        operation_name: str,
    ) -> Any:
        """
        Execute a SmartAPI operation.

        Normal path:

            operation()

        Token-expiry path:

            operation()
                |
                v
            AG8001 / Invalid Token
                |
                v
            refresh()
                |
                v
            operation()  # exactly one retry

        No repeated refresh loop is allowed.
        """

        response = operation()

        if not self._is_invalid_token_response(
            response
        ):

            return response

        print(
            "\n========== SmartAPI Token Recovery =========="
        )

        print(
            "Operation       :",
            operation_name,
        )

        print(
            "Broker Response : Invalid Token / AG8001"
        )

        print(
            "Action          : Refreshing access token"
        )

        #
        # Refresh exactly once.
        #

        self._refresh_and_update_client()

        print(
            "Action          : Retrying request once"
        )

        retry_response = operation()

        if self._is_invalid_token_response(
            retry_response
        ):

            raise RuntimeError(
                "Angel One returned Invalid Token "
                f"again after token refresh during "
                f"{operation_name}. "
                "The broker session may require a "
                "new login."
            )

        print(
            "SmartAPI Token Recovery : SUCCESS"
        )

        return retry_response

    # ========================================================
    # HISTORICAL CANDLES
    # ========================================================

    def get_historical_candles(
        self,
        exchange: str,
        symbol_token: str,
        interval: str,
        from_datetime: datetime,
        to_datetime: datetime,
    ) -> dict[str, Any]:
        """
        Fetch historical candle data from Angel SmartAPI.

        Automatically recovers once from an expired JWT.
        """

        request = {
            "exchange": exchange,
            "symboltoken": str(
                symbol_token
            ),
            "interval": interval,
            "fromdate": from_datetime.strftime(
                "%Y-%m-%d %H:%M"
            ),
            "todate": to_datetime.strftime(
                "%Y-%m-%d %H:%M"
            ),
        }

        print(
            "\n========== SmartAPI Candle Request =========="
        )

        print(request)

        response = self._execute_with_token_recovery(
            operation=lambda: (
                self._api.getCandleData(
                    request
                )
            ),
            operation_name="Historical Candles",
        )

        print(
            "\n========== SmartAPI Candle Response =========="
        )

        print(response)

        return response

    # ========================================================
    # GENERIC HISTORICAL DATA
    # ========================================================

    def get_historical_data(
        self,
        exchange: str,
        token: str,
        interval: str,
        from_datetime: datetime,
        to_datetime: datetime,
    ) -> dict[str, Any]:
        """
        Generic historical-data interface.

        Keeps higher-level datasource code independent
        from SmartAPI-specific candle implementation.
        """

        return self.get_historical_candles(
            exchange=exchange,
            symbol_token=token,
            interval=interval,
            from_datetime=from_datetime,
            to_datetime=to_datetime,
        )

    # ========================================================
    # LIVE LTP
    # ========================================================

    def get_ltp(
        self,
        exchange: str,
        trading_symbol: str,
        symbol_token: str,
    ) -> dict[str, Any]:
        """
        Fetch latest traded price.

        Automatically recovers once from an expired JWT.
        """

        print(
            "\n========== SmartAPI LTP Request =========="
        )

        print(
            "Exchange :",
            exchange,
        )

        print(
            "Symbol   :",
            trading_symbol,
        )

        print(
            "Token    :",
            symbol_token,
        )

        response = self._execute_with_token_recovery(
            operation=lambda: (
                self._api.ltpData(
                    exchange,
                    trading_symbol,
                    str(symbol_token),
                )
            ),
            operation_name="LTP",
        )

        print(
            "\n========== SmartAPI LTP Response =========="
        )

        print(response)

        return response

    # ========================================================
    # FULL MARKET QUOTE
    # ========================================================

    def get_quote(
        self,
        exchange: str,
        symbol_token: str,
    ) -> dict[str, Any]:
        """
        Fetch full market quote.

        Automatically recovers once from an expired JWT.
        """

        print(
            "\n========== SmartAPI Quote Request =========="
        )

        print(
            "Exchange :",
            exchange,
        )

        print(
            "Token    :",
            symbol_token,
        )

        exchange_tokens = {
            exchange: [
                str(symbol_token)
            ]
        }

        response = self._execute_with_token_recovery(
            operation=lambda: (
                self._api.getMarketData(
                    "FULL",
                    exchange_tokens,
                )
            ),
            operation_name="Market Quote",
        )

        print(
            "\n========== SmartAPI Quote Response =========="
        )

        print(response)

        return response


    # ========================================================
    # FULL MARKET QUOTE — BATCH
    # ========================================================

    def get_quotes(
        self,
        exchange: str,
        symbol_tokens: list[str],
    ) -> dict[str, Any]:
        """
        Fetch full market quotes for multiple tokens.

        Automatically recovers once from an expired JWT.

        This is a separate batch API from get_quote().
        """

        if not exchange:
            raise ValueError("exchange is required")

        if not symbol_tokens:
            raise ValueError("symbol_tokens cannot be empty")

        tokens = [
            str(token)
            for token in symbol_tokens
            if token is not None and str(token).strip()
        ]

        if not tokens:
            raise ValueError("symbol_tokens contains no valid tokens")

        print(
            "\n========== SmartAPI Batch Quote Request =========="
        )

        print(
            "Exchange       :",
            exchange,
        )

        print(
            "Token Count    :",
            len(tokens),
        )

        exchange_tokens = {
            exchange: tokens
        }

        response = self._execute_with_token_recovery(
            operation=lambda: (
                self._api.getMarketData(
                    "FULL",
                    exchange_tokens,
                )
            ),
            operation_name="Batch Market Quote",
        )

        print(
            "\n========== SmartAPI Batch Quote Response =========="
        )

        print(response)

        return response

    # ========================================================
    # ORDER DETAILS
    # ========================================================

    def get_order_details(
        self,
        order_id: str,
    ) -> Any:
        """
        Retrieve broker-side details for a previously submitted
        Angel One order.

        This is a read-only broker query. It does not place,
        modify, or cancel an order.

        Automatically recovers once from an expired JWT.
        """
        if not isinstance(order_id, str):
            raise TypeError(
                "order_id must be a string"
            )

        order_id = order_id.strip()

        if not order_id:
            raise ValueError(
                "order_id cannot be empty"
            )

        logger.info(
            "SmartAPI Order Details Request : %s",
            order_id,
        )

        response = self._execute_with_token_recovery(
            operation=lambda: (
                self._api.individual_order_details(
                    order_id
                )
            ),
            operation_name="Order Details",
        )

        logger.info(
            "SmartAPI Order Details Response : %s",
            response,
        )

        return response


    # ========================================================
    # POSITIONS
    # ========================================================

    def get_positions(self) -> Any:
        """
        Retrieve current broker-side positions.

        This is a read-only broker query used by LIVE position
        recovery to reconcile persisted RUSI positions against
        the actual Angel One account.

        Automatically recovers once from an expired JWT.
        """

        logger.info("SmartAPI Positions Request")

        response = self._execute_with_token_recovery(
            operation=lambda: self._api.position(),
            operation_name="Positions",
        )

        logger.info(
            "SmartAPI Positions Response : %s",
            response,
        )

        return response


    # ========================================================
    # ORDER BOOK
    # ========================================================

    def get_order_book(self) -> Any:
        """
        Retrieve the current Angel One order book.

        This is a read-only broker query. It does not place,
        modify, or cancel an order.

        Automatically recovers once from an expired JWT.
        """
        logger.info("SmartAPI Order Book Request")

        response = self._execute_with_token_recovery(
            operation=lambda: self._api.orderBook(),
            operation_name="Order Book",
        )

        logger.info(
            "SmartAPI Order Book Response : %s",
            response,
        )

        return response


    # ========================================================
    # ORDER PLACEMENT
    # ========================================================

    def place_order(
        self,
        order: dict[str, Any],
    ) -> Any:
        """
        Place an order through the authenticated Angel One
        SmartAPI session.

        This method only provides the low-level SmartAPI
        capability. Higher-level trading policy decides when
        this method may be called.

        Automatically recovers once from an expired JWT.

        Broker response diagnostics are logged through the
        RUSI logger so SmartAPI/logzero failures are visible
        through the production system journal.
        """

        if not isinstance(order, dict):
            raise TypeError(
                "order must be a dictionary"
            )

        if not order:
            raise ValueError(
                "order cannot be empty"
            )

        required_fields = (
            "variety",
            "tradingsymbol",
            "symboltoken",
            "transactiontype",
            "exchange",
            "ordertype",
            "producttype",
            "duration",
            "quantity",
        )

        missing_fields = [
            field
            for field in required_fields
            if field not in order
        ]

        if missing_fields:
            raise ValueError(
                "Order is missing required fields: "
                + ", ".join(missing_fields)
            )

        logger.info(
            "SmartAPI Order Request : "
            "symbol=%s exchange=%s transaction=%s "
            "order_type=%s product=%s quantity=%s",
            order.get("tradingsymbol"),
            order.get("exchange"),
            order.get("transactiontype"),
            order.get("ordertype"),
            order.get("producttype"),
            order.get("quantity"),
        )

        def _place_order_raw() -> Any:
            """
            Call the SmartAPI transport directly so the broker's
            raw response remains visible to RUSI.

            SmartConnect.placeOrder() can swallow a broker-side
            status=False response and return None. That prevents
            centralized token recovery from seeing AB1007 /
            Invalid Token.

            _postRequest() is used only for this low-level order
            transport path. All higher-level trading policy remains
            unchanged.
            """

            post_request = getattr(
                self._api,
                "_postRequest",
                None,
            )

            if not callable(post_request):
                raise RuntimeError(
                    "SmartAPI SDK does not expose the expected "
                    "_postRequest transport method."
                )

            return post_request(
                "api.order.place",
                order,
            )

        response = self._execute_with_token_recovery(
            operation=_place_order_raw,
            operation_name="Order Placement",
        )

        logger.info(
            "SmartAPI Order Raw Result : %r",
            response,
        )

        if response is None:
            logger.error(
                "SmartAPI Order Result : "
                "Broker transport returned no response."
            )
            return None

        logger.info(
            "SmartAPI Order Result Type : %s",
            type(response).__name__,
        )

        if not isinstance(response, dict):
            logger.error(
                "SmartAPI Order Result : "
                "Unexpected response type: %s",
                type(response).__name__,
            )
            return None

        if not response.get("status"):
            logger.error(
                "SmartAPI Order Rejected : "
                "message=%s errorcode=%s data=%r",
                response.get("message"),
                response.get("errorcode", response.get("errorCode")),
                response.get("data"),
            )
            return None

        data = response.get("data")

        if not isinstance(data, dict):
            logger.error(
                "SmartAPI Order Result : "
                "Successful response has invalid data=%r",
                data,
            )
            return None

        order_id = data.get("orderid")

        if not order_id:
            logger.error(
                "SmartAPI Order Result : "
                "Successful response contains no order ID. "
                "data=%r",
                data,
            )
            return None

        logger.info(
            "SmartAPI Order Accepted : Order ID=%s",
            order_id,
        )

        return str(order_id)

