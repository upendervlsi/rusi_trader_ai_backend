import 'package:flutter/material.dart';

import '../../widgets/cards/market_status_card.dart';
import '../../widgets/cards/ai_recommendation_card.dart';
import '../../widgets/cards/portfolio_summary_card.dart';

class DashboardScreen extends StatelessWidget {

  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context) {

    return Scaffold(

      appBar: AppBar(

        title: const Text("RUSI Trader AI"),

        actions: const [

          Padding(

            padding: EdgeInsets.only(right:16),

            child: Icon(Icons.notifications_none),

          )

        ],

      ),

      body: ListView(

        padding: const EdgeInsets.all(16),

        children: const [

          MarketStatusCard(),

          SizedBox(height:18),

          AIRecommendationCard(

            symbol:"NIFTY",

            signal:"BUY",

            confidence:96,

            entry:"132.4",

            stopLoss:"101",

            target:"194",

          ),

          SizedBox(height:18),

          PortfolioSummaryCard(

            todaysPnL:"+₹4,250",

            totalPnL:"+₹38,740",

            openPositions:3,

          ),

        ],

      ),

    );

  }

}
