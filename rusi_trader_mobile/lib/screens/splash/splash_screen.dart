import 'package:flutter/material.dart';

import '../../theme/app_colors.dart';

class SplashScreen extends StatefulWidget {

  const SplashScreen({super.key});

  @override
  State<SplashScreen> createState() => _SplashScreenState();

}

class _SplashScreenState extends State<SplashScreen> {

  @override
  void initState() {

    super.initState();

    Future.delayed(

      const Duration(seconds: 2),

      () {

      },

    );

  }

  @override
  Widget build(BuildContext context) {

    return Scaffold(

      body: Center(

        child: Column(

          mainAxisAlignment: MainAxisAlignment.center,

          children: [

            Icon(

              Icons.auto_graph,

              color: AppColors.primary,

              size: 90,

            ),

            const SizedBox(height: 20),

            const Text(

              "RUSI Trader AI",

              style: TextStyle(

                fontSize: 28,

                fontWeight: FontWeight.bold,

              ),

            ),

            const SizedBox(height: 12),

            const CircularProgressIndicator(),

          ],

        ),

      ),

    );

  }

}
