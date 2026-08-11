"""
RUSI Trader AI

Suggestion Service
"""

from backend.adapters.trading_engine_facade import (
    TradingEngineFacade,
)

from backend.models.suggestion_model import (
    SuggestionModel,
)


class SuggestionService:

    def __init__(self):

        self._facade = TradingEngineFacade()

    def get_suggestions(self) -> list[SuggestionModel]:

        state = self._facade.get_runtime_state()

        suggestions = state.suggestions or []

        result = []

        for suggestion in suggestions:

            result.append(
                SuggestionModel(

                    suggestion_id=suggestion.suggestion_id,

                    category=suggestion.category,

                    symbol=suggestion.symbol,

                    exchange=suggestion.exchange,

                    latest_price=suggestion.latest_price,

                    signal=suggestion.signal,

                    entry_price=suggestion.entry_price,

                    stop_loss=suggestion.stop_loss,

                    target_price=suggestion.target_price,

                    risk_reward=suggestion.risk_reward,

                    confidence=suggestion.confidence,

                    score=suggestion.score,

                    status=suggestion.status,

                    created_time=suggestion.created_time,

                    updated_time=suggestion.updated_time,

                    reasons=suggestion.reasons,

                    underlying_symbol=(
                        suggestion.underlying_symbol
                    ),

                    option_symbol=(
                        suggestion.option_symbol
                    ),
                    option_token=(
                        suggestion.option_token
                    ),
                    option_type=(
                        suggestion.option_type
                    ),

                    strike=suggestion.strike,

                    expiry=suggestion.expiry,

                    entry_reached=(
                        suggestion.entry_reached
                    ),

                    profit_booked=(
                        suggestion.profit_booked
                    ),

                    exit_reason=(
                        suggestion.exit_reason
                    ),
                )
            )

        return result
