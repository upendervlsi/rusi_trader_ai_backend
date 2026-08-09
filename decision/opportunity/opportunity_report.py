"""
============================================================

Opportunity Report

============================================================
"""

from common.logger import get_logger

logger = get_logger("RUSI")


class OpportunityReport:

    def print(self, opportunities):

        logger.info("")
        logger.info("========================================")
        logger.info("AI Opportunity Ranking")
        logger.info("========================================")

        if not opportunities:

            logger.info("No opportunities found.")
            return

        logger.info(
            "%-4s %-15s %-8s %-10s %-10s",
            "Rank",
            "Instrument",
            "Signal",
            "Conf",
            "Score",
        )

        logger.info(
            "--------------------------------------------------------------"
        )

        for rank, item in enumerate(opportunities, start=1):

            logger.info(
                "%-4d %-15s %-8s %-10.2f %-10.2f",
                rank,
                item.symbol,
                item.signal,
                item.confidence,
                item.opportunity_score,
            )

        logger.info("")
        logger.info("Best Opportunity")

        best = opportunities[0]

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

        logger.info(
            "Score      : %.2f",
            best.opportunity_score,
        )
