"""
============================================================

Recommendation Service

============================================================
"""

from backend.adapters.trading_engine_facade import (
    TradingEngineFacade,
)

from backend.models.recommendation_model import (
    RecommendationModel,
)


class RecommendationService:

    def __init__(self):

        self._facade = TradingEngineFacade()

    def get_recommendation(self):

        state = self._facade.get_runtime_state()

        recommendation = state.recommendation

        if recommendation is None:

            return RecommendationModel(

                recommendation=None,

                confidence=None,

                score=None,

                option_symbol=None,

                exchange=None,

                strike=None,

                expiry=None,

                option_type=None,

                entry_price=None,

                stop_loss=None,

                target_price=None,

                risk_reward=None,

                reasons=[],

                updated_time=state.updated_time,

            )

        return RecommendationModel(

            recommendation=recommendation.recommendation,

            confidence=recommendation.confidence,

            score=recommendation.score,

            option_symbol=recommendation.option_symbol,

            exchange=recommendation.exchange,

            strike=recommendation.strike,

            expiry=recommendation.expiry,

            option_type=recommendation.option_type,

            entry_price=recommendation.entry_price,

            stop_loss=recommendation.stop_loss,

            target_price=recommendation.target_price,

            risk_reward=recommendation.risk_reward,

            reasons=recommendation.reasons,

            updated_time=state.updated_time,

        )
