/*
============================================================

RUSI Trader AI

Professional Trade Plan Card

============================================================
*/

import 'package:flutter/material.dart';

import '../../models/trade_plan_model.dart';

class TradePlanCard extends StatelessWidget {
  final TradePlanModel trade;

  const TradePlanCard({
    super.key,
    required this.trade,
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
      child: Padding(
        padding:
            const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment:
              CrossAxisAlignment.start,
          children: [

            //------------------------------------------------
            // Header
            //------------------------------------------------

            const Row(
              children: [

                Icon(
                  Icons.analytics,
                  size: 28,
                ),

                SizedBox(
                  width: 10,
                ),

                Text(
                  "Trade Plan",
                  style: TextStyle(
                    fontSize: 22,
                    fontWeight:
                        FontWeight.bold,
                  ),
                ),

              ],
            ),

            const Divider(
              height: 30,
            ),
            _buildRow(
              Icons.login,
              "Entry Price",
              trade.entryPrice
                  .toStringAsFixed(2),
            ),

            _buildRow(
              Icons.stop_circle,
              "Stop Loss",
              trade.stopLoss
                  .toStringAsFixed(2),
            ),

            _buildRow(
              Icons.flag,
              "Target 1",
              trade.target1
                  .toStringAsFixed(2),
            ),

            _buildRow(
              Icons.flag_outlined,
              "Target 2",
              trade.target2
                  .toStringAsFixed(2),
            ),

            _buildRow(
              Icons.balance,
              "Risk / Reward",
              trade.riskReward,
            ),

            _buildRow(
              Icons.account_balance_wallet,
              "Position Size",
              trade.positionSize,
            ),

            _buildRow(
              Icons.schedule,
              "Holding Type",
              trade.holdingType,
            ),

          ],
        ),
      ),
    );
  }

  //--------------------------------------------------
  // Information Row
  //--------------------------------------------------

  Widget _buildRow(
    IconData icon,
    String title,
    String value,
  ) {
    return Padding(
      padding:
          const EdgeInsets.symmetric(
        vertical: 6,
      ),
      child: Row(
        children: [

          Icon(
            icon,
            size: 20,
            color: Colors.blueGrey,
          ),

          const SizedBox(
            width: 12,
          ),

          Expanded(
            child: Text(
              title,
              style: const TextStyle(
                fontSize: 15,
              ),
            ),
          ),

          Text(
            value,
            style: const TextStyle(
              fontWeight:
                  FontWeight.bold,
              fontSize: 16,
            ),
          ),

        ],
      ),
    );
  }
}
