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

from execution.position_manager.position_persistence import (
    PositionPersistence,
)


logger = get_logger("RUSI")


class PositionManager:

    def __init__(
        self,
        market_name="UNKNOWN",
    ):

        self._registry = PositionRegistry()

        self._persistence = PositionPersistence(
            market_name=market_name,
        )

    # =========================================================
    # RESTORE
    # =========================================================

    def restore_persisted_positions(self):

        positions = (
            self._persistence.restore()
        )

        for position in positions:

            if self._registry.get(
                position.position_id
            ):
                continue

            self._registry.add(
                position
            )

            logger.info(
                "Position Restored | "
                "Market Position=%s | "
                "Symbol=%s | Entry=%.2f | Qty=%d",
                position.position_id,
                position.symbol,
                position.entry_price,
                position.quantity,
            )

        if positions:

            logger.info(
                "Persisted OPEN Positions Restored : %d",
                len(positions),
            )

        return positions

    # =========================================================
    # PERSIST CURRENT STATE
    # =========================================================

    def remove_position(self, position_id):
        """
        Remove a position from the in-memory registry.

        Used only for broker reconciliation when a persisted
        LIVE position is proven stale or externally divergent.
        """

        if not position_id:
            return None

        return self._registry.remove(position_id)

    def persist_positions(self):

        self._persistence.save(
            self._registry.open_positions()
        )

    # =========================================================
    # OPEN POSITION
    # =========================================================

    def open_position(

        self,

        broker_result,

        order_request,

        stop_loss: float = 0.0,

        target_price: float = 0.0,

    ):

        position = Position(

            position_id=str(uuid4()),

            order_id=broker_result.order_id,

            symbol=order_request.symbol,

            exchange=order_request.exchange,

            token=str(
                getattr(order_request, "token", "")
            ),

            transaction_type=order_request.transaction_type,

            quantity=order_request.quantity,

            entry_price=broker_result.average_price or 0.0,

            current_price=broker_result.average_price or 0.0,

            highest_price=broker_result.average_price or 0.0,

            highest_unrealized_pnl=0.0,

            profit_protection_active=False,

            protected_price=0.0,

            reversal_count=0,

            last_reversal_signal="",

            stop_loss=stop_loss,

            target_price=target_price,

            unrealized_pnl=0.0,

            realized_pnl=0.0,

            entry_time=datetime.now(),

            exit_time=None,

            exit_reason="",

            status=PositionStatus.OPEN,

        )

        self._registry.add(
            position
        )

        self.persist_positions()

        logger.info("")
        logger.info(
            "Step 14 : Position Manager"
        )

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
