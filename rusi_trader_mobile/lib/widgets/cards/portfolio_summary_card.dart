import 'package:flutter/material.dart';

class PortfolioSummaryCard extends StatelessWidget {
  final String todaysPnL;
  final String totalPnL;
  final int openPositions;

  const PortfolioSummaryCard({
    super.key,
    required this.todaysPnL,
    required this.totalPnL,
    required this.openPositions,
  });

  Widget _item(String title, String value) {
    return Expanded(
      child: Column(
        children: [
          Text(
            title,
            style: const TextStyle(fontSize: 13),
          ),
          const SizedBox(height: 8),
          Text(
            value,
            style: const TextStyle(
              fontWeight: FontWeight.bold,
              fontSize: 18,
            ),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: Row(
          children: [
            _item("Today's P&L", todaysPnL),
            _item("Total P&L", totalPnL),
            _item("Positions", openPositions.toString()),
          ],
        ),
      ),
    );
  }
}
