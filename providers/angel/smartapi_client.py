"""
RUSI Trader AI

Smart API Client

Encapsulates all SmartAPI communication.

No other layer should directly use SmartConnect.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from SmartApi import SmartConnect


class SmartApiClient:
    """
    Wrapper around Angel One SmartAPI.

    This is the only layer that should directly
    communicate with SmartConnect.
    """

    def __init__(self, smart_api: SmartConnect):
        self._api = smart_api

    # ---------------------------------------------------------
    # Properties
    # ---------------------------------------------------------

    @property
    def api(self) -> SmartConnect:
        return self._api

    # ---------------------------------------------------------
    # Historical Candles
    # ---------------------------------------------------------

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
        """

        request = {
            "exchange": exchange,
            "symboltoken": str(symbol_token),
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

        response = self._api.getCandleData(
            request
        )

        print(
            "\n========== SmartAPI Candle Response =========="
        )

        print(response)

        return response

    # ---------------------------------------------------------
    # Generic Historical Data
    # ---------------------------------------------------------

    def get_historical_data(
        self,
        exchange: str,
        token: str,
        interval: str,
        from_datetime: datetime,
        to_datetime: datetime,
    ) -> dict[str, Any]:
        """
        Generic historical data interface.

        Keeps the higher-level datasource independent
        from the SmartAPI-specific candle method.
        """

        return self.get_historical_candles(
            exchange=exchange,
            symbol_token=token,
            interval=interval,
            from_datetime=from_datetime,
            to_datetime=to_datetime,
        )

    # ---------------------------------------------------------
    # Live LTP
    # ---------------------------------------------------------

    def get_ltp(
        self,
        exchange: str,
        trading_symbol: str,
        symbol_token: str,
    ) -> dict[str, Any]:
        """
        Fetch the latest traded price from Angel SmartAPI.

        SmartAPI requires:

            exchange
            tradingsymbol
            symboltoken
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

        response = self._api.ltpData(
            exchange,
            trading_symbol,
            str(symbol_token),
        )

        print(
            "\n========== SmartAPI LTP Response =========="
        )

        print(response)

        return response

    # ---------------------------------------------------------
    # Full Market Quote
    # ---------------------------------------------------------

    def get_quote(
        self,
        exchange: str,
        symbol_token: str,
    ) -> dict[str, Any]:
        """
        Fetch full market quote information.

        SmartAPI expects:

            getMarketData(
                mode,
                exchangeTokens
            )

        The broker-specific request format remains
        completely isolated inside this client.
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

        # IMPORTANT:
        #
        # Installed SmartAPI version expects:
        #
        #     getMarketData(mode, exchangeTokens)
        #
        # NOT:
        #
        #     getMarketData({
        #         "mode": ...,
        #         "exchangeTokens": ...
        #     })
        #

        response = self._api.getMarketData(
            "FULL",
            exchange_tokens,
        )

        print(
            "\n========== SmartAPI Quote Response =========="
        )

        print(response)

        return response
    # ---------------------------------------------------------
    # Put / Call Ratio
    # ---------------------------------------------------------

    def get_put_call_ratio(self):
        """
        Fetch cumulative Put / Call Ratio from Angel One.
        """

        print(
            "\n========== SmartAPI PCR Request =========="
        )

        response = self._api.putCallRatio()

        print(
            "\n========== SmartAPI PCR Response =========="
        )

        print(response)

        return response

    # ---------------------------------------------------------
    # OI Buildup
    # ---------------------------------------------------------

    def get_oi_buildup(
        self,
        params,
    ):
        """
        Fetch option OI buildup information.
        """

        print(
            "\n========== SmartAPI OI Buildup Request =========="
        )

        print(params)

        response = self._api.oIBuildup(
            params
        )

        print(
            "\n========== SmartAPI OI Buildup Response =========="
        )

        print(response)

        return response

    # ---------------------------------------------------------
    # Option Greeks
    # ---------------------------------------------------------

    def get_option_greeks(
        self,
        params,
    ):
        """
        Fetch option Greeks information.
        """

        print(
            "\n========== SmartAPI Option Greeks Request =========="
        )

        print(params)

        response = self._api.optionGreek(
            params
        )

        print(
            "\n========== SmartAPI Option Greeks Response =========="
        )

        print(response)

        return response
