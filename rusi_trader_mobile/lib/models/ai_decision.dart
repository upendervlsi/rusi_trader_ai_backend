class AIDecision {

  final String signal;

  final double confidence;

  final bool ema;

  final bool macd;

  final bool vwap;

  final bool oi;

  final bool volume;

  final bool news;

  const AIDecision({

    required this.signal,

    required this.confidence,

    required this.ema,

    required this.macd,

    required this.vwap,

    required this.oi,

    required this.volume,

    required this.news,

  });

}
