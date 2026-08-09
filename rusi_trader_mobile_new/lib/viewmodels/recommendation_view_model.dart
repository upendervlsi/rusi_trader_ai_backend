import 'package:flutter/foundation.dart';

import '../models/recommendation_model.dart';
import '../repositories/recommendation_repository.dart';

class RecommendationViewModel extends ChangeNotifier {
  final RecommendationRepository _repository =
      RecommendationRepository();

  RecommendationModel? recommendation;

  bool loading = false;

  String? error;

  Future<void> load() async {
    loading = true;
    error = null;

    notifyListeners();

    try {
      recommendation =
          await _repository.getRecommendation();
    } catch (e) {
      error = e.toString();
    }

    loading = false;

    notifyListeners();
  }

  Future<void> refresh() async {
    await load();
  }
}
