/*
============================================================
RUSI Trader AI

Market Screen

Displays complete market information to the user.

============================================================
*/

import 'package:flutter/material.dart';

import '../../viewmodels/market_view_model.dart';

import '../../widgets/cards/market_summary_card.dart';

import '../../widgets/market/ai_market_decision_card.dart';
import '../../widgets/market/market_health_card.dart';
import '../../widgets/market/moving_average_card.dart';
import '../../widgets/market/momentum_card.dart';
import '../../widgets/market/option_analytics_card.dart';

class MarketScreen extends StatefulWidget {
  const MarketScreen({super.key});

  @override
  State<MarketScreen> createState() =>
      _MarketScreenState();
}

class _MarketScreenState extends State<MarketScreen> {
  final MarketViewModel vm =
      MarketViewModel();

  @override
  void initState() {
    super.initState();

    vm.load();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: vm,
      builder: (context, _) {

        //--------------------------------------------------
        // Loading
        //--------------------------------------------------

        if (vm.loading) {
          return const Center(
            child: CircularProgressIndicator(),
          );
        }

        //--------------------------------------------------
        // Error
        //--------------------------------------------------

        if (vm.error != null) {
          return Center(
            child: Text(vm.error!),
          );
        }

        //--------------------------------------------------
        // Safety
        //--------------------------------------------------

        if (vm.market == null ||
            vm.recommendation == null) {
          return const Center(
            child: Text(
              "Market data unavailable",
            ),
          );
        }

        final market = vm.market!;
        final ai = vm.recommendation!;

        return RefreshIndicator(
          onRefresh: vm.refresh,

          child: ListView(
            padding: const EdgeInsets.all(20),

            children: [

              //--------------------------------------------------
              // Market Summary
              //--------------------------------------------------

              MarketSummaryCard(
                status:
                    market.marketStatus,

                // IMPORTANT:
                // Display the real-time LTP received
                // from Angel One through the backend.
                price:
                    market.livePrice,

                structure:
                    market.marketStructure,
              ),

              const SizedBox(height: 20),

              //--------------------------------------------------
              // AI Decision
              //--------------------------------------------------

              AiMarketDecisionCard(
                recommendation:
                    ai.recommendation,

                confidence:
                    ai.confidence,

                score:
                    ai.score,

                optionSymbol:
                    ai.optionSymbol,

                entryPrice:
                    ai.entryPrice,

                stopLoss:
                    ai.stopLoss,

                targetPrice:
                    ai.targetPrice,
              ),

              const SizedBox(height: 20),

              //--------------------------------------------------
              // Market Health
              //--------------------------------------------------

              MarketHealthCard(
                trend:
                    market.marketStructure,

                strength:
                    market.rsi,

                volatility:
                    market.atr,

                momentum:
                    market.macd,
              ),

              const SizedBox(height: 20),

              //--------------------------------------------------
              // Moving Average
              //--------------------------------------------------

              MovingAverageCard(
                sma20:
                    market.sma20,

                sma50:
                    market.sma50,

                ema20:
                    market.ema20,

                ema50:
                    market.ema50,

                vwap:
                    market.vwap,
              ),

              const SizedBox(height: 20),

              //--------------------------------------------------
              // Momentum
              //--------------------------------------------------

              MomentumCard(
                rsi:
                    market.rsi,

                macd:
                    market.macd,

                adx:
                    market.adx,

                atr:
                    market.atr,
              ),

              const SizedBox(height: 20),

              //--------------------------------------------------
              // Options
              //--------------------------------------------------

              OptionAnalyticsCard(
                pcr:
                    market.pcr,

                openInterest:
                    market.openInterest,

                changeOi:
                    market.changeOi,

                iv:
                    market.iv,

                maxPain:
                    market.maxPain,
              ),

              const SizedBox(height: 30),
            ],
          ),
        );
      },
    );
  }
}
