"""
RUSI Trader AI

Persistent authentication user store.

Phase 3B-4:
    - Persist User records to a local JSON file.
    - Store password hashes only.
    - Never store plaintext passwords.
    - Sessions remain in-memory.
    - No broker credentials.
    - No trading state.
"""

from __future__ import annotations

import json
from pathlib import Path
from threading import RLock

from backend.accounts.auth_models import (
    User,
    UserStatus,
)


class AuthUserStore:

    def __init__(
        self,
        path: str | Path = "data/auth/users.json",
    ) -> None:

        self._path = Path(path)
        self._lock = RLock()

    @property
    def path(self) -> Path:
        return self._path

    def load_users(self) -> list[User]:

        with self._lock:

            if not self._path.exists():
                return []

            raw = json.loads(
                self._path.read_text(
                    encoding="utf-8"
                )
            )

            if not isinstance(raw, list):
                raise ValueError(
                    "Authentication user store "
                    "must contain a JSON list."
                )

            users: list[User] = []

            for item in raw:

                if not isinstance(item, dict):
                    raise ValueError(
                        "Invalid user record."
                    )

                users.append(
                    User(
                        user_id=str(
                            item["user_id"]
                        ),
                        username=str(
                            item["username"]
                        ),
                        password_hash=str(
                            item["password_hash"]
                        ),
                        status=UserStatus(
                            item.get(
                                "status",
                                UserStatus.ACTIVE.value,
                            )
                        ),
                        created_at=str(
                            item["created_at"]
                        ),
                    )
                )

            return users

    def save_users(
        self,
        users: list[User],
    ) -> None:

        records = [
            {
                "user_id": user.user_id,
                "username": user.username,
                "password_hash": user.password_hash,
                "status": user.status.value,
                "created_at": user.created_at,
            }
            for user in users
        ]

        with self._lock:

            self._path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            temporary_path = self._path.with_suffix(
                ".tmp"
            )

            temporary_path.write_text(
                json.dumps(
                    records,
                    indent=2,
                ),
                encoding="utf-8",
            )

            temporary_path.replace(
                self._path
            )

            self._path.chmod(0o600)
