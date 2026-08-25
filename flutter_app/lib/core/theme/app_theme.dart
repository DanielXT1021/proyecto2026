import 'package:flutter/material.dart';

class AppTheme {
  static const _seedColor = Color(0xFF2E7D32); // verde bosque

  static ThemeData get light => ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: _seedColor,
          brightness: Brightness.light,
        ),
        useMaterial3: true,
        fontFamily: 'Roboto',
        appBarTheme: const AppBarTheme(centerTitle: true, elevation: 0),
        cardTheme: CardThemeData(
          elevation: 2,
          shape:
              RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        ),
        filledButtonTheme: FilledButtonThemeData(
          style: FilledButton.styleFrom(
            shape:
                RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
          ),
        ),
        inputDecorationTheme: InputDecorationTheme(
          border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
          contentPadding:
              const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
        ),
      );

  static ThemeData get dark => ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: _seedColor,
          brightness: Brightness.dark,
        ),
        useMaterial3: true,
      );

  // Colores semánticos de salud
  static Color healthColor(String status) => switch (status) {
        'excellent' => const Color(0xFF1B5E20),
        'good' => const Color(0xFF388E3C),
        'moderate' => const Color(0xFFF9A825),
        'stressed' => const Color(0xFFE65100),
        'critical' => const Color(0xFFB71C1C),
        _ => Colors.grey,
      };

  static Color urgencyColor(String urgency) => switch (urgency) {
        'immediate' => const Color(0xFFB71C1C),
        'soon' => const Color(0xFFE65100),
        'normal' => const Color(0xFF388E3C),
        _ => Colors.grey,
      };
}
