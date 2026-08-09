"""
============================================================

Configuration Manager

============================================================
"""

from pathlib import Path

import yaml

from config.application_config import ApplicationConfig
from common.enums import (
    ExecutionMode,
    DataSourceType,
)

class ConfigManager:

    def __init__(self, config_file: str):

        self._config_file = Path(config_file)

    def load(self) -> ApplicationConfig:

        with self._config_file.open(
            "r",
            encoding="utf-8",
        ) as fp:

            data = yaml.safe_load(fp)

        app = data["application"]

        return ApplicationConfig(
            application_name=app["application_name"],
            version=app["version"],
            execution_mode=ExecutionMode(app["execution_mode"]),
            datasource=DataSourceType(app["datasource"]),
            market=app["market"],
            timezone=app["timezone"],
        )
