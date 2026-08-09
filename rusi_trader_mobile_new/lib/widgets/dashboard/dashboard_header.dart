import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

class DashboardHeader extends StatelessWidget {
  const DashboardHeader({
    super.key,
    required this.marketStatus,
    required this.lastUpdated,
  });

  final String marketStatus;
  final DateTime lastUpdated;

  @override
  Widget build(BuildContext context) {
    final now = DateFormat(
      "EEEE, dd MMM yyyy",
    ).format(lastUpdated);

    final time = DateFormat(
      "HH:mm:ss",
    ).format(lastUpdated);

    return Container(
      padding: const EdgeInsets.all(24),

      decoration: BoxDecoration(
        color: const Color(0xff161B22),

        borderRadius:
            BorderRadius.circular(18),
      ),

      child: Row(
        children: [

          const Expanded(
            child: Column(
              crossAxisAlignment:
                  CrossAxisAlignment.start,
              children: [

                Text(
                  "RUSI Trader AI Dashboard",
                  style: TextStyle(
                    fontSize: 26,
                    fontWeight: FontWeight.bold,
                  ),
                ),

                SizedBox(height: 8),
              ],
            ),
          ),

          Column(
            crossAxisAlignment:
                CrossAxisAlignment.end,
            children: [

              Text(now),

              const SizedBox(height: 8),

              Row(
                children: [

                  const Icon(
                    Icons.circle,
                    color: Colors.green,
                    size: 10,
                  ),

                  const SizedBox(width: 6),

                  Text(
                    marketStatus,
                    style: const TextStyle(
                      color: Colors.green,
                      fontWeight:
                          FontWeight.bold,
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 8),

              Text(
                "Updated : $time",
              ),
            ],
          ),
        ],
      ),
    );
  }
}
