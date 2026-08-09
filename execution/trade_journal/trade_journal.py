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

            decision_signal=context.decision.signal.name,

            decision_score=context.decision.score,

            decision_confidence=context.decision.confidence,

            execution_time=datetime.now(),

            status=position.status.value,

        )

        self._writer.append(record)

        logger.info("")
        logger.info("Step 15 : Trade Journal")

        logger.info(
            "Trade ID : %s",
            record.trade_id,
        )

        logger.info(
            "Trade Recorded Successfully",
        )
