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
                    "ExitPrice",
                    "RealizedPnL",
                    "Signal",
                    "Score",
                    "Confidence",
                    "Status",
                    "ExitReason",
                    "ExecutionTime",
                    "ExitTime",
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
                record.exit_price,
                record.realized_pnl,
                record.decision_signal,
                record.decision_score,
                record.decision_confidence,
                record.status,
                record.exit_reason,
                record.execution_time.isoformat(),
                (
                    record.exit_time.isoformat()
                    if record.exit_time
                    else ""
                ),
            ])

    def close(self, position):

        if not self._file.exists():

            return False

        rows = []

        updated = False

        with self._file.open(
            "r",
            newline="",
        ) as fp:

            reader = csv.DictReader(fp)

            fieldnames = reader.fieldnames or []

            for row in reader:

                if (
                    row.get("PositionID")
                    == position.position_id
                ):

                    row["ExitPrice"] = (
                        position.current_price
                    )

                    row["RealizedPnL"] = (
                        position.realized_pnl
                    )

                    row["Status"] = (
                        position.status.value
                    )

                    row["ExitReason"] = (
                        position.exit_reason
                    )

                    row["ExitTime"] = (
                        position.exit_time.isoformat()
                        if position.exit_time
                        else ""
                    )

                    updated = True

                rows.append(row)

        if not updated:

            return False

        with self._file.open(
            "w",
            newline="",
        ) as fp:

            writer = csv.DictWriter(
                fp,
                fieldnames=fieldnames,
            )

            writer.writeheader()

            writer.writerows(rows)

        return True
