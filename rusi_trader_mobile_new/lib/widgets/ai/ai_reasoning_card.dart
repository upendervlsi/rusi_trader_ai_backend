/*
============================================================

RUSI Trader AI

Professional AI Reasoning Card

============================================================
*/

import 'package:flutter/material.dart';

class AIReasoningCard extends StatelessWidget {
  final List<String> reasons;

  const AIReasoningCard({
    super.key,
    required this.reasons,
  });

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
      child: ExpansionTile(
        initiallyExpanded: true,

        leading: const Icon(
          Icons.psychology,
          size: 30,
        ),

        title: const Text(
          "AI Reasoning",
          style: TextStyle(
            fontWeight: FontWeight.bold,
            fontSize: 20,
          ),
        ),

        subtitle: Text(
          "${reasons.length} Analysis Points",
        ),

        children: [

          const Divider(),

          ...reasons.map(
            (reason) {

              return _ReasonTile(
                reason: reason,
              );

            },
          ),

          const SizedBox(
            height: 10,
          ),

        ],
      ),
    );
  }
}
class _ReasonTile extends StatelessWidget {
  final String reason;

  const _ReasonTile({
    required this.reason,
  });

  @override
  Widget build(
    BuildContext context,
  ) {

    final lower =
        reason.toLowerCase();

    IconData icon;

    Color color;

    if (lower.contains("bullish") ||
        lower.contains("above") ||
        lower.contains("healthy") ||
        lower.contains("strong")) {

      icon = Icons.trending_up;

      color = Colors.green;

    } else if (lower.contains("bearish") ||
        lower.contains("below") ||
        lower.contains("blocked") ||
        lower.contains("weak")) {

      icon = Icons.trending_down;

      color = Colors.red;

    } else {

      icon = Icons.info_outline;

      color = Colors.orange;

    }

    return ListTile(

      dense: true,

      leading: CircleAvatar(
        radius: 18,
        backgroundColor:
            color.withAlpha(35),
        child: Icon(
          icon,
          color: color,
          size: 18,
        ),
      ),

      title: Text(
        reason,
        style: const TextStyle(
          fontSize: 15,
        ),
      ),

    );
  }
}
