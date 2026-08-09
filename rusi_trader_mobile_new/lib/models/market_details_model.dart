class MarketDetailsModel {
  final double livePrice;
  final double latestClose;

  final String dataStatus;
  final String marketStatus;

  final String marketStructure;

  final double ema20;
  final double ema50;

  final double sma20;
  final double sma50;

  final double vwap;

  final double rsi;
  final double macd;
  final double adx;
  final double atr;

  final double pcr;

  final double openInterest;

  final double changeOi;

  final double iv;

  final double maxPain;

  final String updatedTime;

  const MarketDetailsModel({
    required this.livePrice,
    required this.latestClose,
    required this.dataStatus,
    required this.marketStatus,
    required this.marketStructure,
    required this.ema20,
    required this.ema50,
    required this.sma20,
    required this.sma50,
    required this.vwap,
    required this.rsi,
    required this.macd,
    required this.adx,
    required this.atr,
    required this.pcr,
    required this.openInterest,
    required this.changeOi,
    required this.iv,
    required this.maxPain,
    required this.updatedTime,
  });

  factory MarketDetailsModel.fromJson(
    Map<String, dynamic> json,
  ) {
    return MarketDetailsModel(
      livePrice:
          (json["live_price"] as num?)
                  ?.toDouble() ??
              0.0,

      latestClose:
          (json["latest_close"] as num?)
                  ?.toDouble() ??
              0.0,

      dataStatus:
          json["data_status"] ??
              "UNKNOWN",

      marketStatus:
          json["market_status"] ??
              "UNKNOWN",

      marketStructure:
          json["market_structure"] ??
              "UNKNOWN",

      ema20:
          (json["ema20"] as num?)
                  ?.toDouble() ??
              0.0,

      ema50:
          (json["ema50"] as num?)
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

      vwap:
          (json["vwap"] as num?)
                  ?.toDouble() ??
              0.0,

      rsi:
          (json["rsi"] as num?)
                  ?.toDouble() ??
              0.0,

      macd:
          (json["macd"] as num?)
                  ?.toDouble() ??
              0.0,

      adx:
          (json["adx"] as num?)
                  ?.toDouble() ??
              0.0,

      atr:
          (json["atr"] as num?)
                  ?.toDouble() ??
              0.0,

      pcr:
          (json["pcr"] as num?)
                  ?.toDouble() ??
              0.0,

      openInterest:
          (json["oi"] as num?)
                  ?.toDouble() ??
              0.0,

      changeOi:
          (json["change_oi"] as num?)
                  ?.toDouble() ??
              0.0,

      iv:
          (json["iv"] as num?)
                  ?.toDouble() ??
              0.0,

      maxPain:
          (json["max_pain"] as num?)
                  ?.toDouble() ??
              0.0,

      updatedTime:
          json["updated_time"] ??
              "",
    );
  }
}
