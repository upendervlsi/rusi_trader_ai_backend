import 'package:flutter/material.dart';

import '../../models/market_data.dart';

class LiveMarketCard extends StatelessWidget {

  final MarketData market;

  const LiveMarketCard({

    super.key,

    required this.market,

  });

  @override
  Widget build(BuildContext context) {

    return Card(

      child: ListTile(

        leading: CircleAvatar(

          child: Text(

            market.symbol.substring(0,1),

          ),

        ),

        title: Text(

          market.symbol,

        ),

        subtitle: Text(

          market.ltp.toString(),

        ),

        trailing: Column(

          mainAxisAlignment: MainAxisAlignment.center,

          children: [

            Text(

              market.change.toString(),

              style: TextStyle(

                color: market.positive

                    ? Colors.green
                    : Colors.red,

              ),

            ),

            Text(

              "${market.percent}%",

            ),

          ],

        ),

      ),

    );

  }

}
