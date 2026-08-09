/*
============================================================

RUSI Trader AI

Execution Model

============================================================
*/

class ExecutionModel {
  final bool approved;

  final String reason;

  final bool confidenceOk;

  final bool marketOpen;

  final bool riskOk;

  final bool marginOk;

  final bool cooldownOk;

  final bool dailyLimitOk;

  final bool positionOk;

  const ExecutionModel({
    required this.approved,
    required this.reason,
    required this.confidenceOk,
    required this.marketOpen,
    required this.riskOk,
    required this.marginOk,
    required this.cooldownOk,
    required this.dailyLimitOk,
    required this.positionOk,
  });

  factory ExecutionModel.fromJson(
    Map<String, dynamic> json,
  ) {
    return ExecutionModel(
      approved:
          json["approved"] ?? false,

      reason:
          json["reason"] ?? "",

      confidenceOk:
          json["confidence_ok"] ?? false,

      marketOpen:
          json["market_open"] ?? false,

      riskOk:
          json["risk_ok"] ?? false,

      marginOk:
          json["margin_ok"] ?? false,

      cooldownOk:
          json["cooldown_ok"] ?? false,

      dailyLimitOk:
          json["daily_limit_ok"] ?? false,

      positionOk:
          json["position_ok"] ?? false,
    );
  }
}
