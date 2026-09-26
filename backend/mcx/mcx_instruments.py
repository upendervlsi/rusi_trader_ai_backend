"""
RUSI Trader AI - MCX instrument definitions.

Only these three MCX instruments are supported:

    CRUDEOILM
    GOLDM
    SILVERM

Contract tokens are never hard-coded here.
The existing InstrumentResolver is used to resolve
the currently available MCX futures contract.
"""

from __future__ import annotations

from dataclasses import dataclass

from tools.market_universe.instrument_resolver import InstrumentResolver
from trading.context.trading_context import TradingInstrument


@dataclass(frozen=True, slots=True)
class McxInstrumentDefinition:
    key: str
    symbol: str
    name: str
    emoji: str


MCX_INSTRUMENTS: tuple[McxInstrumentDefinition, ...] = (
    McxInstrumentDefinition(
        key="crude",
        symbol="CRUDEOILM",
        name="Crude Oil Mini",
        emoji="🥇",
    ),
    McxInstrumentDefinition(
        key="gold",
        symbol="GOLDM",
        name="Gold Mini",
        emoji="🥈",
    ),
    McxInstrumentDefinition(
        key="silver",
        symbol="SILVERM",
        name="Silver Mini",
        emoji="🥉",
    ),
)


class McxInstrumentResolver:
    """
    Resolve the current MCX futures contract for each
    supported MCX instrument.

    This class does not modify the existing resolver.
    It simply consumes the existing resolver.
    """

    def __init__(self) -> None:
        self._resolver = InstrumentResolver()

    def resolve(
        self,
        definition: McxInstrumentDefinition,
    ) -> TradingInstrument:
        """
        Resolve the current contract for one MCX instrument.
        """

        instrument = TradingInstrument(
            symbol=definition.symbol,
            exchange="MCX",
            token="",
            quantity=1,
            order_type="MARKET",
            product_type="INTRADAY",
        )

        return self._resolver.resolve(instrument)

    def resolve_all(
        self,
    ) -> dict[str, TradingInstrument]:
        """
        Resolve all three supported MCX instruments.
        """

        resolved: dict[str, TradingInstrument] = {}

        for definition in MCX_INSTRUMENTS:
            resolved[definition.key] = self.resolve(definition)

        return resolved
