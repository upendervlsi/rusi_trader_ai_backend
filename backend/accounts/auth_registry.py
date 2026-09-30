"""
RUSI Trader AI

Authentication registry.

Phase 3A:
    - In-process user registry.
    - Password-hash based authentication.
    - In-process session registry.
    - Thread safe.
    - No broker credentials.
    - No trading operations.

Persistent authentication will be introduced later.
"""

from __future__ import annotations

import hashlib
import hmac
import secrets
from threading import RLock

from backend.accounts.auth_models import (
    AuthSession,
    User,
)
from backend.accounts.auth_store import (
    AuthUserStore,
)


class AuthRegistry:

    def __init__(
        self,
        store: AuthUserStore | None = None,
    ) -> None:

        self._lock = RLock()

        self._users: dict[str, User] = {}
        self._username_index: dict[str, str] = {}
        self._sessions: dict[str, AuthSession] = {}

        self._store = store

        if self._store is not None:
            self._load_persisted_users()

    def _load_persisted_users(self) -> None:

        users = self._store.load_users()

        for user in users:
            self.register_user(
                user,
                persist=False,
            )


    @staticmethod
    def _normalize_username(
        username: str,
    ) -> str:

        if not username:
            raise ValueError(
                "username cannot be empty."
            )

        return username.strip().lower()

    @staticmethod
    def hash_password(
        password: str,
    ) -> str:

        if not password:
            raise ValueError(
                "password cannot be empty."
            )

        salt = secrets.token_bytes(16)

        digest = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            310_000,
        )

        return (
            "pbkdf2_sha256$"
            "310000$"
            f"{salt.hex()}$"
            f"{digest.hex()}"
        )

    @staticmethod
    def verify_password(
        password: str,
        password_hash: str,
    ) -> bool:

        if not password or not password_hash:
            return False

        try:
            algorithm, iterations, salt_hex, digest_hex = (
                password_hash.split("$")
            )

            if algorithm != "pbkdf2_sha256":
                return False

            expected_iterations = int(iterations)

            salt = bytes.fromhex(
                salt_hex
            )

            expected_digest = bytes.fromhex(
                digest_hex
            )

            actual_digest = hashlib.pbkdf2_hmac(
                "sha256",
                password.encode("utf-8"),
                salt,
                expected_iterations,
            )

            return hmac.compare_digest(
                actual_digest,
                expected_digest,
            )

        except (
            ValueError,
            TypeError,
        ):
            return False

    def register_user(
        self,
        user: User,
        persist: bool = True,
    ) -> User:

        if not user.user_id:
            raise ValueError(
                "user_id cannot be empty."
            )

        username = self._normalize_username(
            user.username
        )

        with self._lock:

            if user.user_id in self._users:
                raise ValueError(
                    f"User already exists: "
                    f"{user.user_id}"
                )

            if username in self._username_index:
                raise ValueError(
                    f"Username already exists: "
                    f"{username}"
                )

            self._users[user.user_id] = user
            self._username_index[
                username
            ] = user.user_id

            if (
                persist
                and self._store is not None
            ):
                self._store.save_users(
                    list(self._users.values())
                )

        return user

    def get_user(
        self,
        user_id: str,
    ) -> User:

        if not user_id:
            raise ValueError(
                "user_id cannot be empty."
            )

        with self._lock:

            user = self._users.get(
                user_id
            )

        if user is None:
            raise KeyError(
                f"User not found: {user_id}"
            )

        return user

    def change_password(
        self,
        user_id: str,
        new_password: str,
        persist: bool = True,
    ) -> User:

        if not user_id:
            raise ValueError(
                "user_id cannot be empty."
            )

        if not new_password:
            raise ValueError(
                "password cannot be empty."
            )

        new_password_hash = self.hash_password(
            new_password
        )

        with self._lock:

            user = self._users.get(
                user_id
            )

            if user is None:
                raise KeyError(
                    f"User not found: {user_id}"
                )

            updated_user = User(
                user_id=user.user_id,
                username=user.username,
                password_hash=new_password_hash,
                status=user.status,
                created_at=user.created_at,
            )

            self._users[user_id] = updated_user

            if (
                persist
                and self._store is not None
            ):
                self._store.save_users(
                    list(self._users.values())
                )

        return updated_user

    def authenticate(
        self,
        username: str,
        password: str,
    ) -> AuthSession:

        normalized_username = (
            self._normalize_username(
                username
            )
        )

        with self._lock:

            user_id = self._username_index.get(
                normalized_username
            )

            user = (
                self._users.get(user_id)
                if user_id is not None
                else None
            )

        if user is None:
            raise ValueError(
                "Invalid username or password."
            )

        if not user.is_active():
            raise ValueError(
                "User account is disabled."
            )

        if not self.verify_password(
            password,
            user.password_hash,
        ):
            raise ValueError(
                "Invalid username or password."
            )

        session = AuthSession(
            session_id=secrets.token_urlsafe(32),
            user_id=user.user_id,
        )

        with self._lock:
            self._sessions[
                session.session_id
            ] = session

        return session

    def get_session(
        self,
        session_id: str,
    ) -> AuthSession:

        if not session_id:
            raise ValueError(
                "session_id cannot be empty."
            )

        with self._lock:

            session = self._sessions.get(
                session_id
            )

        if session is None:
            raise KeyError(
                "Session not found."
            )

        return session

    def logout(
        self,
        session_id: str,
    ) -> None:

        if not session_id:
            raise ValueError(
                "session_id cannot be empty."
            )

        with self._lock:
            self._sessions.pop(
                session_id,
                None,
            )

    def list_users(self) -> list[User]:

        with self._lock:
            return list(
                self._users.values()
            )

    def clear(self) -> None:

        with self._lock:
            self._users.clear()
            self._username_index.clear()
            self._sessions.clear()
