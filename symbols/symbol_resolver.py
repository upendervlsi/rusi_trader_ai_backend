from symbols.symbol import TradingSymbol
from symbols.symbol_master import SymbolMaster


class SymbolResolver:

    def __init__(self, master: SymbolMaster):
        self._master = master

    def resolve(
        self,
        symbol: str,
        exchange: str | None = None,
    ) -> TradingSymbol:

        result = self._master.cache.get(symbol)

        if result is None:
            raise LookupError(f"Unknown symbol: {symbol}")

        if exchange is None:
            return result

        if result.exchange.upper() != exchange.upper():
            raise LookupError(
                f"{symbol} found, but not on exchange {exchange}"
            )

        return result
