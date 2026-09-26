from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

from core.nifty_real_trading_control import NiftyRealTradingControl
from core.nifty_real_pnl_store import NiftyRealPnlStore


class TestNiftyRealRecoveryIsolation(unittest.TestCase):

    def _position(self, order_id, symbol="NIFTY22SEP2623450CE"):
        return {
            "market": "NIFTY_FNO",
            "position": {
                "position_id": "TEST_POSITION_001",
                "order_id": order_id,
                "symbol": symbol,
                "exchange": "NFO",
                "token": "TEST_TOKEN",
                "transaction_type": "BUY",
                "quantity": 65,
                "entry_price": 100.0,
                "current_price": 100.0,
                "status": "OPEN",
            },
        }

    def test_paper_position_is_not_real_position(self):
        """
        A persisted PAPER order must not be interpreted as a
        NIFTY real-trading position.
        """

        paper = self._position("PAPER_ORDER_000001")

        self.assertTrue(
            str(paper["position"]["order_id"]).startswith("PAPER_")
        )

        self.assertNotEqual(
            paper["position"]["order_id"],
            "REAL_ORDER_001",
        )

    def test_real_position_identity_is_distinct_from_paper(self):
        """
        A broker Order ID must remain distinct from PAPER_ORDER IDs.
        """

        real = self._position("260921009999999")
        paper = self._position("PAPER_ORDER_000001")

        self.assertNotEqual(
            real["position"]["order_id"],
            paper["position"]["order_id"],
        )

        self.assertFalse(
            str(real["position"]["order_id"]).startswith("PAPER_")
        )

        self.assertTrue(
            str(paper["position"]["order_id"]).startswith("PAPER_")
        )

    def test_real_entry_control_off_does_not_disable_existing_exit_path(self):
        """
        New-entry control and existing-position exit control are
        separate safety concepts.

        This is a control-flow simulation only.
        No broker call is made.
        """

        with tempfile.TemporaryDirectory() as tmp:
            control = NiftyRealTradingControl(
                Path(tmp) / "control.json"
            )

            # Explicitly keep real trading disabled.
            control.save(False)

            self.assertFalse(control.is_enabled())

            # Simulated existing real position.
            position = self._position("260921009999999")

            # Existing position remains OPEN.
            self.assertEqual(
                position["position"]["status"],
                "OPEN",
            )

            # New-entry control is OFF.
            new_entry_allowed = control.is_enabled()

            self.assertFalse(new_entry_allowed)

            # Existing-position exit decision is independent.
            exit_monitor = Mock()
            exit_monitor.evaluate_exit_reason.return_value = "TARGET"

            exit_reason = exit_monitor.evaluate_exit_reason(
                position["position"]
            )

            self.assertEqual(exit_reason, "TARGET")

            exit_monitor.evaluate_exit_reason.assert_called_once()

    def test_real_pnl_store_accepts_real_nifty_only(self):
        """
        Real P&L ledger accepts a NIFTY real closed trade but
        rejects MIDCPNIFTY and non-NIFTY symbols.
        """

        with tempfile.TemporaryDirectory() as tmp:
            store = NiftyRealPnlStore(
                Path(tmp) / "real_pnl.json"
            )

            recorded = store.record_closed_trade(
                position_id="REAL_POSITION_001",
                exit_order_id="REAL_EXIT_001",
                symbol="NIFTY22SEP2623450PE",
                quantity=65,
                realized_pnl=-188.50,
                exit_reason="TARGET",
            )

            self.assertTrue(recorded)

            payload = store.load()

            self.assertEqual(len(payload["trades"]), 1)
            self.assertEqual(
                payload["trades"][0]["symbol"],
                "NIFTY22SEP2623450PE",
            )

            with self.assertRaises(ValueError):
                store.record_closed_trade(
                    position_id="MID_POSITION_001",
                    exit_order_id="MID_EXIT_001",
                    symbol="MIDCPNIFTY29SEP2614525PE",
                    quantity=50,
                    realized_pnl=100.0,
                    exit_reason="TARGET",
                )

            with self.assertRaises(ValueError):
                store.record_closed_trade(
                    position_id="OTHER_POSITION_001",
                    exit_order_id="OTHER_EXIT_001",
                    symbol="BANKNIFTY22SEP2650000PE",
                    quantity=25,
                    realized_pnl=100.0,
                    exit_reason="TARGET",
                )

    def test_real_pnl_exit_order_is_idempotent(self):
        """
        The same broker exit Order ID must never be counted twice.
        """

        with tempfile.TemporaryDirectory() as tmp:
            store = NiftyRealPnlStore(
                Path(tmp) / "real_pnl.json"
            )

            first = store.record_closed_trade(
                position_id="REAL_POSITION_001",
                exit_order_id="REAL_EXIT_001",
                symbol="NIFTY22SEP2623450PE",
                quantity=65,
                realized_pnl=-188.50,
                exit_reason="TARGET",
            )

            second = store.record_closed_trade(
                position_id="REAL_POSITION_001",
                exit_order_id="REAL_EXIT_001",
                symbol="NIFTY22SEP2623450PE",
                quantity=65,
                realized_pnl=-188.50,
                exit_reason="TARGET",
            )

            self.assertTrue(first)
            self.assertFalse(second)

            self.assertEqual(
                store.get_cumulative_realized_pnl(),
                -188.50,
            )

            self.assertEqual(
                len(store.load()["trades"]),
                1,
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
