"""
=============================================================
RUSI Trader AI

Instrument Master Downloader

Sprint-17 Part-3

Responsibilities
----------------
* Download broker instrument master
* Return parsed JSON
* No cache handling here

=============================================================
"""

from __future__ import annotations

import requests


class InstrumentMasterDownloader:

    """
    Downloads broker instrument master.
    """

    #
    # Angel Instrument Master
    #
    MASTER_URL = (
        "https://margincalculator.angelbroking.com/"
        "OpenAPI_File/files/OpenAPIScripMaster.json"
    )

    def download(self):

        print()
        print("=" * 60)
        print("Downloading Instrument Master")
        print("=" * 60)

        response = requests.get(
            self.MASTER_URL,
            timeout=60,
        )

        response.raise_for_status()

        data = response.json()

        print(
            f"Downloaded Records : {len(data)}"
        )

        return data
