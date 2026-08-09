"""
============================================================

Execution Manager

============================================================
"""

from datetime import datetime, UTC, timedelta

from common.logger import get_logger

from core.broker_manager import BrokerManager
from builders.candle_builder import CandleBuilder
from builders.market_snapshot_builder import MarketSnapshotBuilder
from intelligence.intelligence_manager import IntelligenceManager
from intelligence.features.feature_engine import FeatureEngine

from intelligence.features.default_feature_registry import (
    create_default_feature_registry,
)

from intelligence.data.market_series_builder import (
    MarketSeriesBuilder,
)
from trading.context.trading_context import TradingContext
from intelligence.evidence.default_evidence_registry import (
    create_default_evidence_manager,
)
from intelligence.decision.default_decision_manager import (
    build_default_decision_manager,
)
from intelligence.execution_policy.default_execution_policy import (
    DefaultExecutionPolicy,
)

from intelligence.execution_policy.execution_policy_manager import (
    ExecutionPolicyManager,
)
from execution.position_manager.position_manager import (
    PositionManager,
)

from execution.order_builder.default_order_builder import (
    DefaultOrderBuilder,
)

from execution.risk_manager.default_risk_manager import (
    DefaultRiskManager,
)
from execution.trade_journal.trade_journal import (
    TradeJournal,
)
from execution.portfolio.portfolio_manager import (
    PortfolioManager,
)
from decision.recommendation.recommendation_engine import (
    RecommendationEngine,
)
from config.watchlist.watchlist_manager import WatchlistManager
from tools.market_universe.universe_builder import UniverseBuilder

from trading.runtime.runtime_manager import RuntimeManager
from datetime import datetime
from backend.services.market_session_service import (
    MarketSessionService,
)
from market_data.market_data_engine import (
    MarketDataEngine,
)
logger = get_logger("RUSI")


class ExecutionManager:

    def __init__(self, config):

        self._config = config
        self._watchlist = WatchlistManager()
        #
        # Evidence Runtime
        #
        self._evidence_manager = (
            create_default_evidence_manager()
        )
        self._market_session_service = (
            MarketSessionService()
        )
        #
        # Decision Runtime
        #
        self._decision_manager = (
            build_default_decision_manager()
        )
        #
        # Recommendation Engine
        #

        self._recommendation_engine = RecommendationEngine()
        #
        # Execution Policy
        #

        self._execution_policy = (
            ExecutionPolicyManager(
                DefaultExecutionPolicy()
            )
        )
        #
        # Core Components
        #
        self._broker_manager = BrokerManager(config)

        #
        # Builders
        #
        self._snapshot_builder = MarketSnapshotBuilder()

        #
        # Intelligence
        #
        self._intelligence_manager = IntelligenceManager()

        #
        # Feature Engine
        #
        registry = create_default_feature_registry()

        self._feature_engine = FeatureEngine(registry)
        #
        # Order Builder
        #

        self._order_builder = DefaultOrderBuilder()

        #
        # Risk Manager
        #

        self._risk_manager = DefaultRiskManager()

        #
        # Position Manager
        #

        self._position_manager = PositionManager()
        #
        # Portfolio Manager
        #

        self._portfolio_manager = PortfolioManager(
            self._position_manager.registry
        )
        #
        # Trade Journal
        #

        self._trade_journal = TradeJournal()

        #
        # Runtime Manager
        #
        self._runtime = RuntimeManager()

    def run(self):

        logger.info("Execution Started")
        logger.info("Application : %s", self._config.application_name)
        logger.info("Version     : %s", self._config.version)
        logger.info("Mode        : %s", self._config.execution_mode.value)
        logger.info("Datasource  : %s", self._config.datasource.value)
        logger.info("Market      : %s", self._config.market)

        logger.info("")

        #
        # Step 1
        #
        logger.info("Step 1 : Initialize Broker")

        self._broker_manager.initialize()

        #
        # Market Universe
        #
        logger.info("Building Market Universe")

        UniverseBuilder().build()

        logger.info("Market Universe Ready")

        logger.info("")

        logger.info("")

        #
        # Step 2
        #
        logger.info("Step 2 : Download Historical Data")

        # Get logical instrument
        instrument = self._watchlist.current()

        # Resolve broker token
        from tools.market_universe.instrument_resolver import (
            InstrumentResolver,
        )

        resolver = InstrumentResolver()

        instrument = resolver.resolve(instrument)

        logger.info(
            "Resolved Instrument : %s | %s | %s",
            instrument.symbol,
            instrument.exchange,
            instrument.token,
        )

        # Create datasource using resolved instrument
        self._broker_manager.create_datasource(instrument)

        datasource = self._broker_manager.datasource

        #
        # Market Data Engine
        #

        market_data_engine = MarketDataEngine(
            datasource
        )

        end_time = datetime.now(UTC)

        start_time = end_time - timedelta(days=30)

        candles = datasource.get_historical_data(
            exchange=instrument.exchange,
            token=instrument.token,
            interval="ONE_MINUTE",
            from_datetime=start_time,
            to_datetime=end_time,
        )

        if candles is None:

            logger.error("Historical download failed")

            return

        raw_data = candles.get("data")

        if not raw_data:
            logger.error(
                "Historical data download failed."
            )
            logger.error(
                "Broker Response : %s",
                candles,
            )
            return

        logger.info(
            "Historical Candles Downloaded : %d",
            len(raw_data),
        )

        #
        # Live Market Data
        #

        live_market_data = (
            market_data_engine.get_live_ltp()
        )

        logger.info("")

        logger.info(
            "Live Market Data"
        )

        logger.info(
            "Data Status : %s",
            live_market_data.data_status,
        )

        logger.info(
            "Live Price  : %.2f",
            live_market_data.last_price,
        )
        #
        # Live Market Quote
        #

        live_market_quote = (
            market_data_engine.get_quote()
        )

        logger.info("")
        logger.info(
            "Live Market Quote"
        )

        logger.info(
            "Quote Status : %s",
            live_market_quote.get("status"),
        )

        logger.info(
            "Quote Time   : %s",
            live_market_quote.get(
                "received_time"
            ),
        )

        logger.info(
            "Quote Data   : %s",
            live_market_quote.get(
                "data"
            ),
        )
        #
        # Step 3
        #
        logger.info("")
        logger.info("Step 3 : Build Candle Objects")

        candle_objects = CandleBuilder.build(raw_data)

        logger.info(
            "Internal Candle Objects : %d",
            len(candle_objects),
        )

        #
        # Step 4
        #
        logger.info("")
        logger.info("Step 4 : Build Market Snapshot")

        snapshot = self._snapshot_builder.build(
            candle_objects
        )

        logger.info("Market Snapshot Created")

        latest = snapshot.latest_candle

        logger.info(
            "Latest Close : %.2f",
            latest.close,
        )

        #
        # Step 5
        #
        logger.info("")
        logger.info("Step 5 : Technical Indicators")

        logger.info("------------------------------")

        if snapshot.indicators.sma20 is not None:

            logger.info(
                "SMA20 : %.2f",
                snapshot.indicators.sma20,
            )

        if snapshot.indicators.sma50 is not None:

            logger.info(
                "SMA50 : %.2f",
                snapshot.indicators.sma50,
            )

        if snapshot.indicators.ema20 is not None:

            logger.info(
                "EMA20 : %.2f",
                snapshot.indicators.ema20,
            )

        if snapshot.indicators.ema50 is not None:

            logger.info(
                "EMA50 : %.2f",
                snapshot.indicators.ema50,
            )

        #
        # Step 6
        #
        logger.info("")
        logger.info("Step 6 : Intelligence Analysis")

        intelligence = self._intelligence_manager.analyze(
            snapshot
        )
        #
        # Step 7
        #

        logger.info("")
        logger.info("Step 7 : Feature Extraction")

        series = MarketSeriesBuilder.build(
            candle_objects
        )

        feature_store = self._feature_engine.calculate(
            series
        )

        logger.info(
            "Registered Feature Calculators : %d",
            self._feature_engine.feature_count(),
        )

        logger.info(
            "Calculated Features            : %d",
            feature_store.count(),
        )

        #
        # Trading Context
        #

        context = TradingContext(
            market_snapshot=snapshot
        )
        context.instrument = instrument

        context.features = feature_store
        #
        # Step 8
        #
        logger.info("")
        logger.info("Step 8 : Evidence Runtime")

        evidence_context = (
            self._evidence_manager.generate(
                feature_store
            )
        )

        context.evidence = evidence_context

        logger.info(
            "Evidence Providers      : %d",
            self._evidence_manager.provider_count,
        )

        logger.info(
            "Evidence Generated      : %d",
            evidence_context.count,
        )

        logger.info(
            "Trading Context Created"
        )
        #
        # Step 9
        #
        logger.info("")
        logger.info("Step 9 : Decision Runtime")

        decision = self._decision_manager.evaluate(
            context.evidence
        )

        context.decision = decision
        #
        # Recommendation Engine
        #

        recommendation = (

            self._recommendation_engine.generate(

                context,

            )

        )

        self._recommendation_engine.print_report(

            recommendation,

        )

        context.recommendation = recommendation
        logger.info(
            "Decision Generated"
        )

        logger.info("")
        logger.info("--------------------------------")
        logger.info("Decision Summary")
        logger.info("--------------------------------")

        logger.info(
            "Signal      : %s",
            decision.signal.name,
        )

        logger.info(
            "Confidence  : %.2f",
            decision.confidence,
        )

        logger.info(
            "Score       : %.2f",
            decision.score,
        )

        logger.info("")
        logger.info("Reasons")
        logger.info("-------")

        for reason in decision.reasons:

            logger.info(
                "- %s",
                reason,
            )
        for result in intelligence.results:

            logger.info("")
            logger.info("--------------------------------")
            logger.info("%s", result.engine_name)
            logger.info("--------------------------------")

            logger.info(
                "Signal      : %s",
                result.signal,
            )

            logger.info(
                "Confidence  : %.2f",
                result.confidence,
            )

            if result.score is not None:

                logger.info(
                    "Score       : %.2f",
                    result.score,
                )

            if result.reasons:

                logger.info("")

                logger.info("Reasons")

                logger.info("-------")

                for reason in result.reasons:

                    logger.info(
                        "- %s",
                        reason,
                    )
        #
        # Step 10
        #

        logger.info("")
        logger.info("Step 10 : Execution Policy")

        policy = self._execution_policy.evaluate(
            context.decision
        )

        context.execution_policy = policy

        logger.info(
            "Trade Allowed : %s",
            policy.trade_allowed,
        )

        logger.info(
            "Reason        : %s",
            policy.reason,
        )

        logger.info("")
        logger.info("Step 11 : Market Session")

        exchange = context.instrument.exchange

        market_status = (
            self._market_session_service.get_market_status(
                exchange
            )
        )

        logger.info(
            "Exchange      : %s",
            exchange,
        )

        logger.info(
            "Market Status : %s",
            market_status,
        )

        logger.info("")
        logger.info("Step 12 : Order Builder")

        if (
            policy.trade_allowed
            and market_status == "OPEN"
        ):

            order = self._order_builder.build(
                context
            )

            context.order = order

            logger.info(
                "Symbol      : %s",
                order.symbol,
            )

            logger.info(
                "Exchange    : %s",
                order.exchange,
            )

            logger.info(
                "Transaction : %s",
                order.transaction_type,
            )

            logger.info(
                "Quantity    : %d",
                order.quantity,
            )

        else:

            if not policy.trade_allowed:

                logger.info(
                    "Order Builder Skipped : Execution Policy"
                )

            elif market_status != "OPEN":

                logger.info(
                    "Order Builder Skipped : Market Closed"
                )

        logger.info("")
        logger.info("Step 13 : Risk Manager")

        if hasattr(context, "order"):

            risk = self._risk_manager.evaluate(
                context.order
            )

            context.risk_result = risk

            logger.info(
                "Trade Allowed : %s",
                risk.trade_allowed,
            )

            logger.info(
                "Reason        : %s",
                risk.reason,
            )

            logger.info(
                "Approved Qty  : %d",
                risk.approved_quantity,
            )

            if risk.warnings:

                logger.info("Warnings")

                for warning in risk.warnings:

                    logger.info(
                        "- %s",
                        warning,
                    )

        else:

            logger.info(
                "Risk Manager Skipped : No Order"
            )


        # ---------------------------------------------------------
        # Broker Execution
        # ---------------------------------------------------------

        logger.info("")
        logger.info("Step 14 : Broker Execution")

        if (
            hasattr(context, "order")
            and hasattr(context, "risk_result")
            and context.risk_result.trade_allowed
        ):

            broker_result = (
                self._broker_manager.place_order(
                    context.order
                )
            )

            context.broker_result = broker_result

            position = (
                self._position_manager.open_position(
                    broker_result,
                    context.order,
                )
            )

            context.position = position

            self._trade_journal.record(
                context,
                position,
            )

            # -----------------------------------------------------
            # Portfolio Summary
            # -----------------------------------------------------

            portfolio = (
                self._portfolio_manager.build_portfolio()
            )

            summary = (
                self._portfolio_manager.summary()
            )

            logger.info("")
            logger.info("Step 15 : Portfolio Manager")

            logger.info(
                "Open Positions : %d",
                summary.open_positions,
            )

            logger.info(
                "Invested Amount : %.2f",
                summary.invested_amount,
            )

            logger.info(
                "Market Value : %.2f",
                summary.market_value,
            )

            logger.info(
                "Unrealized PnL : %.2f",
                summary.unrealized_pnl,
            )

            logger.info("")

            logger.info(
                "Broker Result"
            )

            logger.info(
                "Status      : %s",
                broker_result.success,
            )

            logger.info(
                "Order ID    : %s",
                broker_result.order_id,
            )

            logger.info(
                "Message     : %s",
                broker_result.message,
            )

        else:

            logger.info(
                "Broker Execution Skipped : "
                "No executable order"
            )
        logger.info("")
        logger.info("Feature Summary")
        logger.info("------------------------------")

        logger.info(
            "Registered Calculators : %d",
            self._feature_engine.feature_count(),
        )

        logger.info(
            "Calculated Features    : %d",
            feature_store.count(),
        )
        logger.info("")
        logger.info("Evidence Summary")
        logger.info("------------------------------")

        for evidence in context.evidence.evidences:

            logger.info(
                "%s : %s (%.2f)",
                evidence.feature_id,
                evidence.signal,
                evidence.confidence,
            )
        logger.info("")
        logger.info("========================================")
        logger.info("Execution Summary")
        logger.info("========================================")

        logger.info(
            "Successful Engines : %d",
            intelligence.successful_engines,
        )

        logger.info(
            "Failed Engines     : %d",
            intelligence.failed_engines,
        )

        logger.info(
            "Execution Time     : %.2f ms",
            intelligence.execution_time_ms,
        )
        logger.info("")
        logger.info("Execution Finished")

        #
        # Publish Runtime State
        #

        runtime_data = {
            "snapshot": snapshot,
            "intelligence": intelligence,
            "feature_store": feature_store,
            "evidence": context.evidence,
            "decision": context.decision,
            "recommendation": context.recommendation,
            "execution_policy": context.execution_policy,
            "instrument": instrument,
            "updated_time": datetime.now().isoformat(),
            "data_status": live_market_data.data_status,
            "live_price": live_market_data.last_price,
        }

        if "portfolio" in locals():
            runtime_data["portfolio"] = portfolio

        if "summary" in locals():
            runtime_data["portfolio_summary"] = summary

        if hasattr(context, "position"):
            runtime_data["position"] = context.position

        if hasattr(context, "order"):
            runtime_data["order"] = context.order

        if hasattr(context, "risk_result"):
            runtime_data["risk_result"] = context.risk_result

        if hasattr(context, "broker_result"):
            runtime_data["broker_result"] = context.broker_result

        self._runtime.update(**runtime_data)

        logger.info("Trading Runtime Updated")
