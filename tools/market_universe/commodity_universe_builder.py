"""
=============================================================
RUSI Trader AI

Commodity Universe Builder

Sprint-17

Builds the commodity trading universe.

=============================================================
"""

from pathlib import Path

from .universe_builder_base import UniverseBuilderBase


class CommodityUniverseBuilder(UniverseBuilderBase):
    """
    Builds the commodity universe.
    """

    def __init__(
        self,
        output_file: Path,
    ):

        super().__init__(
            universe_name="Commodity",
            output_file=output_file,
        )
    # ---------------------------------------------------------

    def select_instruments(self):
        """
        Select all commodity instruments from
        the instrument master.
        """

        return self.parser.get_commodities()

    # ---------------------------------------------------------

    @property
    def instrument_count(self) -> int:
        """
        Return the number of commodity instruments.
        """

        return len(self.universe.instruments)
    # ---------------------------------------------------------

    def summary(self) -> dict[str, object]:
        """
        Return a summary of the commodity universe.
        """

        summary = super().summary()

        summary.update(
            {
                "commodity_count": self.instrument_count,
            }
        )

        return summary

    # ---------------------------------------------------------

    def print_summary(self) -> None:
        """
        Print the commodity universe summary.
        """

        summary = self.summary()

        print()
        print("=" * 60)
        print("Commodity Universe Summary")
        print("=" * 60)
        print(f"Universe        : {summary['universe']}")
        print(f"Commodities     : {summary['commodity_count']}")
        print(f"Output File     : {summary['output_file']}")
        print("=" * 60)
        print()
    # ---------------------------------------------------------

    def build_from_master(
        self,
        master_file: Path,
    ):
        """
        Load the instrument master and build
        the commodity universe.
        """

        self.load_master(master_file)

        return self.build()

    # ---------------------------------------------------------

    def save_from_master(
        self,
        master_file: Path,
    ):
        """
        Load the instrument master and save
        the commodity universe.
        """

        self.load_master(master_file)

        return self.save()
    # ---------------------------------------------------------

    def run_from_master(
        self,
        master_file: Path,
    ):
        """
        Execute the complete commodity universe
        generation workflow.
        """

        self.load_master(master_file)

        return self.run()

    # ---------------------------------------------------------

    @property
    def universe_type(self) -> str:
        """
        Return the universe type.
        """

        return "Commodity"
    # ---------------------------------------------------------

    def __str__(self) -> str:
        """
        Return a user-friendly string representation.
        """

        return (
            f"{self.universe_type}UniverseBuilder"
            f"(count={self.instrument_count})"
        )

    # ---------------------------------------------------------

    def __repr__(self) -> str:
        """
        Return the developer representation.
        """

        return self.__str__()
