class RecommendationModel {
  final String recommendation;

  final double confidence;

  final double score;

  final String optionSymbol;

  final double entryPrice;

  final double stopLoss;

  final double targetPrice;

  RecommendationModel({
    required this.recommendation,
    required this.confidence,
    required this.score,
    required this.optionSymbol,
    required this.entryPrice,
    required this.stopLoss,
    required this.targetPrice,
  });

  factory RecommendationModel.fromJson(
      Map<String, dynamic> json) {
    return RecommendationModel(
      recommendation:
          json["recommendation"]?.toString() ?? "--",

      confidence:
          (json["confidence"] as num?)?.toDouble() ?? 0.0,

      score:
          (json["score"] as num?)?.toDouble() ?? 0.0,

      optionSymbol:
          json["option_symbol"]?.toString() ?? "--",

      entryPrice:
          (json["entry_price"] as num?)?.toDouble() ?? 0.0,

      stopLoss:
          (json["stop_loss"] as num?)?.toDouble() ?? 0.0,

      targetPrice:
          (json["target_price"] as num?)?.toDouble() ?? 0.0,
    );
  }
}
