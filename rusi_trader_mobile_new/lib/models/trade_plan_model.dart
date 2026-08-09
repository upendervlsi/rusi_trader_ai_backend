/*
============================================================

RUSI Trader AI

Trade Plan Model

============================================================
*/

class TradePlanModel {
  final String recommendation;

  final double confidence;

  final double tradeQuality;

  final double entryPrice;

  final double stopLoss;

  final double target1;

  final double target2;

  final String riskReward;

  final String positionSize;

  final String holdingType;

  final String risk;

  final List<String> reasons;

  const TradePlanModel({
    required this.recommendation,
    required this.confidence,
    required this.tradeQuality,
    required this.entryPrice,
    required this.stopLoss,
    required this.target1,
    required this.target2,
    required this.riskReward,
    required this.positionSize,
    required this.holdingType,
    required this.risk,
    required this.reasons,
  });

  factory TradePlanModel.fromJson(
    Map<String, dynamic> json,
  ) {
    return TradePlanModel(
      recommendation:
          json["recommendation"] ?? "",

      confidence:
          (json["confidence"] ?? 0).toDouble(),

      tradeQuality:
          (json["trade_quality"] ?? 0).toDouble(),

      entryPrice:
          (json["entry_price"] ?? 0).toDouble(),

      stopLoss:
          (json["stop_loss"] ?? 0).toDouble(),

      target1:
          (json["target1"] ?? 0).toDouble(),

      target2:
          (json["target2"] ?? 0).toDouble(),

      riskReward:
          json["risk_reward"] ?? "",

      positionSize:
          json["position_size"] ?? "",

      holdingType:
          json["holding_type"] ?? "",

      risk:
          json["risk"] ?? "",

      reasons:
          List<String>.from(
        json["reasons"] ?? [],
      ),
    );
  }
}
