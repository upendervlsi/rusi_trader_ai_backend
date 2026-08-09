"""
========================================================================

RUSI Trader AI

Angel One Credentials

Description:
    Immutable credentials model for Angel One SmartAPI.

========================================================================
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AngelCredentials:
    """
    Angel One login credentials.

    All values are loaded from configuration.
    """

    api_key: str

    client_id: str

    pin: str

    totp_secret: str

    vendor_code: str = ""

    imei: str = ""
