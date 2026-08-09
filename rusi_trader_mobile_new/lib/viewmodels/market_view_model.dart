/*
============================================================

RUSI Trader AI

Market View Model

Loads:
1. Market Data
2. AI Recommendation

============================================================
*/

import 'package:flutter/material.dart';

import '../models/market_details_model.dart';
import '../models/recommendation_model.dart';

import '../repositories/market_repository.dart';
import '../repositories/recommendation_repository.dart';

class MarketViewModel extends ChangeNotifier {
  //--------------------------------------------------
  // Repositories
  //--------------------------------------------------

  final MarketRepository _marketRepository =
      MarketRepository();

  final RecommendationRepository
      _recommendationRepository =
      RecommendationRepository();

  //--------------------------------------------------
  // Data
  //--------------------------------------------------

  MarketDetailsModel? _market;

  RecommendationModel? _recommendation;

  //--------------------------------------------------
  // UI State
  //--------------------------------------------------

  bool _loading = false;

  String? _error;

  //--------------------------------------------------
  // Getters
  //--------------------------------------------------

  MarketDetailsModel? get market => _market;

  RecommendationModel? get recommendation =>
      _recommendation;

  bool get loading => _loading;

  String? get error => _error;

  //--------------------------------------------------
  // Load
  //--------------------------------------------------

  Future<void> load() async {
    try {
      _loading = true;
      _error = null;

      notifyListeners();

      //--------------------------------------------------
      // Load Market
      //--------------------------------------------------

      _market =
          await _marketRepository.getMarketDetails();

      //--------------------------------------------------
      // Load Recommendation
      //--------------------------------------------------

      _recommendation =
          await _recommendationRepository
              .getRecommendation();
    } catch (e, stackTrace) {
      debugPrint("");

      debugPrint(
        "================================",
      );

      debugPrint(
        "Market ViewModel Error",
      );

      debugPrint(e.toString());

      debugPrint(stackTrace.toString());

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
