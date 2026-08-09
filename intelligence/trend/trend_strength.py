class TrendStrength:

    @staticmethod
    def calculate(
            ema20,
            ema50,
            ema200):

        distance = abs(ema20 - ema200)

        score = min(distance / 20.0, 100)

        return round(score, 2)
