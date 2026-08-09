import 'market_details_model.dart';
import 'recommendation_model.dart';

class MarketDashboardModel {
  final MarketDetailsModel market;
  final RecommendationModel recommendation;

  const MarketDashboardModel({
    required this.market,
    required this.recommendation,
  });
}
