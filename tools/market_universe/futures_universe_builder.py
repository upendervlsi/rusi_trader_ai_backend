"""
=============================================================
RUSI Trader AI

Futures Universe Builder

Sprint-17

Builds the futures trading universe.

=============================================================
"""

from pathlib import Path

from .universe_builder_base import UniverseBuilderBase


class FuturesUniverseBuilder(UniverseBuilderBase):
    """
    Builds the futures universe.
    """

    def __init__(
        self,
        output_file: Path,
    ):

        super().__init__(
            universe_name="Futures",
            output_file=output_file,
        )
    # ---------------------------------------------------------

    def select_instruments(self):
        """
        Select all futures instruments from
        the instrument master.
        """

        return self.parser.get_futures()

    # ---------------------------------------------------------

    @property
    def instrument_count(self) -> int:
        """
        Return the number of futures instruments.
        """

        return len(self.universe.instruments)
    # ---------------------------------------------------------

    def summary(self) -> dict[str, object]:
        """
        Return futures universe summary.
        """

        summary = super().summary()

        summary.update(
            {
                "futures_count": self.instrument_count,
            }
        )

        return summary

    # ---------------------------------------------------------

    def print_summary(self) -> None:
        """
        Print futures universe summary.
        """

        summary = self.summary()

        print()
        print("=" * 60)
        print("Futures Universe Summary")
        print("=" * 60)
        print(f"Universe        : {summary['universe']}")
        print(f"Futures         : {summary['futures_count']}")
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
        the futures universe.
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
        the futures universe.
        """

        self.load_master(master_file)

        return self.save()
    # ---------------------------------------------------------

    def run_from_master(
        self,
        master_file: Path,
    ):
        """
        Execute the complete futures universe
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

        return "Futures"
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
