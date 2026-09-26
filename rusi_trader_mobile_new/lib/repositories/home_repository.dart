import '../core/api/api_client.dart';
import '../core/api/endpoints.dart';

import '../models/dashboard_model.dart';
import '../models/market_model.dart';
import '../models/recommendation_model.dart';
import '../models/portfolio_model.dart';
import '../models/paper_trading_model.dart';

class HomeRepository {

  final ApiClient _api = ApiClient();

  //==========================================================
  // MARKET
  //==========================================================

  Future<MarketModel> getMarket() async {

    print("Loading Dashboard1");

    final json = await _api.get(
      Endpoints.market,
    );

    return MarketModel.fromJson(json);

  }

  //==========================================================
  // RECOMMENDATION
  //==========================================================

  Future<RecommendationModel> getRecommendation() async {

    print("Loading Dashboard2");

    final json = await _api.get(
      Endpoints.recommendation,
    );

    return RecommendationModel.fromJson(json);

  }

  //==========================================================
  // PORTFOLIO
  //==========================================================

  Future<PortfolioModel> getPortfolio() async {

    print("Loading Dashboard3");

    final json = await _api.get(
      Endpoints.portfolio,
    );

    return PortfolioModel.fromJson(json);

  }

  //==========================================================
  // DASHBOARD
  //==========================================================

  Future<DashboardModel> getDashboard() async {

    print("Loading Dashboard4");

    final json = await _api.get(
      Endpoints.dashboard,
    );

    return DashboardModel.fromJson(json);

  }

  //==========================================================
  // PAPER TRADING
  //
  // Reads the automatic paper-trading runtime status
  // from the backend.
  //==========================================================

  Future<PaperTradingModel> getPaperTrading() async {

    print("Loading Paper Trading");

    final json = await _api.get(
      Endpoints.paperTrading,
    );

    return PaperTradingModel.fromJson(
      json,
    );

  }

}
