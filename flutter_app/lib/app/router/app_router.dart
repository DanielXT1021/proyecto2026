import 'package:go_router/go_router.dart';

import '../../presentation/screens/home/home_screen.dart';
import '../../presentation/screens/plant_form/plant_form_screen.dart';
import '../../presentation/screens/plant_detail/plant_detail_screen.dart';
import '../../presentation/screens/analysis/analysis_screen.dart';

final appRouter = GoRouter(
  initialLocation: '/',
  routes: [
    GoRoute(path: '/', builder: (_, __) => const HomeScreen()),
    GoRoute(path: '/add-plant', builder: (_, __) => const PlantFormScreen()),
    GoRoute(
      path: '/plant/:id',
      builder: (_, state) {
        final id = int.parse(state.pathParameters['id']!);
        return PlantDetailScreen(plantId: id);
      },
      routes: [
        GoRoute(
          path: 'analyze',
          builder: (context, state) {
            final id = int.parse(state.pathParameters['id']!);
            final name = state.extra as String? ?? 'Planta';
            return AnalysisScreen(plantId: id, plantName: name);
          },
        ),
      ],
    ),
  ],
);
