import '../core/api/api_client.dart';
import '../models/recommendation_model.dart';

class RecommendationRepository {
  final ApiClient _api = ApiClient();

  Future<RecommendationModel> getRecommendation() async {
    final json = await _api.get(
      "/api/recommendation",
    );

    return RecommendationModel.fromJson(
      json,
    );
  }
}
