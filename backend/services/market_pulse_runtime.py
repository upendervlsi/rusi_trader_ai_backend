"""
============================================================
RUSI Trader AI

Market Pulse Runtime

Maintains independent runtime state for the seven
dashboard markets.

IMPORTANT
---------
This runtime is analysis-only.

It does NOT:
    - place orders
    - modify portfolio positions
    - change the selected execution market
    - select an option contract
    - execute futures

The execution runtime remains owned by ExecutionManager.

Market Pulse will publish real analysis results into this
store once the multi-market analyzer is connected.
============================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, UTC
from threading import RLock


@dataclass
class MarketPulseState:

    market: str

    display_name: str

    signal: str = "WAIT"

    confidence: float | None = None

    status: str = "WAITING"

    updated_time: str = ""

    #
    # Analysis information
    #

    symbol: str = ""

    exchange: str = ""

    last_price: float | None = None

    trend: str = ""

    #
    # Optional AI information
    #

    score: float | None = None

    reason: str = ""


class MarketPulseRuntime:

    """
    Singleton runtime store for independent market analysis.

    This class intentionally contains no broker calls.

    A future Market Pulse Analyzer will publish results here.
    """

    _instance: MarketPulseRuntime | None = None

    MARKETS = (
        ("NIFTY_FNO", "NIFTY"),
        ("BANKNIFTY_FNO", "BANKNIFTY"),
        ("FINNIFTY_FNO", "FINNIFTY"),
        ("MIDCPNIFTY_FNO", "MIDCAP NIFTY"),
        ("SENSEX_FNO", "SENSEX"),
        ("BANKEX_FNO", "BANKEX"),
        ("CRUDEOIL_FNO", "CRUDE OIL"),
    )

    def __new__(cls):

        if cls._instance is None:

            cls._instance = super().__new__(cls)

            cls._instance._lock = RLock()

            cls._instance._states = {}

            cls._instance._initialize()

        return cls._instance

    # ---------------------------------------------------------
    # Initialization
    # ---------------------------------------------------------

    def _initialize(self):

        now = self._now()

        for market, display_name in self.MARKETS:

            self._states[market] = MarketPulseState(

                market=market,

                display_name=display_name,

                signal="WAIT",

                confidence=None,

                status="WAITING",

                updated_time=now,

            )

    # ---------------------------------------------------------
    # Time
    # ---------------------------------------------------------

    @staticmethod
    def _now() -> str:

        return datetime.now(
            UTC
        ).isoformat()

    # ---------------------------------------------------------
    # Market list
    # ---------------------------------------------------------

    def markets(self) -> list[str]:

        with self._lock:

            return list(
                self._states.keys()
            )

    # ---------------------------------------------------------
    # Get single state
    # ---------------------------------------------------------

    def get(
        self,
        market: str,
    ) -> MarketPulseState:

        with self._lock:

            state = self._states.get(
                market
            )

            if state is None:

                raise ValueError(
                    f"Unknown market: {market}"
                )

            return self._copy(
                state
            )

    # ---------------------------------------------------------
    # Get all states
    # ---------------------------------------------------------

    def all(self) -> list[MarketPulseState]:

        with self._lock:

            return [
                self._copy(state)
                for state in self._states.values()
            ]

    # ---------------------------------------------------------
    # Publish analysis result
    # ---------------------------------------------------------

    def publish(
        self,
        market: str,
        *,
        signal: str,
        confidence: float | None,
        status: str = "LIVE",
        symbol: str = "",
        exchange: str = "",
        last_price: float | None = None,
        trend: str = "",
        score: float | None = None,
        reason: str = "",
        updated_time: str | None = None,
    ) -> MarketPulseState:

        with self._lock:

            state = self._states.get(
                market
            )

            if state is None:

                raise ValueError(
                    f"Unknown market: {market}"
                )

            state.signal = (
                str(signal).upper()
            )

            if confidence is not None:

                state.confidence = float(
                    confidence
                )

            else:

                state.confidence = None

            state.status = (
                str(status).upper()
            )

            state.symbol = symbol

            state.exchange = exchange

            state.last_price = last_price

            state.trend = trend

            state.score = score

            state.reason = reason

            state.updated_time = (
                updated_time
                if updated_time
                else self._now()
            )

            return self._copy(
                state
            )

    # ---------------------------------------------------------
    # Reset
    # ---------------------------------------------------------

    def reset(
        self,
        market: str | None = None,
    ):

        with self._lock:

            now = self._now()

            if market is not None:

                state = self._states.get(
                    market
                )

                if state is None:

                    raise ValueError(
                        f"Unknown market: {market}"
                    )

                self._reset_state(
                    state,
                    now,
                )

                return

            for state in self._states.values():

                self._reset_state(
                    state,
                    now,
                )

    # ---------------------------------------------------------
    # Strongest market
    # ---------------------------------------------------------

    def strongest(
        self,
    ) -> MarketPulseState | None:

        with self._lock:

            valid = [

                state

                for state in self._states.values()

                if state.confidence is not None
                and state.status != "WAITING"
            ]

            if not valid:

                return None

            strongest = max(

                valid,

                key=lambda item:
                    item.confidence
                    if item.confidence is not None
                    else -1,
            )

            return self._copy(
                strongest
            )

    # ---------------------------------------------------------
    # Internal helpers
    # ---------------------------------------------------------

    @staticmethod
    def _reset_state(
        state: MarketPulseState,
        updated_time: str,
    ):

        state.signal = "WAIT"

        state.confidence = None

        state.status = "WAITING"

        state.updated_time = updated_time

        state.symbol = ""

        state.exchange = ""

        state.last_price = None

        state.trend = ""

        state.score = None

        state.reason = ""

    @staticmethod
    def _copy(
        state: MarketPulseState,
    ) -> MarketPulseState:

        return MarketPulseState(

            market=state.market,

            display_name=state.display_name,

            signal=state.signal,

            confidence=state.confidence,

            status=state.status,

            updated_time=state.updated_time,

            symbol=state.symbol,

            exchange=state.exchange,

            last_price=state.last_price,

            trend=state.trend,

            score=state.score,

            reason=state.reason,
        )
