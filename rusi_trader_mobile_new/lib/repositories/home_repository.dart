import '../core/api/api_client.dart';
import '../core/api/endpoints.dart';

import '../models/dashboard_model.dart';
import '../models/market_model.dart';
import '../models/recommendation_model.dart';
import '../models/portfolio_model.dart';

class HomeRepository {

  final ApiClient _api = ApiClient();

  Future<MarketModel> getMarket() async {

    print("Loading Dashboard1");

    final json = await _api.get(
      Endpoints.market,
    );

    return MarketModel.fromJson(json);

  }

  Future<RecommendationModel> getRecommendation() async {

    print("Loading Dashboard2");

    final json = await _api.get(
      Endpoints.recommendation,
    );

    return RecommendationModel.fromJson(json);

  }

  Future<PortfolioModel> getPortfolio() async {

    print("Loading Dashboard3");

    final json = await _api.get(
      Endpoints.portfolio,
    );

    return PortfolioModel.fromJson(json);

  }

  Future<DashboardModel> getDashboard() async {

    print("Loading Dashboard4");

    final json = await _api.get(
      Endpoints.dashboard,
    );

    return DashboardModel.fromJson(json);

  }

}
