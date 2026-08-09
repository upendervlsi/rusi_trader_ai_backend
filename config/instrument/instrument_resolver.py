from dataclasses import dataclass


@dataclass(slots=True)
class TradingInstrument:

    symbol: str
    exchange: str
    token: str

    quantity: int = 1
    order_type: str = "MARKET"
    product_type: str = "INTRADAY"


class InstrumentResolver:

    def __init__(self, config):

        self._config = config

    def resolve(self) -> TradingInstrument:

        #
        # Temporary implementation.
        # Later this can read from:
        #
        #   • Watchlist
        #   • Scanner
        #   • GUI
        #   • Broker Search
        #

        return TradingInstrument(

            symbol=self._config.symbol,

            exchange=self._config.exchange,

            token=self._config.token,

            quantity=self._config.quantity,

            order_type=self._config.order_type,

            product_type=self._config.product_type,
        )
