"""
RUSI Trader AI

Stock Options Observation Orchestrator

Stage 9

Purpose
-------
Connect the already validated stock-options components into
one observation-only workflow.

Flow
----
Stock market data
    -> Bull/Bear analysis
    -> Direction-specific option selection
    -> Option quote collection
    -> Quality selection
    -> Risk calculation
    -> Observation recording

This module does NOT:
- modify the NIFTY V1 runtime
- place broker orders
- modify strategy thresholds
- hardcode stocks, strikes, expiries, or lot sizes
"""

from __future__ import annotations

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from tools.market_universe.instrument_master_manager import (
    InstrumentMasterManager,
)
from tools.market_universe.instrument_master_parser import (
    InstrumentMasterParser,
)
from tools.market_universe.stock_options_universe import (
    StockOptionsUniverse,
)
from tools.market_universe.stock_option_selector import (
    StockOptionSelector,
)
from tools.market_universe.stock_option_quality_selector import (
    StockOptionQualitySelector,
)
from tools.scanner.stock_bull_bear_analyzer import (
    StockBullBearAnalyzer,
)
from tools.scanner.stock_option_candidate_decision import (
    StockOptionCandidateDecisionEngine,
)
from tools.risk.stock_options_risk_engine import (
    StockOptionsRiskEngine,
)
from tools.stock_options_observation.option_quote_collector import (
    StockOptionsObservationQuoteCollector,
)
from intelligence.data.market_series_builder import (
    MarketSeriesBuilder,
)
from tools.stock_options_observation.observation_recorder import (
    StockOptionsObservationRecorder,
)


class StockOptionsObservationOrchestrator:

    def __init__(
        self,
        market_scanner,
        broker_manager=None,
        request_delay_seconds: float = 0.0,
    ):

        if request_delay_seconds < 0:
            raise ValueError(
                "request_delay_seconds cannot be negative."
            )

        self._market_scanner = market_scanner

        master_manager = InstrumentMasterManager()
        master_file = master_manager.load_master()

        parser = InstrumentMasterParser()
        parser.load(master_file)

        self._universe = StockOptionsUniverse(parser)
        self._universe.build()

        self._option_selector = StockOptionSelector(
            self._universe
        )

        self._quality_selector = StockOptionQualitySelector(
            option_selector=self._option_selector
        )

        self._analyzer = StockBullBearAnalyzer()

        self._decision_engine = (
            StockOptionCandidateDecisionEngine(
                quality_selector=self._quality_selector
            )
        )

        self._risk_engine = StockOptionsRiskEngine()

        self._quote_collector = (
            StockOptionsObservationQuoteCollector(
                broker_manager=broker_manager,
                request_delay_seconds=request_delay_seconds,
            )
        )

        self._recorder = StockOptionsObservationRecorder()

    @property
    def universe(self):
        return self._universe

    @staticmethod
    def _quote_from_response(
        quote_response,
    ) -> dict | None:
        """
        Extract one raw Angel quote from the existing quote
        response structure.

        This is diagnostic-only. It does not modify the quote
        structure consumed by the decision engine.
        """

        if not isinstance(quote_response, dict):
            return None

        data = quote_response.get("data")

        if isinstance(data, list) and data:
            quote = data[0]
            return quote if isinstance(quote, dict) else None

        if isinstance(data, dict):

            fetched = data.get("fetched")

            if isinstance(fetched, list) and fetched:
                quote = fetched[0]
                return quote if isinstance(quote, dict) else None

            if isinstance(fetched, dict):
                return fetched

            if "ltp" in data:
                return data

        if "ltp" in quote_response:
            return quote_response

        return None

    @staticmethod
    def _parse_angel_timestamp(
        value,
    ) -> datetime | None:
        """
        Parse Angel One exchange timestamps.

        Angel timestamps are exchange-local IST values such as:

            08-Sep-2026 14:28:04

        They are explicitly interpreted as Asia/Kolkata and
        converted to UTC for reliable age calculations.
        """

        if not value:
            return None

        text = str(value).strip()

        if not text:
            return None

        try:
            parsed = datetime.strptime(
                text,
                "%d-%b-%Y %H:%M:%S",
            )

            ist = ZoneInfo("Asia/Kolkata")

            return parsed.replace(
                tzinfo=ist
            ).astimezone(
                timezone.utc
            )

        except (TypeError, ValueError):
            return None

    @classmethod
    def _build_quote_diagnostics(
        cls,
        quote_response,
        direction,
    ) -> dict:
        """
        Build observation-only quote diagnostics.

        Existing LTP, quality, risk, selection and execution
        behavior remain unchanged.

        The diagnostics are stored in decision.metadata.
        """

        quote = cls._quote_from_response(
            quote_response
        )

        if not quote:
            return {
                "quote_diagnostics": {
                    "available": False,
                    "quote_status": "UNAVAILABLE",
                }
            }

        now = datetime.now(timezone.utc)

        raw_ltp = quote.get("ltp")

        raw_bid = None
        raw_ask = None

        depth = quote.get("depth")

        if isinstance(depth, dict):

            buy = depth.get("buy") or []
            sell = depth.get("sell") or []

            if isinstance(buy, list) and buy:
                first_buy = buy[0]

                if isinstance(first_buy, dict):
                    raw_bid = first_buy.get("price")

            if isinstance(sell, list) and sell:
                first_sell = sell[0]

                if isinstance(first_sell, dict):
                    raw_ask = first_sell.get("price")

        try:
            ltp = (
                float(raw_ltp)
                if raw_ltp is not None
                else None
            )
        except (TypeError, ValueError):
            ltp = None

        try:
            best_bid = (
                float(raw_bid)
                if raw_bid is not None
                else None
            )
        except (TypeError, ValueError):
            best_bid = None

        try:
            best_ask = (
                float(raw_ask)
                if raw_ask is not None
                else None
            )
        except (TypeError, ValueError):
            best_ask = None

        spread = None

        if (
            best_bid is not None
            and best_ask is not None
            and best_ask >= best_bid
        ):
            spread = best_ask - best_bid

        spread_percent = None

        if (
            spread is not None
            and ltp is not None
            and ltp > 0
        ):
            spread_percent = (
                spread / ltp
            ) * 100.0

        feed_time = cls._parse_angel_timestamp(
            quote.get("exchFeedTime")
        )

        trade_time = cls._parse_angel_timestamp(
            quote.get("exchTradeTime")
        )

        quote_age_seconds = None
        trade_age_seconds = None

        if feed_time is not None:
            quote_age_seconds = max(
                0.0,
                (
                    now - feed_time
                ).total_seconds(),
            )

        if trade_time is not None:
            trade_age_seconds = max(
                0.0,
                (
                    now - trade_time
                ).total_seconds(),
            )

        #
        # Diagnostic freshness classification only.
        #
        # <= 120 seconds  : FRESH
        # <= 300 seconds  : AGING
        # > 300 seconds   : STALE
        #

        if quote_age_seconds is None:
            quote_status = "UNKNOWN"
        elif quote_age_seconds <= 120:
            quote_status = "FRESH"
        elif quote_age_seconds <= 300:
            quote_status = "AGING"
        else:
            quote_status = "STALE"

        executable_price = None

        #
        # Long option positions/candidates are expected to
        # sell into the bid. Short positions/candidates would
        # buy into the ask.
        #
        # This is recorded for analysis only and does not
        # replace the existing LTP-based option_price.
        #

        if str(direction).upper() in {
            "BULLISH",
            "LONG",
        }:
            executable_price = best_bid

        elif str(direction).upper() in {
            "BEARISH",
            "SHORT",
        }:
            executable_price = best_ask

        diagnostics = {
            "available": True,
            "quote_status": quote_status,
            "quote_age_seconds": quote_age_seconds,
            "trade_age_seconds": trade_age_seconds,
            "exchange_feed_time": quote.get(
                "exchFeedTime"
            ),
            "exchange_trade_time": quote.get(
                "exchTradeTime"
            ),
            "ltp": ltp,
            "best_bid": best_bid,
            "best_ask": best_ask,
            "spread": spread,
            "spread_percent": spread_percent,
            "executable_price": executable_price,
            "last_trade_quantity": quote.get(
                "lastTradeQty"
            ),
            "trade_volume": quote.get(
                "tradeVolume"
            ),
            "open_interest": quote.get(
                "opnInterest"
            ),
        }

        return {
            "quote_diagnostics": diagnostics
        }

    def observe_stock(self, scan_result):
        """
        Observe one stock scan result.

        This method intentionally performs no execution.
        """

        if not scan_result:
            return None

        if scan_result.get("status") != "OK":
            return None

        symbol = str(
            scan_result.get("symbol", "")
        ).strip()

        candles = scan_result.get("candles") or []
        underlying_price = float(
            scan_result.get("live_price") or 0.0
        )

        if not symbol or not candles or underlying_price <= 0:
            return None

        series = MarketSeriesBuilder.build(candles)

        analysis = self._analyzer.analyze(
            symbol=symbol,
            series=series,
        )

        if analysis.direction == "NO_TRADE":
            decision = self._decision_engine.decide(
                analysis=analysis,
                underlying_price=underlying_price,
                quotes={},
            )

            return self._recorder.record(decision)

        candidates = self._option_selector.select(
            symbol=symbol,
            direction=analysis.direction,
            underlying_price=underlying_price,
        )

        if not candidates:
            decision = self._decision_engine.decide(
                analysis=analysis,
                underlying_price=underlying_price,
                quotes={},
            )

            return self._recorder.record(decision)

        quotes, quote_errors = self._quote_collector.collect(
            candidates
        )

        decision = self._decision_engine.decide(
            analysis=analysis,
            underlying_price=underlying_price,
            quotes=quotes,
        )

        #
        # ----------------------------------------------------
        # QUOTE DIAGNOSTICS
        # ----------------------------------------------------
        #
        # The selected candidate and its raw quote are used
        # only to add observation metadata.
        #
        # Existing decision/quality behavior is untouched.
        #

        quote_diagnostics = {}

        if (
            decision.candidate is not None
            and decision.candidate.candidate is not None
        ):

            selected_candidate = (
                decision.candidate.candidate
            )

            selected_option_symbol = str(
                selected_candidate.option_symbol
            ).strip()

            selected_quote_response = quotes.get(
                selected_option_symbol
            )

            quote_diagnostics = (
                self._build_quote_diagnostics(
                    selected_quote_response,
                    analysis.direction,
                )
            )

        risk_stop_loss = None
        risk_target = None
        risk_reward_ratio = None
        maximum_loss = None
        maximum_reward = None

        risk_metadata = {
            "risk_evaluated": False,
        }

        if decision.decision == "CANDIDATE":
            option_price = (
                decision.candidate.quality.ltp
            )

            risk = self._risk_engine.evaluate(
                entry_price=option_price,
                quantity=int(
                    decision.candidate.candidate.lot_size
                ),
            )

            risk_metadata = {
                "risk_evaluated": True,
                "risk_allowed": risk.allowed,
                "risk_reasons": list(risk.reasons),
                "risk_metadata": dict(risk.metadata),
            }

            if risk.allowed:
                risk_stop_loss = risk.stop_loss
                risk_target = risk.target_price
                risk_reward_ratio = (
                    risk.risk_reward_ratio
                )
                maximum_loss = risk.maximum_loss
                maximum_reward = risk.maximum_reward

        decision.metadata.update(
            {
                "risk": risk_metadata,
                **quote_diagnostics,
            }
        )

        observation = self._recorder.record(
            decision,
            stop_loss=risk_stop_loss,
            target_price=risk_target,
            risk_reward_ratio=risk_reward_ratio,
            maximum_loss=maximum_loss,
            maximum_reward=maximum_reward,
        )

        observation.metadata.update(
            {
                "quote_error_count": len(
                    quote_errors
                ),
                "quote_errors": quote_errors,
                "candle_count": len(candles),
            }
        )

        return observation
