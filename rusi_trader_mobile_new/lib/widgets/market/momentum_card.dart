import 'package:flutter/material.dart';

import '../common/base_card.dart';
import '../common/metric_grid.dart';
import '../common/metric_tile.dart';

class MomentumCard extends StatelessWidget {
  final double rsi;
  final double macd;
  final double adx;
  final double atr;

  const MomentumCard({
    super.key,
    required this.rsi,
    required this.macd,
    required this.adx,
    required this.atr,
  });

  @override
  Widget build(BuildContext context) {
    return BaseCard(
      title: "Momentum",
      icon: Icons.speed,
      child: MetricGrid(
        children: [
          MetricTile(
            title: "RSI",
            value: rsi.toStringAsFixed(2),
            icon: Icons.show_chart,
          ),
          MetricTile(
            title: "MACD",
            value: macd.toStringAsFixed(2),
            icon: Icons.trending_up,
          ),
          MetricTile(
            title: "ADX",
            value: adx.toStringAsFixed(2),
            icon: Icons.analytics,
          ),
          MetricTile(
            title: "ATR",
            value: atr.toStringAsFixed(2),
            icon: Icons.timeline,
          ),
        ],
      ),
    );
  }
}
