"""
Trading Engine Adapter

Reads the latest runtime state.
"""

from backend.adapters.trading_engine_facade import TradingEngineFacade


class TradingEngineAdapter:

    def __init__(self):
        self._facade = TradingEngineFacade()

    def get_dashboard(self):

        state = self._facade.get_runtime_state()

        snapshot = state.snapshot

        decision = state.decision

        summary = state.portfolio_summary

        latest_close = None

        if snapshot is not None:
            latest_close = snapshot.latest_candle.close

        return {
            "market_status": "OPEN",
            "updated_time": state.updated_time,
            "latest_close": latest_close,
            "decision": decision.signal.name if decision else None,
            "confidence": decision.confidence if decision else None,
            "portfolio": {
                "open_positions": (
                    summary.open_positions
                    if summary else 0
                ),
                "invested_amount": (
                    summary.invested_amount
                    if summary else 0.0
                ),
                "market_value": (
                    summary.market_value
                    if summary else 0.0
                ),
                "unrealized_pnl": (
                    summary.unrealized_pnl
                    if summary else 0.0
                ),
            },
        }
