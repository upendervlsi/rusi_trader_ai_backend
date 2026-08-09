import 'package:flutter/material.dart';

class MarketStatusCard extends StatelessWidget {

  const MarketStatusCard({super.key});

  @override
  Widget build(BuildContext context) {

    return Card(

      child: ListTile(

        leading: const Icon(

          Icons.circle,

          color: Colors.green,

        ),

        title: const Text(

          "Market Open",

        ),

        subtitle: const Text(

          "NSE • MCX Connected",

        ),

        trailing: const Icon(

          Icons.wifi,

          color: Colors.green,

        ),

      ),

    );

  }

}
