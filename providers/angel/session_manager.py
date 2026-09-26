"""
============================================================

RUSI Trader AI

Angel One Session Manager

Centralized, process-wide SmartAPI session manager.

Responsibilities
----------------
- Create one SmartAPI session per backend process.
- Reuse the authenticated SmartConnect instance.
- Protect login from concurrent threads.
- Refresh an expired JWT using the refresh token.
- Keep credentials and tokens private from logs.
- Avoid unnecessary repeated Angel One logins.

Authentication lifecycle
------------------------
Initial login:

    generateSession()
        |
        +-- jwtToken
        +-- refreshToken
        +-- feedToken

Normal operation:

    existing SmartConnect
        |
        +-- historical data
        +-- LTP
        +-- quotes
        +-- orders

JWT expiry:

    Invalid Token / AG8001
        |
        v
    refresh()
        |
        +-- generateToken(refresh_token)
        |
        +-- new JWT
        +-- new feed token
        |
        v
    same SmartConnect continues

Important
---------
Refresh does NOT perform a new login and therefore does not
generate a new TOTP.

============================================================
"""

from __future__ import annotations

import os
import threading
from typing import ClassVar

import pyotp
from dotenv import load_dotenv
from SmartApi import SmartConnect


class SessionManager:
    """
    Centralized Angel One SmartAPI session manager.

    All SessionManager instances inside the same Python process
    share one authenticated SmartConnect instance.

    This is important because RUSI Trader AI has multiple
    services that may independently create SessionManager()
    objects.
    """

    _shared_lock: ClassVar[threading.RLock] = (
        threading.RLock()
    )

    _shared_smart_api: ClassVar[
        SmartConnect | None
    ] = None

    _shared_jwt_token: ClassVar[
        str | None
    ] = None

    _shared_refresh_token: ClassVar[
        str | None
    ] = None

    _shared_feed_token: ClassVar[
        str | None
    ] = None

    def __init__(self) -> None:

        load_dotenv()

        self._client_code = os.getenv(
            "ANGEL_CLIENT_CODE"
        )

        self._password = os.getenv(
            "ANGEL_PASSWORD"
        )

        self._api_key = os.getenv(
            "ANGEL_API_KEY"
        )

        self._totp_secret = os.getenv(
            "ANGEL_TOTP_SECRET_KEY"
        )

        print(
            "Angel Session Manager Initialized"
            f" | CLIENT="
            f"{'SET' if self._client_code else 'MISSING'}"
            f" | API_KEY="
            f"{'SET' if self._api_key else 'MISSING'}"
        )

    # ========================================================
    # CONNECTION
    # ========================================================

    def connect(self) -> SmartConnect:
        """
        Return the existing SmartAPI session or create one.

        A new login is performed only when there is no shared
        SmartConnect instance in this Python process.
        """

        #
        # Fast path.
        #

        if (
            SessionManager._shared_smart_api
            is not None
        ):

            print(
                "Angel Session Manager | "
                "Reusing existing SmartAPI session"
            )

            return (
                SessionManager._shared_smart_api
            )

        #
        # Only one thread may create a login session.
        #

        with SessionManager._shared_lock:

            #
            # Double-check after lock acquisition.
            #

            if (
                SessionManager._shared_smart_api
                is not None
            ):

                print(
                    "Angel Session Manager | "
                    "Reusing existing SmartAPI session"
                )

                return (
                    SessionManager._shared_smart_api
                )

            #
            # Validate credentials.
            #

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
                    "Please configure the required "
                    "environment variables."
                )

            print(
                "Angel Session Manager | "
                "Creating SmartAPI session"
            )

            #
            # Create SmartConnect.
            #

            smart_api = SmartConnect(
                api_key=self._api_key
            )

            # ========================================================
            # AWS EC2 STATIC-IP CONFIGURATION
            # ========================================================
            # This RUSI instance runs on AWS EC2 with:
            #   Public / Elastic IP : 16.113.128.173
            #   Private IP          : 172.31.39.188
            #
            # Angel One SmartAPI is registered for the AWS Elastic IP.
            # The SmartAPI SDK defaults to stale client-IP values, so
            # explicitly configure the actual AWS instance values.
            # ========================================================

            smart_api.clientPublicIp = "16.113.128.173"
            smart_api.clientLocalIp = "172.31.39.188"

            # ========================================================
            # AWS STATIC-IP DIAGNOSTIC
            # ========================================================
            # Verify the SmartAPI SDK request headers use the actual
            # AWS EC2 public/private IP values.
            # Do NOT log credentials, JWT, refresh token, or TOTP.
            # ========================================================

            print(
                "Angel Session Manager | "
                f"SDK clientPublicIp={smart_api.clientPublicIp} | "
                f"SDK clientLocalIp={smart_api.clientLocalIp}"
            )

            try:
                diagnostic_headers = smart_api.requestHeaders()

                print(
                    "Angel Session Manager | "
                    f"Header X-ClientPublicIP="
                    f"{diagnostic_headers.get('X-ClientPublicIP')} | "
                    f"Header X-ClientLocalIP="
                    f"{diagnostic_headers.get('X-ClientLocalIP')}"
                )
            except Exception as exc:
                print(
                    "Angel Session Manager | "
                    f"IP header diagnostic failed: {exc}"
                )

            #
            # Generate current TOTP.
            #
            # TOTP is used ONLY for initial login.
            # It is NOT used for normal token refresh.
            #

            totp = pyotp.TOTP(
                self._totp_secret
            ).now()

            try:

                response = (
                    smart_api.generateSession(
                        self._client_code,
                        self._password,
                        totp,
                    )
                )

            except Exception as exc:

                SessionManager._clear_shared_state()

                raise RuntimeError(
                    "Angel One session creation failed: "
                    f"{exc}"
                ) from exc

            #
            # Validate login response.
            #

            if (
                not response
                or not response.get("status")
            ):

                SessionManager._clear_shared_state()

                raise RuntimeError(
                    "Angel One login failed: "
                    f"{response}"
                )

            data = response.get("data")

            if not data:

                SessionManager._clear_shared_state()

                raise RuntimeError(
                    "Angel One login returned no "
                    "session data."
                )

            jwt_token = data.get(
                "jwtToken"
            )

            refresh_token = data.get(
                "refreshToken"
            )

            #
            # SmartAPI's generateSession normally
            # already installs the feed token internally.
            #

            try:

                feed_token = (
                    data.get("feedToken")
                    or smart_api.getfeedToken()
                )

            except Exception:

                feed_token = None

            if not jwt_token:

                SessionManager._clear_shared_state()

                raise RuntimeError(
                    "Angel One login returned no JWT token."
                )

            if not refresh_token:

                SessionManager._clear_shared_state()

                raise RuntimeError(
                    "Angel One login returned no "
                    "refresh token."
                )

            #
            # Store authenticated session centrally.
            #

            SessionManager._shared_smart_api = (
                smart_api
            )

            SessionManager._shared_jwt_token = (
                jwt_token
            )

            SessionManager._shared_refresh_token = (
                refresh_token
            )

            SessionManager._shared_feed_token = (
                feed_token
            )

            print(
                "Angel Session Manager | "
                "SmartAPI session established"
            )

            return smart_api

    # ========================================================
    # TOKEN REFRESH
    # ========================================================

    def refresh(self) -> SmartConnect:
        """
        Refresh the current SmartAPI session.

        Normal path:
            existing refresh token -> new JWT

        Recovery path:
            refresh token rejected/invalid
                -> clear stale local session
                -> create a completely new SmartAPI login
                   using a fresh TOTP

        This is important because Angel One may invalidate both
        the JWT and the refresh token. In that situation,
        generateToken() cannot recover the session and a fresh
        generateSession() login is required.
        """

        with SessionManager._shared_lock:

            #
            # No active session.
            #

            if (
                SessionManager._shared_smart_api
                is None
            ):

                print(
                    "Angel Session Manager | "
                    "No active session during refresh; "
                    "creating initial session"
                )

                return self.connect()

            smart_api = (
                SessionManager._shared_smart_api
            )

            refresh_token = (
                SessionManager._shared_refresh_token
            )

            if not refresh_token:

                print(
                    "Angel Session Manager | "
                    "Refresh token unavailable; "
                    "starting fresh login"
                )

                SessionManager._clear_shared_state()

                return self.connect()

            print(
                "Angel Session Manager | "
                "Refreshing SmartAPI access token"
            )

            try:

                response = (
                    smart_api.generateToken(
                        refresh_token
                    )
                )

            except Exception as exc:

                #
                # The existing refresh lifecycle failed.
                # Do not keep the invalid SmartConnect/token
                # state. Start a completely fresh login.
                #

                print(
                    "Angel Session Manager | "
                    "Token refresh exception; "
                    "starting fresh login"
                )

                SessionManager._clear_shared_state()

                try:

                    return self.connect()

                except Exception as login_exc:

                    raise RuntimeError(
                        "Angel One token refresh failed and "
                        "fresh login also failed: "
                        f"{login_exc}"
                    ) from exc

            #
            # Refresh token was rejected by Angel One.
            #
            # Example:
            #
            # {
            #     "status": False,
            #     "message": "Invalid Token",
            #     "errorCode": "AG8001"
            # }
            #
            # The old refresh token cannot recover the session.
            # Clear it before connect(), otherwise connect()
            # would incorrectly reuse the stale SmartConnect.
            #

            if (
                not response
                or not response.get("status")
            ):

                print(
                    "Angel Session Manager | "
                    "Refresh rejected; "
                    "starting fresh login"
                )

                SessionManager._clear_shared_state()

                try:

                    return self.connect()

                except Exception as login_exc:

                    raise RuntimeError(
                        "Angel One token refresh was rejected "
                        "and fresh login also failed: "
                        f"{login_exc}"
                    ) from login_exc

            data = response.get("data")

            if not data:

                print(
                    "Angel Session Manager | "
                    "Refresh returned no token data; "
                    "starting fresh login"
                )

                SessionManager._clear_shared_state()

                return self.connect()

            new_jwt = data.get(
                "jwtToken"
            )

            new_refresh = data.get(
                "refreshToken"
            )

            try:

                new_feed = (
                    data.get("feedToken")
                    or smart_api.getfeedToken()
                )

            except Exception:

                new_feed = (
                    SessionManager._shared_feed_token
                )

            if not new_jwt:

                print(
                    "Angel Session Manager | "
                    "Refresh returned no JWT; "
                    "starting fresh login"
                )

                SessionManager._clear_shared_state()

                return self.connect()

            #
            # Update shared token state.
            #

            SessionManager._shared_jwt_token = (
                new_jwt
            )

            if new_refresh:

                SessionManager._shared_refresh_token = (
                    new_refresh
                )

            if new_feed:

                SessionManager._shared_feed_token = (
                    new_feed
                )

            #
            # Ensure SmartConnect uses the new credentials.
            #

            smart_api.setAccessToken(
                new_jwt
            )

            if (
                SessionManager._shared_feed_token
            ):

                smart_api.setFeedToken(
                    SessionManager._shared_feed_token
                )

            print(
                "Angel Session Manager | "
                "SmartAPI access token refreshed"
            )

            return smart_api

    # ========================================================
    # SMART API
    # ========================================================

    @property
    def smart_api(self) -> SmartConnect:
        """
        Return the shared authenticated SmartAPI instance.
        """

        if (
            SessionManager._shared_smart_api
            is None
        ):

            return self.connect()

        return (
            SessionManager._shared_smart_api
        )

    # ========================================================
    # FEED TOKEN
    # ========================================================

    @property
    def feed_token(self) -> str:

        if (
            SessionManager._shared_feed_token
            is None
        ):

            self.connect()

        if (
            SessionManager._shared_feed_token
            is None
        ):

            raise RuntimeError(
                "Feed token unavailable."
            )

        return (
            SessionManager._shared_feed_token
        )

    # ========================================================
    # TOKENS
    # ========================================================

    @property
    def jwt_token(self) -> str:

        if (
            SessionManager._shared_jwt_token
            is None
        ):

            self.connect()

        if (
            SessionManager._shared_jwt_token
            is not None
        ):

            return (
                SessionManager._shared_jwt_token
            )

        raise RuntimeError(
            "JWT token unavailable."
        )

    @property
    def refresh_token(self) -> str:

        if (
            SessionManager._shared_refresh_token
            is None
        ):

            self.connect()

        if (
            SessionManager._shared_refresh_token
            is not None
        ):

            return (
                SessionManager._shared_refresh_token
            )

        raise RuntimeError(
            "Refresh token unavailable."
        )

    # ========================================================
    # STATE
    # ========================================================

    @classmethod
    def _clear_shared_state(cls) -> None:
        """
        Clear the process-wide authentication state.

        This does NOT terminate the broker session remotely.
        It only clears local state after a failed login/reset.
        """

        cls._shared_smart_api = None
        cls._shared_jwt_token = None
        cls._shared_refresh_token = None
        cls._shared_feed_token = None

    # ========================================================
    # DISCONNECT
    # ========================================================

    def disconnect(self) -> None:
        """
        Clear the shared local session state.

        Intended for application shutdown or an explicit
        authentication reset.
        """

        with SessionManager._shared_lock:

            smart_api = (
                SessionManager._shared_smart_api
            )

            #
            # Attempt remote logout only when a client
            # code and SmartConnect session exist.
            #
            # Logout failure must not prevent local
            # cleanup.
            #

            if (
                smart_api is not None
                and self._client_code
            ):

                try:

                    smart_api.terminateSession(
                        self._client_code
                    )

                except Exception:

                    pass

            SessionManager._clear_shared_state()

        print(
            "Angel Session Manager | "
            "Shared SmartAPI session cleared"
        )
