import 'package:flutter/material.dart';

class TradingStatusCard extends StatelessWidget {
  final String broker;
  final String marketStatus;
  final bool autoTrading;
  final bool backendConnected;
  final int todayTrades;

  const TradingStatusCard({
    super.key,
    required this.broker,
    required this.marketStatus,
    required this.autoTrading,
    required this.backendConnected,
    required this.todayTrades,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      color: const Color(0xff151515),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(18),
      ),
      child: Padding(
        padding: const EdgeInsets.all(22),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Row(
              children: [
                Icon(
                  Icons.candlestick_chart,
                  color: Colors.orange,
                ),
                SizedBox(width: 8),
                Text(
                  "Trading Status",
                  style: TextStyle(
                    fontSize: 22,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),

            const SizedBox(height: 22),

            _row("Broker", broker),

            const SizedBox(height: 14),

            _row("Market", marketStatus),

            const SizedBox(height: 14),

            _row(
              "Auto Trade",
              autoTrading ? "ON" : "OFF",
              autoTrading ? Colors.green : Colors.orange,
            ),

            const SizedBox(height: 14),

            _row(
              "Backend",
              backendConnected
                  ? "Connected"
                  : "Disconnected",
              backendConnected
                  ? Colors.green
                  : Colors.red,
            ),

            const SizedBox(height: 14),

            _row(
              "Today's Trades",
              todayTrades.toString(),
            ),
          ],
        ),
      ),
    );
  }

  Widget _row(
    String title,
    String value, [
    Color? color,
  ]) {
    return Row(
      mainAxisAlignment:
          MainAxisAlignment.spaceBetween,
      children: [
        Text(title),
        Text(
          value,
          style: TextStyle(
            color: color,
            fontWeight: FontWeight.bold,
          ),
        ),
      ],
    );
  }
}
