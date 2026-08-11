/*
============================================================

RUSI Trader AI

Application Configuration

============================================================
*/

import 'dart:io';

class AppConfig {

  AppConfig._();

  //==========================================================
  // WINDOWS PC LAN IP
  //
  // Used when Flutter runs on a physical Android device.
  //==========================================================

  static const String serverIp =
      "16.113.87.242";

  static const int serverPort = 8000;

  //==========================================================
  // BASE URL
  //==========================================================

  static String get baseUrl {

    // -------------------------------------------------------
    // Flutter Linux desktop
    //
    // Backend is running in the same WSL environment.
    // -------------------------------------------------------

    if (Platform.isLinux) {

      return "http://$serverIp:$serverPort";

    }

    // -------------------------------------------------------
    // Flutter Windows desktop
    // -------------------------------------------------------

    if (Platform.isWindows) {

      return "http://localhost:$serverPort";

    }

    // -------------------------------------------------------
    // Android / physical device
    //
    // Use Windows PC LAN IP.
    // -------------------------------------------------------

    if (Platform.isAndroid) {

      return "http://$serverIp:$serverPort";

    }

    // -------------------------------------------------------
    // macOS / iOS development fallback
    // -------------------------------------------------------

    return "http://$serverIp:$serverPort";
  }

  //==========================================================
  // TIMEOUT
  //==========================================================

  static const Duration apiTimeout =
      Duration(
        seconds: 30,
      );
}
