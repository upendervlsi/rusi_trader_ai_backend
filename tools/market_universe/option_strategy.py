"""
=============================================================

RUSI Trader AI

Option Strategy

Defines how the AI wants to select an option contract.

This module contains NO broker logic.

Sprint-19

=============================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


# ============================================================
# Option Type
# ============================================================


class OptionType(str, Enum):

    AUTO = "AUTO"

    CE = "CE"

    PE = "PE"


# ============================================================
# Strike Strategy
# ============================================================


class StrikeStrategy(str, Enum):

    #
    # At The Money
    #

    ATM = "ATM"

    #
    # In The Money
    #

    ITM = "ITM"

    #
    # Out Of The Money
    #

    OTM = "OTM"

    #
    # Exact Strike
    #

    EXACT = "EXACT"

    #
    # Future AI Ranking
    #

    AI_SELECTED = "AI_SELECTED"


# ============================================================
# Expiry Strategy
# ============================================================


class ExpiryStrategy(str, Enum):

    #
    # Nearest Expiry
    #

    NEAREST = "NEAREST"

    #
    # Second Expiry
    #

    NEXT = "NEXT"

    #
    # Monthly Expiry
    #

    MONTHLY = "MONTHLY"

    #
    # All Expiries
    #

    ALL = "ALL"


# ============================================================
# Option Strategy
# ============================================================


@dataclass(slots=True)
class OptionStrategy:
    """
    Defines how an option should be selected.

    This object contains strategy only.

    OptionResolver simply follows these rules.
    """

    #
    # CE / PE
    #

    option_type: OptionType = OptionType.AUTO

    #
    # ATM / ITM / OTM
    #

    strike_strategy: StrikeStrategy = StrikeStrategy.ATM

    #
    # Used for

    # ITM1
    # ITM2
    # OTM1
    # OTM2

    #

    strike_distance: int = 0

    #
    # Expiry
    #

    expiry_strategy: ExpiryStrategy = ExpiryStrategy.NEAREST

    #
    # Exact Strike

    #

    exact_strike: float | None = None

    #
    # Future

    #

    use_ai_ranking: bool = False

    use_oi: bool = False

    use_iv: bool = False

    use_liquidity: bool = False

    use_volume: bool = False

    use_spread: bool = False

    use_delta: bool = False

    use_gamma: bool = False

    use_theta: bool = False

    use_vega: bool = False


# ============================================================
# Default Strategy
# ============================================================


def default_strategy(
    recommendation: str,
) -> OptionStrategy:
    """
    Current V1 compatibility.

    BUY  -> CE

    SELL -> PE

    HOLD -> AUTO

    ATM

    Nearest Expiry
    """

    recommendation = recommendation.upper()

    if recommendation == "BUY":

        option_type = OptionType.CE

    elif recommendation == "SELL":

        option_type = OptionType.PE

    else:

        option_type = OptionType.AUTO

    return OptionStrategy(

        option_type=option_type,

        strike_strategy=StrikeStrategy.ATM,

        expiry_strategy=ExpiryStrategy.NEAREST,

    )
