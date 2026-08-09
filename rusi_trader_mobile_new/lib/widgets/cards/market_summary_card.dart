import 'package:flutter/material.dart';

import '../common/base_card.dart';
import '../common/metric_row.dart';
import '../common/status_chip.dart';

class MarketSummaryCard extends StatelessWidget {

  final String status;

  final String? symbol;

  final String? exchange;

  final double? price;

  final String structure;

  const MarketSummaryCard({

    super.key,

    required this.status,

    this.symbol,

    this.exchange,

    required this.price,

    required this.structure,
  });

  Color _statusColor() {

    switch (status.toUpperCase()) {

      case "OPEN":
        return Colors.green;

      case "CLOSED":
        return Colors.red;

      default:
        return Colors.orange;
    }
  }

  @override
  Widget build(
    BuildContext context,
  ) {

    return BaseCard(

      title: "Market Summary",

      icon: Icons.show_chart,

      child: Column(

        crossAxisAlignment:
            CrossAxisAlignment.start,

        children: [

          Align(

            alignment:
                Alignment.centerLeft,

            child: StatusChip(

              text: status,

              color: _statusColor(),
            ),
          ),

          const SizedBox(height: 20),

          // -------------------------------------------------
          // Instrument
          // -------------------------------------------------

          if (symbol != null &&
              symbol!.isNotEmpty) ...[

            MetricRow(

              label: "Instrument",

              value: symbol!,

              icon: Icons.show_chart,
            ),
          ],

          // -------------------------------------------------
          // Exchange
          // -------------------------------------------------

          if (exchange != null &&
              exchange!.isNotEmpty) ...[

            MetricRow(

              label: "Exchange",

              value: exchange!,

              icon: Icons.account_balance,
            ),
          ],

          // -------------------------------------------------
          // Price
          // -------------------------------------------------

          MetricRow(

            label: "Price",

            value:
                price?.toStringAsFixed(2) ??
                "--",

            icon: Icons.trending_up,
          ),

          // -------------------------------------------------
          // Market Structure
          // -------------------------------------------------

          MetricRow(

            label: "Structure",

            value: structure,

            icon:
                Icons.account_tree_outlined,
          ),
        ],
      ),
    );
  }
}
