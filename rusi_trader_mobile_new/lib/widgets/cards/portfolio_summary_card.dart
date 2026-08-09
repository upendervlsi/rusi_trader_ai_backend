import 'package:flutter/material.dart';

import '../common/base_card.dart';
import '../common/metric_row.dart';
import '../common/status_chip.dart';

class PortfolioSummaryCard extends StatelessWidget {
  final int openPositions;
  final double investedAmount;
  final double marketValue;
  final double unrealizedPnl;

  const PortfolioSummaryCard({
    super.key,
    required this.openPositions,
    required this.investedAmount,
    required this.marketValue,
    required this.unrealizedPnl,
  });

  Color get pnlColor {
    if (unrealizedPnl > 0) {
      return Colors.green;
    }

    if (unrealizedPnl < 0) {
      return Colors.red;
    }

    return Colors.orange;
  }

  String get pnlStatus {
    if (unrealizedPnl > 0) {
      return "PROFIT";
    }

    if (unrealizedPnl < 0) {
      return "LOSS";
    }

    return "FLAT";
  }

  @override
  Widget build(BuildContext context) {
    return BaseCard(
      title: "Portfolio",
      icon: Icons.account_balance_wallet,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [

          Align(
            alignment: Alignment.centerLeft,
            child: StatusChip(
              text: pnlStatus,
              color: pnlColor,
            ),
          ),

          const SizedBox(height: 20),

          MetricRow(
            label: "Open Positions",
            value: openPositions.toString(),
            icon: Icons.work_outline,
          ),

          MetricRow(
            label: "Investment",
            value:
                "₹ ${investedAmount.toStringAsFixed(2)}",
            icon: Icons.account_balance,
          ),

          MetricRow(
            label: "Market Value",
            value:
                "₹ ${marketValue.toStringAsFixed(2)}",
            icon: Icons.show_chart,
          ),

          MetricRow(
            label: "Unrealized P/L",
            value:
                "₹ ${unrealizedPnl.toStringAsFixed(2)}",
            valueColor: pnlColor,
            icon: Icons.trending_up,
          ),
        ],
      ),
    );
  }
}
