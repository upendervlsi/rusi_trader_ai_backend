import 'dart:convert';
import 'dart:io';

void main() async {
  const url = "http://localhost:8000/api/market";

  print("");
  print("================================================");
  print("RUSI TRADER AI - BACKEND CONNECTION TEST");
  print("================================================");
  print("URL : $url");
  print("");

  final client = HttpClient();

  try {
    final request = await client.getUrl(
      Uri.parse(url),
    );

    print("REQUEST CREATED");

    final response = await request.close();

    print("HTTP STATUS : ${response.statusCode}");

    final body = await response
        .transform(utf8.decoder)
        .join();

    print("");
    print("RESPONSE:");
    print(body);

    if (response.statusCode != 200) {
      print("");
      print("RESULT : FAILED");
      exitCode = 1;
      return;
    }

    final json = jsonDecode(body);

    print("");
    print("========== LIVE DATA CHECK ==========");

    print(
      "Data Status : ${json["data_status"]}",
    );

    print(
      "Live Price  : ${json["live_price"]}",
    );

    print(
      "Latest Close: ${json["latest_close"]}",
    );

    print("");

    if (json["data_status"] == "LIVE" &&
        json["live_price"] != null) {
      print("RESULT : BACKEND LIVE DATA VERIFIED");
    } else {
      print(
        "RESULT : BACKEND RESPONDED "
        "BUT LIVE DATA NOT VERIFIED",
      );
      exitCode = 1;
    }
  } catch (e, stackTrace) {
    print("");
    print("RESULT : CONNECTION FAILED");
    print("ERROR  : $e");
    print("");
    print(stackTrace);
    exitCode = 1;
  } finally {
    client.close(force: true);
  }
}
