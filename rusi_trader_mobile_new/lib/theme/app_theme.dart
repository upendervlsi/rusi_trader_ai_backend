import 'package:flutter/material.dart';

import 'app_colors.dart';

class AppTheme {

  static ThemeData get darkTheme {

    return ThemeData(

      brightness: Brightness.dark,

      scaffoldBackgroundColor: AppColors.background,

      cardColor: AppColors.card,

      useMaterial3: true,

      colorScheme: const ColorScheme.dark(

        primary: AppColors.primary,

        secondary: AppColors.secondary,

      ),

      appBarTheme: const AppBarTheme(

        backgroundColor: AppColors.background,

        centerTitle: true,

        elevation: 0,

      ),

    );

  }

}
