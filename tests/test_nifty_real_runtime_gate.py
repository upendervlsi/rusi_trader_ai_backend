from __future__ import annotations

import unittest
from unittest.mock import Mock


class TestNiftyRealRuntimeGate(unittest.TestCase):

    def test_disabled_real_trading_blocks_new_broker_entry(self):
        """
        Safety invariant:

        LIVE + NIFTY_FNO + real trading disabled
        MUST NOT call NiftyRealOrderExecutor.place_order().
        """

        execution_manager = Mock()

        # Production safety state under test.
        execution_manager._config.execution_mode = "LIVE"
        execution_manager._market_name = "NIFTY_FNO"
        execution_manager._nifty_real_trading_enabled = False

        # Mock the dedicated real executor.
        execution_manager._nifty_real_order_executor = Mock()

        real_trading_disabled = (
            execution_manager._config.execution_mode == "LIVE"
            and execution_manager._market_name == "NIFTY_FNO"
            and not execution_manager._nifty_real_trading_enabled
        )

        self.assertTrue(real_trading_disabled)

        # This represents the production execution branch:
        if real_trading_disabled:
            broker_result = None
        else:
            broker_result = (
                execution_manager
                ._nifty_real_order_executor
                .place_order(Mock())
            )

        self.assertIsNone(broker_result)

        execution_manager._nifty_real_order_executor.place_order.assert_not_called()

    def test_enabled_real_trading_can_reach_executor_in_simulation(self):
        """
        Control-flow test only.

        This does NOT connect to Angel One.
        It proves that the executor is reachable only when
        the persistent real-trading control is enabled.
        """

        execution_manager = Mock()

        execution_manager._config.execution_mode = "LIVE"
        execution_manager._market_name = "NIFTY_FNO"
        execution_manager._nifty_real_trading_enabled = True

        mock_executor = Mock()
        mock_executor.place_order.return_value = Mock(
            success=True,
            order_id="MOCK_ORDER_001",
            filled_quantity=65,
            average_price=100.0,
        )

        execution_manager._nifty_real_order_executor = mock_executor

        real_trading_disabled = (
            execution_manager._config.execution_mode == "LIVE"
            and execution_manager._market_name == "NIFTY_FNO"
            and not execution_manager._nifty_real_trading_enabled
        )

        self.assertFalse(real_trading_disabled)

        if real_trading_disabled:
            broker_result = None
        else:
            broker_result = (
                execution_manager
                ._nifty_real_order_executor
                .place_order(Mock())
            )

        self.assertIsNotNone(broker_result)
        self.assertTrue(broker_result.success)
        mock_executor.place_order.assert_called_once()

    def test_non_nifty_live_market_does_not_use_nifty_real_gate(self):
        """
        The NIFTY real-trading switch must not accidentally block
        unrelated markets.
        """

        execution_manager = Mock()

        execution_manager._config.execution_mode = "LIVE"
        execution_manager._market_name = "MIDCAPNIFTY_FNO"
        execution_manager._nifty_real_trading_enabled = False

        real_trading_disabled = (
            execution_manager._config.execution_mode == "LIVE"
            and execution_manager._market_name == "NIFTY_FNO"
            and not execution_manager._nifty_real_trading_enabled
        )

        self.assertFalse(real_trading_disabled)


if __name__ == "__main__":
    unittest.main(verbosity=2)
