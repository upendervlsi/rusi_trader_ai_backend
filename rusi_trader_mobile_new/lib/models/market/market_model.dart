import 'package:flutter/foundation.dart';

@immutable
class MarketModel {
  final String marketStatus;
  final String dataStatus;
  final String updatedTime;

  final double? livePrice;
  final double? latestClose;

  final double? sma20;
  final double? sma50;

  final double? ema20;
  final double? ema50;

  final String? marketStructure;

  const MarketModel({
    required this.marketStatus,
    required this.dataStatus,
    required this.updatedTime,
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
      marketStatus:
          json["market_status"]?.toString() ?? "UNKNOWN",

      dataStatus:
          json["data_status"]?.toString() ?? "UNKNOWN",

      updatedTime:
          json["updated_time"]?.toString() ?? "",

      livePrice:
          (json["live_price"] as num?)?.toDouble(),

      latestClose:
          (json["latest_close"] as num?)?.toDouble(),

      sma20:
          (json["sma20"] as num?)?.toDouble(),

      sma50:
          (json["sma50"] as num?)?.toDouble(),

      ema20:
          (json["ema20"] as num?)?.toDouble(),

      ema50:
          (json["ema50"] as num?)?.toDouble(),

      marketStructure:
          json["market_structure"]?.toString(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      "market_status": marketStatus,
      "data_status": dataStatus,
      "updated_time": updatedTime,
      "live_price": livePrice,
      "latest_close": latestClose,
      "sma20": sma20,
      "sma50": sma50,
      "ema20": ema20,
      "ema50": ema50,
      "market_structure": marketStructure,
    };
  }
}
