import 'package:flutter/material.dart';

import '../../models/ai_decision.dart';

class AIDecisionBreakdownCard extends StatelessWidget {

  final AIDecision decision;

  const AIDecisionBreakdownCard({
    super.key,
    required this.decision,
  });

  Widget rowItem(String title, bool value) {

    return ListTile(

      dense: true,

      title: Text(title),

      trailing: Icon(

        value
            ? Icons.check_circle
            : Icons.cancel,

        color: value
            ? Colors.green
            : Colors.red,

      ),

    );

  }

  @override
  Widget build(BuildContext context) {

    return Card(

      child: Column(

        children: [

          const SizedBox(height:12),

          const Text(

            "AI Decision Engine",

            style: TextStyle(

              fontSize:20,

              fontWeight: FontWeight.bold,

            ),

          ),

          rowItem("EMA", decision.ema),

          rowItem("MACD", decision.macd),

          rowItem("VWAP", decision.vwap),

          rowItem("Open Interest", decision.oi),

          rowItem("Volume", decision.volume),

          rowItem("News Sentiment", decision.news),

          const Divider(),

          Padding(

            padding: const EdgeInsets.all(16),

            child: Text(

              "Confidence ${decision.confidence}%",

              style: const TextStyle(

                fontSize:18,

                fontWeight: FontWeight.bold,

              ),

            ),

          ),

        ],

      ),

    );

  }

}
