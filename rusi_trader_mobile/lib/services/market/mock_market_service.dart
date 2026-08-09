import '../../models/market_data.dart';

class MockMarketService {

  static List<MarketData> getMarkets() {

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

        change: -85.30,

        percent: -0.15,

        positive: false,

      ),

      MarketData(

        symbol: "CRUDE",

        ltp: 6123,

        change: 32,

        percent: 0.61,

        positive: true,

      ),

      MarketData(

        symbol: "GOLD",

        ltp: 101254,

        change: -152,

        percent: -0.18,

        positive: false,

      ),

    ];

  }

}
