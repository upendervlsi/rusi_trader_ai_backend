/*
============================================================

RUSI Trader AI

REST API Endpoints

============================================================
*/

import '../config/app_config.dart';

class Endpoints {

  Endpoints._();

  static String get baseUrl =>
      AppConfig.baseUrl;

  static const String dashboard =
      "/api/dashboard";

  static const String market =
      "/api/market";

  static const String recommendation =
      "/api/recommendation";

  static const String portfolio =
      "/api/portfolio";

  static const String intelligence =
      "/api/intelligence";

}
