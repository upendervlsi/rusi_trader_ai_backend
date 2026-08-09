"""
============================================================

RUSI Trader AI

Decision Engine

============================================================
"""

from .trade_plan import TradePlan


class DecisionEngine:

    def generate(
        self,
        snapshot,
        recommendation,
        confidence,
        reasons,
    ) -> TradePlan:

        price = snapshot.latest_close

        action = recommendation

        #
        # Entry
        #

        entry = price

        #
        # ATR Based Stop
        #

        atr = max(snapshot.atr, 1)

        stop_loss = round(
            entry - (1.5 * atr),
            2,
        )

        target1 = round(
            entry + (2.0 * atr),
            2,
        )

        target2 = round(
            entry + (3.5 * atr),
            2,
        )

        #
        # Risk Reward
        #

        risk = entry - stop_loss

        reward = target1 - entry

        if risk > 0:

            rr = f"1:{reward/risk:.2f}"

        else:

            rr = "N/A"

        #
        # Trade Quality
        #

        trade_quality = min(
            confidence,
            100,
        )

        #
        # Position Size
        #

        if confidence >= 85:

            size = "FULL"

        elif confidence >= 70:

            size = "HALF"

        else:

            size = "SMALL"

        return TradePlan(

            recommendation=action,

            confidence=round(confidence, 2),

            trade_quality=round(trade_quality, 2),

            entry_price=entry,

            stop_loss=stop_loss,

            target1=target1,

            target2=target2,

            risk_reward=rr,

            position_size=size,

            holding_type="INTRADAY",

            risk="MEDIUM",

            reasons=reasons,

        )
