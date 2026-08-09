import '../models/market_data.dart';
import '../models/market_details_model.dart';
import 'market_repository.dart';

class MockMarketRepository extends MarketRepository {
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

  @override
  Future<MarketDetailsModel> getMarketDetails() async {
    await Future.delayed(
      const Duration(milliseconds: 300),
    );

    return const MarketDetailsModel(
      livePrice: 24863.40,
      latestClose: 24863.40,

      dataStatus: "LIVE",
      marketStatus: "OPEN",

      marketStructure: "BULLISH",

      ema20: 24810.15,
      ema50: 24680.25,

      sma20: 24780.20,
      sma50: 24610.50,

      vwap: 24805.40,

      rsi: 61.25,
      macd: 14.62,
      adx: 28.15,
      atr: 96.40,

      pcr: 1.14,

      openInterest: 2450000,
      changeOi: 142500,

      iv: 12.40,
      maxPain: 24400,

      updatedTime: "09:30:15",
    );
  }
}
