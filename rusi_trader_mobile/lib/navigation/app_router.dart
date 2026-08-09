import 'package:go_router/go_router.dart';

import '../screens/dashboard/dashboard_screen.dart';
import '../screens/login/login_screen.dart';
import '../screens/splash/splash_screen.dart';

import 'route_names.dart';

class AppRouter {

  static final router = GoRouter(

    initialLocation: RouteNames.splash,

    routes: [

      GoRoute(

        path: RouteNames.splash,

        builder: (context, state) => const SplashScreen(),

      ),

      GoRoute(

        path: RouteNames.login,

        builder: (context, state) => const LoginScreen(),

      ),

      GoRoute(

        path: RouteNames.dashboard,

        builder: (context, state) => const DashboardScreen(),

      ),

    ],

  );

}
