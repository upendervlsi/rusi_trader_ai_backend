/*
============================================================

RUSI Trader AI

AI Decision Model

============================================================
*/

import 'execution_model.dart';
import 'trade_plan_model.dart';

class AIDecisionModel {
  final TradePlanModel tradePlan;

  final ExecutionModel execution;

  const AIDecisionModel({
    required this.tradePlan,
    required this.execution,
  });

  factory AIDecisionModel.fromJson(
    Map<String, dynamic> json,
  ) {
    return AIDecisionModel(
      tradePlan: TradePlanModel.fromJson(
        json["trade_plan"] ??
            <String, dynamic>{},
      ),
      execution: ExecutionModel.fromJson(
        json["execution"] ??
            <String, dynamic>{},
      ),
    );
  }
}
