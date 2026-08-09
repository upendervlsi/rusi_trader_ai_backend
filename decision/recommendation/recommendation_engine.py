"""
RUSI Trader AI

Recommendation Engine

============================================================
"""

from common.logger import get_logger

from decision.recommendation.recommendation import (
    TradingRecommendation,
)

from tools.market_universe.option_resolver import (
    OptionResolver,
)


logger = get_logger("RUSI")


class RecommendationEngine:

    def __init__(self):

        self._option_resolver = OptionResolver()

    # ---------------------------------------------------------
    # Generate Recommendation
    # ---------------------------------------------------------

    def generate(

        self,

        context,

    ) -> TradingRecommendation:

        recommendation = TradingRecommendation(

            recommendation=context.decision.signal.name,

            symbol=(
                context.instrument.symbol
                if context.instrument
                else ""
            ),

            confidence=context.decision.confidence,

            score=context.decision.score,

        )

        #
        # Evidence
        #

        for evidence in context.evidence.evidences:

            recommendation.reasons.append(

                f"{evidence.feature_id} : "
                f"{evidence.signal}"

            )

        #
        # Entry Price
        #

        recommendation.entry_price = (

            context.market_snapshot.latest_candle.close

        )

        #
        # Temporary Risk Values
        #

        recommendation.stop_loss = (

            recommendation.entry_price * 0.99

        )

        recommendation.target_price = (

            recommendation.entry_price * 1.02

        )

        risk = (

            recommendation.entry_price
            - recommendation.stop_loss

        )

        reward = (

            recommendation.target_price
            - recommendation.entry_price

        )

        if risk > 0:

            recommendation.risk_reward = (

                reward / risk

            )

        #
        # Option Resolution
        #

        try:

            #
            # Resolve exchange from the actual
            # runtime instrument.
            #
            # This is critical for MCX:
            #
            # CRUDEOIL19AUG26FUT
            #       ↓
            # exchange = MCX
            #       ↓
            # MCX option lookup
            #
            exchange = (

                getattr(
                    context.instrument,
                    "exchange",
                    None,
                )

                if context.instrument
                else None

            )

            option = self._option_resolver.resolve(

                underlying_symbol=(
                    context.instrument.symbol
                    if context.instrument
                    else ""
                ),

                recommendation=(
                    recommendation.recommendation
                ),

                underlying_price=(
                    recommendation.entry_price
                ),

                exchange=exchange,

            )

            if option:

                recommendation.underlying_symbol = (

                    option.underlying_symbol

                )

                recommendation.option_symbol = (

                    option.option_symbol

                )

                recommendation.exchange = (

                    option.exchange

                )

                recommendation.option_token = (

                    option.token

                )

                recommendation.strike = (

                    option.strike

                )

                recommendation.expiry = (

                    option.expiry

                )

                recommendation.option_type = (

                    option.option_type

                )

        except Exception as ex:

            logger.warning(

                "Option resolution failed : %s",

                ex,

            )

        return recommendation

    # ---------------------------------------------------------
    # Print Recommendation
    # ---------------------------------------------------------

    def print_report(

        self,

        recommendation,

    ):

        logger.info("")

        logger.info(
            "===================================="
        )

        logger.info(
            "Trading Recommendation"
        )

        logger.info(
            "===================================="
        )

        logger.info(

            "Underlying          : %s",

            recommendation.underlying_symbol
            or recommendation.symbol,

        )

        #
        # Analysis Instrument
        #

        if recommendation.symbol:

            logger.info(

                "Analysis Instrument : %s",

                recommendation.symbol,

            )

        #
        # Recommended Option
        #

        if recommendation.option_symbol:

            logger.info("")

            logger.info(

                "Recommended Option  : %s",

                recommendation.option_symbol,

            )

            logger.info(

                "Exchange            : %s",

                recommendation.exchange,

            )

            logger.info(

                "Token               : %s",

                recommendation.option_token,

            )

            logger.info(

                "Strike              : %.2f",

                recommendation.strike,

            )

            logger.info(

                "Expiry              : %s",

                recommendation.expiry,

            )

            logger.info(

                "Option Type         : %s",

                recommendation.option_type,

            )

        logger.info("")

        logger.info(

            "Recommendation      : %s",

            recommendation.recommendation,

        )

        logger.info(

            "Confidence          : %.2f",

            recommendation.confidence,

        )

        logger.info(

            "Score               : %.2f",

            recommendation.score,

        )

        logger.info("")

        logger.info(

            "Entry Price         : %.2f",

            recommendation.entry_price,

        )

        logger.info(

            "Stop Loss           : %.2f",

            recommendation.stop_loss,

        )

        logger.info(

            "Target Price       : %.2f",

            recommendation.target_price,

        )

        logger.info(

            "Risk Reward        : %.2f",

            recommendation.risk_reward,

        )

        #
        # AI Reasons
        #

        if recommendation.reasons:

            logger.info("")

            logger.info("Reasons")

            logger.info("-------")

            for reason in recommendation.reasons:

                logger.info(

                    "- %s",

                    reason,

                )
