"""
=============================================================

RUSI Trader AI

Option Ranking Engine

Ranks all candidate option contracts.

Sprint-19

Future Features
---------------
✓ OI Ranking
✓ Volume Ranking
✓ Liquidity Ranking
✓ IV Ranking
✓ Greeks Ranking
✓ Spread Ranking
✓ AI Confidence Ranking
✓ News Impact Ranking

=============================================================
"""

from __future__ import annotations

from dataclasses import (
    dataclass,
    field,
)

from .option_strategy import (
    OptionStrategy,
)


# =============================================================
# Default Engineering Weights
# =============================================================

DEFAULT_WEIGHTS = {

    "strike": 15.0,

    "oi": 20.0,

    "volume": 15.0,

    "liquidity": 10.0,

    "iv": 10.0,

    "spread": 10.0,

    "delta": 10.0,

    "gamma": 5.0,

    "theta": 5.0,

    "vega": 5.0,

    "news": 20.0,

    "trend": 20.0,

    "ai": 25.0,

}


# =============================================================
# Engineering Breakdown
# =============================================================

@dataclass(slots=True)
class RankingBreakdown:

    strike_score: float = 0.0

    oi_score: float = 0.0

    volume_score: float = 0.0

    liquidity_score: float = 0.0

    iv_score: float = 0.0

    spread_score: float = 0.0

    delta_score: float = 0.0

    gamma_score: float = 0.0

    theta_score: float = 0.0

    vega_score: float = 0.0

    news_score: float = 0.0

    trend_score: float = 0.0

    ai_score: float = 0.0

    total_score: float = 0.0

    details: dict = field(default_factory=dict)


# =============================================================
# Score Result
# =============================================================

@dataclass(slots=True)
class OptionScore:

    option: dict

    score: float

    breakdown: RankingBreakdown


# =============================================================
# Option Ranker
# =============================================================

class OptionRanker:

    """
    Engineering based option ranking engine.

    Every candidate contract receives a weighted score.
    """

    def __init__(self):

        self._weights = DEFAULT_WEIGHTS

    # ---------------------------------------------------------

    def rank(

        self,

        options: list[dict],

        strategy: OptionStrategy,

        underlying_price: float,

    ) -> list[dict]:

        scored = []

        for option in options:

            scored.append(

                self._score(

                    option,

                    strategy,

                    underlying_price,

                )

            )

        scored.sort(

            key=lambda item: item.score,

            reverse=True,

        )

        return [

            item.option

            for item in scored

        ]

    # ---------------------------------------------------------

    def _score(

        self,

        option,

        strategy,

        underlying_price,

    ) -> OptionScore:

        breakdown = RankingBreakdown()

        #
        # Strike
        #

        breakdown.strike_score = self._strike_score(

            option,

            strategy,

            underlying_price,

        )

        #
        # Market Quality
        #

        breakdown.oi_score = self._oi_score(option)

        breakdown.volume_score = self._volume_score(option)

        breakdown.liquidity_score = self._liquidity_score(option)

        breakdown.iv_score = self._iv_score(option)

        breakdown.spread_score = self._spread_score(option)

        #
        # Greeks
        #

        breakdown.delta_score = self._delta_score(option)

        breakdown.gamma_score = self._gamma_score(option)

        breakdown.theta_score = self._theta_score(option)

        breakdown.vega_score = self._vega_score(option)

        #
        # Intelligence
        #

        breakdown.news_score = self._news_score(option)

        breakdown.trend_score = self._trend_score(option)

        breakdown.ai_score = self._ai_score(option)

        #
        # Final Engineering Score
        #

        breakdown.total_score = (

              breakdown.strike_score
            + breakdown.oi_score
            + breakdown.volume_score
            + breakdown.liquidity_score
            + breakdown.iv_score
            + breakdown.spread_score
            + breakdown.delta_score
            + breakdown.gamma_score
            + breakdown.theta_score
            + breakdown.vega_score
            + breakdown.news_score
            + breakdown.trend_score
            + breakdown.ai_score

        )

        return OptionScore(

            option=option,

            score=breakdown.total_score,

            breakdown=breakdown,

        )
    # ---------------------------------------------------------
    # Strike Score
    # ---------------------------------------------------------

    def _strike_score(

        self,

        option,

        strategy,

        underlying_price,

    ) -> float:

        strike = self._strike(option)

        distance = abs(

            strike - underlying_price

        )

        #
        # ATM Strategy
        #

        if strategy.strike_strategy.name == "ATM":

            value = max(

                0.0,

                100.0 - distance,

            )

            return (

                value / 100.0

            ) * self._weights["strike"]

        #
        # Future:
        # ITM / OTM / EXACT
        #

        return 0.0

    # ---------------------------------------------------------
    # Open Interest Score
    # ---------------------------------------------------------

    def _oi_score(

        self,

        option,

    ) -> float:

        #
        # Future:
        # option["oi"]
        #

        return 0.0

    # ---------------------------------------------------------
    # Volume Score
    # ---------------------------------------------------------

    def _volume_score(

        self,

        option,

    ) -> float:

        #
        # Future:
        # option["volume"]
        #

        return 0.0

    # ---------------------------------------------------------
    # Liquidity Score
    # ---------------------------------------------------------

    def _liquidity_score(

        self,

        option,

    ) -> float:

        #
        # Future:
        # bid/ask depth
        #

        return 0.0

    # ---------------------------------------------------------
    # Implied Volatility Score
    # ---------------------------------------------------------

    def _iv_score(

        self,

        option,

    ) -> float:

        #
        # Future:
        # option["iv"]
        #

        return 0.0

    # ---------------------------------------------------------
    # Bid / Ask Spread Score
    # ---------------------------------------------------------

    def _spread_score(

        self,

        option,

    ) -> float:

        #
        # Future:
        #
        # ask - bid
        #

        return 0.0

    # ---------------------------------------------------------
    # Delta Score
    # ---------------------------------------------------------

    def _delta_score(

        self,

        option,

    ) -> float:

        #
        # Future Greeks
        #

        return 0.0

    # ---------------------------------------------------------
    # Gamma Score
    # ---------------------------------------------------------

    def _gamma_score(

        self,

        option,

    ) -> float:

        return 0.0

    # ---------------------------------------------------------
    # Theta Score
    # ---------------------------------------------------------

    def _theta_score(

        self,

        option,

    ) -> float:

        return 0.0

    # ---------------------------------------------------------
    # Vega Score
    # ---------------------------------------------------------

    def _vega_score(

        self,

        option,

    ) -> float:

        return 0.0
    # ---------------------------------------------------------
    # News Score
    # ---------------------------------------------------------

    def _news_score(

        self,

        option,

    ) -> float:

        """
        Future:
            News Engine
            Sentiment Engine
            Sector Impact
            Global Market Impact

        Expected Range:
            0.0 -> weight
        """

        return 0.0

    # ---------------------------------------------------------
    # Trend Score
    # ---------------------------------------------------------

    def _trend_score(

        self,

        option,

    ) -> float:

        """
        Future:
            EMA Trend
            SuperTrend
            VWAP
            Market Structure
            Multi Timeframe Alignment
        """

        return 0.0

    # ---------------------------------------------------------
    # AI Score
    # ---------------------------------------------------------

    def _ai_score(

        self,

        option,

    ) -> float:

        """
        Future:

        AI Model Confidence

        Features may include

            OI
            IV
            Greeks
            Price Action
            Volume
            News
            Trend
            Volatility
        """

        return 0.0

    # ---------------------------------------------------------
    # Strike
    # ---------------------------------------------------------

    def _strike(

        self,

        option,

    ) -> float:

        try:

            strike = float(

                option["strike"]

            )

            #
            # Angel One stores strikes
            # multiplied by 100
            #

            if strike > 100000:

                strike /= 100.0

            return strike

        except Exception:

            return 0.0

    # ---------------------------------------------------------
    # Print Ranking
    # ---------------------------------------------------------

    def print_ranking(

        self,

        options,

        count=10,

    ):

        print()

        print("=" * 120)

        print("OPTION RANKING")

        print("=" * 120)

        print(

            f'{"Rank":<6}'
            f'{"Strike":<12}'
            f'{"Type":<8}'
            f'{"Expiry":<15}'
            f'{"Symbol":<40}'

        )

        print("-" * 120)

        for index, option in enumerate(

            options[:count],

            start=1,

        ):

            print(

                f"{index:<6}"

                f"{self._strike(option):<12.2f}"

                f"{option.get('option_type',''):<8}"

                f"{option.get('expiry',''):<15}"

                f"{option.get('display_symbol','')}"

            )

        print("=" * 120)
