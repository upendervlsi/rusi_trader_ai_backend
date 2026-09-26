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

    max_open_positions: int = 1

    # --------------------------------------------------
    # Risk Management
    # --------------------------------------------------

    risk_per_trade: float = 0.02             # 2%

    max_daily_loss: float = 0.05             # 5%

    minimum_risk_reward: float = 2.0

    # --------------------------------------------------
    # Option Premium Risk Model
    # --------------------------------------------------

    # Stop-loss percentage applied to the option premium.
    option_stop_loss_percent: float = 25.0

    # Target percentage applied to the option premium.
    option_target_percent: float = 40.0
    nifty_real_max_adverse_slippage_percent: float = 2.0

    # --------------------------------------------------
    # Decision Engine
    # --------------------------------------------------

    minimum_confidence: float = 70.0

    # --------------------------------------------------
    # Position Exit Intelligence
    # --------------------------------------------------

    # Number of consecutive strong opposite decisions
    # required before a market-reversal exit.
    reversal_confirmation_cycles: int = 2

    # Minimum confidence required for a reversal signal.
    reversal_confirmation_confidence: float = 1.45

    # Profit level at which dynamic profit protection activates.
    profit_protection_activation_percent: float = 10.0

    # Percentage of the favorable move to protect.
    profit_protection_retrace_percent: float = 50.0

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
