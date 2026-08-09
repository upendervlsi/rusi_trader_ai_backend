/*
============================================================

RUSI Trader AI

AI Repository

============================================================
*/

import '../core/api/api_client.dart';

import '../models/ai_decision_model.dart';

class AIRepository {
  final ApiClient _api = ApiClient();

  //--------------------------------------------------
  // Intelligence API
  //--------------------------------------------------

  Future<AIDecisionModel> getDecision() async {
    final json = await _api.get(
      "/api/intelligence",
    );

    return AIDecisionModel.fromJson(
      json,
    );
  }
}
