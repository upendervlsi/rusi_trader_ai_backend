"""
=============================================================
RUSI Trader AI

Universe Builder

Master entry point for generating market universes.

Sprint-17
=============================================================
"""

from __future__ import annotations

from pathlib import Path

from .constants import (
    UNIVERSE_DIR,
)


class UniverseBuilder:

    def __init__(self):

        UNIVERSE_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

    def build(self) -> None:

        from .instrument_master_manager import (
            InstrumentMasterManager,
        )

        from .instrument_master_downloader import (
            InstrumentMasterDownloader,
        )

        manager = InstrumentMasterManager()

        print("=" * 60)
        print("Market Universe Builder")
        print("=" * 60)

        manager.print_status()

        #
        # Download if cache missing/expired
        #
        if manager.refresh_required():

            print("Downloading latest instrument master...")

            downloader = InstrumentMasterDownloader()

            data = downloader.download()

            manager.save_master(data)

            print("Instrument master saved.")

        else:

            print("Using cached instrument master.")

        print()

        print("Market Universe Ready")
