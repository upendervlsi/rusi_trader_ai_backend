"""
============================================================

Opportunity Ranker

============================================================
"""

from decision.opportunity.opportunity import TradingOpportunity


class OpportunityRanker:

    def rank(self, recommendations):

        opportunities = []

        for recommendation in recommendations:

            item = TradingOpportunity()

            item.symbol = (
                recommendation.underlying_symbol
                or recommendation.symbol
            )

            item.exchange = recommendation.exchange

            item.signal = recommendation.recommendation

            item.confidence = recommendation.confidence

            item.score = recommendation.score

            item.recommendation = recommendation

            #
            # V1 Opportunity Score
            #

            item.opportunity_score = (

                recommendation.confidence * 0.60
                + abs(recommendation.score) * 0.40

            )

            opportunities.append(item)

        opportunities.sort(

            key=lambda x: x.opportunity_score,

            reverse=True,

        )

        return opportunities
