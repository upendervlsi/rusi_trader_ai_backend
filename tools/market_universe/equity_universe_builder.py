"""
=============================================================
RUSI Trader AI

Equity Universe Builder

Sprint-17

Builds the equity trading universe.

=============================================================
"""

from pathlib import Path

from .universe_builder_base import UniverseBuilderBase


class EquityUniverseBuilder(UniverseBuilderBase):
    """
    Builds the equity universe.
    """

    def __init__(
        self,
        output_file: Path,
    ):

        super().__init__(
            universe_name="Equity",
            output_file=output_file,
        )
    # ---------------------------------------------------------

    def select_instruments(self):
        """
        Select all equity instruments from
        the instrument master.
        """

        return self.parser.get_equities()

    # ---------------------------------------------------------

    @property
    def instrument_count(self) -> int:
        """
        Return the number of equity instruments.
        """

        return len(self.universe.instruments)
    # ---------------------------------------------------------

    def summary(self) -> dict[str, object]:
        """
        Return equity universe summary.
        """

        summary = super().summary()

        summary.update(
            {
                "equity_count": self.instrument_count,
            }
        )

        return summary

    # ---------------------------------------------------------

    def print_summary(self) -> None:
        """
        Print equity universe summary.
        """

        summary = self.summary()

        print()
        print("=" * 60)
        print("Equity Universe Summary")
        print("=" * 60)
        print(f"Universe        : {summary['universe']}")
        print(f"Equities        : {summary['equity_count']}")
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
        the equity universe.
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
        the equity universe.
        """

        self.load_master(master_file)

        return self.save()
    # ---------------------------------------------------------

    def run_from_master(
        self,
        master_file: Path,
    ):
        """
        Execute the complete equity universe
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

        return "Equity"
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
