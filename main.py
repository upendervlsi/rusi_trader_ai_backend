"""
============================================================

rusi_trader_ai

Main Entry

============================================================
"""

from common.logger import get_logger

from config.config_manager import ConfigManager
from core.execution_manager import ExecutionManager

logger = get_logger("RUSI")


from backend.services.trading_engine_service import (
    TradingEngineService,
)


def main():

    logger.info("Starting rusi_trader_ai")

    service = TradingEngineService()

    service.start()

    try:

        while True:

            import time

            time.sleep(1)

    except KeyboardInterrupt:

        service.stop()

if __name__ == "__main__":
    main()
