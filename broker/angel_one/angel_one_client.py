"""
========================================================================

RUSI Trader AI

Angel One Client

Description
-----------
SmartAPI 1.5.5 client wrapper.

========================================================================
"""

from __future__ import annotations

from SmartApi import SmartConnect

from broker.angel_one.angel_credentials import AngelCredentials


class AngelOneClient:
    """
    Wrapper around SmartAPI SmartConnect.
    """

    def __init__(
        self,
        credentials: AngelCredentials,
    ) -> None:

        self._credentials = credentials

        self._smart_api = SmartConnect(
            api_key=credentials.api_key,
        )

        self._jwt_token = ""
        self._refresh_token = ""
        self._feed_token = ""

        self._logged_in = False

    @property
    def smart_api(self) -> SmartConnect:
        return self._smart_api

    @property
    def feed_token(self) -> str:
        return self._feed_token

    @property
    def jwt_token(self) -> str:
        return self._jwt_token

    @property
    def refresh_token(self) -> str:
        return self._refresh_token

    def is_logged_in(self) -> bool:
        return self._logged_in

    def login(
        self,
        totp: str,
    ) -> bool:
        """
        Login using a runtime-generated TOTP.
        """

        response = self._smart_api.generateSession(
            self._credentials.client_id,
            self._credentials.pin,
            totp,
        )

        if not response.get("status", False):
            raise RuntimeError(
                response.get("message", "Angel One login failed.")
            )

        data = response["data"]

        self._jwt_token = data["jwtToken"]
        self._refresh_token = data["refreshToken"]

        self._feed_token = self._smart_api.getfeedToken()

        self._logged_in = True

        return True

    def logout(self) -> None:

        if not self._logged_in:
            return

        try:
            self._smart_api.terminateSession(
                self._credentials.client_id,
            )
        finally:
            self._logged_in = False

            self._jwt_token = ""
            self._refresh_token = ""
            self._feed_token = ""
