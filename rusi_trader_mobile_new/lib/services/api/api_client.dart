import 'package:dio/dio.dart';

import '../../core/config/app_config.dart';

class ApiClient {

  late final Dio dio;

  ApiClient() {

    dio = Dio(

      BaseOptions(

        baseUrl: AppConfig.baseUrl,

        connectTimeout: AppConfig.apiTimeout,

        receiveTimeout: AppConfig.apiTimeout,

        headers: {

          "Content-Type": "application/json",

        },

      ),

    );

  }

}
