import pytest
from pathlib import Path

from execution.execution_manager import (
    ExecutionManager,
)
from tools.watchlist.watchlist_manager import (
    WatchlistManager,
)
class TestMarketUniverseIntegration:

    def setup_method(self):
        """
        Runs before every test.
        """
        self.execution_manager = ExecutionManager()
    # ---------------------------------------------------------

    def test_supported_universe_types(self):
        """
        Verify the supported market universe types.
        """

        universe_types = (
            self.execution_manager.supported_universe_types()
        )

        assert "equity" in universe_types
        assert "futures" in universe_types
        assert "options" in universe_types
        assert "commodity" in universe_types
    # ---------------------------------------------------------

    def test_is_supported_universe(self):
        """
        Verify supported and unsupported
        universe type detection.
        """

        assert self.execution_manager.is_supported_universe(
            "equity"
        )

        assert self.execution_manager.is_supported_universe(
            "futures"
        )

        assert self.execution_manager.is_supported_universe(
            "options"
        )

        assert self.execution_manager.is_supported_universe(
            "commodity"
        )

        assert not self.execution_manager.is_supported_universe(
            "crypto"
        )

        assert not self.execution_manager.is_supported_universe(
            "forex"
        )
    # ---------------------------------------------------------

    def test_build_market_universe(self):
        """
        Verify that the ExecutionManager delegates
        market universe construction correctly.
        """

        master_file = Path(
            "data/instrument_master.json"
        )

        output_file = Path(
            "output/equity_universe.json"
        )

        # Skip if the sample master file is unavailable.
        if not master_file.exists():
            return

        self.execution_manager.build_market_universe(
            universe_type="equity",
            master_file=master_file,
            output_file=output_file,
        )
    # ---------------------------------------------------------

    def test_save_market_universe(self):
        """
        Verify that the ExecutionManager delegates
        market universe saving correctly.
        """

        master_file = Path(
            "data/instrument_master.json"
        )

        output_file = Path(
            "output/equity_universe.json"
        )

        # Skip if the sample master file is unavailable.
        if not master_file.exists():
            return

        self.execution_manager.save_market_universe(
            universe_type="equity",
            master_file=master_file,
            output_file=output_file,
        )

        assert output_file.exists()
    # ---------------------------------------------------------

    def test_invalid_universe_type(self):
        """
        Verify that an unsupported universe type
        raises ValueError.
        """

        master_file = Path(
            "data/instrument_master.json"
        )

        output_file = Path(
            "output/invalid_universe.json"
        )

        with pytest.raises(ValueError):
            self.execution_manager.build_market_universe(
                universe_type="crypto",
                master_file=master_file,
                output_file=output_file,
            )
    # ---------------------------------------------------------

    def test_get_watchlist_manager(self):
        """
        Verify that the ExecutionManager exposes
        the WatchlistManager instance.
        """

        manager = (
            self.execution_manager.get_watchlist_manager()
        )

        assert isinstance(
            manager,
            WatchlistManager,
        )

        assert (
            manager
            is self.execution_manager.watchlist_manager
        )
    # ---------------------------------------------------------

    def test_execution_manager_string_methods(self):
        """
        Verify __str__() and __repr__() are consistent.
        """

        manager = self.execution_manager

        string_repr = str(manager)
        repr_string = repr(manager)

        assert isinstance(string_repr, str)
        assert isinstance(repr_string, str)

        assert string_repr == repr_string

        assert "ExecutionManager" in string_repr
    # ---------------------------------------------------------

    def test_execution_manager_initialization(self):
        """
        Smoke test for ExecutionManager initialization.
        """

        manager = ExecutionManager()

        assert manager is not None
        assert manager.get_watchlist_manager() is not None
        assert len(manager.supported_universe_types()) > 0
