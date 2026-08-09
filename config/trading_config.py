"""
============================================================
RUSI Trader AI

Trading Configuration

Central location for all configurable trading limits.
============================================================
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class TradingConfig:
    """
    Global trading configuration.

    All trading engines should obtain runtime limits
    from this configuration rather than hard-coded values.
    """

    # --------------------------------------------------
    # Capital Management
    # --------------------------------------------------

    initial_capital: float = 100000.0

    max_capital_per_trade: float = 0.10      # 10%

    max_open_positions: int = 5

    # --------------------------------------------------
    # Risk Management
    # --------------------------------------------------

    risk_per_trade: float = 0.02             # 2%

    max_daily_loss: float = 0.05             # 5%

    minimum_risk_reward: float = 2.0

    # --------------------------------------------------
    # Decision Engine
    # --------------------------------------------------

    minimum_confidence: float = 70.0

    # --------------------------------------------------
    # Stop Loss
    # --------------------------------------------------

    default_stop_loss_percent: float = 2.0

    trailing_stop_enabled: bool = True

    # --------------------------------------------------
    # Position Sizing
    # --------------------------------------------------

    use_atr_position_sizing: bool = True

    atr_multiplier: float = 2.0

    # --------------------------------------------------
    # Execution
    # --------------------------------------------------

    allow_short_selling: bool = False

    paper_trading: bool = True

    # --------------------------------------------------

    def __str__(self):

        return (
            "TradingConfig("
            f"risk_per_trade={self.risk_per_trade}, "
            f"minimum_confidence={self.minimum_confidence})"
        )

    __repr__ = __str__
