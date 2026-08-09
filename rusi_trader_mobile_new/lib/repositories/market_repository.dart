/*
============================================================
RUSI Trader AI

Market Repository

Responsible ONLY for market data.

Authoritative backend sources:

    /api/market
    /api/indicators
    /api/momentum
    /api/options

All four endpoints are merged into one
MarketDetailsModel for the Market screen.

============================================================
*/

import '../core/api/api_client.dart';
import '../models/market_details_model.dart';

class MarketRepository {

  final ApiClient _api = ApiClient();

  // ---------------------------------------------------------
  // Market Details
  // ---------------------------------------------------------

  Future<MarketDetailsModel> getMarketDetails() async {

    // -------------------------------------------------------
    // Market
    // -------------------------------------------------------

    final market = await _api.get(
      "/api/market",
    );

    // -------------------------------------------------------
    // Indicators
    // -------------------------------------------------------

    final indicators = await _api.get(
      "/api/indicators",
    );

    // -------------------------------------------------------
    // Momentum
    // -------------------------------------------------------

    final momentum = await _api.get(
      "/api/momentum",
    );

    // -------------------------------------------------------
    // Options
    // -------------------------------------------------------

    final options = await _api.get(
      "/api/options",
    );

    // -------------------------------------------------------
    // Merge all authoritative backend responses
    // -------------------------------------------------------

    final Map<String, dynamic> json = {};

    json.addAll(market);
    json.addAll(indicators);
    json.addAll(momentum);
    json.addAll(options);

    // -------------------------------------------------------
    // Convert merged response to domain model
    // -------------------------------------------------------

    return MarketDetailsModel.fromJson(
      json,
    );
  }
}
