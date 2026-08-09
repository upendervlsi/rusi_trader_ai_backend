"""
====================================================================
RUSI Trader AI

File:
    intelligence/core/base_model.py

Description:
    Common base class for all immutable data models used throughout
    the intelligence framework.

Design Goals
------------
* Immutable
* Strong typing
* Easy serialization
* Easy logging
* JSON friendly
* Production ready

Author:
    RUSI Trader AI
====================================================================
"""

from __future__ import annotations

from dataclasses import asdict
from dataclasses import fields
from dataclasses import is_dataclass
import json
from typing import Any
from typing import Dict
from typing import Type
from typing import TypeVar

T = TypeVar("T", bound="BaseModel")


class BaseModel:
    """
    Base class for all intelligence models.

    Provides common helper methods without forcing
    business logic into the model classes.
    """

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert dataclass to dictionary.
        """

        if not is_dataclass(self):
            raise TypeError(
                f"{self.__class__.__name__} must be a dataclass."
            )

        return asdict(self)

    def to_json(self, indent: int = 4) -> str:
        """
        Convert object to JSON string.
        """

        return json.dumps(
            self.to_dict(),
            indent=indent,
            default=str,
        )

    @classmethod
    def from_dict(
        cls: Type[T],
        data: Dict[str, Any],
    ) -> T:
        """
        Construct object from dictionary.
        """

        valid_fields = {
            f.name for f in fields(cls)
        }

        filtered = {
            k: v
            for k, v in data.items()
            if k in valid_fields
        }

        return cls(**filtered)

    def validate(self) -> None:
        """
        Override in child classes if validation
        is required.
        """

        return

    def __str__(self) -> str:

        return self.to_json(indent=2)
