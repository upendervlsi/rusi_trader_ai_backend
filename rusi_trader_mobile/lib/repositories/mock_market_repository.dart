import '../models/market_data.dart';
import 'market_repository.dart';

class MockMarketRepository implements MarketRepository {

  @override
  Future<List<MarketData>> getMarketData() async {

    await Future.delayed(
      const Duration(milliseconds: 500),
    );

    return const [

      MarketData(
        symbol: "NIFTY",
        ltp: 24863.40,
        change: 126.30,
        percent: 0.52,
        positive: true,
      ),

      MarketData(
        symbol: "BANKNIFTY",
        ltp: 56892.30,
        change: -82.60,
        percent: -0.14,
        positive: false,
      ),

      MarketData(
        symbol: "CRUDE",
        ltp: 6124,
        change: 28,
        percent: 0.45,
        positive: true,
      ),

      MarketData(
        symbol: "GOLD",
        ltp: 101250,
        change: -154,
        percent: -0.17,
        positive: false,
      ),

    ];

  }

}
