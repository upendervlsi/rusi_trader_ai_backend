class TrendExplainer:

    @staticmethod
    def explain(trend):

        if trend.value == "Bullish":

            return [

                "EMA20 is above EMA50",

                "EMA50 is above EMA200",

                "Trend is healthy"

            ]

        elif trend.value == "Bearish":

            return [

                "EMA20 below EMA50",

                "EMA50 below EMA200",

                "Downtrend confirmed"

            ]

        return [

            "Mixed EMA alignment",

            "No strong trend"
        ]
