import 'package:flutter/material.dart';

import '../screens/home/home_screen.dart';

class BottomNavigation extends StatefulWidget {
  const BottomNavigation({super.key});

  @override
  State<BottomNavigation> createState() =>
      _BottomNavigationState();
}

class _BottomNavigationState
    extends State<BottomNavigation> {

  int selectedIndex = 0;

  final List<Widget> pages = [

    const HomeScreen(),

    const Center(
      child: Text("Markets"),
    ),

    const Center(
      child: Text("AI Center"),
    ),

    const Center(
      child: Text("Portfolio"),
    ),

    const Center(
      child: Text("Settings"),
    ),

  ];

  @override
  Widget build(BuildContext context) {

    return Scaffold(

      body: pages[selectedIndex],

      bottomNavigationBar: NavigationBar(

        selectedIndex: selectedIndex,

        onDestinationSelected: (value) {

          setState(() {

            selectedIndex = value;

          });

        },

        destinations: const [

          NavigationDestination(

            icon: Icon(Icons.dashboard_outlined),

            selectedIcon: Icon(Icons.dashboard),

            label: "Home",

          ),

          NavigationDestination(

            icon: Icon(Icons.candlestick_chart),

            label: "Markets",

          ),

          NavigationDestination(

            icon: Icon(Icons.auto_graph),

            label: "AI",

          ),

          NavigationDestination(

            icon: Icon(Icons.account_balance_wallet),

            label: "Portfolio",

          ),

          NavigationDestination(

            icon: Icon(Icons.settings),

            label: "Settings",

          ),

        ],

      ),

    );

  }

}
