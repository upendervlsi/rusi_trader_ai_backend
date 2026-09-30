"""
RUSI Trader AI
SENSEX BFO Paper Trading Scheduler

Stage 3

Architecture
------------
Market Pulse
    ->
SENSEX_FNO signal
    ->
BULLISH / BEARISH
    ->
BFO OptionResolver
    ->
SENSEX Paper Trading Service
    ->
5 lots = 100 units

Safety
------
- SENSEX only
- BFO only
- PAPER execution only
- one open position at a time
- no real broker execution
- independent SENSEX state directory
- independent 15:15 cutoff
- NIFTY TradingEngineService is untouched
"""

from __future__ import annotations

import logging
import threading
import time
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from backend.services.market_pulse_service import (
    MarketPulseService,
)

from backend.services.market_pulse_scanner_service import (
    MarketPulseScannerService,
)

from backend.services.sensex_paper_trading_service import (
    SensexPaperTradingService,
)

from tools.market_universe.option_resolver import (
    OptionResolver,
)


logger = logging.getLogger(__name__)


class SensexPaperScheduler:

    _instance = None

    MARKET = "SENSEX_FNO"
    UNDERLYING = "SENSEX"
    EXCHANGE = "BFO"

    # BFO SENSEX contract size is 20.
    SENSEX_LOTS = 5
    CONTRACT_LOT_SIZE = 20
    EXPECTED_QUANTITY = (
        SENSEX_LOTS * CONTRACT_LOT_SIZE
    )

    MARKET_TIMEZONE = ZoneInfo(
        "Asia/Kolkata"
    )

    ENTRY_START_HOUR = 9
    ENTRY_START_MINUTE = 15

    ENTRY_CUTOFF_HOUR = 15
    ENTRY_CUTOFF_MINUTE = 15

    FORCE_EXIT_HOUR = 15
    FORCE_EXIT_MINUTE = 15

    POSITION_MONITOR_INTERVAL = 60

    # Market Pulse is scanned approximately once per minute.
    # Never enter from an old/stale SENSEX signal.
    MAX_PULSE_AGE_SECONDS = 90
    ENTRY_SCAN_INTERVAL = 60

    def __new__(cls):

        if cls._instance is None:

            cls._instance = super().__new__(cls)

            cls._instance._thread = None
            cls._instance._running = False
            cls._instance._service = None
            cls._instance._pulse = None
            cls._instance._resolver = None

        return cls._instance

    # ========================================================
    # START / STOP
    # ========================================================

    def start(self, service=None):

        if self._running:

            logger.info(
                "SENSEX Paper Scheduler already running."
            )

            return

        self._service = (
            service
            if service is not None
            else SensexPaperTradingService()
        )

        self._pulse = MarketPulseService()

        # Targeted Market Pulse refresh service.
        #
        # The global Market Pulse scheduler continues to run every
        # five minutes. SENSEX can request a fresh analysis immediately
        # before an entry so the 90-second freshness guard remains
        # meaningful.
        self._pulse_scanner = MarketPulseScannerService()

        self._resolver = OptionResolver()

        # HARD SAFETY
        execution_engine = (
            getattr(
                self._service,
                "_execution_engine",
                None,
            )
        )

        if execution_engine is None:
            raise RuntimeError(
                "SENSEX service has no execution engine."
            )

        if not execution_engine.is_paper_engine():
            raise RuntimeError(
                "SENSEX scheduler refuses to start "
                "with a non-paper execution engine."
            )

        self._running = True

        self._thread = threading.Thread(
            target=self._run_scheduler,
            daemon=True,
            name="SensexPaperScheduler",
        )

        self._thread.start()

        logger.info(
            "SENSEX Paper Scheduler Started | "
            "lots=%d lot_size=%d quantity=%d "
            "cutoff=%02d:%02d",
            self.SENSEX_LOTS,
            self.CONTRACT_LOT_SIZE,
            self.EXPECTED_QUANTITY,
            self.ENTRY_CUTOFF_HOUR,
            self.ENTRY_CUTOFF_MINUTE,
        )

    def stop(self):

        if not self._running:
            return

        logger.info(
            "Stopping SENSEX Paper Scheduler..."
        )

        self._running = False

        thread = self._thread

        if (
            thread is not None
            and thread.is_alive()
            and thread is not threading.current_thread()
        ):

            thread.join(timeout=2.0)

        self._thread = None

        logger.info(
            "SENSEX Paper Scheduler Stopped"
        )

    @property
    def running(self) -> bool:
        return self._running

    # ========================================================
    # TIME HELPERS
    # ========================================================

    @classmethod
    def _now(cls) -> datetime:

        return datetime.now(
            cls.MARKET_TIMEZONE
        )

    @classmethod
    def _entry_allowed(
        cls,
        now: datetime,
    ) -> bool:

        current = (
            now.hour,
            now.minute,
        )

        start = (
            cls.ENTRY_START_HOUR,
            cls.ENTRY_START_MINUTE,
        )

        cutoff = (
            cls.ENTRY_CUTOFF_HOUR,
            cls.ENTRY_CUTOFF_MINUTE,
        )

        return start <= current < cutoff

    @classmethod
    def _force_exit_time(
        cls,
        now: datetime,
    ) -> bool:

        current = (
            now.hour,
            now.minute,
        )

        cutoff = (
            cls.FORCE_EXIT_HOUR,
            cls.FORCE_EXIT_MINUTE,
        )

        return current >= cutoff

    # ========================================================
    # POSITION HELPERS
    # ========================================================

    def _has_open_position(self) -> bool:

        status = self._service.status()

        positions = (
            status.get("positions")
            or []
        )

        return bool(positions)

    # ========================================================
    # MARKET PULSE
    # ========================================================

    def _get_sensex_pulse(self):

        #
        # First reuse an existing fresh SENSEX Market Pulse.
        #
        # The global Market Pulse scanner may already have refreshed
        # SENSEX recently. Avoid an unnecessary SmartAPI historical
        # request when the existing pulse is still within the
        # SENSEX freshness window.
        #

        now = self._now()

        pulse_list = (
            self._pulse.get_market_pulse(
                updated_time=now.isoformat()
            )
        )

        current_pulse = None

        for pulse in pulse_list:

            if (
                str(
                    getattr(
                        pulse,
                        "market",
                        "",
                    )
                ).upper()
                == self.MARKET
            ):

                current_pulse = pulse
                break

        if current_pulse is not None:

            updated_raw = getattr(
                current_pulse,
                "updated_time",
                None,
            )

            if updated_raw:

                try:

                    updated_time = datetime.fromisoformat(
                        str(
                            updated_raw
                        ).replace(
                            "Z",
                            "+00:00",
                        )
                    )

                    if updated_time.tzinfo is not None:

                        age_seconds = (
                            now.astimezone(
                                timezone.utc
                            )
                            - updated_time.astimezone(
                                timezone.utc
                            )
                        ).total_seconds()

                        if (
                            0 <= age_seconds
                            <= self.MAX_PULSE_AGE_SECONDS
                        ):

                            logger.info(
                                "SENSEX Market Pulse reused | "
                                "age=%.1fs signal=%s",
                                age_seconds,
                                getattr(
                                    current_pulse,
                                    "signal",
                                    "UNKNOWN",
                                ),
                            )

                            return current_pulse

                except (
                    TypeError,
                    ValueError,
                ):

                    pass

        #
        # Existing pulse is missing or stale.
        # Request a targeted SENSEX refresh.
        #

        try:

            self._pulse_scanner.scan_market(
                "SENSEX_FNO"
            )

        except Exception:

            logger.exception(
                "SENSEX targeted Market Pulse refresh failed"
            )

        #
        # Read the refreshed pulse.
        #

        now = self._now()

        pulse_list = (
            self._pulse.get_market_pulse(
                updated_time=now.isoformat()
            )
        )

        for pulse in pulse_list:

            if (
                str(
                    getattr(
                        pulse,
                        "market",
                        "",
                    )
                ).upper()
                == self.MARKET
            ):

                return pulse

        return None

    # ========================================================
    # MARKET PULSE FRESHNESS
    # ========================================================

    def _validate_fresh_sensex_pulse(
        self,
        pulse,
    ) -> tuple[bool, str]:
        """Validate that SENSEX entry signal is current and usable.

        This guard is intentionally local to SENSEX paper trading.
        Shared Market Pulse and NIFTY behavior are not modified.
        """

        status = str(
            getattr(
                pulse,
                "status",
                "",
            )
            or ""
        ).upper().strip()

        if status != "LIVE":
            return (
                False,
                f"Market Pulse status is not LIVE: {status or 'EMPTY'}",
            )

        signal = str(
            getattr(
                pulse,
                "signal",
                "",
            )
            or ""
        ).upper().strip()

        if signal not in {"BULLISH", "BEARISH"}:
            return (
                False,
                f"Market Pulse signal is not entry eligible: "
                f"{signal or 'EMPTY'}",
            )

        confidence = getattr(
            pulse,
            "confidence",
            None,
        )

        if confidence is None:
            return (
                False,
                "Market Pulse confidence is missing.",
            )

        try:
            confidence_value = float(confidence)
        except (TypeError, ValueError):
            return (
                False,
                f"Market Pulse confidence is invalid: {confidence!r}",
            )

        if confidence_value < 0:
            return (
                False,
                f"Market Pulse confidence is invalid: {confidence_value}",
            )

        last_price = getattr(
            pulse,
            "last_price",
            None,
        )

        try:
            last_price_value = float(last_price)
        except (TypeError, ValueError):
            return (
                False,
                f"Market Pulse last_price is invalid: {last_price!r}",
            )

        if last_price_value <= 0:
            return (
                False,
                f"Market Pulse last_price is invalid: {last_price_value}",
            )

        updated_raw = getattr(
            pulse,
            "updated_time",
            None,
        )

        if not updated_raw:
            return (
                False,
                "Market Pulse updated_time is missing.",
            )

        try:
            updated_time = datetime.fromisoformat(
                str(updated_raw).replace("Z", "+00:00")
            )
        except (TypeError, ValueError):
            return (
                False,
                f"Market Pulse updated_time is invalid: {updated_raw!r}",
            )

        if updated_time.tzinfo is None:
            return (
                False,
                "Market Pulse updated_time has no timezone.",
            )

        now = self._now()
        age_seconds = (
            now.astimezone(timezone.utc)
            - updated_time.astimezone(timezone.utc)
        ).total_seconds()

        if age_seconds < 0:
            return (
                False,
                f"Market Pulse timestamp is in the future: "
                f"age={age_seconds:.1f}s",
            )

        if age_seconds > self.MAX_PULSE_AGE_SECONDS:
            return (
                False,
                f"Market Pulse is stale: age={age_seconds:.1f}s "
                f"> {self.MAX_PULSE_AGE_SECONDS}s",
            )

        return (
            True,
            f"Fresh SENSEX pulse: age={age_seconds:.1f}s "
            f"signal={signal} confidence={confidence_value:.4f} "
            f"last_price={last_price_value:.2f}",
        )

    # ========================================================
    # OPTION CANDIDATE
    # ========================================================

    def _resolve_candidate(
        self,
        pulse,
    ) -> tuple[dict | None, str]:

        signal = str(
            getattr(
                pulse,
                "signal",
                "",
            )
            or ""
        ).upper().strip()

        if signal not in {
            "BULLISH",
            "BEARISH",
        }:

            return (
                None,
                (
                    "Market Pulse signal is not "
                    f"entry eligible: {signal or 'EMPTY'}"
                ),
            )

        underlying_price = float(
            getattr(
                pulse,
                "last_price",
                0,
            )
            or 0
        )

        if underlying_price <= 0:

            return (
                None,
                "Market Pulse has no valid SENSEX price.",
            )

        # IMPORTANT:
        # Do not use default_strategy() for SENSEX because
        # the existing resolver's generic recommendation
        # mapping has previously produced incorrect PE
        # semantics for directional SENSEX validation.
        #
        # Explicit SENSEX mapping:
        #     BULLISH -> CE
        #     BEARISH -> PE

        recommendation = (
            "BUY"
            if signal == "BULLISH"
            else "SELL"
        )

        contract = self._resolver.resolve(
            underlying_symbol=self.UNDERLYING,
            recommendation=recommendation,
            underlying_price=underlying_price,
            exchange=self.EXCHANGE,
        )

        if contract is None:

            return (
                None,
                (
                    "No BFO SENSEX option contract "
                    "resolved."
                ),
            )

        expected_option_type = (
            "CE"
            if signal == "BULLISH"
            else "PE"
        )

        actual_option_type = str(
            getattr(
                contract,
                "option_type",
                "",
            )
            or ""
        ).upper()

        if actual_option_type != expected_option_type:

            return (
                None,
                (
                    "Resolved option type mismatch: "
                    f"signal={signal} "
                    f"expected={expected_option_type} "
                    f"actual={actual_option_type}"
                ),
            )

        contract_lot_size = int(
            getattr(
                contract,
                "lot_size",
                0,
            )
            or 0
        )

        if contract_lot_size != self.CONTRACT_LOT_SIZE:

            return (
                None,
                (
                    "Unexpected BFO SENSEX lot size: "
                    f"{contract_lot_size}; "
                    f"expected={self.CONTRACT_LOT_SIZE}"
                ),
            )

        candidate = {
            "option_symbol": str(
                getattr(
                    contract,
                    "symbol",
                    "",
                )
                or ""
            ),
            "token": str(
                getattr(
                    contract,
                    "token",
                    "",
                )
                or ""
            ),
            "exchange": self.EXCHANGE,
            "option_type": actual_option_type,
            "strike": float(
                getattr(
                    contract,
                    "strike",
                    0,
                )
                or 0
            ),
            "expiry": str(
                getattr(
                    contract,
                    "expiry",
                    "",
                )
                or ""
            ),
            "lot_size": contract_lot_size,
            "underlying": self.UNDERLYING,
        }

        if not candidate["option_symbol"]:
            return None, "Resolved contract has no option symbol."

        if not candidate["token"]:
            return None, "Resolved contract has no broker token."

        return candidate, (
            f"Resolved {signal} -> "
            f"{actual_option_type} "
            f"{candidate['option_symbol']}"
        )

    # ========================================================
    # ENTRY
    # ========================================================

    def _try_entry(self) -> dict:

        if self._has_open_position():

            return {
                "action": "POSITION_OPEN",
                "message": (
                    "SENSEX paper position already open."
                ),
            }

        pulse = self._get_sensex_pulse()

        if pulse is None:

            return {
                "action": "NO_SIGNAL",
                "message": (
                    "No SENSEX_FNO Market Pulse state."
                ),
            }

        pulse_fresh, freshness_message = (
            self._validate_fresh_sensex_pulse(
                pulse
            )
        )

        if not pulse_fresh:

            logger.warning(
                "SENSEX entry blocked by Market Pulse freshness guard | %s",
                freshness_message,
            )

            return {
                "action": "STALE_SIGNAL",
                "message": freshness_message,
            }

        signal = str(
            getattr(
                pulse,
                "signal",
                "",
            )
            or ""
        ).upper()

        confidence = float(
            getattr(
                pulse,
                "confidence",
                0,
            )
            or 0
        )

        status = str(
            getattr(
                pulse,
                "status",
                "",
            )
            or ""
        )

        reason = str(
            getattr(
                pulse,
                "reason",
                "",
            )
            or ""
        )

        logger.info(
            "SENSEX Market Pulse | "
            "signal=%s confidence=%.4f status=%s reason=%s",
            signal,
            confidence,
            status,
            reason,
        )

        candidate, message = (
            self._resolve_candidate(
                pulse
            )
        )

        if candidate is None:

            return {
                "action": "NO_TRADE",
                "message": message,
                "signal": signal,
                "confidence": confidence,
            }

        result = self._service.paper_trade(
            candidate=candidate,
            direction=signal,
        )

        if result.get("success"):

            position = (
                result.get("position")
                or {}
            )

            quantity = int(
                position.get(
                    "quantity",
                    0,
                )
                or 0
            )

            # HARD QUANTITY VALIDATION
            if quantity != self.EXPECTED_QUANTITY:

                logger.error(
                    "SENSEX QUANTITY SAFETY FAILURE | "
                    "expected=%d actual=%d",
                    self.EXPECTED_QUANTITY,
                    quantity,
                )

                # Do not attempt any broker action.
                # This is paper-only. Leave diagnosis in logs.
                return {
                    "action": "QUANTITY_MISMATCH",
                    "message": (
                        "SENSEX paper trade filled with "
                        "unexpected quantity."
                    ),
                    "expected_quantity": (
                        self.EXPECTED_QUANTITY
                    ),
                    "actual_quantity": quantity,
                    "result": result,
                }

            logger.info(
                "SENSEX PAPER ENTRY | "
                "signal=%s option=%s quantity=%d",
                signal,
                result.get("option_symbol"),
                quantity,
            )

        return result

    # ========================================================
    # ONE CYCLE
    # ========================================================

    def run_cycle(self) -> dict:

        if self._service is None:

            self._service = (
                SensexPaperTradingService()
            )

        now = self._now()

        # Weekend guard.
        if now.weekday() >= 5:

            return {
                "action": "MARKET_CLOSED",
                "message": "Weekend.",
            }

        # ----------------------------------------------------
        # HARD 15:15 EXIT BOUNDARY
        # ----------------------------------------------------

        if self._force_exit_time(now):

            if self._has_open_position():

                result = (
                    self._service
                    .close_paper_position_admin()
                )

                logger.info(
                    "SENSEX forced paper exit at 15:15 | %s",
                    result,
                )

                return result

            return {
                "action": "CUTOFF",
                "message": (
                    "SENSEX entry/monitor cycle "
                    "past 15:15 cutoff."
                ),
            }

        # ----------------------------------------------------
        # OPEN POSITION
        # ----------------------------------------------------

        if self._has_open_position():

            result = (
                self._service
                .monitor_open_position()
            )

            logger.info(
                "SENSEX paper monitor | %s",
                result,
            )

            return result

        # ----------------------------------------------------
        # NEW ENTRY
        # ----------------------------------------------------

        if not self._entry_allowed(now):

            return {
                "action": "ENTRY_BLOCKED",
                "message": (
                    "Outside SENSEX new-entry window."
                ),
            }

        return self._try_entry()

    # ========================================================
    # BACKGROUND LOOP
    # ========================================================

    def _run_scheduler(self):

        logger.info(
            "SENSEX scheduler loop started."
        )

        while self._running:

            try:

                result = self.run_cycle()

                action = (
                    result.get("action")
                    if isinstance(result, dict)
                    else None
                )

                logger.info(
                    "SENSEX scheduler cycle | action=%s",
                    action,
                )

            except Exception:

                logger.exception(
                    "SENSEX scheduler cycle failed."
                )

            time.sleep(
                self.POSITION_MONITOR_INTERVAL
            )

        logger.info(
            "SENSEX scheduler loop stopped."
        )
