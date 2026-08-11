import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

class NavigationItem {
  final String title;
  final IconData icon;
  final String route;

  const NavigationItem({
    required this.title,
    required this.icon,
    required this.route,
  });
}

class ApplicationShell extends StatelessWidget {
  final Widget child;

  const ApplicationShell({
    super.key,
    required this.child,
  });

  static const List<NavigationItem> _items = [
    NavigationItem(title: "Home", icon: Icons.home_rounded, route: "/home"),
    NavigationItem(title: "Market", icon: Icons.show_chart, route: "/market"),
    NavigationItem(title: "AI Decision", icon: Icons.psychology, route: "/ai"),
    NavigationItem(
        title: "Trading", icon: Icons.candlestick_chart, route: "/trading"),
    NavigationItem(
        title: "Portfolio",
        icon: Icons.account_balance_wallet,
        route: "/portfolio"),
    NavigationItem(title: "Scanner", icon: Icons.radar, route: "/scanner"),
    NavigationItem(title: "News", icon: Icons.newspaper, route: "/news"),
    NavigationItem(
        title: "Intelligence", icon: Icons.memory, route: "/intelligence"),
    NavigationItem(
        title: "Analytics", icon: Icons.analytics, route: "/analytics"),
    NavigationItem(
        title: "Monitor", icon: Icons.monitor_heart, route: "/monitor"),
    NavigationItem(title: "Settings", icon: Icons.settings, route: "/settings"),
  ];

  static const List<String> _mobileRoutes = [
    "/home",
    "/market",
    "/ai",
    "/portfolio",
    "/settings",
  ];

  int _mobileIndex(String location) {
    if (location.startsWith("/market")) return 1;
    if (location.startsWith("/ai")) return 2;
    if (location.startsWith("/portfolio")) return 3;
    if (location.startsWith("/settings")) return 4;
    return 0;
  }

  @override
  Widget build(BuildContext context) {
    final location = GoRouterState.of(context).uri.toString();

    //==========================================================
    // MOBILE
    //
    // Android uses the full screen for content.
    // Desktop sidebar is intentionally hidden on mobile.
    //==========================================================

    if (Theme.of(context).platform == TargetPlatform.android) {
      return Scaffold(
        body: child,
        bottomNavigationBar: NavigationBar(
          selectedIndex: _mobileIndex(location),
          onDestinationSelected: (index) {
            context.go(_mobileRoutes[index]);
          },
          destinations: const [
            NavigationDestination(
              icon: Icon(Icons.home_outlined),
              selectedIcon: Icon(Icons.home_rounded),
              label: "Home",
            ),
            NavigationDestination(
              icon: Icon(Icons.show_chart_outlined),
              selectedIcon: Icon(Icons.show_chart),
              label: "Market",
            ),
            NavigationDestination(
              icon: Icon(Icons.psychology_outlined),
              selectedIcon: Icon(Icons.psychology),
              label: "AI",
            ),
            NavigationDestination(
              icon: Icon(Icons.account_balance_wallet_outlined),
              selectedIcon: Icon(Icons.account_balance_wallet),
              label: "Portfolio",
            ),
            NavigationDestination(
              icon: Icon(Icons.settings_outlined),
              selectedIcon: Icon(Icons.settings),
              label: "Settings",
            ),
          ],
        ),
      );
    }

    //==========================================================
    // DESKTOP
    //
    // Preserve the existing desktop sidebar exactly.
    //==========================================================

    return Scaffold(
      body: Row(
        children: [
          Material(
            color: const Color(0xff171C26),
            child: SizedBox(
              width: 250,
              child: Column(
                children: [
                  const SizedBox(height: 30),
                  const Icon(
                    Icons.auto_graph,
                    size: 70,
                    color: Colors.lightBlueAccent,
                  ),
                  const SizedBox(height: 10),
                  const Text(
                    "RUSI Trader AI",
                    style: TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 40),
                  Expanded(
                    child: ListView.builder(
                      itemCount: _items.length,
                      itemBuilder: (context, index) {
                        final item = _items[index];

                        final selected = location.startsWith(item.route);

                        return Padding(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 12,
                            vertical: 4,
                          ),
                          child: Material(
                            color: Colors.transparent,
                            borderRadius: BorderRadius.circular(12),
                            child: ListTile(
                              selected: selected,
                              leading: Icon(item.icon),
                              title: Text(item.title),
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(12),
                              ),
                              onTap: () {
                                context.go(item.route);
                              },
                            ),
                          ),
                        );
                      },
                    ),
                  ),
                  const Divider(),
                  const Padding(
                    padding: EdgeInsets.all(16),
                    child: Column(
                      children: [
                        Text(
                          "Backend",
                          style: TextStyle(
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        SizedBox(height: 8),
                        Row(
                          children: [
                            Icon(
                              Icons.circle,
                              size: 10,
                              color: Colors.green,
                            ),
                            SizedBox(width: 8),
                            Text("Connected"),
                          ],
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
          Expanded(
            child: Container(
              color: const Color(0xff10151D),
              child: child,
            ),
          ),
        ],
      ),
    );
  }
}
