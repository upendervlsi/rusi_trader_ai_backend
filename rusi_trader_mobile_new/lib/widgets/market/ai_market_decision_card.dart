/*
============================================================

RUSI Trader AI

AI Market Decision Card

============================================================
*/

import 'package:flutter/material.dart';

import '../common/base_card.dart';
import '../common/metric_grid.dart';
import '../common/metric_tile.dart';

class AiMarketDecisionCard extends StatelessWidget {
  final String recommendation;

  final double confidence;

  final double score;

  final String optionSymbol;

  final double entryPrice;

  final double stopLoss;

  final double targetPrice;

  const AiMarketDecisionCard({
    super.key,
    required this.recommendation,
    required this.confidence,
    required this.score,
    required this.optionSymbol,
    required this.entryPrice,
    required this.stopLoss,
    required this.targetPrice,
  });

  //----------------------------------------------------------
  // Recommendation Color
  //----------------------------------------------------------

  Color get signalColor {
    switch (recommendation.toUpperCase()) {
      case "BUY":
        return Colors.green;

      case "SELL":
        return Colors.red;

      default:
        return Colors.orange;
    }
  }

  //----------------------------------------------------------
  // Recommendation Icon
  //----------------------------------------------------------

  IconData get signalIcon {
    switch (recommendation.toUpperCase()) {
      case "BUY":
        return Icons.trending_up;

      case "SELL":
        return Icons.trending_down;

      default:
        return Icons.pause_circle_outline;
    }
  }

  @override
  Widget build(BuildContext context) {
    return BaseCard(
      title: "AI Market Decision",
      icon: Icons.psychology,
      child: Column(
        children: [

          //------------------------------------------------
          // Decision
          //------------------------------------------------

          Icon(
            signalIcon,
            size: 60,
            color: signalColor,
          ),

          const SizedBox(height: 10),

          Text(
            recommendation,
            style: TextStyle(
              fontSize: 34,
              fontWeight: FontWeight.bold,
              color: signalColor,
            ),
          ),

          const SizedBox(height: 25),

          //------------------------------------------------
          // Metrics
          //------------------------------------------------

          MetricGrid(
            children: [

              MetricTile(
                title: "Confidence",
                value:
                    "${confidence.toStringAsFixed(1)}%",
                icon: Icons.speed,
                valueColor: Colors.green,
              ),

              MetricTile(
                title: "Score",
                value: score.toStringAsFixed(2),
                icon: Icons.analytics,
                valueColor: Colors.orange,
              ),

              MetricTile(
                title: "Option",
                value: optionSymbol,
                icon: Icons.account_balance,
              ),

              MetricTile(
                title: "Entry",
                value:
                    entryPrice.toStringAsFixed(2),
                icon: Icons.login,
              ),

              MetricTile(
                title: "Stop Loss",
                value:
                    stopLoss.toStringAsFixed(2),
                icon: Icons.shield,
                valueColor: Colors.red,
              ),

              MetricTile(
                title: "Target",
                value:
                    targetPrice.toStringAsFixed(2),
                icon: Icons.flag,
                valueColor: Colors.green,
              ),
            ],
          ),
        ],
      ),
    );
  }
}
