class MarketModel {

  final double livePrice;
  final double latestClose;

  final double sma20;
  final double sma50;

  final double ema20;
  final double ema50;

  final String marketStructure;

  MarketModel({
    required this.livePrice,
    required this.latestClose,
    required this.sma20,
    required this.sma50,
    required this.ema20,
    required this.ema50,
    required this.marketStructure,
  });

  factory MarketModel.fromJson(
    Map<String, dynamic> json,
  ) {
    return MarketModel(

      livePrice:
          (json["live_price"] as num?)
                  ?.toDouble() ??
              0.0,

      latestClose:
          (json["latest_close"] as num?)
                  ?.toDouble() ??
              0.0,

      sma20:
          (json["sma20"] as num?)
                  ?.toDouble() ??
              0.0,

      sma50:
          (json["sma50"] as num?)
                  ?.toDouble() ??
              0.0,

      ema20:
          (json["ema20"] as num?)
                  ?.toDouble() ??
              0.0,

      ema50:
          (json["ema50"] as num?)
                  ?.toDouble() ??
              0.0,

      marketStructure:
          json["market_structure"] ??
              "--",
    );
  }
}
