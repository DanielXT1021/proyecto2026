class AppConstants {
  // URL base de la API — cambiar según entorno
  static const String baseUrl =
      'https://1a2c-2803-c600-511b-9d48-1ca0-e030-23f2-bfef.ngrok-free.app/api/v1';
  static const String uploadsUrl =
      'https://1a2c-2803-c600-511b-9d48-1ca0-e030-23f2-bfef.ngrok-free.app/uploads';

  static const Duration connectTimeout = Duration(seconds: 15);
  static const Duration receiveTimeout = Duration(seconds: 30);

  static const Map<String, String> speciesLabels = {
    'hortaliza': 'Hortaliza',
    'quinoa': 'Quinoa',
    'quillay': 'Quillay',
    'lavanda': 'Lavanda',
  };

  static const Map<String, String> speciesEmojis = {
    'hortaliza': '🥬',
    'quinoa': '🌾',
    'quillay': '🌳',
    'lavanda': '💜',
  };

  static const Map<String, String> healthStatusLabels = {
    'excellent': 'Excelente',
    'good': 'Buena',
    'moderate': 'Moderada',
    'stressed': 'Estresada',
    'critical': 'Crítica',
  };

  static const Map<String, String> growthStageLabels = {
    'seedling': 'Plántula',
    'growing': 'Crecimiento',
    'mature': 'Madurez',
    'declining': 'Senescencia',
  };

  static const Map<String, String> urgencyLabels = {
    'immediate': 'Inmediato',
    'soon': 'Pronto',
    'normal': 'Normal',
    'skip': 'Omitir',
  };
}
