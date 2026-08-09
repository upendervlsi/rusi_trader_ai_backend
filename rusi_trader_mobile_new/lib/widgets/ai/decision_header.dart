/*
============================================================

RUSI Trader AI

Professional Decision Header

============================================================
*/

import 'package:flutter/material.dart';

import '../../models/trade_plan_model.dart';

class DecisionHeader extends StatelessWidget {
  final TradePlanModel trade;

  const DecisionHeader({
    super.key,
    required this.trade,
  });

  //--------------------------------------------------
  // Recommendation Color
  //--------------------------------------------------

  Color get recommendationColor {
    switch (trade.recommendation.toUpperCase()) {
      case "BUY":
        return Colors.green;

      case "SELL":
        return Colors.red;

      default:
        return Colors.orange;
    }
  }

  //--------------------------------------------------
  // Recommendation Icon
  //--------------------------------------------------

  IconData get recommendationIcon {
    switch (trade.recommendation.toUpperCase()) {
      case "BUY":
        return Icons.trending_up;

      case "SELL":
        return Icons.trending_down;

      default:
        return Icons.pause_circle;
    }
  }

  @override
  Widget build(
    BuildContext context,
  ) {
    return Card(
      elevation: 5,
      shape: RoundedRectangleBorder(
        borderRadius:
            BorderRadius.circular(16),
      ),
      child: Padding(
        padding:
            const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment:
              CrossAxisAlignment.start,
          children: [

            //------------------------------------------
            // Recommendation
            //------------------------------------------

            Row(
              children: [

                Icon(
                  recommendationIcon,
                  color:
                      recommendationColor,
                  size: 40,
                ),

                const SizedBox(
                  width: 16,
                ),

                Expanded(
                  child: Column(
                    crossAxisAlignment:
                        CrossAxisAlignment
                            .start,
                    children: [

                      const Text(
                        "AI Recommendation",
                        style: TextStyle(
                          fontSize: 14,
                          color:
                              Colors.grey,
                        ),
                      ),

                      Text(
                        trade.recommendation,
                        style: TextStyle(
                          color:
                              recommendationColor,
                          fontSize: 30,
                          fontWeight:
                              FontWeight.bold,
                        ),
                      ),

                    ],
                  ),
                ),

              ],
            ),

            const SizedBox(
              height: 24,
            ),
            //------------------------------------------
            // Confidence
            //------------------------------------------

            Text(
              "Confidence : "
              "${trade.confidence.toStringAsFixed(1)}%",
              style: const TextStyle(
                fontWeight:
                    FontWeight.bold,
              ),
            ),

            const SizedBox(
              height: 8,
            ),

            LinearProgressIndicator(
              value:
                  trade.confidence / 100,
              minHeight: 10,
              borderRadius:
                  BorderRadius.circular(10),
            ),

            const SizedBox(
              height: 20,
            ),

            //------------------------------------------
            // Summary
            //------------------------------------------

            Row(
              mainAxisAlignment:
                  MainAxisAlignment
                      .spaceBetween,
              children: [

                _buildMetric(
                  "Trade Quality",
                  trade.tradeQuality
                      .toStringAsFixed(1),
                ),

                _buildMetric(
                  "Risk",
                  trade.risk,
                ),

                _buildMetric(
                  "Holding",
                  trade.holdingType,
                ),

              ],
            ),

          ],
        ),
      ),
    );
  }

  //--------------------------------------------------
  // Metric Widget
  //--------------------------------------------------

  Widget _buildMetric(
    String title,
    String value,
  ) {
    return Column(
      children: [

        Text(
          title,
          style: const TextStyle(
            color: Colors.grey,
            fontSize: 12,
          ),
        ),

        const SizedBox(
          height: 4,
        ),

        Text(
          value,
          style: const TextStyle(
            fontWeight:
                FontWeight.bold,
            fontSize: 18,
          ),
        ),

      ],
    );
  }
}
