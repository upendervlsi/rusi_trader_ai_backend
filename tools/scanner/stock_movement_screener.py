"""
RUSI Trader AI

Lightweight Stock Movement Screener
Stage 11E.1

Purpose:
    Screen the complete dynamically discovered stock-options
    underlying universe using LIVE NSE quotes only.

This component:
    - uses the existing stock-options universe
    - resolves existing NSE equity instruments
    - uses batch live quotes
    - calculates a movement opportunity score
    - returns the strongest Top-N stocks

This component does NOT:
    - request historical candles
    - analyze options
    - select CE/PE contracts
    - perform risk calculations
    - place orders
    - modify NIFTY V1
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from common.logger import get_logger
from core.broker_manager import BrokerManager
from tools.market_universe.instrument_master_manager import (
    InstrumentMasterManager,
)
from tools.market_universe.instrument_master_parser import (
    InstrumentMasterParser,
)
from tools.market_universe.stock_options_universe import (
    StockOptionsUniverse,
)


logger = get_logger("RUSI")


@dataclass(slots=True)
class StockMovementCandidate:
    symbol: str
    token: str

    ltp: float
    open_price: float
    high: float
    low: float
    previous_close: float
    average_price: float

    percent_change: float
    trade_volume: float

    movement_score: float
    direction: str

    range_percent: float
    open_displacement_percent: float
    average_price_displacement_percent: float
    volume_score: float

    quote: dict[str, Any]


@dataclass(slots=True)
class StockMovementScreenResult:
    success: bool
    universe_count: int
    quote_request_count: int
    successful_quote_count: int
    failed_quote_count: int
    top_candidates: list[StockMovementCandidate]
    errors: list[dict[str, Any]]


class StockMovementScreener:

    """
    Lightweight live-quote screener for the complete
    stock-options underlying universe.
    """

    BATCH_SIZE = 50
    TOP_N = 3

    # Movement score weights.
    WEIGHT_PERCENT_CHANGE = 35.0
    WEIGHT_RANGE = 25.0
    WEIGHT_OPEN_DISPLACEMENT = 15.0
    WEIGHT_AVG_PRICE_DISPLACEMENT = 15.0
    WEIGHT_VOLUME = 10.0

    def __init__(
        self,
        top_n: int = TOP_N,
        batch_size: int = BATCH_SIZE,
    ):

        if top_n <= 0:
            raise ValueError(
                "top_n must be greater than zero."
            )

        if batch_size <= 0:
            raise ValueError(
                "batch_size must be greater than zero."
            )

        self._top_n = top_n
        self._batch_size = batch_size

        self._broker_manager = BrokerManager()

        self._master_manager = (
            InstrumentMasterManager()
        )

        self._parser = (
            InstrumentMasterParser()
        )

        self._parser.load(
            self._master_manager.load_master()
        )

        self._universe = (
            StockOptionsUniverse(
                self._parser
            )
        )

        self._universe.build()

        self._initialized = False

    # =========================================================
    # PUBLIC
    # =========================================================

    @property
    def universe(self):
        return self._universe

    def screen(self) -> StockMovementScreenResult:
        """
        Screen the complete stock universe using live quotes only.
        """

        self._ensure_broker()

        symbols = list(
            self._universe.stock_symbols
        )

        if not symbols:
            return StockMovementScreenResult(
                success=False,
                universe_count=0,
                quote_request_count=0,
                successful_quote_count=0,
                failed_quote_count=0,
                top_candidates=[],
                errors=[
                    {
                        "stage": "universe",
                        "error": "Stock universe is empty.",
                    }
                ],
            )

        instruments: list[dict[str, str]] = []
        errors: list[dict[str, Any]] = []

        # -----------------------------------------------------
        # Resolve NSE tokens
        # -----------------------------------------------------

        for symbol in symbols:

            try:

                records = (
                    self._parser.get_by_exchange_symbol(
                        "NSE",
                        symbol,
                    )
                )

                selected = (
                    self._select_nse_record(
                        symbol,
                        records,
                    )
                )

                instruments.append(
                    {
                        "symbol": symbol,
                        "token": str(
                            selected["token"]
                        ),
                    }
                )

            except Exception as exc:

                errors.append(
                    {
                        "symbol": symbol,
                        "stage": "instrument_resolution",
                        "error": str(exc),
                    }
                )

        # -----------------------------------------------------
        # Batch live quotes
        # -----------------------------------------------------

        quote_map: dict[str, dict[str, Any]] = {}

        quote_request_count = 0

        for start in range(
            0,
            len(instruments),
            self._batch_size,
        ):

            batch = instruments[
                start:start + self._batch_size
            ]

            tokens = [
                item["token"]
                for item in batch
            ]

            try:

                quote_request_count += 1

                logger.info(
                    "Stock Movement Screener: "
                    "live quote batch %s-%s of %s",
                    start + 1,
                    min(
                        start + self._batch_size,
                        len(instruments),
                    ),
                    len(instruments),
                )

                response = (
                    self._broker_manager
                    .smartapi_client
                    .get_quotes(
                        exchange="NSE",
                        symbol_tokens=tokens,
                    )
                )

                fetched = self._extract_fetched(
                    response
                )

                for quote in fetched:

                    token = str(
                        quote.get(
                            "symbolToken",
                            "",
                        )
                    ).strip()

                    if token:
                        quote_map[token] = quote

            except Exception as exc:

                errors.append(
                    {
                        "stage": "quote_batch",
                        "batch_start": start,
                        "batch_size": len(batch),
                        "error": str(exc),
                    }
                )

                logger.error(
                    "Stock Movement Screener: "
                    "quote batch failed: %s",
                    exc,
                )

        # -----------------------------------------------------
        # Build candidates
        # -----------------------------------------------------

        raw_candidates: list[dict[str, Any]] = []

        for instrument in instruments:

            symbol = instrument["symbol"]
            token = instrument["token"]

            quote = quote_map.get(token)

            if not quote:
                continue

            parsed = self._parse_quote(
                symbol=symbol,
                token=token,
                quote=quote,
            )

            if parsed is not None:
                raw_candidates.append(parsed)

        # -----------------------------------------------------
        # Relative volume score
        # -----------------------------------------------------

        volume_values = [
            item["trade_volume"]
            for item in raw_candidates
            if item["trade_volume"] >= 0
        ]

        volume_scores = self._percentile_scores(
            volume_values
        )

        for index, item in enumerate(
            raw_candidates
        ):

            item["volume_score"] = (
                volume_scores[index]
                if index < len(volume_scores)
                else 0.0
            )

            item["movement_score"] = (
                (
                    item["percent_change_score"]
                    * self.WEIGHT_PERCENT_CHANGE
                )
                + (
                    item["range_score"]
                    * self.WEIGHT_RANGE
                )
                + (
                    item["open_displacement_score"]
                    * self.WEIGHT_OPEN_DISPLACEMENT
                )
                + (
                    item[
                        "average_price_displacement_score"
                    ]
                    * self.WEIGHT_AVG_PRICE_DISPLACEMENT
                )
                + (
                    item["volume_score"]
                    * self.WEIGHT_VOLUME
                )
            ) / 100.0

        # -----------------------------------------------------
        # Sort strongest movement
        # -----------------------------------------------------

        raw_candidates.sort(
            key=lambda item: (
                item["movement_score"],
                abs(item["percent_change"]),
                item["trade_volume"],
            ),
            reverse=True,
        )

        top_candidates: list[
            StockMovementCandidate
        ] = []

        for item in raw_candidates[
            :self._top_n
        ]:

            candidate = (
                StockMovementCandidate(
                    symbol=item["symbol"],
                    token=item["token"],
                    ltp=item["ltp"],
                    open_price=item["open_price"],
                    high=item["high"],
                    low=item["low"],
                    previous_close=item[
                        "previous_close"
                    ],
                    average_price=item[
                        "average_price"
                    ],
                    percent_change=item[
                        "percent_change"
                    ],
                    trade_volume=item[
                        "trade_volume"
                    ],
                    movement_score=round(
                        item["movement_score"],
                        2,
                    ),
                    direction=item["direction"],
                    range_percent=round(
                        item["range_percent"],
                        2,
                    ),
                    open_displacement_percent=round(
                        item[
                            "open_displacement_percent"
                        ],
                        2,
                    ),
                    average_price_displacement_percent=round(
                        item[
                            "average_price_displacement_percent"
                        ],
                        2,
                    ),
                    volume_score=round(
                        item["volume_score"],
                        2,
                    ),
                    quote=item["quote"],
                )
            )

            top_candidates.append(
                candidate
            )

        logger.info(
            "Stock Movement Screener: "
            "universe=%s resolved=%s quotes=%s top=%s",
            len(symbols),
            len(instruments),
            len(raw_candidates),
            len(top_candidates),
        )

        for rank, candidate in enumerate(
            top_candidates,
            1,
        ):

            logger.info(
                "Stock Movement Top %s: "
                "%s direction=%s score=%.2f "
                "change=%.2f%% range=%.2f%% "
                "volume=%.0f",
                rank,
                candidate.symbol,
                candidate.direction,
                candidate.movement_score,
                candidate.percent_change,
                candidate.range_percent,
                candidate.trade_volume,
            )

        return StockMovementScreenResult(
            success=bool(top_candidates),
            universe_count=len(symbols),
            quote_request_count=quote_request_count,
            successful_quote_count=len(
                raw_candidates
            ),
            failed_quote_count=(
                len(instruments)
                - len(raw_candidates)
            ),
            top_candidates=top_candidates,
            errors=errors,
        )

    # =========================================================
    # QUOTE PARSING
    # =========================================================

    @staticmethod
    def _extract_fetched(
        response,
    ) -> list[dict[str, Any]]:

        if not isinstance(response, dict):
            return []

        data = response.get("data")

        if not isinstance(data, dict):
            return []

        fetched = data.get("fetched")

        if not isinstance(fetched, list):
            return []

        return [
            item
            for item in fetched
            if isinstance(item, dict)
        ]

    def _parse_quote(
        self,
        symbol: str,
        token: str,
        quote: dict[str, Any],
    ) -> dict[str, Any] | None:

        ltp = self._number(
            quote.get("ltp")
        )

        open_price = self._number(
            quote.get("open")
        )

        high = self._number(
            quote.get("high")
        )

        low = self._number(
            quote.get("low")
        )

        previous_close = self._number(
            quote.get("close")
        )

        average_price = self._number(
            quote.get("avgPrice")
        )

        percent_change = self._number(
            quote.get("percentChange")
        )

        trade_volume = self._number(
            quote.get("tradeVolume")
        )

        if ltp is None:
            return None

        if open_price is None or open_price <= 0:
            return None

        if high is None or low is None:
            return None

        if previous_close is None or previous_close <= 0:
            return None

        if average_price is None or average_price <= 0:
            average_price = ltp

        if percent_change is None:
            percent_change = (
                (
                    ltp - previous_close
                )
                / previous_close
            ) * 100.0

        if trade_volume is None:
            trade_volume = 0.0

        range_percent = (
            max(
                high - low,
                0.0,
            )
            / previous_close
        ) * 100.0

        open_displacement_percent = (
            abs(
                ltp - open_price
            )
            / open_price
        ) * 100.0

        average_price_displacement_percent = (
            abs(
                ltp - average_price
            )
            / average_price
        ) * 100.0

        direction = (
            "BULLISH"
            if percent_change > 0
            else "BEARISH"
            if percent_change < 0
            else "NEUTRAL"
        )

        return {
            "symbol": symbol,
            "token": token,
            "ltp": ltp,
            "open_price": open_price,
            "high": high,
            "low": low,
            "previous_close": previous_close,
            "average_price": average_price,
            "percent_change": percent_change,
            "trade_volume": trade_volume,
            "range_percent": range_percent,
            "open_displacement_percent": (
                open_displacement_percent
            ),
            "average_price_displacement_percent": (
                average_price_displacement_percent
            ),
            "direction": direction,
            "percent_change_score": 0.0,
            "range_score": 0.0,
            "open_displacement_score": 0.0,
            "average_price_displacement_score": 0.0,
            "volume_score": 0.0,
            "movement_score": 0.0,
            "quote": quote,
        }

    # =========================================================
    # NORMALIZATION
    # =========================================================

    @staticmethod
    def _percentile_scores(
        values: list[float],
    ) -> list[float]:

        if not values:
            return []

        indexed = sorted(
            range(len(values)),
            key=lambda index: values[index],
        )

        scores = [0.0] * len(values)

        if len(values) == 1:
            scores[0] = 100.0
            return scores

        for rank, index in enumerate(
            indexed
        ):

            scores[index] = (
                rank
                / (len(values) - 1)
            ) * 100.0

        return scores

    @staticmethod
    def _bounded_percentile_scores(
        values: list[float],
    ) -> list[float]:

        if not values:
            return []

        scores = StockMovementScreener._percentile_scores(
            values
        )

        return [
            max(
                0.0,
                min(
                    100.0,
                    score,
                ),
            )
            for score in scores
        ]

    # =========================================================
    # NSE INSTRUMENT
    # =========================================================

    @staticmethod
    def _select_nse_record(
        symbol: str,
        records: list[dict[str, Any]],
    ) -> dict[str, Any]:

        exact = [
            record
            for record in records
            if str(
                record.get(
                    "display_symbol",
                    "",
                )
            ).upper()
            == f"{symbol.upper()}-EQ"
        ]

        if exact:
            return exact[0]

        valid = [
            record
            for record in records
            if record.get("token")
        ]

        if not valid:
            raise RuntimeError(
                f"No valid NSE token found for {symbol}"
            )

        return valid[0]

    # =========================================================
    # BROKER
    # =========================================================

    def _ensure_broker(self):

        if self._initialized:
            return

        self._broker_manager.initialize()

        self._initialized = True

    # =========================================================
    # NUMBER
    # =========================================================

    @staticmethod
    def _number(value) -> float | None:

        if value in (
            None,
            "",
        ):
            return None

        try:
            return float(value)

        except (
            TypeError,
            ValueError,
        ):
            return None


# =============================================================
# SCORE CALCULATION PATCH
# =============================================================

def _movement_score_components(
    candidates: list[dict[str, Any]],
) -> None:

    if not candidates:
        return

    percent_values = [
        abs(
            item["percent_change"]
        )
        for item in candidates
    ]

    range_values = [
        item["range_percent"]
        for item in candidates
    ]

    open_values = [
        item["open_displacement_percent"]
        for item in candidates
    ]

    average_values = [
        item[
            "average_price_displacement_percent"
        ]
        for item in candidates
    ]

    percent_scores = (
        StockMovementScreener._bounded_percentile_scores(
            percent_values
        )
    )

    range_scores = (
        StockMovementScreener._bounded_percentile_scores(
            range_values
        )
    )

    open_scores = (
        StockMovementScreener._bounded_percentile_scores(
            open_values
        )
    )

    average_scores = (
        StockMovementScreener._bounded_percentile_scores(
            average_values
        )
    )

    for index, item in enumerate(
        candidates
    ):

        item["percent_change_score"] = (
            percent_scores[index]
        )

        item["range_score"] = (
            range_scores[index]
        )

        item["open_displacement_score"] = (
            open_scores[index]
        )

        item[
            "average_price_displacement_score"
        ] = average_scores[index]


_original_screen = (
    StockMovementScreener.screen
)


def _screen_with_components(
    self,
) -> StockMovementScreenResult:

    self._ensure_broker()

    symbols = list(
        self._universe.stock_symbols
    )

    if not symbols:
        return StockMovementScreenResult(
            success=False,
            universe_count=0,
            quote_request_count=0,
            successful_quote_count=0,
            failed_quote_count=0,
            top_candidates=[],
            errors=[
                {
                    "stage": "universe",
                    "error": "Stock universe is empty.",
                }
            ],
        )

    instruments = []
    errors = []

    for symbol in symbols:

        try:

            records = (
                self._parser.get_by_exchange_symbol(
                    "NSE",
                    symbol,
                )
            )

            selected = (
                self._select_nse_record(
                    symbol,
                    records,
                )
            )

            instruments.append(
                {
                    "symbol": symbol,
                    "token": str(
                        selected["token"]
                    ),
                }
            )

        except Exception as exc:

            errors.append(
                {
                    "symbol": symbol,
                    "stage": "instrument_resolution",
                    "error": str(exc),
                }
            )

    quote_map = {}
    quote_request_count = 0

    for start in range(
        0,
        len(instruments),
        self._batch_size,
    ):

        batch = instruments[
            start:start + self._batch_size
        ]

        tokens = [
            item["token"]
            for item in batch
        ]

        try:

            quote_request_count += 1

            logger.info(
                "Stock Movement Screener: "
                "live quote batch %s-%s of %s",
                start + 1,
                min(
                    start + self._batch_size,
                    len(instruments),
                ),
                len(instruments),
            )

            response = (
                self._broker_manager
                .smartapi_client
                .get_quotes(
                    exchange="NSE",
                    symbol_tokens=tokens,
                )
            )

            for quote in self._extract_fetched(
                response
            ):

                token = str(
                    quote.get(
                        "symbolToken",
                        "",
                    )
                ).strip()

                if token:
                    quote_map[token] = quote

        except Exception as exc:

            errors.append(
                {
                    "stage": "quote_batch",
                    "batch_start": start,
                    "batch_size": len(batch),
                    "error": str(exc),
                }
            )

            logger.error(
                "Stock Movement Screener: "
                "quote batch failed: %s",
                exc,
            )

    raw_candidates = []

    for instrument in instruments:

        quote = quote_map.get(
            instrument["token"]
        )

        if not quote:
            continue

        parsed = self._parse_quote(
            symbol=instrument["symbol"],
            token=instrument["token"],
            quote=quote,
        )

        if parsed is not None:
            raw_candidates.append(parsed)

    _movement_score_components(
        raw_candidates
    )

    volume_scores = (
        self._percentile_scores(
            [
                item["trade_volume"]
                for item in raw_candidates
            ]
        )
    )

    for index, item in enumerate(
        raw_candidates
    ):

        item["volume_score"] = (
            volume_scores[index]
            if index < len(volume_scores)
            else 0.0
        )

        item["movement_score"] = (
            (
                item["percent_change_score"]
                * self.WEIGHT_PERCENT_CHANGE
            )
            + (
                item["range_score"]
                * self.WEIGHT_RANGE
            )
            + (
                item["open_displacement_score"]
                * self.WEIGHT_OPEN_DISPLACEMENT
            )
            + (
                item[
                    "average_price_displacement_score"
                ]
                * self.WEIGHT_AVG_PRICE_DISPLACEMENT
            )
            + (
                item["volume_score"]
                * self.WEIGHT_VOLUME
            )
        ) / 100.0

    raw_candidates.sort(
        key=lambda item: (
            item["movement_score"],
            abs(item["percent_change"]),
            item["trade_volume"],
        ),
        reverse=True,
    )

    top_candidates = []

    for item in raw_candidates[
        :self._top_n
    ]:

        top_candidates.append(
            StockMovementCandidate(
                symbol=item["symbol"],
                token=item["token"],
                ltp=item["ltp"],
                open_price=item["open_price"],
                high=item["high"],
                low=item["low"],
                previous_close=item[
                    "previous_close"
                ],
                average_price=item[
                    "average_price"
                ],
                percent_change=item[
                    "percent_change"
                ],
                trade_volume=item[
                    "trade_volume"
                ],
                movement_score=round(
                    item["movement_score"],
                    2,
                ),
                direction=item["direction"],
                range_percent=round(
                    item["range_percent"],
                    2,
                ),
                open_displacement_percent=round(
                    item[
                        "open_displacement_percent"
                    ],
                    2,
                ),
                average_price_displacement_percent=round(
                    item[
                        "average_price_displacement_percent"
                    ],
                    2,
                ),
                volume_score=round(
                    item["volume_score"],
                    2,
                ),
                quote=item["quote"],
            )
        )

    for rank, candidate in enumerate(
        top_candidates,
        1,
    ):

        logger.info(
            "Stock Movement Top %s: "
            "%s direction=%s score=%.2f "
            "change=%.2f%% range=%.2f%% "
            "volume=%.0f",
            rank,
            candidate.symbol,
            candidate.direction,
            candidate.movement_score,
            candidate.percent_change,
            candidate.range_percent,
            candidate.trade_volume,
        )

    return StockMovementScreenResult(
        success=bool(top_candidates),
        universe_count=len(symbols),
        quote_request_count=quote_request_count,
        successful_quote_count=len(
            raw_candidates
        ),
        failed_quote_count=(
            len(instruments)
            - len(raw_candidates)
        ),
        top_candidates=top_candidates,
        errors=errors,
    )


StockMovementScreener.screen = (
    _screen_with_components
)
