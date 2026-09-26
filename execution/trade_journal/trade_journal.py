"""
============================================================

Trade Journal

============================================================
"""

from datetime import datetime
from uuid import uuid4

from common.logger import get_logger

from execution.trade_journal.trade_record import (
    TradeRecord,
)

from execution.trade_journal.csv_trade_writer import (
    CsvTradeWriter,
)


logger = get_logger("RUSI")


class TradeJournal:

    def __init__(self):

        self._writer = CsvTradeWriter()

    def record(

        self,

        context,

        position,

    ):

        record = TradeRecord(

            trade_id=str(uuid4()),

            order_id=position.order_id,

            position_id=position.position_id,

            symbol=position.symbol,

            exchange=position.exchange,

            transaction_type=position.transaction_type,

            quantity=position.quantity,

            entry_price=position.entry_price,

            exit_price=0.0,

            realized_pnl=0.0,

            decision_signal=context.decision.signal.name,

            decision_score=context.decision.score,

            decision_confidence=context.decision.confidence,

            execution_time=datetime.now(),

            exit_time=None,

            exit_reason="",

            status=position.status.value,

        )

        self._writer.append(record)

        logger.info("")

        logger.info(
            "Step 15 : Trade Journal"
        )

        logger.info(
            "Trade ID : %s",
            record.trade_id,
        )

        logger.info(
            "Trade Recorded Successfully",
        )

    def close(

        self,

        position,

    ):

        updated = self._writer.close(
            position
        )

        if updated:

            logger.info("")

            logger.info(
                "Step 15 : Trade Journal Close"
            )

            logger.info(
                "Position ID : %s",
                position.position_id,
            )

            logger.info(
                "Exit Price  : %.2f",
                position.current_price,
            )

            logger.info(
                "Realized P&L: %.2f",
                position.realized_pnl,
            )

            logger.info(
                "Exit Reason : %s",
                position.exit_reason,
            )

            logger.info(
                "Status      : %s",
                position.status.value,
            )

            logger.info(
                "Trade Close Recorded Successfully"
            )

        else:

            logger.warning(
                "Trade Journal Close Skipped | "
                "Position not found | PositionID=%s",
                position.position_id,
            )

        return updated
