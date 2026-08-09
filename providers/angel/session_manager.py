"""
============================================================

Angel One Session Manager

============================================================
"""

from __future__ import annotations

import os

import pyotp
from dotenv import load_dotenv
from SmartApi import SmartConnect


class SessionManager:
    """
    Handles authentication with Angel One SmartAPI.
    """

    def __init__(self) -> None:

        load_dotenv()

        self._client_code = os.getenv("ANGEL_CLIENT_CODE")
        self._password = os.getenv("ANGEL_PASSWORD")
        self._api_key = os.getenv("ANGEL_API_KEY")
        self._totp_secret = os.getenv("ANGEL_TOTP_SECRET_KEY")

        self._smart_api: SmartConnect | None = None
        self._jwt_token: str | None = None
        self._refresh_token: str | None = None
        self._feed_token: str | None = None
        print("API KEY      :", self._api_key)
        print("CLIENT CODE  :", self._client_code)
        print("PASSWORD LEN :", len(self._password))

    def connect(self) -> SmartConnect:

        if self._smart_api is not None:
            return self._smart_api

        if not all(
            [
                self._client_code,
                self._password,
                self._api_key,
                self._totp_secret,
            ]
        ):
            raise RuntimeError(
                "Angel One credentials are missing. "
                "Please configure the required environment variables."
            )

        self._smart_api = SmartConnect(api_key=self._api_key)

        totp = pyotp.TOTP(self._totp_secret).now()

        response = self._smart_api.generateSession(
            self._client_code,
            self._password,
            totp,
        )

        if not response or not response.get("status"):
            raise RuntimeError(
                f"Angel One login failed: {response}"
            )

        data = response["data"]

        self._jwt_token = data["jwtToken"]
        self._refresh_token = data["refreshToken"]
        self._feed_token = self._smart_api.getfeedToken()

        return self._smart_api

    @property
    def smart_api(self) -> SmartConnect:
        if self._smart_api is None:
            raise RuntimeError("Session not established.")
        return self._smart_api

    @property
    def feed_token(self) -> str:
        if self._feed_token is None:
            raise RuntimeError("Feed token unavailable.")
        return self._feed_token

    def disconnect(self) -> None:
        self._smart_api = None
        self._jwt_token = None
        self._refresh_token = None
        self._feed_token = None
