import 'package:flutter/material.dart';

import '../common/base_card.dart';
import '../../models/recommendation_model.dart';

class AIRecommendationCard extends StatelessWidget {
  final RecommendationModel recommendation;

  const AIRecommendationCard({
    super.key,
    required this.recommendation,
  });

  Color _signalColor() {
    switch (recommendation.recommendation.toUpperCase()) {
      case "BUY":
        return Colors.green;

      case "SELL":
        return Colors.red;

      default:
        return Colors.orange;
    }
  }

  @override
  Widget build(BuildContext context) {
    return BaseCard(
      title: "AI Recommendation",
      icon: Icons.psychology,
      child: Column(
        crossAxisAlignment:
            CrossAxisAlignment.start,
        children: [

          Row(
            children: [

              Expanded(
                child: Text(
                  recommendation.optionSymbol,
                  style: const TextStyle(
                    fontSize: 18,
                    fontWeight:
                        FontWeight.bold,
                  ),
                ),
              ),

              Chip(
                backgroundColor:
                    _signalColor(),

                label: Text(
                  recommendation
                      .recommendation,
                  style: const TextStyle(
                    color: Colors.white,
                    fontWeight:
                        FontWeight.bold,
                  ),
                ),
              ),
            ],
          ),

          const SizedBox(height: 18),

          Text(
            "Confidence : "
            "${recommendation.confidence.toStringAsFixed(1)}%",
          ),

          const SizedBox(height: 6),

          LinearProgressIndicator(
            value:
                recommendation.confidence /
                100,
          ),

          const SizedBox(height: 20),

          Row(
            children: [

              Expanded(
                child: _value(
                  "Entry",
                  recommendation
                      .entryPrice
                      .toStringAsFixed(2),
                ),
              ),

              Expanded(
                child: _value(
                  "SL",
                  recommendation
                      .stopLoss
                      .toStringAsFixed(2),
                ),
              ),

              Expanded(
                child: _value(
                  "Target",
                  recommendation
                      .targetPrice
                      .toStringAsFixed(2),
                ),
              ),
            ],
          ),

          const SizedBox(height: 18),

          _value(
            "Engine Score",
            recommendation.score
                .toStringAsFixed(2),
          ),
        ],
      ),
    );
  }

  Widget _value(
    String title,
    String value,
  ) {
    return Column(
      crossAxisAlignment:
          CrossAxisAlignment.start,
      children: [

        Text(
          title,
          style: const TextStyle(
            fontSize: 12,
            color: Colors.grey,
          ),
        ),

        const SizedBox(height: 4),

        Text(
          value,
          style: const TextStyle(
            fontWeight:
                FontWeight.bold,
            fontSize: 16,
          ),
        ),
      ],
    );
  }
}
