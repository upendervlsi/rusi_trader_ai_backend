import 'package:flutter/material.dart';

import '../common/base_card.dart';
import '../common/metric_row.dart';

class AiSummaryCard extends StatelessWidget {
  final String decision;
  final double confidence;
  final double score;
  final String optionType;
  final String marketStatus;

  const AiSummaryCard({
    super.key,
    required this.decision,
    required this.confidence,
    required this.score,
    required this.optionType,
    required this.marketStatus,
  });

  // --------------------------------------------------------
  // Decision Color
  // --------------------------------------------------------

  Color get decisionColor {
    switch (decision.toUpperCase()) {
      case "BUY":
        return Colors.green;

      case "SELL":
        return Colors.red;

      default:
        return Colors.orange;
    }
  }

  // --------------------------------------------------------
  // Decision Icon
  // --------------------------------------------------------

  IconData get decisionIcon {
    switch (decision.toUpperCase()) {
      case "BUY":
        return Icons.trending_up;

      case "SELL":
        return Icons.trending_down;

      default:
        return Icons.remove;
    }
  }

  // --------------------------------------------------------
  // Market Status
  // --------------------------------------------------------

  bool get marketIsOpen {
    return marketStatus.toUpperCase() == "OPEN";
  }

  // --------------------------------------------------------
  // Execution Status
  // --------------------------------------------------------

  String get executionStatus {
    if (!marketIsOpen) {
      return "WAIT — MARKET $marketStatus";
    }

    return decision.toUpperCase();
  }

  // --------------------------------------------------------
  // Execution Status Color
  // --------------------------------------------------------

  Color get executionStatusColor {
    if (!marketIsOpen) {
      return Colors.orange;
    }

    return decisionColor;
  }

  // --------------------------------------------------------
  // Build
  // --------------------------------------------------------

  @override
  Widget build(BuildContext context) {
    return BaseCard(
      title: "AI Decision",
      icon: Icons.psychology,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [

          //==================================================
          // Hero Section
          //==================================================

          Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [

                Icon(
                  decisionIcon,
                  size: 38,
                  color: decisionColor,
                ),

                const SizedBox(height: 6),

                Text(
                  decision,
                  style: TextStyle(
                    color: decisionColor,
                    fontSize: 30,
                    fontWeight: FontWeight.bold,
                  ),
                ),

                const SizedBox(height: 4),

                Text(
                  "${confidence.toStringAsFixed(1)} % Confidence",
                  style: const TextStyle(
                    fontSize: 15,
                    color: Colors.white70,
                  ),
                ),
              ],
            ),
          ),

          const SizedBox(height: 10),

          //==================================================
          // Execution Status
          //==================================================

          MetricRow(
            label: "Execution",
            value: executionStatus,
            icon: marketIsOpen
                ? Icons.play_arrow
                : Icons.pause_circle_outline,
            valueColor: executionStatusColor,
          ),

          const SizedBox(height: 8),

          //==================================================
          // Engine Score
          //==================================================

          MetricRow(
            label: "Engine Score",
            value: score.toStringAsFixed(2),
            icon: Icons.analytics_outlined,
            valueColor: decisionColor,
          ),
        ],
      ),
    );
  }
}
