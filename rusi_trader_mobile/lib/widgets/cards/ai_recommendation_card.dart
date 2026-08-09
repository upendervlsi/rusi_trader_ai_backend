import 'package:flutter/material.dart';

import '../../theme/app_colors.dart';

class AIRecommendationCard extends StatelessWidget {

  final String symbol;
  final String signal;
  final double confidence;
  final String entry;
  final String stopLoss;
  final String target;

  const AIRecommendationCard({

    super.key,

    required this.symbol,

    required this.signal,

    required this.confidence,

    required this.entry,

    required this.stopLoss,

    required this.target,

  });

  @override
  Widget build(BuildContext context) {

    return Card(

      elevation: 0,

      child: Padding(

        padding: const EdgeInsets.all(18),

        child: Column(

          crossAxisAlignment: CrossAxisAlignment.start,

          children: [

            const Text(

              "AI Recommendation",

              style: TextStyle(

                fontWeight: FontWeight.bold,

                fontSize: 20,

              ),

            ),

            const SizedBox(height: 15),

            Row(

              mainAxisAlignment: MainAxisAlignment.spaceBetween,

              children: [

                Text(

                  symbol,

                  style: const TextStyle(

                    fontSize: 24,

                    fontWeight: FontWeight.bold,

                  ),

                ),

                Chip(

                  label: Text(signal),

                  backgroundColor:

                      signal == "BUY"

                          ? Colors.green

                          : Colors.red,

                ),

              ],

            ),

            const SizedBox(height: 15),

            LinearProgressIndicator(

              value: confidence / 100,

              minHeight: 10,

            ),

            const SizedBox(height: 10),

            Text("Confidence : ${confidence.toStringAsFixed(0)}%"),

            const Divider(),

            Row(

              mainAxisAlignment: MainAxisAlignment.spaceBetween,

              children: [

                _buildValue("Entry", entry),

                _buildValue("SL", stopLoss),

                _buildValue("Target", target),

              ],

            ),

            const SizedBox(height: 20),

            SizedBox(

              width: double.infinity,

              child: ElevatedButton(

                onPressed: () {},

                child: const Text(

                  "BUY NOW",

                ),

              ),

            ),

          ],

        ),

      ),

    );

  }

  Widget _buildValue(

      String title,

      String value,

      ) {

    return Column(

      children: [

        Text(title),

        const SizedBox(height: 5),

        Text(

          value,

          style: const TextStyle(

            fontWeight: FontWeight.bold,

          ),

        ),

      ],

    );

  }

}
