from pathlib import Path

from tools.watchlist.watchlist_manager import (
    WatchlistManager,
)

class ExecutionManager:
    """
    Coordinates trade execution workflows.
    """

    def __init__(self):
        """
        Initialize the execution manager.
        """

        self.watchlist_manager = WatchlistManager()
    # ---------------------------------------------------------

    def build_market_universe(
        self,
        universe_type: str,
        master_file: Path,
        output_file: Path,
    ):
        """
        Build a market universe using the WatchlistManager.
        """

        return self.watchlist_manager.build_universe(
            universe_type=universe_type,
            master_file=master_file,
            output_file=output_file,
        )
    # ---------------------------------------------------------

    def save_market_universe(
        self,
        universe_type: str,
        master_file: Path,
        output_file: Path,
    ):
        """
        Build and save a market universe using the
        WatchlistManager.
        """

        return self.watchlist_manager.save_universe(
            universe_type=universe_type,
            master_file=master_file,
            output_file=output_file,
        )
    # ---------------------------------------------------------

    def supported_universe_types(self) -> tuple[str, ...]:
        """
        Return the supported market universe types.
        """

        return self.watchlist_manager.supported_universe_types()
    # ---------------------------------------------------------

    def __str__(self) -> str:
        """
        Return a user-friendly string representation.
        """

        return (
            f"ExecutionManager("
            f"supported_universes="
            f"{len(self.supported_universe_types())}"
            f")"
        )

    # ---------------------------------------------------------

    def __repr__(self) -> str:
        """
        Return the developer representation.
        """

        return self.__str__()
    # ---------------------------------------------------------

    def is_supported_universe(
        self,
        universe_type: str,
    ) -> bool:
        """
        Check whether the requested universe type is supported.
        """

        return (
            universe_type.lower()
            in self.supported_universe_types()
        )
    # ---------------------------------------------------------

    def get_watchlist_manager(
        self,
    ) -> WatchlistManager:
        """
        Return the associated WatchlistManager instance.
        """

        return self.watchlist_manager
