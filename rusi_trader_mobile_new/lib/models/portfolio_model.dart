class PortfolioModel {

  final int openPositions;

  final double investedAmount;

  final double marketValue;

  final double unrealizedPnl;

  PortfolioModel({

    required this.openPositions,

    required this.investedAmount,

    required this.marketValue,

    required this.unrealizedPnl,

  });

  factory PortfolioModel.fromJson(
      Map<String, dynamic> json) {

    return PortfolioModel(

      openPositions:
          json["open_positions"],

      investedAmount:
          (json["invested_amount"] as num).toDouble(),

      marketValue:
          (json["market_value"] as num).toDouble(),

      unrealizedPnl:
          (json["unrealized_pnl"] as num).toDouble(),

    );
  }

}
