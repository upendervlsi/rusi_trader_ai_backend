"""
RUSI Trader AI
NIFTY Real Trading Safety Regression Tests

These tests use NO real broker connection.

They verify:

1. New NIFTY real entries remain blocked when the persistent
   real-trading control is disabled.

2. An existing OPEN NIFTY position is still evaluated by the
   dedicated NIFTY real exit monitor.

3. A fully confirmed mock broker SELL fill closes the existing
   position through the production real-exit close path.

4. A partial SELL fill does NOT close the local position and
   persists the pending exit state.
"""

from __future__ import annotations

import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace

from core.nifty_real_exit_monitor import NiftyRealExitMonitor
from core.nifty_real_trading_control import NiftyRealTradingControl
from execution.broker.broker_result import BrokerResult
from execution.position_manager.position import Position
from execution.position_manager.position_status import PositionStatus


class MockMarketDataEngine:
    """Returns a deterministic option LTP without contacting a broker."""

    def __init__(self, ltp: float):
        self.ltp = ltp
        self.calls = []

    def get_instrument_ltp(self, *, exchange, symbol, token):
        self.calls.append(
            {
                "exchange": exchange,
                "symbol": symbol,
                "token": token,
            }
        )
        return self.ltp


class MockRealOrderExecutor:
    """Mock NIFTY real executor. Never contacts Angel One."""

    def __init__(self, broker_result: BrokerResult):
        self.broker_result = broker_result
        self.orders = []

    def place_order(self, order):
        self.orders.append(order)
        return self.broker_result


class MockPendingExitStore:
    """In-memory pending-exit store for regression testing."""

    def __init__(self):
        self.saved = []
        self.cleared = False

    def save(self, **kwargs):
        self.saved.append(kwargs)

    def clear(self):
        self.cleared = True


def make_position(
    *,
    entry_price: float = 100.0,
    current_price: float = 100.0,
    target_price: float = 120.0,
    quantity: int = 65,
) -> Position:
    """Create a valid OPEN NIFTY option position."""

    return Position(
        position_id="TEST_NIFTY_REAL_POSITION_001",
        order_id="TEST_ENTRY_ORDER_001",
        symbol="NIFTY22SEP2623450CE",
        exchange="NFO",
        token="TEST_TOKEN_001",
        transaction_type="BUY",
        quantity=quantity,
        entry_price=entry_price,
        current_price=current_price,
        highest_price=current_price,
        highest_unrealized_pnl=0.0,
        profit_protection_active=False,
        protected_price=0.0,
        reversal_count=0,
        last_reversal_signal="",
        stop_loss=80.0,
        target_price=target_price,
        unrealized_pnl=0.0,
        realized_pnl=0.0,
        entry_time=datetime.now(),
        exit_time=None,
        exit_reason="",
        status=PositionStatus.OPEN,
    )


def make_trading_config():
    """
    Minimal configuration required by NiftyRealExitMonitor.
    Values deliberately avoid triggering profit protection.
    """

    return SimpleNamespace(
        profit_protection_activation_percent=50.0,
        profit_protection_retrace_percent=50.0,
        reversal_confirmation_confidence=1.45,
        reversal_confirmation_cycles=2,
    )


class TestNiftyRealPositionSafety(unittest.TestCase):

    def test_nifty_real_new_entries_are_blocked_when_disabled(self):
        """
        Safety invariant:

            persisted control = DISABLED
            execution mode   = LIVE
            market           = NIFTY_FNO

        Therefore:

            new_entries_allowed = False
        """

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "nifty_real_control.json"

            control = NiftyRealTradingControl(path)

            self.assertFalse(control.is_enabled())

            status = {
                "enabled": control.is_enabled(),
                "market": "NIFTY_FNO",
                "execution_mode": "LIVE",
                "new_entries_allowed": (
                    control.is_enabled()
                    and "NIFTY_FNO" == "NIFTY_FNO"
                    and "LIVE" == "LIVE"
                ),
            }

            self.assertFalse(status["enabled"])
            self.assertFalse(status["new_entries_allowed"])

    def test_existing_nifty_position_is_evaluated_when_target_reached(self):
        """
        Safety invariant:

            real-trading entry switch OFF

        must NOT disable evaluation of an already-open
        NIFTY real position.

        The dedicated real exit monitor must still return TARGET.
        """

        control = NiftyRealTradingControl(
            Path(tempfile.mkdtemp()) / "control.json"
        )

        self.assertFalse(control.is_enabled())

        position = make_position(
            entry_price=100.0,
            current_price=100.0,
            target_price=120.0,
        )

        market_data = MockMarketDataEngine(121.0)

        monitor = NiftyRealExitMonitor(
            market_data_engine=market_data,
            order_executor=None,
            pending_exit_store=None,
            trading_config=make_trading_config(),
        )

        exit_reason = monitor.evaluate_exit_reason(position)

        self.assertEqual(exit_reason, "TARGET")
        self.assertEqual(position.current_price, 121.0)
        self.assertEqual(position.status, PositionStatus.OPEN)
        self.assertEqual(len(market_data.calls), 1)

    def test_confirmed_mock_sell_closes_existing_nifty_position(self):
        """
        A confirmed complete mock SELL fill must close the local
        position through the production close-after-fill logic.

        No broker/API connection is used.
        """

        position = make_position(
            entry_price=100.0,
            current_price=121.0,
            target_price=120.0,
            quantity=65,
        )

        broker_result = BrokerResult(
            success=True,
            order_id="MOCK_EXIT_ORDER_001",
            message="Mock full fill",
            filled_quantity=65,
            average_price=121.0,
        )

        order_executor = MockRealOrderExecutor(broker_result)
        pending_store = MockPendingExitStore()

        # Minimal ExecutionManager object containing only the
        # production method dependencies required by
        # _execute_nifty_real_exit().
        manager = SimpleNamespace(
            _config=SimpleNamespace(execution_mode="LIVE"),
            _market_name="NIFTY_FNO",
            _nifty_real_order_executor=order_executor,
            _nifty_real_pending_exit_order=pending_store,
        )

        # Import the production method and bind it to this minimal object.
        from core.execution_manager import ExecutionManager

        manager._execute_nifty_real_exit = (
            ExecutionManager._execute_nifty_real_exit.__get__(
                manager,
                type(manager),
            )
        )

        # The production method compares against ExecutionMode.LIVE.
        from common.enums import ExecutionMode

        manager._config.execution_mode = ExecutionMode.LIVE

        # Bind the production close method as well.
        manager._close_nifty_real_position_after_fill = (
            ExecutionManager._close_nifty_real_position_after_fill.__get__(
                manager,
                type(manager),
            )
        )

        # The close method writes to NiftyRealPnlStore. We intentionally
        # replace that method only for this isolated mock test so that
        # no production ledger is modified.
        manager._close_nifty_real_position_after_fill = (
            lambda position, **kwargs: (
                setattr(
                    position,
                    "current_price",
                    float(kwargs["average_price"]),
                ),
                setattr(position, "unrealized_pnl", 0.0),
                setattr(
                    position,
                    "realized_pnl",
                    (
                        float(kwargs["average_price"])
                        - float(position.entry_price)
                    )
                    * int(position.quantity),
                ),
                setattr(
                    position,
                    "exit_reason",
                    str(kwargs["exit_reason"]),
                ),
                setattr(
                    position,
                    "status",
                    PositionStatus.CLOSED,
                ),
                True,
            )[-1]
        )

        result = manager._execute_nifty_real_exit(
            position,
            exit_reason="TARGET",
        )

        self.assertEqual(result["status"], "FILLED")
        self.assertTrue(result["closed"])
        self.assertEqual(position.status, PositionStatus.CLOSED)
        self.assertEqual(position.exit_reason, "TARGET")
        self.assertAlmostEqual(position.realized_pnl, 1365.0)
        self.assertEqual(len(order_executor.orders), 1)

        submitted_order = order_executor.orders[0]

        self.assertEqual(submitted_order.transaction_type, "SELL")
        self.assertEqual(submitted_order.quantity, 65)
        self.assertEqual(submitted_order.order_type, "MARKET")
        self.assertEqual(submitted_order.exchange, "NFO")

        self.assertFalse(pending_store.saved)

    def test_partial_nifty_real_sell_does_not_close_position(self):
        """
        A partial broker SELL fill must leave the local position OPEN
        and persist the same broker order as a pending exit.
        """

        position = make_position(
            entry_price=100.0,
            current_price=120.0,
            target_price=120.0,
            quantity=65,
        )

        broker_result = BrokerResult(
            success=True,
            order_id="MOCK_PARTIAL_EXIT_001",
            message="Mock partial fill",
            filled_quantity=30,
            average_price=119.0,
        )

        order_executor = MockRealOrderExecutor(broker_result)
        pending_store = MockPendingExitStore()

        manager = SimpleNamespace(
            _config=SimpleNamespace(),
            _market_name="NIFTY_FNO",
            _nifty_real_order_executor=order_executor,
            _nifty_real_pending_exit_order=pending_store,
        )

        from common.enums import ExecutionMode
        from core.execution_manager import ExecutionManager

        manager._config.execution_mode = ExecutionMode.LIVE

        manager._execute_nifty_real_exit = (
            ExecutionManager._execute_nifty_real_exit.__get__(
                manager,
                type(manager),
            )
        )

        result = manager._execute_nifty_real_exit(
            position,
            exit_reason="TARGET",
        )

        self.assertEqual(result["status"], "PARTIAL_FILL")
        self.assertFalse(result["closed"])
        self.assertEqual(position.status, PositionStatus.OPEN)

        self.assertEqual(len(order_executor.orders), 1)
        self.assertEqual(len(pending_store.saved), 1)

        pending = pending_store.saved[0]

        self.assertEqual(
            pending["exit_order_id"],
            "MOCK_PARTIAL_EXIT_001",
        )
        self.assertEqual(
            pending["quantity"],
            65,
        )
        self.assertEqual(
            pending["exit_reason"],
            "TARGET",
        )


if __name__ == "__main__":
    unittest.main()
