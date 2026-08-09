import 'package:flutter/material.dart';

import '../common/base_card.dart';
import '../common/metric_grid.dart';
import '../common/metric_tile.dart';

class MarketHealthCard extends StatelessWidget {
  final String trend;
  final double strength;
  final double volatility;
  final double momentum;

  const MarketHealthCard({
    super.key,
    required this.trend,
    required this.strength,
    required this.volatility,
    required this.momentum,
  });

  Color get trendColor {
    switch (trend.toUpperCase()) {
      case "BULLISH":
        return Colors.green;
      case "BEARISH":
        return Colors.red;
      default:
        return Colors.orange;
    }
  }

  @override
  Widget build(BuildContext context) {
    return BaseCard(
      title: "Market Health",
      icon: Icons.monitor_heart,
      child: MetricGrid(
        children: [
          MetricTile(
            title: "Trend",
            value: trend,
            valueColor: trendColor,
            icon: Icons.trending_up,
          ),
          MetricTile(
            title: "Strength",
            value: "${strength.toStringAsFixed(1)}%",
            icon: Icons.fitness_center,
          ),
          MetricTile(
            title: "Volatility",
            value: volatility.toStringAsFixed(2),
            icon: Icons.show_chart,
          ),
          MetricTile(
            title: "Momentum",
            value: momentum.toStringAsFixed(2),
            icon: Icons.speed,
          ),
        ],
      ),
    );
  }
}
