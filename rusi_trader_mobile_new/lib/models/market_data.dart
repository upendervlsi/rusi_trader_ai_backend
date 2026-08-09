class MarketData {

  final String symbol;

  final double ltp;

  final double change;

  final double percent;

  final bool positive;

  const MarketData({

    required this.symbol,

    required this.ltp,

    required this.change,

    required this.percent,

    required this.positive,

  });

}
