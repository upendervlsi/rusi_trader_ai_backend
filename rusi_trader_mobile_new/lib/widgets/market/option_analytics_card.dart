import 'package:flutter/material.dart';

import '../common/base_card.dart';
import '../common/metric_grid.dart';
import '../common/metric_tile.dart';

class OptionAnalyticsCard extends StatelessWidget {
  final double pcr;
  final double openInterest;
  final double changeOi;
  final double iv;
  final double maxPain;

  const OptionAnalyticsCard({
    super.key,
    required this.pcr,
    required this.openInterest,
    required this.changeOi,
    required this.iv,
    required this.maxPain,
  });

  @override
  Widget build(BuildContext context) {
    return BaseCard(
      title: "Option Analytics",
      icon: Icons.analytics,
      child: MetricGrid(
        children: [
          MetricTile(
            title: "PCR",
            value: pcr.toStringAsFixed(2),
            icon: Icons.balance,
          ),
          MetricTile(
            title: "Open Interest",
            value: openInterest.toStringAsFixed(0),
            icon: Icons.layers,
          ),
          MetricTile(
            title: "OI Change",
            value: changeOi.toStringAsFixed(0),
            icon: Icons.swap_vert,
          ),
          MetricTile(
            title: "IV",
            value: iv.toStringAsFixed(2),
            icon: Icons.bolt,
          ),
          MetricTile(
            title: "Max Pain",
            value: maxPain.toStringAsFixed(0),
            icon: Icons.warning_amber,
          ),
        ],
      ),
    );
  }
}
