import 'package:flutter/material.dart';

import '../common/base_card.dart';
import '../common/metric_grid.dart';
import '../common/metric_tile.dart';

class MovingAverageCard extends StatelessWidget {
  final double ema20;
  final double ema50;
  final double sma20;
  final double sma50;
  final double vwap;

  const MovingAverageCard({
    super.key,
    required this.ema20,
    required this.ema50,
    required this.sma20,
    required this.sma50,
    required this.vwap,
  });

  @override
  Widget build(BuildContext context) {
    return BaseCard(
      title: "Moving Averages",
      icon: Icons.show_chart,
      child: MetricGrid(
        children: [
          MetricTile(
            title: "EMA20",
            value: ema20.toStringAsFixed(2),
            icon: Icons.trending_up,
          ),
          MetricTile(
            title: "EMA50",
            value: ema50.toStringAsFixed(2),
            icon: Icons.trending_up,
          ),
          MetricTile(
            title: "SMA20",
            value: sma20.toStringAsFixed(2),
            icon: Icons.timeline,
          ),
          MetricTile(
            title: "SMA50",
            value: sma50.toStringAsFixed(2),
            icon: Icons.timeline,
          ),
          MetricTile(
            title: "VWAP",
            value: vwap.toStringAsFixed(2),
            icon: Icons.analytics,
          ),
        ],
      ),
    );
  }
}
