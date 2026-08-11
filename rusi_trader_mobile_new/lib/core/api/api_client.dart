import 'dart:convert';
import 'dart:io';

import 'endpoints.dart';

class ApiClient {
  Future<Map<String, dynamic>> get(
    String url,
  ) async {
    final uri = Uri.parse(
      "${Endpoints.baseUrl}$url",
    );

    print("");
    print("================================================");
    print("API REQUEST");
    print("================================================");
    print("Base URL : ${Endpoints.baseUrl}");
    print("Path     : $url");
    print("Full URL : $uri");
    print("================================================");

    final client = HttpClient();

    client.findProxy = (
      Uri requestUri,
    ) {
      print(
        "PROXY CHECK : DIRECT -> $requestUri",
      );

      return "DIRECT";
    };

    try {
      print(
        "CONNECTING TO : "
        "${uri.host}:${uri.port}",
      );

      final request = await client.getUrl(uri);

      print(
        "REQUEST CREATED : $uri",
      );

      final response = await request.close();

      print(
        "HTTP STATUS : ${response.statusCode}",
      );

      final body = await response
          .transform(
            utf8.decoder,
          )
          .join();

      print(
        "HTTP RESPONSE : $body",
      );

      if (response.statusCode < 200 || response.statusCode >= 300) {
        throw HttpException(
          "HTTP ${response.statusCode}: $body",
          uri: uri,
        );
      }

      final decoded = jsonDecode(body);

      if (decoded is! Map<String, dynamic>) {
        throw FormatException(
          "Expected JSON object from API.",
        );
      }

      print(
        "API SUCCESS : $url",
      );

      return decoded;
    } catch (e, stackTrace) {
      print("");
      print("================================================");
      print("API REQUEST FAILED");
      print("================================================");
      print("Base URL : ${Endpoints.baseUrl}");
      print("Path     : $url");
      print("Full URL : $uri");
      print("Host     : ${uri.host}");
      print("Port     : ${uri.port}");
      print("Error    : $e");
      print("================================================");

      print(stackTrace);

      rethrow;
    } finally {
      client.close(
        force: true,
      );
    }
  }
}
