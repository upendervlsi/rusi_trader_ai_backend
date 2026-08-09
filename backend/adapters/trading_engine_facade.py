"""
============================================================

Trading Engine Facade

Single entry point for the REST API.

The facade never talks directly to the broker or
execution pipeline. It only reads the latest runtime
state.

============================================================
"""

from trading.runtime.runtime_manager import RuntimeManager


class TradingEngineFacade:

    def __init__(self):

        self._runtime = RuntimeManager()

    @property
    def state(self):
        return self._runtime.get_state()

    def get_market_snapshot(self):

        return self.state.snapshot

    def get_intelligence(self):

        return self.state.intelligence

    def get_decision(self):

        return self.state.decision

    def get_recommendation(self):

        return self.state.recommendation

    def get_portfolio(self):

        return self.state.portfolio

    def get_portfolio_summary(self):

        return self.state.portfolio_summary

    def get_position(self):

        return self.state.position

    def get_runtime_state(self):

        return self.state
