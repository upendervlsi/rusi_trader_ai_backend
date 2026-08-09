"""
============================================================
RUSI Trader AI

File    : paper_broker.py

Purpose :
    Paper trading broker implementation.

Author  : RUSI Trader AI
============================================================
"""

from typing import Any

from market.instrument import Instrument


class PaperBroker:
    """
    Simple paper broker implementation.
    """

    def __init__(self):

        self._logged_in = False

    def login(self) -> bool:

        print("[PaperBroker] Login successful.")

        self._logged_in = True

        return True

    def logout(self) -> None:

        print("[PaperBroker] Logout.")

        self._logged_in = False

    def get_historical_data(
        self,
        instrument: Instrument,
        interval: str,
        lookback: int,
    ) -> Any:
        """
        Placeholder for historical data.

        Initially returns None.
        Later this will connect to the actual
        market data provider.
        """

        print(
            f"[PaperBroker] Historical Data Request "
            f"{instrument.display_name()} "
            f"{interval} "
            f"{lookback}"
        )

        return None

    def place_order(
        self,
        instrument: Instrument,
        side: str,
        quantity: int,
    ):

        order = {
            "status": "PAPER_EXECUTED",
            "instrument": instrument.display_name(),
            "side": side,
            "quantity": quantity,
        }

        print(order)

        return order
