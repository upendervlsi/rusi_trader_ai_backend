/*
============================================================

RUSI Trader AI

Market Intelligence Card

============================================================
*/

import 'package:flutter/material.dart';

import '../common/base_card.dart';

class MarketIntelligenceCard extends StatelessWidget {

  final String trend;

  final List<String> reasons;

  final String risk;

  final double confidence;

  const MarketIntelligenceCard({

    super.key,

    required this.trend,

    required this.reasons,

    required this.risk,

    required this.confidence,

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

      title: "Market Intelligence",

      icon: Icons.psychology,

      child: Column(

        crossAxisAlignment:
            CrossAxisAlignment.start,

        children: [

          Text(

            trend,

            style: TextStyle(

              color: trendColor,

              fontSize: 28,

              fontWeight: FontWeight.bold,

            ),

          ),

          const SizedBox(height: 20),

          const Text(

            "Why?",

            style: TextStyle(

              fontWeight: FontWeight.bold,

            ),

          ),

          const SizedBox(height: 10),

          ...reasons.map(

            (e) => Padding(

              padding:
                  const EdgeInsets.symmetric(
                vertical: 4,
              ),

              child: Row(

                children: [

                  const Icon(

                    Icons.check_circle,

                    color: Colors.green,

                    size: 18,

                  ),

                  const SizedBox(width: 10),

                  Expanded(
                    child: Text(e),
                  ),

                ],

              ),

            ),

          ),

          const Divider(height: 30),

          Row(

            children: [

              const Text("Confidence"),

              const Spacer(),

              Text(

                "${confidence.toStringAsFixed(0)}%",

                style: const TextStyle(

                  color: Colors.green,

                  fontWeight: FontWeight.bold,

                ),

              ),

            ],

          ),

          const SizedBox(height: 10),

          Row(

            children: [

              const Text("Risk"),

              const Spacer(),

              Text(

                risk,

                style: TextStyle(

                  color:
                      risk == "LOW"
                          ? Colors.green
                          : Colors.orange,

                  fontWeight:
                      FontWeight.bold,

                ),

              ),

            ],

          ),

        ],

      ),

    );

  }

}
