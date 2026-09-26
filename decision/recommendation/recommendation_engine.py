"""
RUSI Trader AI

Recommendation Engine

Responsible for converting the Decision Runtime result into
a complete trading recommendation.

=============================================================

RUSI V1 = OPTION BUYING ONLY

Trading model:

    Bullish underlying
        -> select CE
        -> BUY CE

    Bearish underlying
        -> select PE
        -> BUY PE

    HOLD
        -> no option contract
        -> no executable trade

IMPORTANT:

The underlying NIFTY/BANKNIFTY/etc. price is used ONLY
for selecting the option contract.

The actual option premium is ALWAYS obtained from the
selected option's LIVE LTP.

Risk management is applied to the OPTION PREMIUM.

V1 option-buying risk model:

    Stop Loss = 25% below option entry
    Target    = 40% above option entry

This applies identically to:

    BUY CE
    BUY PE

We never sell the option in V1.
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

    """
    Converts Decision Runtime output into a
    TradingRecommendation.

    RUSI V1 OPTION BUYING:

        BUY decision  -> BUY CE
        SELL decision -> BUY PE
        HOLD          -> no trade

    The recommendation field represents the
    underlying AI direction.

    The selected option contract represents the
    actual instrument to BUY.
    """

    # =========================================================
    # V1 OPTION BUYING RISK MODEL
    # =========================================================

    # Option premium risk percentages are supplied
    # by TradingConfig.

    # =========================================================
    # INITIALIZATION
    # =========================================================

    def __init__(self, trading_config):

        self._trading_config = trading_config
        self._option_resolver = OptionResolver()

    # =========================================================
    # GENERATE RECOMMENDATION
    # =========================================================

    def generate(
        self,
        context,
        market_data_engine=None,
    ) -> TradingRecommendation:

        # -----------------------------------------------------
        # Decision Signal
        # -----------------------------------------------------

        try:

            decision_signal = (
                context.decision.signal.name.upper()
            )

        except Exception as exc:

            logger.exception(
                "Unable to resolve decision signal | "
                "Error=%s",
                exc,
            )

            return TradingRecommendation(
                recommendation="HOLD",
                symbol="",
            )

        # -----------------------------------------------------
        # Base Recommendation
        # -----------------------------------------------------

        recommendation = TradingRecommendation(

            recommendation=decision_signal,

            symbol=(
                context.instrument.symbol
                if context.instrument
                else ""
            ),

            confidence=(
                context.decision.confidence
            ),

            score=(
                context.decision.score
            ),

        )

        # -----------------------------------------------------
        # Evidence
        # -----------------------------------------------------

        if (
            context.evidence is not None
            and hasattr(
                context.evidence,
                "evidences",
            )
        ):

            for evidence in (
                context.evidence.evidences
            ):

                recommendation.reasons.append(

                    f"{evidence.feature_id} : "
                    f"{evidence.signal}"

                )

        # -----------------------------------------------------
        # HOLD
        # -----------------------------------------------------
        #
        # HOLD is NOT an option transaction.
        #
        # Therefore:
        #
        #   no option
        #   no entry
        #   no SL
        #   no target
        #

        if decision_signal == "HOLD":

            logger.info(
                "Recommendation HOLD | "
                "No option contract selected"
            )

            return recommendation

        # -----------------------------------------------------
        # Validate Actionable Direction
        # -----------------------------------------------------

        if decision_signal not in (
            "BUY",
            "SELL",
        ):

            logger.warning(
                "Unsupported Decision Signal | %s",
                decision_signal,
            )

            return recommendation

        # -----------------------------------------------------
        # Underlying Price
        # -----------------------------------------------------
        #
        # IMPORTANT:
        #
        # This price is used ONLY for option selection.
        #
        # It must NEVER become the option entry price.
        #

        try:

            underlying_price = float(
                context
                .market_snapshot
                .latest_candle
                .close
            )

        except Exception as exc:

            logger.warning(
                "Unable to resolve underlying price | "
                "Signal=%s | Error=%s",
                decision_signal,
                exc,
            )

            return recommendation

        if underlying_price <= 0:

            logger.warning(
                "Invalid underlying price | "
                "Signal=%s | Price=%s",
                decision_signal,
                underlying_price,
            )

            return recommendation

        # -----------------------------------------------------
        # Underlying / Analysis Instrument
        # -----------------------------------------------------

        exchange = (

            getattr(
                context.instrument,
                "exchange",
                None,
            )

            if context.instrument
            else None

        )

        underlying_symbol = (

            context.instrument.symbol

            if context.instrument

            else ""

        )

        if not underlying_symbol:

            logger.warning(
                "Underlying symbol unavailable | "
                "Signal=%s",
                decision_signal,
            )

            return recommendation

        # -----------------------------------------------------
        # OPTION RESOLUTION
        # -----------------------------------------------------
        #
        # BUY underlying  -> CE
        # SELL underlying -> PE
        #
        # The resulting option is ALWAYS bought.
        #

        try:

            option = self._option_resolver.resolve(

                underlying_symbol=(
                    underlying_symbol
                ),

                recommendation=(
                    decision_signal
                ),

                underlying_price=(
                    underlying_price
                ),

                exchange=exchange,

            )

        except Exception as exc:

            logger.exception(
                "Option Resolution Failed | "
                "Signal=%s | Underlying=%s | "
                "Error=%s",
                decision_signal,
                underlying_symbol,
                exc,
            )

            return recommendation

        if option is None:

            logger.warning(
                "Option Resolution Returned None | "
                "Signal=%s | Underlying=%s | "
                "Price=%.2f",
                decision_signal,
                underlying_symbol,
                underlying_price,
            )

            return recommendation

        # -----------------------------------------------------
        # Selected Option Contract
        # -----------------------------------------------------

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

        recommendation.lot_size = (
            option.lot_size
        )

        # -----------------------------------------------------
        # V1 OPTION BUYING MODEL
        # -----------------------------------------------------
        #
        # Regardless of underlying direction:
        #
        #   BUY underlying  -> BUY CE
        #   SELL underlying -> BUY PE
        #
        # Actual transaction is ALWAYS BUY.
        #

        option_transaction = "BUY"

        logger.info(
            "OPTION BUYING MODE | "
            "Underlying Signal=%s | "
            "Transaction=%s | "
            "Underlying=%s | "
            "UnderlyingPrice=%.2f | "
            "Option=%s | Type=%s | "
            "Strike=%s | Expiry=%s | Token=%s",

            decision_signal,

            option_transaction,

            underlying_symbol,

            underlying_price,

            recommendation.option_symbol,

            recommendation.option_type,

            recommendation.strike,

            recommendation.expiry,

            recommendation.option_token,

        )

        # -----------------------------------------------------
        # MARKET DATA ENGINE
        # -----------------------------------------------------

        if market_data_engine is None:

            logger.warning(
                "Market Data Engine unavailable for "
                "option LTP | %s",
                recommendation.option_symbol,
            )

            return recommendation

        # -----------------------------------------------------
        # LIVE OPTION LTP
        # -----------------------------------------------------
        #
        # This is the ONLY valid option entry price.
        #

        try:

            option_ltp = (

                market_data_engine
                .get_instrument_ltp(

                    exchange=(
                        recommendation.exchange
                    ),

                    symbol=(
                        recommendation.option_symbol
                    ),

                    token=(
                        recommendation.option_token
                    ),

                )

            )

        except Exception as exc:

            logger.exception(
                "Option LTP Lookup Failed | "
                "Option=%s | Token=%s | Error=%s",

                recommendation.option_symbol,

                recommendation.option_token,

                exc,

            )

            return recommendation

        if option_ltp is None:

            logger.warning(
                "Option LTP Response None | "
                "Option=%s",
                recommendation.option_symbol,
            )

            return recommendation

        # -----------------------------------------------------
        # LTP VALUE
        # -----------------------------------------------------

        if option_ltp.last_price is None:

            logger.warning(
                "Option LTP Missing | %s",
                recommendation.option_symbol,
            )

            return recommendation

        try:

            live_option_price = float(
                option_ltp.last_price
            )

        except (
            TypeError,
            ValueError,
        ):

            logger.warning(
                "Invalid Option LTP Value | "
                "Option=%s | Value=%s",

                recommendation.option_symbol,

                option_ltp.last_price,

            )

            return recommendation

        if live_option_price <= 0:

            logger.warning(
                "Invalid Option LTP | "
                "Option=%s | LTP=%.4f",

                recommendation.option_symbol,

                live_option_price,

            )

            return recommendation

        # -----------------------------------------------------
        # LIVE DATA VALIDATION
        # -----------------------------------------------------

        if (
            option_ltp.data_status
            != "LIVE"
        ):

            logger.warning(
                "Option LTP Not LIVE | "
                "Option=%s | Status=%s",

                recommendation.option_symbol,

                option_ltp.data_status,

            )

            return recommendation

        # -----------------------------------------------------
        # ACTUAL OPTION ENTRY PRICE
        # -----------------------------------------------------
        #
        # NEVER use underlying_price here.
        #

        recommendation.entry_price = round(
            live_option_price,
            2,
        )

        # -----------------------------------------------------
        # OPTION BUYING RISK PLAN
        # -----------------------------------------------------
        #
        # Both CE and PE are BUY transactions.
        #
        # SL     = Entry - 25%
        # Target = Entry + 40%
        #

        recommendation.stop_loss = round(

            recommendation.entry_price
            * (
                1.0
                - (
                    self._trading_config
                    .option_stop_loss_percent
                    / 100.0
                )
            ),

            2,

        )

        recommendation.target_price = round(

            recommendation.entry_price
            * (
                1.0
                + (
                    self._trading_config
                    .option_target_percent
                    / 100.0
                )
            ),

            2,

        )

        # -----------------------------------------------------
        # RISK / REWARD
        # -----------------------------------------------------

        risk = (

            recommendation.entry_price
            - recommendation.stop_loss

        )

        reward = (

            recommendation.target_price
            - recommendation.entry_price

        )

        if risk > 0:

            recommendation.risk_reward = round(

                reward / risk,

                2,

            )

        else:

            recommendation.risk_reward = 0.0

        # -----------------------------------------------------
        # FINAL VALIDATION
        # -----------------------------------------------------

        if (
            recommendation.entry_price <= 0
            or recommendation.stop_loss <= 0
            or recommendation.target_price <= 0
        ):

            logger.warning(
                "Invalid Option Trade Plan | "
                "Option=%s | Entry=%.2f | "
                "SL=%.2f | Target=%.2f",

                recommendation.option_symbol,

                recommendation.entry_price,

                recommendation.stop_loss,

                recommendation.target_price,

            )

            return recommendation

        # -----------------------------------------------------
        # FINAL OPTION LOGGING
        # -----------------------------------------------------

        logger.info(
            "Option Live Price | "
            "Underlying Signal=%s | "
            "Transaction=%s | "
            "Option=%s | Type=%s | "
            "LTP=%.2f",

            decision_signal,

            option_transaction,

            recommendation.option_symbol,

            recommendation.option_type,

            recommendation.entry_price,

        )

        logger.info(
            "Option Trade Plan | "
            "BUY %s | "
            "Entry=%.2f | "
            "SL=%.2f | "
            "Target=%.2f | "
            "RR=%.2f",

            recommendation.option_symbol,

            recommendation.entry_price,

            recommendation.stop_loss,

            recommendation.target_price,

            recommendation.risk_reward,

        )

        return recommendation
