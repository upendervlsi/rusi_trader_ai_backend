import 'package:flutter/material.dart';

import 'navigation/app_router.dart';
import 'theme/app_theme.dart';

class RusiTraderApp extends StatelessWidget {

  const RusiTraderApp({super.key});

  @override
  Widget build(BuildContext context) {

    return MaterialApp.router(

      title: "RUSI Trader AI",

      debugShowCheckedModeBanner: false,

      theme: AppTheme.darkTheme,

      routerConfig: AppRouter.router,

    );

  }

}
