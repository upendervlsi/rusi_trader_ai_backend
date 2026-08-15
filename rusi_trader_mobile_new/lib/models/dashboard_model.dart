import 'market_pulse_model.dart';

class DashboardModel {
  final String marketStatus;

  final double? latestClose;

  final String? decision;

  final double? confidence;

  //==========================================================
  // Active Market
  //==========================================================

  final String marketSymbol;

  final String marketExchange;

  //==========================================================
  // Complete Market Pulse
  //
  // NIFTY
  // BANKNIFTY
  // FINNIFTY
  // MIDCAP NIFTY
  // SENSEX
  // BANKEX
  // CRUDE OIL
  //==========================================================

  final List<MarketPulseModel> marketPulse;

  //==========================================================
  // Strongest Market
  //==========================================================

  final String? strongestMarket;

  final double? strongestConfidence;

  DashboardModel({
    required this.marketStatus,
    required this.latestClose,
    required this.decision,
    required this.confidence,
    required this.marketSymbol,
    required this.marketExchange,
    required this.marketPulse,
    required this.strongestMarket,
    required this.strongestConfidence,
  });

  factory DashboardModel.fromJson(
    Map<String, dynamic> json,
  ) {
    //========================================================
    // Extract active market from dashboard response
    //========================================================

    String marketSymbol = "--";

    String marketExchange = "--";

    final markets = json["markets"];

    if (markets is List &&
        markets.isNotEmpty &&
        markets.first is Map) {
      final market =
          Map<String, dynamic>.from(
        markets.first as Map,
      );

      marketSymbol =
          market["symbol"]?.toString() ?? "--";

      marketExchange =
          market["exchange"]?.toString() ?? "--";
    }

    //========================================================
    // Parse Market Pulse
    //========================================================

    final List<MarketPulseModel> pulse = [];

    final rawPulse = json["market_pulse"];

    if (rawPulse is List) {
      for (final item in rawPulse) {
        if (item is Map) {
          pulse.add(
            MarketPulseModel.fromJson(
              Map<String, dynamic>.from(item),
            ),
          );
        }
      }
    }

    //========================================================
    // Build Dashboard
    //========================================================

    return DashboardModel(
      marketStatus:
          json["market_status"]?.toString() ??
          "UNKNOWN",

      latestClose:
          (json["latest_close"] as num?)
              ?.toDouble(),

      decision:
          json["decision"]?.toString(),

      confidence:
          (json["confidence"] as num?)
              ?.toDouble(),

      marketSymbol:
          marketSymbol,

      marketExchange:
          marketExchange,

      marketPulse:
          pulse,

      strongestMarket:
          json["strongest_market"]?.toString(),

      strongestConfidence:
          (json["strongest_confidence"] as num?)
              ?.toDouble(),
    );
  }
}
