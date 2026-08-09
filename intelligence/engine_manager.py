"""
============================================================

Engine Manager

============================================================
"""

from time import perf_counter

from common.logger import get_logger
from common.intelligence_result import IntelligenceResult

logger = get_logger("RUSI")


class EngineManager:

    def __init__(self):

        self._engines = []

    def register(self, engine):

        self._engines.append(engine)

    def execute(self, snapshot):

        intelligence = IntelligenceResult()

        start_time = perf_counter()

        for engine in self._engines:

            logger.info("Running %s", engine.name)

            try:

                result = engine.analyze(snapshot)

                intelligence.results.append(result)

                intelligence.successful_engines += 1

            except Exception:

                logger.exception(
                    "Engine Failed : %s",
                    engine.name,
                )

                intelligence.failed_engines += 1

        end_time = perf_counter()

        intelligence.execution_time_ms = (
            end_time - start_time
        ) * 1000

        return intelligence
