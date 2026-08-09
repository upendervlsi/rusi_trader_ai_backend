"""
RUSI Trader AI

Option Resolver

Responsible only for finding contracts that satisfy
a given OptionStrategy.

It does NOT contain trading strategy.

Sprint-19

=============================================================
"""

from __future__ import annotations

from datetime import datetime

from common.logger import get_logger

from tools.market_universe.instrument_master_manager import (
    InstrumentMasterManager,
)

from tools.market_universe.option_contract import (
    OptionContract,
)

from tools.market_universe.option_strategy import (
    OptionStrategy,
    default_strategy,
    ExpiryStrategy,
)

from tools.market_universe.option_ranker import (
    OptionRanker,
)


logger = get_logger("RUSI")


class OptionResolver:

    def __init__(self):

        self._master = InstrumentMasterManager()

        self._ranker = OptionRanker()

    # ---------------------------------------------------------
    # Resolve Best Contract
    # ---------------------------------------------------------

    def resolve(

        self,

        underlying_symbol: str,

        recommendation: str,

        underlying_price: float,

        strategy: OptionStrategy | None = None,

        exchange: str | None = None,

    ) -> OptionContract | None:

        #
        # Maintain backward compatibility
        #

        if strategy is None:

            strategy = default_strategy(

                recommendation

            )

        #
        # Default exchange
        #
        # Existing callers historically used NFO.
        # Therefore, when no exchange is supplied,
        # preserve the existing NFO behavior.
        #

        if exchange is None:

            exchange = "NFO"

        exchange = exchange.upper().strip()

        #
        # Candidate Contracts
        #

        options = self._candidate_contracts(

            underlying_symbol,

            strategy,

            exchange,

        )

        if not options:

            logger.warning(

                "No option candidates found "
                "for %s on %s.",

                underlying_symbol,

                exchange,

            )

            return None

        #
        # Rank Contracts
        #

        ranked = self._ranker.rank(

            options,

            strategy,

            underlying_price,

        )

        if not ranked:

            return None

        #
        # Best Option
        #

        return self._build_contract(

            ranked[0],

            recommendation,

        )

    # ---------------------------------------------------------
    # Candidate Contracts
    # ---------------------------------------------------------

    def _candidate_contracts(

        self,

        symbol,

        strategy,

        exchange,

    ):

        #
        # Read options from the appropriate
        # exchange-specific instrument master.
        #
        # NFO -> NFO options
        # MCX -> MCX options
        #

        options = self._master.get_options(

            exchange=exchange,

            underlying=symbol,

        )

        if not options:

            return []

        #
        # CE / PE Filter
        #

        options = self._filter_option_type(

            options,

            strategy,

        )

        #
        # Expiry Filter
        #

        options = self._filter_expiry(

            options,

            strategy,

        )

        #
        # Strike Filter
        #

        options = self._filter_strike(

            options,

            strategy,

        )

        return options

    # ---------------------------------------------------------
    # Build Contract
    # ---------------------------------------------------------

    def _build_contract(

        self,

        option,

        recommendation,

    ) -> OptionContract:

        return OptionContract(

            underlying_symbol=option["symbol"],

            option_symbol=option["display_symbol"],

            exchange=option["exchange"],

            token=option["token"],

            strike=float(option["strike"]),

            expiry=option["expiry"],

            option_type=option["option_type"],

            lot_size=option["lotsize"],

            recommendation=recommendation,

        )

    # ---------------------------------------------------------
    # Filter CE / PE
    # ---------------------------------------------------------

    def _filter_option_type(

        self,

        options,

        strategy,

    ):

        if strategy.option_type.name == "AUTO":

            return options

        return [

            option

            for option in options

            if option.get("option_type")
            == strategy.option_type.value

        ]

    # ---------------------------------------------------------
    # Filter Expiry
    # ---------------------------------------------------------

    def _filter_expiry(

        self,

        options,

        strategy,

    ):

        if not options:

            return []

        #
        # Collect unique expiries
        #

        expiries = sorted(

            {

                option["expiry"]

                for option in options

                if option.get("expiry")

            },

            key=self._parse_expiry,

        )

        if not expiries:

            return []

        #
        # ALL Expiries
        #

        if strategy.expiry_strategy == ExpiryStrategy.ALL:

            return options

        #
        # Nearest Expiry
        #

        if strategy.expiry_strategy == ExpiryStrategy.NEAREST:

            expiry = expiries[0]

        #
        # Next Expiry
        #

        elif strategy.expiry_strategy == ExpiryStrategy.NEXT:

            expiry = (
                expiries[1]
                if len(expiries) > 1
                else expiries[0]
            )

        #
        # Monthly
        #

        elif strategy.expiry_strategy == ExpiryStrategy.MONTHLY:

            expiry = expiries[-1]

        else:

            expiry = expiries[0]

        return [

            option

            for option in options

            if option["expiry"] == expiry

        ]

    # ---------------------------------------------------------
    # Filter Strike
    # ---------------------------------------------------------

    def _filter_strike(

        self,

        options,

        strategy,

    ):

        #
        # Current resolver leaves all contracts for ranking.
        #
        # Future versions can reduce candidates
        # before ranking for better performance.
        #

        return options

    # ---------------------------------------------------------
    # Parse Expiry
    # ---------------------------------------------------------

    def _parse_expiry(

        self,

        expiry,

    ):

        if not expiry:

            return datetime.max

        expiry = str(expiry).strip()

        formats = [

            "%d%b%Y",

            "%d-%b-%Y",

            "%Y-%m-%d",

        ]

        for fmt in formats:

            try:

                return datetime.strptime(

                    expiry,

                    fmt,

                )

            except ValueError:

                pass

        return datetime.max

    # ---------------------------------------------------------
    # Normalize Strike
    # ---------------------------------------------------------

    def _normalize_strike(

        self,

        strike,

    ):

        strike = float(strike)

        #
        # Angel One sometimes stores strikes
        # multiplied by 100.
        #

        if strike > 100000:

            strike /= 100.0

        return strike
