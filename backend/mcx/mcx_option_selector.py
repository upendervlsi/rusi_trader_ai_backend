"""
RUSI Trader AI - MCX Option Selector.

MCX-only option contract selection.

Policy:
    BUY  -> CE
    SELL -> PE
    WAIT -> no option

Selection:
    1. Read MCX options from existing InstrumentMasterManager.
    2. Filter CE/PE from underlying direction.
    3. Remove expired contracts.
    4. Select nearest valid expiry.
    5. Select nearest strike to the underlying price.

Important:
    - Does not modify OptionResolver.
    - Does not modify OptionRanker.
    - Does not modify MCX Intelligence.
    - Does not place broker orders.
    - Does not modify NIFTY, Stock Options, or Midcap.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, date
from typing import Any

from tools.market_universe.instrument_master_manager import (
    InstrumentMasterManager,
)


SUPPORTED = {
    "crude": "CRUDEOILM",
    "gold": "GOLDM",
    "silver": "SILVERM",
}


@dataclass(slots=True)
class McxOptionSelection:
    analysis_symbol: str
    option_type: str
    strike: float
    expiry: str
    trade_symbol: str
    exchange: str
    token: str
    lot_size: int


class McxOptionSelector:
    """
    Isolated MCX option selector.

    This component resolves a real option contract only.
    It does not decide whether the underlying trade is qualified.
    """

    def __init__(self) -> None:
        self._master = InstrumentMasterManager()

    def select(
        self,
        analysis_symbol: str,
        signal: str,
        qualified: int,
        underlying_price: float,
    ) -> McxOptionSelection | None:
        symbol = str(analysis_symbol).upper().strip()
        direction = str(signal).upper().strip()

        if not qualified:
            return None

        if direction not in ("BUY", "SELL"):
            return None

        if underlying_price <= 0:
            return None

        option_type = "CE" if direction == "BUY" else "PE"

        options = self._master.get_options(
            exchange="MCX",
            underlying=symbol,
        )

        if not options:
            return None

        options = [
            option
            for option in options
            if str(option.get("option_type", "")).upper() == option_type
        ]

        if not options:
            return None

        options = self._remove_expired(options)

        if not options:
            return None

        expiry = self._nearest_expiry(options)

        options = [
            option
            for option in options
            if str(option.get("expiry", "")) == expiry
        ]

        if not options:
            return None

        selected = min(
            options,
            key=lambda option: abs(
                self._strike(option) - underlying_price
            ),
        )

        strike = self._strike(selected)

        trade_symbol = str(
            selected.get("display_symbol")
            or selected.get("tradingsymbol")
            or selected.get("symbol")
            or ""
        ).strip()

        if not trade_symbol:
            return None

        return McxOptionSelection(
            analysis_symbol=symbol,
            option_type=option_type,
            strike=strike,
            expiry=expiry,
            trade_symbol=trade_symbol,
            exchange=str(
                selected.get("exchange") or "MCX"
            ),
            token=str(
                selected.get("token") or ""
            ),
            lot_size=self._lot_size(selected),
        )

    def _remove_expired(
        self,
        options: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        today = date.today()

        valid = []

        for option in options:
            expiry = self._parse_expiry(
                option.get("expiry")
            )

            if expiry is None:
                continue

            if expiry.date() >= today:
                valid.append(option)

        return valid

    def _nearest_expiry(
        self,
        options: list[dict[str, Any]],
    ) -> str:
        parsed = []

        for option in options:
            expiry_text = str(
                option.get("expiry") or ""
            ).strip()

            expiry = self._parse_expiry(
                expiry_text
            )

            if expiry is not None:
                parsed.append(
                    (expiry, expiry_text)
                )

        if not parsed:
            raise RuntimeError(
                "MCX option expiry could not be parsed"
            )

        parsed.sort(
            key=lambda item: item[0]
        )

        return parsed[0][1]

    @staticmethod
    def _parse_expiry(
        value: Any,
    ) -> datetime | None:
        if value is None:
            return None

        text = str(value).strip()

        formats = (
            "%d%b%Y",
            "%d%b%y",
            "%d-%b-%Y",
            "%d-%b-%y",
            "%Y-%m-%d",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%S%z",
        )

        for fmt in formats:
            try:
                return datetime.strptime(
                    text,
                    fmt,
                )
            except ValueError:
                continue

        return None

    @staticmethod
    def _strike(
        option: dict[str, Any],
    ) -> float:
        value = option.get("strike")

        try:
            return float(value)
        except (TypeError, ValueError) as exc:
            raise RuntimeError(
                f"Invalid MCX option strike: {value}"
            ) from exc

    @staticmethod
    def _lot_size(
        option: dict[str, Any],
    ) -> int:
        value = (
            option.get("lotsize")
            or option.get("lot_size")
            or 0
        )

        try:
            return int(float(value))
        except (TypeError, ValueError):
            return 0


def select_mcx_option(
    analysis_symbol: str,
    signal: str,
    qualified: int,
    underlying_price: float,
) -> McxOptionSelection | None:
    """
    Convenience entry point for MCX callers.
    """
    return McxOptionSelector().select(
        analysis_symbol=analysis_symbol,
        signal=signal,
        qualified=qualified,
        underlying_price=underlying_price,
    )


if __name__ == "__main__":
    print("=" * 72)
    print("RUSI MCX OPTION SELECTOR TEST")
    print("=" * 72)

    selector = McxOptionSelector()

    tests = (
        ("CRUDEOILM", "SELL", 1, 9528.0),
        ("GOLDM", "BUY", 1, 152900.0),
        ("SILVERM", "BUY", 1, 236859.0),
        ("SILVERM", "WAIT", 1, 236859.0),
        ("CRUDEOILM", "SELL", 0, 9528.0),
    )

    for symbol, signal, qualified, price in tests:
        print()
        print("-" * 72)
        print(
            f"UNDERLYING : {symbol}"
        )
        print(
            f"SIGNAL     : {signal}"
        )
        print(
            f"QUALIFIED  : {qualified}"
        )
        print(
            f"LTP        : {price}"
        )

        try:
            result = selector.select(
                analysis_symbol=symbol,
                signal=signal,
                qualified=qualified,
                underlying_price=price,
            )

            if result is None:
                print("RESULT     : NO OPTION")
                continue

            print(
                f"OPTION     : {result.option_type}"
            )
            print(
                f"STRIKE     : {result.strike}"
            )
            print(
                f"EXPIRY     : {result.expiry}"
            )
            print(
                f"TRADE      : {result.trade_symbol}"
            )
            print(
                f"TOKEN      : {result.token}"
            )
            print(
                f"LOT SIZE   : {result.lot_size}"
            )

        except Exception as exc:
            print(
                f"ERROR      : {type(exc).__name__}: {exc}"
            )

    print()
    print("=" * 72)
    print("MCX OPTION SELECTOR TEST COMPLETE")
    print("=" * 72)
