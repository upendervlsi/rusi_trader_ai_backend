"""
=============================================================
RUSI Trader AI

Universe Builder Base

Sprint-17

Base class for all market universe builders.

=============================================================
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from pathlib import Path

from .instrument_master_parser import InstrumentMasterParser
from .universe_models import Universe
from .universe_writer import UniverseWriter


class UniverseBuilderBase(ABC):
    """
    Common functionality shared by all
    universe builders.
    """

    def __init__(
        self,
        universe_name: str,
        output_file: Path,
    ):

        self._parser = InstrumentMasterParser()

        self._writer = UniverseWriter()

        self._universe = Universe(
            name=universe_name,
        )

        self._output_file = output_file

    # ---------------------------------------------------------

    @property
    def parser(self) -> InstrumentMasterParser:
        """
        Return the instrument master parser.
        """

        return self._parser

    # ---------------------------------------------------------

    @property
    def writer(self) -> UniverseWriter:
        """
        Return the universe writer.
        """

        return self._writer

    # ---------------------------------------------------------

    @property
    def universe(self) -> Universe:
        """
        Return the working universe.
        """

        return self._universe

    # ---------------------------------------------------------

    @property
    def output_file(self) -> Path:
        """
        Return the output JSON file.
        """

        return self._output_file

    # ---------------------------------------------------------

    @property
    def universe_name(self) -> str:
        """
        Return the universe name.
        """

        return self._universe.name

    # ---------------------------------------------------------

    @abstractmethod
    def select_instruments(self):
        """
        Return the instruments that belong
        to this universe.
        """

        raise NotImplementedError

    # ---------------------------------------------------------

    def load_master(
        self,
        master_file: Path,
    ) -> None:
        """
        Load the broker instrument master.
        """

        self.parser.load(master_file)

    # ---------------------------------------------------------

    def build(self) -> Universe:
        """
        Build the universe.
        """

        self.universe.instruments = list(
            self.select_instruments()
        )

        return self.universe
    # ---------------------------------------------------------

    def sort_universe(self) -> None:
        """
        Sort instruments by exchange,
        segment and symbol.
        """

        self.universe.instruments.sort(
            key=lambda instrument: (
                instrument.exchange,
                instrument.segment,
                instrument.symbol,
            )
        )

    # ---------------------------------------------------------

    def remove_duplicates(self) -> None:
        """
        Remove duplicate instruments.
        """

        unique = {}

        for instrument in self.universe.instruments:

            key = (
                instrument.exchange,
                instrument.segment,
                instrument.symbol,
                instrument.token,
            )

            unique[key] = instrument

        self.universe.instruments = list(
            unique.values()
        )
    # ---------------------------------------------------------

    def build(self) -> Universe:
        """
        Build the universe.
        """

        self.universe.instruments = list(
            self.select_instruments()
        )

        self.remove_duplicates()

        self.sort_universe()

        return self.universe
    # ---------------------------------------------------------

    def write_universe(self) -> None:
        """
        Write the universe to the configured output file.
        """

        self.writer.write(
            universe=self.universe,
            output_file=self.output_file,
        )

    # ---------------------------------------------------------

    def save(self) -> Universe:
        """
        Build and save the universe.
        """

        universe = self.build()

        self.write_universe()

        return universe
    # ---------------------------------------------------------

    def summary(self) -> dict[str, object]:
        """
        Return build summary.
        """

        return {
            "universe": self.universe_name,
            "instrument_count": len(self.universe.instruments),
            "output_file": str(self.output_file),
        }

    # ---------------------------------------------------------

    def print_summary(self) -> None:
        """
        Print build summary.
        """

        summary = self.summary()

        print()
        print("=" * 60)
        print(f"{summary['universe']} Universe")
        print("=" * 60)
        print(f"Instruments : {summary['instrument_count']}")
        print(f"Output File : {summary['output_file']}")
        print("=" * 60)
        print()

    # ---------------------------------------------------------

    def run(self) -> Universe:
        """
        Execute the complete universe build workflow.
        """

        universe = self.save()

        self.print_summary()

        return universe

    # ---------------------------------------------------------

    def __len__(self) -> int:
        """
        Return the number of instruments in the universe.
        """

        return len(self.universe.instruments)
