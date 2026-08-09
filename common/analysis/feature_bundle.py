from dataclasses import dataclass


@dataclass(slots=True)
class FeatureBundle:

    # Trend
    trend_direction: int = 0          # -1 / 0 / +1
    trend_strength: float = 0.0

    # Momentum
    momentum_strength: float = 0.0

    # Moving averages
    ema_alignment: bool = False
    sma_alignment: bool = False

    # RSI
    rsi_zone: int = 0                 # Oversold/Neutral/Overbought

    # MACD
    macd_signal: int = 0

    # Volatility
    volatility_score: float = 0.0

    # Volume
    volume_strength: float = 0.0

    # Composite
    bullish_score: float = 0.0
    bearish_score: float = 0.0

    confidence_score: float = 0.0
