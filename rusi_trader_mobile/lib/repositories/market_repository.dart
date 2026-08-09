import '../models/market_data.dart';

abstract class MarketRepository {

  Future<List<MarketData>> getMarketData();

}
