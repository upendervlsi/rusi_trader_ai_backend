"""
RUSI Trader AI

Stock Option Quote Quality

Independent quality extraction for OPTSTK contracts.
Does not modify the existing NIFTY option ranking path.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Iterable


@dataclass(slots=True)
class StockOptionQuote:
    option_symbol: str
    token: str
    exchange: str
    ltp: float | None
    volume: float | None
    open_interest: float | None
    avg_price: float | None
    last_trade_qty: float | None
    best_bid: float | None
    best_ask: float | None
    bid_quantity: float | None
    ask_quantity: float | None
    bid_depth_quantity: float | None
    ask_depth_quantity: float | None
    net_change: float | None
    percent_change: float | None
    exchange_feed_time: str | None
    exchange_trade_time: str | None


@dataclass(slots=True)
class StockOptionQuality:
    option_symbol: str
    token: str
    ltp: float | None
    mid_price: float | None
    spread: float | None
    spread_percent: float | None
    volume: float | None
    open_interest: float | None
    volume_oi_ratio: float | None
    bid_quantity: float | None
    ask_quantity: float | None
    depth_quantity: float | None
    depth_imbalance: float | None
    quote_completeness: float
    quality_score: float | None = None
    rank: int | None = None
    components: dict[str, float] | None = None


class StockOptionQualityAnalyzer:
    """
    Extract and compare real option quote quality.

    No fixed liquidity thresholds are used.
    Candidate-group ranking is relative to the candidates supplied.
    """

    def normalize_quote(
        self,
        quote: dict[str, Any],
        option_symbol: str,
        token: str,
    ) -> StockOptionQuote:

        fetched = (
            (quote or {}).get("data") or {}
        ).get("fetched") or []

        if not fetched:
            raise ValueError(
                f"No quote data returned for {option_symbol}"
            )

        row = fetched[0]

        depth = row.get("depth") or {}
        buy = depth.get("buy") or []
        sell = depth.get("sell") or []

        return StockOptionQuote(
            option_symbol=str(
                row.get("tradingSymbol") or option_symbol
            ),
            token=str(
                row.get("symbolToken") or token
            ),
            exchange=str(
                row.get("exchange") or "NFO"
            ),
            ltp=self._number(row.get("ltp")),
            volume=self._number(
                row.get("tradeVolume")
            ),
            open_interest=self._number(
                row.get("opnInterest")
            ),
            avg_price=self._number(
                row.get("avgPrice")
            ),
            last_trade_qty=self._number(
                row.get("lastTradeQty")
            ),
            best_bid=self._best_depth_price(buy),
            best_ask=self._best_depth_price(sell),
            bid_quantity=self._number(
                row.get("totBuyQuan")
            ),
            ask_quantity=self._number(
                row.get("totSellQuan")
            ),
            bid_depth_quantity=self._sum_depth_quantity(
                buy
            ),
            ask_depth_quantity=self._sum_depth_quantity(
                sell
            ),
            net_change=self._number(
                row.get("netChange")
            ),
            percent_change=self._number(
                row.get("percentChange")
            ),
            exchange_feed_time=row.get(
                "exchFeedTime"
            ),
            exchange_trade_time=row.get(
                "exchTradeTime"
            ),
        )

    def measure(
        self,
        quote: StockOptionQuote,
    ) -> StockOptionQuality:

        mid = self._mid(
            quote.best_bid,
            quote.best_ask,
        )

        spread = self._spread(
            quote.best_bid,
            quote.best_ask,
        )

        spread_percent = self._ratio(
            spread,
            mid,
            percent=True,
        )

        volume_oi_ratio = self._ratio(
            quote.volume,
            quote.open_interest,
        )

        depth_quantity = self._sum_values(
            quote.bid_depth_quantity,
            quote.ask_depth_quantity,
        )

        depth_imbalance = self._imbalance(
            quote.bid_depth_quantity,
            quote.ask_depth_quantity,
        )

        completeness_fields = [
            quote.ltp,
            quote.volume,
            quote.open_interest,
            quote.best_bid,
            quote.best_ask,
            quote.bid_quantity,
            quote.ask_quantity,
        ]

        quote_completeness = (
            sum(
                value is not None
                for value in completeness_fields
            )
            / len(completeness_fields)
            * 100.0
        )

        return StockOptionQuality(
            option_symbol=quote.option_symbol,
            token=quote.token,
            ltp=quote.ltp,
            mid_price=mid,
            spread=spread,
            spread_percent=spread_percent,
            volume=quote.volume,
            open_interest=quote.open_interest,
            volume_oi_ratio=volume_oi_ratio,
            bid_quantity=quote.bid_quantity,
            ask_quantity=quote.ask_quantity,
            depth_quantity=depth_quantity,
            depth_imbalance=depth_imbalance,
            quote_completeness=quote_completeness,
        )

    def analyze(
        self,
        quote: dict[str, Any],
        option_symbol: str,
        token: str,
    ) -> StockOptionQuality:

        normalized = self.normalize_quote(
            quote,
            option_symbol,
            token,
        )

        return self.measure(normalized)

    def rank(
        self,
        qualities: Iterable[StockOptionQuality],
    ) -> list[StockOptionQuality]:

        items = list(qualities)

        if not items:
            return []

        metric_names = [
            "spread_percent",
            "volume",
            "open_interest",
            "depth_quantity",
            "quote_completeness",
        ]

        component_scores = {
            name: []
            for name in metric_names
        }

        for name in metric_names:

            values = [
                getattr(item, name)
                for item in items
                if getattr(item, name) is not None
            ]

            for item in items:

                value = getattr(item, name)

                if value is None or not values:
                    score = 0.0
                else:
                    score = self._percentile(
                        value,
                        values,
                        lower_is_better=(
                            name == "spread_percent"
                        ),
                    )

                component_scores[name].append(
                    score
                )

        ranked = []

        for index, item in enumerate(items):

            components = {
                name: component_scores[name][index]
                for name in metric_names
            }

            score = (
                sum(components.values())
                / len(components)
            )

            item.components = components
            item.quality_score = round(
                score,
                2,
            )

            ranked.append(item)

        ranked.sort(
            key=lambda item: (
                item.quality_score
                if item.quality_score is not None
                else -1.0
            ),
            reverse=True,
        )

        for position, item in enumerate(
            ranked,
            start=1,
        ):
            item.rank = position

        return ranked

    @staticmethod
    def to_dict(
        quality: StockOptionQuality,
    ) -> dict[str, Any]:

        return asdict(quality)

    @staticmethod
    def _number(
        value: Any,
    ) -> float | None:

        if value is None or value == "":
            return None

        try:
            return float(value)
        except (
            TypeError,
            ValueError,
        ):
            return None

    @staticmethod
    def _sum_depth_quantity(
        levels: list[dict[str, Any]],
    ) -> float | None:

        if not levels:
            return None

        total = 0.0
        found = False

        for level in levels:

            quantity = (
                StockOptionQualityAnalyzer
                ._number(level.get("quantity"))
            )

            if quantity is not None:
                total += quantity
                found = True

        return total if found else None

    @staticmethod
    def _best_depth_price(
        levels: list[dict[str, Any]],
    ) -> float | None:

        if not levels:
            return None

        return (
            StockOptionQualityAnalyzer
            ._number(levels[0].get("price"))
        )

    @staticmethod
    def _mid(
        bid: float | None,
        ask: float | None,
    ) -> float | None:

        if bid is None or ask is None:
            return None

        return (bid + ask) / 2.0

    @staticmethod
    def _spread(
        bid: float | None,
        ask: float | None,
    ) -> float | None:

        if bid is None or ask is None:
            return None

        return max(
            0.0,
            ask - bid,
        )

    @staticmethod
    def _ratio(
        numerator: float | None,
        denominator: float | None,
        percent: bool = False,
    ) -> float | None:

        if numerator is None:
            return None

        if denominator in (None, 0):
            return None

        value = numerator / denominator

        if percent:
            return value * 100.0

        return value

    @staticmethod
    def _sum_values(
        *values: float | None,
    ) -> float | None:

        present = [
            value
            for value in values
            if value is not None
        ]

        if not present:
            return None

        return sum(present)

    @staticmethod
    def _imbalance(
        bid: float | None,
        ask: float | None,
    ) -> float | None:

        if bid is None or ask is None:
            return None

        total = bid + ask

        if total == 0:
            return None

        return (bid - ask) / total

    @staticmethod
    def _percentile(
        value: float,
        values: list[float],
        lower_is_better: bool,
    ) -> float:

        if len(values) <= 1:
            return 100.0

        minimum = min(values)
        maximum = max(values)

        # If every candidate has the same value,
        # this metric provides no ranking information.
        # Give every candidate the same full score.
        if maximum == minimum:
            return 100.0

        ordered = sorted(values)

        rank = ordered.index(value)

        score = (
            rank
            / (len(ordered) - 1)
            * 100.0
        )

        if lower_is_better:
            return 100.0 - score

        return score
