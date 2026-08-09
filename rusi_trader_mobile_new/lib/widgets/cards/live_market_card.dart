import 'package:flutter/material.dart';

class LiveMarketCard extends StatelessWidget {

  final String symbol;

  final String exchange;

  final double price;

  final double sma20;

  final double sma50;

  final double ema20;

  final double ema50;

  const LiveMarketCard({

    super.key,

    required this.symbol,

    required this.exchange,

    required this.price,

    required this.sma20,

    required this.sma50,

    required this.ema20,

    required this.ema50,
  });

  Widget row(
    String name,
    String value,
  ) {

    return Padding(

      padding:
          const EdgeInsets.symmetric(
        vertical: 6,
      ),

      child: Row(

        mainAxisAlignment:
            MainAxisAlignment.spaceBetween,

        children: [

          Text(name),

          Text(

            value,

            style:
                const TextStyle(
              fontWeight:
                  FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(
    BuildContext context,
  ) {

    return Card(

      color:
          const Color(0xff151515),

      shape:
          RoundedRectangleBorder(
        borderRadius:
            BorderRadius.circular(18),
      ),

      child: Padding(

        padding:
            const EdgeInsets.all(20),

        child: Column(

          crossAxisAlignment:
              CrossAxisAlignment.start,

          children: [

            const Row(

              children: [

                Icon(
                  Icons.show_chart,
                  color: Colors.green,
                ),

                SizedBox(width: 8),

                Text(
                  "Live Market",
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight:
                        FontWeight.bold,
                  ),
                ),
              ],
            ),

            const SizedBox(height: 20),

            row(
              "Instrument",
              symbol,
            ),

            row(
              "Exchange",
              exchange,
            ),

            row(
              "Price",
              price.toStringAsFixed(2),
            ),

            row(
              "SMA20",
              sma20.toStringAsFixed(2),
            ),

            row(
              "SMA50",
              sma50.toStringAsFixed(2),
            ),

            row(
              "EMA20",
              ema20.toStringAsFixed(2),
            ),

            row(
              "EMA50",
              ema50.toStringAsFixed(2),
            ),
          ],
        ),
      ),
    );
  }
}
