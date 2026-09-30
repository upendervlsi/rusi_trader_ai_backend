"""
RUSI Trader AI

Stock Options Observation Quote Collector

Stage 9

Purpose
-------
Fetch full Angel quotes for dynamically selected stock-option
contracts so they can be evaluated by the existing
StockOptionQualitySelector.

This module is isolated from the NIFTY V1 runtime.
"""

from __future__ import annotations

import time

from core.broker_manager import BrokerManager
from providers.angel.angel_datasource import AngelDataSource
from trading.context.trading_context import TradingInstrument


class StockOptionsObservationQuoteCollector:

    def __init__(
        self,
        broker_manager: BrokerManager | None = None,
        request_delay_seconds: float = 0.0,
    ):

        if request_delay_seconds < 0:
            raise ValueError(
                "request_delay_seconds cannot be negative."
            )

        self._broker_manager = (
            broker_manager
            if broker_manager is not None
            else BrokerManager()
        )

        self._request_delay_seconds = float(
            request_delay_seconds
        )

        self._initialized = False

    def _ensure_broker(self) -> None:

        if self._initialized:
            return

        self._broker_manager.initialize()
        self._initialized = True

    def collect(
        self,
        candidates,
    ) -> tuple[dict[str, dict], list[dict]]:

        if not candidates:
            return {}, []

        self._ensure_broker()

        quotes: dict[str, dict] = {}
        errors: list[dict] = []

        valid_candidates = []
        grouped_candidates: dict[str, list] = {}

        # ----------------------------------------------------
        # Validate and group candidates by exchange.
        # ----------------------------------------------------

        for candidate in candidates:

            option_symbol = str(
                candidate.option_symbol
            ).strip()

            token = str(
                candidate.token
            ).strip()

            exchange = str(
                candidate.exchange or "NFO"
            ).strip()

            if not option_symbol or not token:
                errors.append(
                    {
                        "option_symbol": option_symbol,
                        "token": token,
                        "error": (
                            "Missing option symbol or token"
                        ),
                    }
                )
                continue

            valid_candidates.append(
                candidate
            )

            grouped_candidates.setdefault(
                exchange,
                [],
            ).append(candidate)

        # ----------------------------------------------------
        # Fetch each exchange group using one batch request.
        # ----------------------------------------------------

        for exchange_index, (
            exchange,
            exchange_candidates,
        ) in enumerate(
            grouped_candidates.items()
        ):

            if (
                exchange_index > 0
                and self._request_delay_seconds
            ):
                time.sleep(
                    self._request_delay_seconds
                )

            tokens = [
                str(candidate.token).strip()
                for candidate in exchange_candidates
            ]

            try:

                response = (
                    self._broker_manager
                    .smartapi_client
                    .get_quotes(
                        exchange=exchange,
                        symbol_tokens=tokens,
                    )
                )

                if not response:
                    raise RuntimeError(
                        "Empty batch option quote response"
                    )

                data = response.get("data") or {}

                fetched = data.get("fetched") or []
                unfetched = data.get("unfetched") or []

                fetched_by_token = {
                    str(
                        quote.get("symbolToken")
                    ).strip(): quote
                    for quote in fetched
                    if quote.get("symbolToken")
                }

                fetched_by_symbol = {
                    str(
                        quote.get("tradingSymbol")
                    ).strip(): quote
                    for quote in fetched
                    if quote.get("tradingSymbol")
                }

                # ------------------------------------------------
                # Map every requested candidate back to its quote.
                # ------------------------------------------------

                for candidate in exchange_candidates:

                    option_symbol = str(
                        candidate.option_symbol
                    ).strip()

                    token = str(
                        candidate.token
                    ).strip()

                    quote = (
                        fetched_by_token.get(token)
                        or fetched_by_symbol.get(
                            option_symbol
                        )
                    )

                    if quote is not None:

                        quotes[option_symbol] = {
                            "status": response.get(
                                "status"
                            ),
                            "message": response.get(
                                "message"
                            ),
                            "errorcode": response.get(
                                "errorcode"
                            ),
                            "data": {
                                "fetched": [quote],
                                "unfetched": [],
                            },
                        }

                    else:

                        errors.append(
                            {
                                "option_symbol": (
                                    option_symbol
                                ),
                                "token": token,
                                "error": (
                                    "Option quote was "
                                    "not returned by "
                                    "batch request"
                                ),
                                "batch_exchange": exchange,
                                "batch_unfetched": (
                                    unfetched
                                ),
                            }
                        )

            except Exception as exc:

                for candidate in exchange_candidates:

                    errors.append(
                        {
                            "option_symbol": str(
                                candidate.option_symbol
                            ).strip(),
                            "token": str(
                                candidate.token
                            ).strip(),
                            "error": str(exc),
                            "batch_exchange": exchange,
                        }
                    )

        return quotes, errors
