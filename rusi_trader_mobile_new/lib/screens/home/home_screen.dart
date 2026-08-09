import 'package:flutter/material.dart';

import '../../viewmodels/home_view_model.dart';

import '../../widgets/layout/dashboard_grid.dart';

import '../../widgets/cards/market_summary_card.dart';
import '../../widgets/cards/ai_summary_card.dart';
import '../../widgets/cards/portfolio_summary_card.dart';
import '../../widgets/cards/trading_status_card.dart';
import '../../widgets/cards/live_market_card.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() =>
      _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final HomeViewModel vm = HomeViewModel();

  @override
  void initState() {
    super.initState();

    vm.load();

    vm.startLiveRefresh();
  }

  @override
  void dispose() {

    vm.dispose();

    super.dispose();
  }
  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: vm,
      builder: (context, _) {
        if (vm.loading) {
          return const Center(
            child: CircularProgressIndicator(),
          );
        }

        if (vm.error != null) {
          return Center(
            child: Text(vm.error!),
          );
        }

        final dashboard = vm.dashboard!;
        final market = vm.market!;
        final recommendation = vm.recommendation!;
        final portfolio = vm.portfolio!;

        return Padding(
          padding: const EdgeInsets.all(20),
          child: DashboardGrid(
            children: [

              //====================================================
              // Market Summary
              //====================================================

              MarketSummaryCard(
                status: dashboard.marketStatus,
                symbol: dashboard.marketSymbol,
                exchange: dashboard.marketExchange,
                price: market.livePrice,
                structure: market.marketStructure,
              ),

              //====================================================
              // AI Decision
              //====================================================

              AiSummaryCard(
                decision: recommendation.recommendation,
                confidence: recommendation.confidence,
                score: recommendation.score,
                optionType: recommendation.optionSymbol,
                marketStatus: dashboard.marketStatus,
              ),

              //====================================================
              // Portfolio
              //====================================================

              PortfolioSummaryCard(
                openPositions: portfolio.openPositions,
                investedAmount: portfolio.investedAmount,
                marketValue: portfolio.marketValue,
                unrealizedPnl: portfolio.unrealizedPnl,
              ),

              //====================================================
              // Trading Status
              //====================================================

              TradingStatusCard(
                broker: "Angel One",
                marketStatus: dashboard.marketStatus,
                autoTrading: false,
                backendConnected: true,
                todayTrades: portfolio.openPositions,
              ),

              //====================================================
              // Live Market
              //====================================================

              LiveMarketCard(
                symbol: dashboard.marketSymbol,
                exchange: dashboard.marketExchange,
                price: market.livePrice,
                sma20: market.sma20,
                sma50: market.sma50,
                ema20: market.ema20,
                ema50: market.ema50,
              ),
            ],
          ),
        );
      },
    );
  }
}
