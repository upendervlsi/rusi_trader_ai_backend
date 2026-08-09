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

  DashboardModel({

    required this.marketStatus,

    required this.latestClose,

    required this.decision,

    required this.confidence,

    required this.marketSymbol,

    required this.marketExchange,
  });

  factory DashboardModel.fromJson(
      Map<String, dynamic> json) {

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
    // Build model
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
    );
  }
}
