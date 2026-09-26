import 'package:flutter/material.dart';

import '../../models/paper_trading_model.dart';


class PaperTradingSummaryCard
    extends StatelessWidget {

  final PaperTradingModel paperTrading;


  const PaperTradingSummaryCard({

    super.key,

    required this.paperTrading,

  });


  @override
  Widget build(
    BuildContext context,
  ) {

    final bool pnlPositive =
        paperTrading.realizedPnl >= 0;


    final String statusText =
        paperTrading.running
            ? "RUNNING"
            : "STOPPED";


    final String marketText =
        paperTrading.marketOpen
            ? "MARKET OPEN"
            : "MARKET CLOSED";


    return Card(

      child:
          Padding(

        padding:
            const EdgeInsets.all(18),

        child:
            Column(

          crossAxisAlignment:
              CrossAxisAlignment.start,

          children: [

            //==================================================
            // HEADER
            //==================================================

            Row(

              mainAxisAlignment:
                  MainAxisAlignment.spaceBetween,

              children: [

                const Text(

                  "PAPER TRADING",

                  style:
                      TextStyle(

                    fontSize: 18,

                    fontWeight:
                        FontWeight.bold,

                  ),
                ),

                Text(

                  statusText,

                  style:
                      TextStyle(

                    fontWeight:
                        FontWeight.bold,

                    color:
                        paperTrading.running
                            ? Colors.green
                            : Colors.red,

                  ),
                ),
              ],
            ),


            const SizedBox(
              height: 8,
            ),


            Text(
              marketText,

              style:
                  const TextStyle(
                fontSize: 12,
              ),
            ),


            const Divider(),


            //==================================================
            // CAPITAL
            //==================================================

            _row(
              "Capital",

              "₹${paperTrading.capital.toStringAsFixed(2)}",
            ),


            //==================================================
            // AVAILABLE CAPITAL
            //==================================================

            _row(
              "Available",

              "₹${paperTrading.availableCapital.toStringAsFixed(2)}",
            ),


            //==================================================
            // REALIZED P&L
            //==================================================

            _row(

              "Realized P&L",

              "${pnlPositive ? '+' : ''}"
              "₹${paperTrading.realizedPnl.toStringAsFixed(2)}",

              valueColor:
                  pnlPositive
                      ? Colors.green
                      : Colors.red,
            ),


            //==================================================
            // OPEN TRADES
            //==================================================

            _row(
              "Open Trades",

              "${paperTrading.openTrades}",
            ),


            //==================================================
            // CLOSED TRADES
            //==================================================

            _row(
              "Closed Trades",

              "${paperTrading.closedTrades}",
            ),


            //==================================================
            // LAST CYCLE
            //==================================================

            _row(
              "Last Cycle",

              "${paperTrading.lastCycleId}",
            ),
          ],
        ),
      ),
    );
  }


  //============================================================
  // ROW
  //============================================================

  Widget _row(

    String label,

    String value, {

    Color? valueColor,

  }) {

    return Padding(

      padding:
          const EdgeInsets.symmetric(
        vertical: 5,
      ),

      child:
          Row(

        mainAxisAlignment:
            MainAxisAlignment.spaceBetween,

        children: [

          Text(
            label,
          ),

          Text(

            value,

            style:
                TextStyle(

              fontWeight:
                  FontWeight.bold,

              color:
                  valueColor,

            ),
          ),
        ],
      ),
    );
  }
}
