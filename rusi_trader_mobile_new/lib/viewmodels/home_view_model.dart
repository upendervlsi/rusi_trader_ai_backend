import 'dart:async';

import 'package:flutter/material.dart';

import '../repositories/home_repository.dart';

import '../models/dashboard_model.dart';
import '../models/market_model.dart';
import '../models/recommendation_model.dart';
import '../models/portfolio_model.dart';

class HomeViewModel extends ChangeNotifier {

  //==========================================================
  // Repository
  //==========================================================

  final HomeRepository _repository =
      HomeRepository();

  //==========================================================
  // Data
  //==========================================================

  DashboardModel? dashboard;

  MarketModel? market;

  RecommendationModel? recommendation;

  PortfolioModel? portfolio;

  //==========================================================
  // UI State
  //==========================================================

  bool loading = true;

  String? error;

  //==========================================================
  // Live Refresh
  //==========================================================

  Timer? _refreshTimer;

  bool _refreshInProgress = false;

  static const Duration _refreshInterval =
      Duration(seconds: 30);

  //==========================================================
  // Initial Load
  //==========================================================

  Future<void> load() async {

    print("=================================");
    print("HOME VIEWMODEL LOAD()");
    print("=================================");

    loading = true;

    notifyListeners();

    await _loadData();

    loading = false;

    notifyListeners();
  }

  //==========================================================
  // Internal Data Load
  //==========================================================

  Future<void> _loadData() async {

    // Prevent two refresh cycles from running together.
    if (_refreshInProgress) {
      return;
    }

    _refreshInProgress = true;

    try {

      //======================================================
      // Dashboard
      //======================================================

      dashboard =
          await _repository.getDashboard();

      print("Dashboard Loaded");

      //======================================================
      // Market
      //======================================================

      market =
          await _repository.getMarket();

      print("Market Loaded");

      //======================================================
      // Recommendation
      //======================================================

      recommendation =
          await _repository.getRecommendation();

      print("Recommendation Loaded");

      //======================================================
      // Portfolio
      //======================================================

      portfolio =
          await _repository.getPortfolio();

      print("Portfolio Loaded");

      error = null;

    } catch (e, stackTrace) {

      print("=================================");
      print("HOME VIEWMODEL ERROR");
      print("=================================");

      print(e);
      print(stackTrace);

      print("=================================");

      error = e.toString();

    } finally {

      _refreshInProgress = false;
    }
  }

  //==========================================================
  // Start Live Refresh
  //==========================================================

  void startLiveRefresh() {

    // Prevent duplicate timers.
    if (_refreshTimer != null) {
      return;
    }

    print("=================================");
    print("HOME LIVE REFRESH STARTED");
    print(
      "INTERVAL : "
      "${_refreshInterval.inSeconds} seconds",
    );
    print("=================================");

    _refreshTimer =
        Timer.periodic(
      _refreshInterval,
      (_) async {

        await refresh();
      },
    );
  }

  //==========================================================
  // Stop Live Refresh
  //==========================================================

  void stopLiveRefresh() {

    _refreshTimer?.cancel();

    _refreshTimer = null;

    print("=================================");
    print("HOME LIVE REFRESH STOPPED");
    print("=================================");
  }

  //==========================================================
  // Refresh
  //==========================================================

  Future<void> refresh() async {

    print("");
    print("=================================");
    print("HOME LIVE REFRESH");
    print("=================================");

    await _loadData();

    // Update UI with latest values.
    notifyListeners();
  }

  //==========================================================
  // Dispose
  //==========================================================

  @override
  void dispose() {

    stopLiveRefresh();

    super.dispose();
  }
}
