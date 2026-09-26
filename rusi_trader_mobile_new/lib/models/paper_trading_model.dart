class PaperTradingModel {

  final bool running;

  final bool marketOpen;

  final int lastCycleId;

  final double capital;

  final double availableCapital;

  final double realizedPnl;

  final int openTrades;

  final int closedTrades;


  const PaperTradingModel({

    required this.running,

    required this.marketOpen,

    required this.lastCycleId,

    required this.capital,

    required this.availableCapital,

    required this.realizedPnl,

    required this.openTrades,

    required this.closedTrades,

  });


  factory PaperTradingModel.fromJson(
    Map<String, dynamic> json,
  ) {

    return PaperTradingModel(

      running:
          json["running"] == true,

      marketOpen:
          json["market_open"] == true,

      lastCycleId:
          (json["last_cycle_id"] as num?)
              ?.toInt() ??
          0,

      capital:
          (json["capital"] as num?)
              ?.toDouble() ??
          0.0,

      availableCapital:
          (json["available_capital"] as num?)
              ?.toDouble() ??
          0.0,

      realizedPnl:
          (json["realized_pnl"] as num?)
              ?.toDouble() ??
          0.0,

      openTrades:
          (json["open_trades"] as num?)
              ?.toInt() ??
          0,

      closedTrades:
          (json["closed_trades"] as num?)
              ?.toInt() ??
          0,
    );
  }
}
