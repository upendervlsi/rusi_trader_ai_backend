from pathlib import Path

from tools.market_universe.equity_universe_builder import (
    EquityUniverseBuilder,
)
from tools.market_universe.futures_universe_builder import (
    FuturesUniverseBuilder,
)
from tools.market_universe.options_universe_builder import (
    OptionsUniverseBuilder,
)
from tools.market_universe.commodity_universe_builder import (
    CommodityUniverseBuilder,
)
class WatchlistManager:
    """
    Manages watchlist generation from one or more
    market universes.
    """

    def __init__(self):
        """
        Initialize the Watchlist Manager.
        """

        self._builders = {}
    def __init__(self):
        """
        Initialize the Watchlist Manager.
        """

        self._builders = {
            "equity": EquityUniverseBuilder,
            "futures": FuturesUniverseBuilder,
            "options": OptionsUniverseBuilder,
            "commodity": CommodityUniverseBuilder,
        }
    # ---------------------------------------------------------

    def get_builder_class(
        self,
        universe_type: str,
    ):
        """
        Return the builder class for the requested
        universe type.
        """

        universe_type = universe_type.lower()

        if universe_type not in self._builders:
            raise ValueError(
                f"Unsupported universe type: {universe_type}"
            )

        return self._builders[universe_type]
    # ---------------------------------------------------------

    def create_builder(
        self,
        universe_type: str,
        output_file: Path,
    ):
        """
        Create a universe builder instance.
        """

        builder_class = self.get_builder_class(
            universe_type,
        )

        return builder_class(
            output_file=output_file,
        )
    # ---------------------------------------------------------

    def build_universe(
        self,
        universe_type: str,
        master_file: Path,
        output_file: Path,
    ):
        """
        Build and return a market universe.
        """

        builder = self.create_builder(
            universe_type=universe_type,
            output_file=output_file,
        )

        return builder.build_from_master(
            master_file=master_file,
        )
    # ---------------------------------------------------------

    def save_universe(
        self,
        universe_type: str,
        master_file: Path,
        output_file: Path,
    ):
        """
        Build and save a market universe.
        """

        builder = self.create_builder(
            universe_type=universe_type,
            output_file=output_file,
        )

        return builder.save_from_master(
            master_file=master_file,
        )
    # ---------------------------------------------------------

    def supported_universe_types(self) -> tuple[str, ...]:
        """
        Return all supported universe types.
        """

        return tuple(sorted(self._builders.keys()))

    # ---------------------------------------------------------

    def __str__(self) -> str:
        """
        Return a user-friendly string representation.
        """

        return (
            f"WatchlistManager"
            f"(supported={len(self._builders)})"
        )

    # ---------------------------------------------------------

    def __repr__(self) -> str:
        """
        Return the developer representation.
        """

        return self.__str__()
