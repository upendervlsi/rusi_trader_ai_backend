"""
============================================================

Position Manager

============================================================
"""

from datetime import datetime
from uuid import uuid4

from common.logger import get_logger

from execution.position_manager.position import Position

from execution.position_manager.position_registry import (
    PositionRegistry,
)

from execution.position_manager.position_status import (
    PositionStatus,
)

logger = get_logger("RUSI")


class PositionManager:

    def __init__(self):

        self._registry = PositionRegistry()

    def open_position(

        self,

        broker_result,

        order_request,

    ):

        position = Position(

            position_id=str(uuid4()),

            order_id=broker_result.order_id,

            symbol=order_request.symbol,

            exchange=order_request.exchange,

            transaction_type=order_request.transaction_type,

            quantity=order_request.quantity,

            #
            # Paper mode
            #
            entry_price=broker_result.average_price or 0.0,

            current_price=broker_result.average_price or 0.0,

            unrealized_pnl=0.0,

            realized_pnl=0.0,

            entry_time=datetime.now(),

            status=PositionStatus.OPEN,

        )

        self._registry.add(position)

        logger.info("")
        logger.info("Step 14 : Position Manager")

        logger.info(

            "Position ID : %s",

            position.position_id,

        )

        logger.info(

            "Status      : %s",

            position.status.value,

        )

        logger.info(

            "Quantity    : %d",

            position.quantity,

        )

        return position

    @property
    def registry(self):

        return self._registry
