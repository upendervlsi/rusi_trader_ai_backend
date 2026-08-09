"""
=============================================================
RUSI Trader AI

Options Universe Builder

Sprint-17

Builds the options trading universe.

=============================================================
"""

from pathlib import Path

from .universe_builder_base import UniverseBuilderBase


class OptionsUniverseBuilder(UniverseBuilderBase):
    """
    Builds the options universe.
    """

    def __init__(
        self,
        output_file: Path,
    ):

        super().__init__(
            universe_name="Options",
            output_file=output_file,
        )
    # ---------------------------------------------------------

    def select_instruments(self):
        """
        Select all option instruments from
        the instrument master.
        """

        return self.parser.get_options()

    # ---------------------------------------------------------

    @property
    def instrument_count(self) -> int:
        """
        Return the number of option instruments.
        """

        return len(self.universe.instruments)
    # ---------------------------------------------------------

    def summary(self) -> dict[str, object]:
        """
        Return a summary of the options universe.
        """

        summary = super().summary()

        summary.update(
            {
                "options_count": self.instrument_count,
            }
        )

        return summary

    # ---------------------------------------------------------

    def print_summary(self) -> None:
        """
        Print the options universe summary.
        """

        summary = self.summary()

        print()
        print("=" * 60)
        print("Options Universe Summary")
        print("=" * 60)
        print(f"Universe        : {summary['universe']}")
        print(f"Options         : {summary['options_count']}")
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
        the options universe.
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
        the options universe.
        """

        self.load_master(master_file)

        return self.save()
    # ---------------------------------------------------------

    def run_from_master(
        self,
        master_file: Path,
    ):
        """
        Execute the complete options universe
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

        return "Options"
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
