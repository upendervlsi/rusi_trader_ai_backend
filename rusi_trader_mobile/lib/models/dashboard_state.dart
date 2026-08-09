import 'market_data.dart';
import 'ai_decision.dart';

class DashboardState {

  final List<MarketData> markets;

  final AIDecision decision;

  final bool loading;

  final String? error;

  const DashboardState({

    required this.markets,

    required this.decision,

    required this.loading,

    this.error,

  });

}
