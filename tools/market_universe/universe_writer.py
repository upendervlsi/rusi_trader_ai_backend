"""
=============================================================
RUSI Trader AI

Universe Writer

Responsible for writing generated market universes
to JSON files.

Sprint-17
=============================================================
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from .universe_models import Universe


class UniverseWriter:
    """
    Serializes Universe objects into JSON files.
    """

    @staticmethod
    def write(
        universe: Universe,
        output_file: Path,
    ) -> None:

        output_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        payload = {
            "name": universe.name,
            "generated_at": datetime.utcnow().isoformat(),
            "instrument_count": len(universe),
            "instruments": [],
        }

        for instrument in universe:

            payload["instruments"].append(
                {
                    "symbol": instrument.symbol,
                    "token": instrument.token,
                    "exchange": instrument.exchange,
                    "segment": instrument.segment,
                    "expiry": instrument.expiry,
                    "strike": instrument.strike,
                    "option_type": instrument.option_type,
                    "lot_size": instrument.lot_size,
                    "tick_size": instrument.tick_size,
                    "quantity": instrument.quantity,
                    "product": instrument.product,
                    "order_type": instrument.order_type,
                }
            )

        with output_file.open(
            "w",
            encoding="utf-8",
        ) as fp:

            json.dump(
                payload,
                fp,
                indent=4,
            )
