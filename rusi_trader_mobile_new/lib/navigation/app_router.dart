import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../shell/application_shell.dart';

import '../screens/splash/splash_screen.dart';

import '../screens/home/home_screen.dart';
import '../screens/market/market_screen.dart';
import '../screens/ai/ai_screen.dart';
import '../screens/trading/trading_screen.dart';
import '../screens/portfolio/portfolio_screen.dart';
import '../screens/scanner/scanner_screen.dart';
import '../screens/news/news_screen.dart';
import '../screens/intelligence/intelligence_screen.dart';
import '../screens/analytics/analytics_screen.dart';
import '../screens/monitor/monitor_screen.dart';
import '../screens/settings/settings_screen.dart';

import 'route_names.dart';

class AppRouter {
  static final router = GoRouter(
    initialLocation: RouteNames.splash,

    routes: [

      GoRoute(
        path: RouteNames.splash,
        builder: (context, state) => const SplashScreen(),
      ),

      ShellRoute(

        builder: (context, state, child) {

          return ApplicationShell(
            child: child,
          );

        },

        routes: [

          GoRoute(
            path: RouteNames.home,
            builder: (context, state) =>
                const HomeScreen(),
          ),

          GoRoute(
            path: RouteNames.market,
            builder: (context, state) =>
                const MarketScreen(),
          ),

          GoRoute(
            path: RouteNames.ai,
            builder: (context, state) =>
                const AiScreen(),
          ),

          GoRoute(
            path: RouteNames.trading,
            builder: (context, state) =>
                const TradingScreen(),
          ),

          GoRoute(
            path: RouteNames.portfolio,
            builder: (context, state) =>
                const PortfolioScreen(),
          ),

          GoRoute(
            path: RouteNames.scanner,
            builder: (context, state) =>
                const ScannerScreen(),
          ),

          GoRoute(
            path: RouteNames.news,
            builder: (context, state) =>
                const NewsScreen(),
          ),

          GoRoute(
            path: RouteNames.intelligence,
            builder: (context, state) =>
                const IntelligenceScreen(),
          ),

          GoRoute(
            path: RouteNames.analytics,
            builder: (context, state) =>
                const AnalyticsScreen(),
          ),

          GoRoute(
            path: RouteNames.monitor,
            builder: (context, state) =>
                const MonitorScreen(),
          ),

          GoRoute(
            path: RouteNames.settings,
            builder: (context, state) =>
                const SettingsScreen(),
          ),

        ],

      ),

    ],

  );
}
