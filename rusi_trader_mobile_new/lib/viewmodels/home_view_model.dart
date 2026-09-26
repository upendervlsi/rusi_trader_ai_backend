import 'dart:async';

import 'package:flutter/material.dart';

import '../repositories/home_repository.dart';

import '../models/dashboard_model.dart';
import '../models/market_model.dart';
import '../models/recommendation_model.dart';
import '../models/portfolio_model.dart';
import '../models/paper_trading_model.dart';


class HomeViewModel
    extends ChangeNotifier {

  final HomeRepository _repository =
      HomeRepository();


  //==========================================================
  // DATA
  //==========================================================

  DashboardModel? dashboard;

  MarketModel? market;

  RecommendationModel? recommendation;

  PortfolioModel? portfolio;

  PaperTradingModel? paperTrading;


  //==========================================================
  // UI STATE
  //==========================================================

  bool loading = true;

  String? error;


  //==========================================================
  // LIVE REFRESH
  //==========================================================

  Timer? _refreshTimer;

  bool _refreshInProgress =
      false;

  static const Duration
      _refreshInterval =
      Duration(seconds: 5);


  //==========================================================
  // INITIAL LOAD
  //==========================================================

  Future<void> load() async {

    loading = true;

    notifyListeners();

    await _initialLoad();

    loading = false;

    notifyListeners();
  }


  //==========================================================
  // INITIAL LOAD
  //
  // Full supporting data is loaded once.
  //==========================================================

  Future<void> _initialLoad() async {

    if (_refreshInProgress) {
      return;
    }

    _refreshInProgress = true;

    try {

      //======================================================
      // PRIMARY DASHBOARD
      //======================================================

      dashboard =
          await _repository
              .getDashboard();


      //======================================================
      // EXISTING SUPPORTING DATA
      //
      // Needed by the existing detailed cards.
      //======================================================

      market =
          await _repository
              .getMarket();

      recommendation =
          await _repository
              .getRecommendation();

      portfolio =
          await _repository
              .getPortfolio();


      //======================================================
      // PAPER TRADING
      //
      // Automatic paper-trading runtime status.
      //======================================================

      paperTrading =
          await _repository
              .getPaperTrading();


      error = null;

    } catch (
      e,
      stackTrace
    ) {

      debugPrint(
        "HOME INITIAL LOAD ERROR: $e",
      );

      debugPrint(
        "$stackTrace",
      );

      error = e.toString();

    } finally {

      _refreshInProgress = false;

    }
  }


  //==========================================================
  // FAST DASHBOARD REFRESH
  //
  // Dashboard remains the primary fast snapshot.
  //==========================================================

  Future<void> _refreshDashboard()
      async {

    try {

      final latestDashboard =
          await _repository
              .getDashboard();

      dashboard =
          latestDashboard;

    } catch (
      e,
      stackTrace
    ) {

      debugPrint(
        "HOME DASHBOARD REFRESH ERROR: $e",
      );

      debugPrint(
        "$stackTrace",
      );

      //
      // Keep the last good dashboard
      // visible instead of blanking the UI.
      //

      error = e.toString();

    }
  }


  //==========================================================
  // PAPER TRADING REFRESH
  //
  // Reads the latest paper-trading status and P&L.
  //
  // This is intentionally separate from dashboard refresh
  // so a paper-trading API failure does not destroy the
  // existing dashboard.
  //==========================================================

  Future<void> _refreshPaperTrading()
      async {

    try {

      final latestPaperTrading =
          await _repository
              .getPaperTrading();

      paperTrading =
          latestPaperTrading;

    } catch (
      e,
      stackTrace
    ) {

      debugPrint(
        "HOME PAPER TRADING REFRESH ERROR: $e",
      );

      debugPrint(
        "$stackTrace",
      );

      //
      // Keep the last good paper-trading
      // state visible.
      //

    }
  }


  //==========================================================
  // START LIVE REFRESH
  //==========================================================

  void startLiveRefresh() {

    if (_refreshTimer != null) {
      return;
    }

    _refreshTimer =
        Timer.periodic(
      _refreshInterval,
      (_) async {

        await refresh();

      },
    );
  }


  //==========================================================
  // STOP LIVE REFRESH
  //==========================================================

  void stopLiveRefresh() {

    _refreshTimer?.cancel();

    _refreshTimer = null;
  }


  //==========================================================
  // REFRESH
  //==========================================================

  Future<void> refresh() async {

    if (_refreshInProgress) {
      return;
    }

    _refreshInProgress = true;

    try {

      //======================================================
      // FAST DASHBOARD
      //======================================================

      await _refreshDashboard();


      //======================================================
      // PAPER TRADING
      //======================================================

      await _refreshPaperTrading();

    } finally {

      _refreshInProgress = false;

    }

    if (!hasListeners) {
      return;
    }

    notifyListeners();
  }


  //==========================================================
  // DISPOSE
  //==========================================================

  @override
  void dispose() {

    stopLiveRefresh();

    super.dispose();
  }
}
