"""
=============================================================

RUSI Trader AI

Option Strategy

Defines how the AI wants to select an option contract.

RUSI V1 OPTION BUYING POLICY

    Underlying BUY  -> BUY CE
    Underlying SELL -> BUY PE
    Underlying HOLD -> NO OPTION

Important:
    SELL does NOT mean selling an option.
    SELL represents bearish underlying direction.
    The selected PE is still purchased.

This module contains NO broker logic.

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

    ATM = "ATM"

    ITM = "ITM"

    OTM = "OTM"

    EXACT = "EXACT"

    AI_SELECTED = "AI_SELECTED"


# ============================================================
# Expiry Strategy
# ============================================================


class ExpiryStrategy(str, Enum):

    NEAREST = "NEAREST"

    NEXT = "NEXT"

    MONTHLY = "MONTHLY"

    ALL = "ALL"


# ============================================================
# Option Strategy
# ============================================================


@dataclass(slots=True)
class OptionStrategy:
    """
    Defines how an option contract should be selected.

    This object contains selection strategy only.

    It does NOT represent the transaction side.

    RUSI V1 transaction policy:

        CE -> BUY
        PE -> BUY

    The underlying recommendation determines whether
    CE or PE is selected.
    """

    # --------------------------------------------------------
    # CE / PE
    # --------------------------------------------------------

    option_type: OptionType = OptionType.AUTO

    # --------------------------------------------------------
    # ATM / ITM / OTM
    # --------------------------------------------------------

    strike_strategy: StrikeStrategy = StrikeStrategy.ATM

    # --------------------------------------------------------
    # Strike distance
    #
    # Examples:
    #
    # ITM1
    # ITM2
    # OTM1
    # OTM2
    # --------------------------------------------------------

    strike_distance: int = 0

    # --------------------------------------------------------
    # Expiry
    # --------------------------------------------------------

    expiry_strategy: ExpiryStrategy = (
        ExpiryStrategy.NEAREST
    )

    # --------------------------------------------------------
    # Exact strike
    # --------------------------------------------------------

    exact_strike: float | None = None

    # --------------------------------------------------------
    # Future AI ranking inputs
    # --------------------------------------------------------

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
    Convert the underlying AI recommendation into the
    option contract selection strategy.

    RUSI V1 OPTION BUYING:

        BUY  -> CE -> BUY CE

        SELL -> PE -> BUY PE

        HOLD -> AUTO

    IMPORTANT:

        "SELL" here describes the underlying market
        direction only.

        It does NOT instruct the system to sell an option.

    HOLD is represented by AUTO for backward compatibility,
    but the execution/recommendation layer must prevent an
    option trade when the final recommendation is HOLD.

    Default strike:
        ATM

    Default expiry:
        NEAREST
    """

    recommendation = str(
        recommendation
    ).upper().strip()

    # --------------------------------------------------------
    # Bullish underlying
    #
    # NIFTY BUY -> CE
    # Transaction -> BUY CE
    # --------------------------------------------------------

    if recommendation == "BUY":

        option_type = OptionType.CE

    # --------------------------------------------------------
    # Bearish underlying
    #
    # NIFTY SELL -> PE
    # Transaction -> BUY PE
    # --------------------------------------------------------

    elif recommendation == "SELL":

        option_type = OptionType.PE

    # --------------------------------------------------------
    # HOLD
    #
    # No directional option should be selected.
    #
    # AUTO is retained only for backward compatibility.
    # The caller must not create an executable option trade.
    # --------------------------------------------------------

    else:

        option_type = OptionType.AUTO

    return OptionStrategy(

        option_type=option_type,

        strike_strategy=StrikeStrategy.ATM,

        expiry_strategy=ExpiryStrategy.NEAREST,

    )
