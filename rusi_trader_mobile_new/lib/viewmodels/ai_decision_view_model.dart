/*
============================================================

RUSI Trader AI

AI Decision ViewModel

============================================================
*/

import 'package:flutter/foundation.dart';

import '../models/ai_decision_model.dart';

import '../repositories/ai_repository.dart';

class AIDecisionViewModel extends ChangeNotifier {
  final AIRepository _repository = AIRepository();

  AIDecisionModel? _decision;

  bool _loading = false;

  String? _error;

  //--------------------------------------------------
  // Getters
  //--------------------------------------------------

  AIDecisionModel? get decision => _decision;

  bool get loading => _loading;

  String? get error => _error;

  //--------------------------------------------------
  // Load AI Decision
  //--------------------------------------------------

  Future<void> load() async {
    try {
      _loading = true;

      _error = null;

      notifyListeners();

      _decision = await _repository.getDecision();
    } catch (e, stackTrace) {
      debugPrint(
        "================================",
      );

      debugPrint(
        "AI DECISION VIEWMODEL ERROR",
      );

      debugPrint(
        e.toString(),
      );

      debugPrint(
        stackTrace.toString(),
      );

      debugPrint(
        "================================",
      );

      _error = e.toString();
    } finally {
      _loading = false;

      notifyListeners();
    }
  }

  //--------------------------------------------------
  // Refresh
  //--------------------------------------------------

  Future<void> refresh() async {
    await load();
  }
}
