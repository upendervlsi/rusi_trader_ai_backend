"""
============================================================

Scanner Report

============================================================
"""

from common.logger import get_logger

logger = get_logger("RUSI")


class ScannerReport:

    def print(self, results):

        logger.info("")
        logger.info("========================================")
        logger.info("Today's Market Opportunities")
        logger.info("========================================")

        if not results:

            logger.info("No opportunities available.")
            return

        results = sorted(
            results,
            key=lambda x: x.confidence,
            reverse=True,
        )

        for index, item in enumerate(results, start=1):

            logger.info("")

            logger.info(
                "%d. %s",
                index,
                item.symbol,
            )

            logger.info(
                "Signal      : %s",
                item.signal,
            )

            logger.info(
                "Confidence  : %.2f",
                item.confidence,
            )

            logger.info(
                "Score       : %.2f",
                item.score,
            )

            if item.option_symbol:

                logger.info(
                    "Option      : %s",
                    item.option_symbol,
                )

        logger.info("")

        best = results[0]

        logger.info("========================================")
        logger.info("Best Opportunity")
        logger.info("========================================")
        logger.info(
            "Instrument : %s",
            best.symbol,
        )
        logger.info(
            "Signal     : %s",
            best.signal,
        )
        logger.info(
            "Confidence : %.2f",
            best.confidence,
        )
