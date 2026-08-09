import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../repositories/mock_market_repository.dart';
import '../repositories/market_repository.dart';

final marketRepositoryProvider =
    Provider<MarketRepository>((ref) {

  return MockMarketRepository();

});
