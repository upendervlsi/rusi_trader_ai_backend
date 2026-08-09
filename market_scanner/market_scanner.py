"""
============================================================

Market Scanner

============================================================
"""

from market_scanner.scanner_result import ScannerResult


class MarketScanner:

    def __init__(self):

        self._watchlist = [

            ("NIFTY", "NSE"),

            ("BANKNIFTY", "NSE"),

            ("GOLDM", "MCX"),

            ("CRUDEOILM", "MCX"),

            ("SILVERM", "MCX"),

        ]

    def instruments(self):

        return self._watchlist

    def add_result(
        self,
        recommendation,
    ):

        result = ScannerResult()

        result.symbol = recommendation.symbol

        result.signal = recommendation.recommendation

        result.confidence = recommendation.confidence

        result.score = recommendation.score

        result.entry = recommendation.entry_price

        result.stop_loss = recommendation.stop_loss

        result.target = recommendation.target_price

        result.option_symbol = recommendation.option_symbol

        result.underlying = recommendation.underlying_symbol

        return result
