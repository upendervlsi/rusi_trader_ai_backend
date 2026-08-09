"""
============================================================

Application Configuration

============================================================
"""

from dataclasses import dataclass
from common.enums import (
    ExecutionMode,
    DataSourceType,
)


@dataclass(slots=True)
class ApplicationConfig:
    """
    Global runtime configuration.
    """

    application_name: str

    version: str

    execution_mode: str

    datasource: str

    market: str

    timezone: str
@dataclass(slots=True)
class ApplicationConfig:

    application_name: str

    version: str

    execution_mode: ExecutionMode

    datasource: DataSourceType

    market: str

    timezone: str
