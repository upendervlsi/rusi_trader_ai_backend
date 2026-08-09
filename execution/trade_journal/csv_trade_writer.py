"""
============================================================

CSV Trade Writer

============================================================
"""

import csv
from pathlib import Path


class CsvTradeWriter:

    def __init__(self):

        self._path = Path("runs")

        self._path.mkdir(exist_ok=True)

        self._file = self._path / "trade_journal.csv"

        if not self._file.exists():

            with self._file.open("w", newline="") as fp:

                writer = csv.writer(fp)

                writer.writerow([
                    "TradeID",
                    "OrderID",
                    "PositionID",
                    "Symbol",
                    "Exchange",
                    "Transaction",
                    "Quantity",
                    "EntryPrice",
                    "Signal",
                    "Score",
                    "Confidence",
                    "Status",
                    "ExecutionTime",
                ])

    def append(self, record):

        with self._file.open("a", newline="") as fp:

            writer = csv.writer(fp)

            writer.writerow([
                record.trade_id,
                record.order_id,
                record.position_id,
                record.symbol,
                record.exchange,
                record.transaction_type,
                record.quantity,
                record.entry_price,
                record.decision_signal,
                record.decision_score,
                record.decision_confidence,
                record.status,
                record.execution_time.isoformat(),
            ])
