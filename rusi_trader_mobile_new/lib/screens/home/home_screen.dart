import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../viewmodels/home_view_model.dart';

import '../../models/market_pulse_model.dart';

import '../../widgets/layout/dashboard_grid.dart';

import '../../widgets/dashboard/market_pulse_card.dart';

import '../../widgets/cards/market_summary_card.dart';
import '../../widgets/cards/ai_summary_card.dart';
import '../../widgets/cards/portfolio_summary_card.dart';
import '../../widgets/cards/trading_status_card.dart';
import '../../widgets/cards/live_market_card.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({
    super.key,
  });

  @override
  State<HomeScreen> createState() =>
      _HomeScreenState();
}

class _HomeScreenState
    extends State<HomeScreen> {

  final HomeViewModel vm =
      HomeViewModel();

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

  //============================================================
  // OPEN MARKET
  //============================================================

  void _openMarket(
    MarketPulseModel market,
  ) {
    //
    // Pass the logical market identifier
    // to the Market screen.
    //
    // Example:
    //
    // NIFTY_FNO
    // BANKNIFTY_FNO
    // SENSEX_FNO
    //
    context.push(
      "/market",
      extra: market.market,
    );
  }

  //============================================================
  // BUILD
  //============================================================

  @override
  Widget build(
    BuildContext context,
  ) {
    return AnimatedBuilder(
      animation: vm,

      builder: (
        context,
        _,
      ) {
        //======================================================
        // INITIAL LOADING
        //======================================================

        if (vm.loading &&
            vm.dashboard == null) {
          return const Center(
            child:
                CircularProgressIndicator(),
          );
        }

        //======================================================
        // ERROR
        //======================================================

        if (vm.error != null &&
            vm.dashboard == null) {
          return Center(
            child:
                Text(vm.error!),
          );
        }

        //======================================================
        // DATA
        //======================================================

        final dashboard =
            vm.dashboard!;

        final market =
            vm.market;

        final recommendation =
            vm.recommendation;

        final portfolio =
            vm.portfolio;

        //======================================================
        // DASHBOARD
        //======================================================

        return RefreshIndicator(
          onRefresh:
              vm.refresh,

          child:
              SingleChildScrollView(
            physics:
                const AlwaysScrollableScrollPhysics(),

            child:
                Padding(
              padding:
                  const EdgeInsets.all(20),

              child:
                  DashboardGrid(
                children: [

                  //================================================
                  // MARKET PULSE
                  //
                  // Complete market-wide view:
                  //
                  // NIFTY
                  // BANKNIFTY
                  // FINNIFTY
                  // MIDCAP NIFTY
                  // SENSEX
                  // BANKEX
                  // CRUDE OIL
                  //
                  //================================================

                  MarketPulseCard(
                    markets:
                        dashboard.marketPulse,

                    strongestMarket:
                        dashboard
                            .strongestMarket,

                    strongestConfidence:
                        dashboard
                            .strongestConfidence,

                    onMarketTap:
                        _openMarket,
                  ),

                  //================================================
                  // MARKET SUMMARY
                  //================================================

                  if (market != null)
                    MarketSummaryCard(
                      status:
                          dashboard
                              .marketStatus,

                      symbol:
                          dashboard
                              .marketSymbol,

                      exchange:
                          dashboard
                              .marketExchange,

                      price:
                          market.livePrice,

                      structure:
                          market
                              .marketStructure,
                    ),

                  //================================================
                  // AI DECISION
                  //================================================

                  if (recommendation != null)
                    AiSummaryCard(
                      decision:
                          recommendation
                              .recommendation,

                      confidence:
                          recommendation
                              .confidence,

                      score:
                          recommendation
                              .score,

                      optionType:
                          recommendation
                              .optionSymbol,

                      marketStatus:
                          dashboard
                              .marketStatus,
                    ),

                  //================================================
                  // PORTFOLIO
                  //================================================

                  if (portfolio != null)
                    PortfolioSummaryCard(
                      openPositions:
                          portfolio
                              .openPositions,

                      investedAmount:
                          portfolio
                              .investedAmount,

                      marketValue:
                          portfolio
                              .marketValue,

                      unrealizedPnl:
                          portfolio
                              .unrealizedPnl,
                    ),

                  //================================================
                  // TRADING STATUS
                  //================================================

                  if (portfolio != null)
                    TradingStatusCard(
                      broker:
                          "Angel One",

                      marketStatus:
                          dashboard
                              .marketStatus,

                      autoTrading:
                          false,

                      backendConnected:
                          true,

                      todayTrades:
                          portfolio
                              .openPositions,
                    ),

                  //================================================
                  // LIVE MARKET
                  //================================================

                  if (market != null)
                    LiveMarketCard(
                      symbol:
                          dashboard
                              .marketSymbol,

                      exchange:
                          dashboard
                              .marketExchange,

                      price:
                          market.livePrice,

                      sma20:
                          market.sma20,

                      sma50:
                          market.sma50,

                      ema20:
                          market.ema20,

                      ema50:
                          market.ema50,
                    ),
                ],
              ),
            ),
          ),
        );
      },
    );
  }
}
