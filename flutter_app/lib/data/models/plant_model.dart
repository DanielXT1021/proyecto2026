import 'analysis_model.dart';

class PlantImage {
  final int id;
  final String imageFilename;
  final DateTime capturedAt;
  final String source;
  final PlantAnalysis? analysis;

  const PlantImage({
    required this.id,
    required this.imageFilename,
    required this.capturedAt,
    required this.source,
    this.analysis,
  });

  factory PlantImage.fromJson(Map<String, dynamic> json) => PlantImage(
    id: json['id'] as int,
    imageFilename: json['image_filename'] as String,
    capturedAt: DateTime.parse(json['captured_at'] as String),
    source: json['source'] as String,
    analysis: json['analysis'] != null
        ? PlantAnalysis.fromJson(json['analysis'] as Map<String, dynamic>)
        : null,
  );
}

class Plant {
  final int id;
  final String name;
  final String species;
  final String? description;
  final String? location;
  final DateTime createdAt;
  final List<PlantImage> images;

  const Plant({
    required this.id,
    required this.name,
    required this.species,
    this.description,
    this.location,
    required this.createdAt,
    this.images = const [],
  });

  factory Plant.fromJson(Map<String, dynamic> json) => Plant(
    id: json['id'] as int,
    name: json['name'] as String,
    species: json['species'] as String,
    description: json['description'] as String?,
    location: json['location'] as String?,
    createdAt: DateTime.parse(json['created_at'] as String),
    images: (json['images'] as List? ?? [])
        .map((e) => PlantImage.fromJson(e as Map<String, dynamic>))
        .toList(),
  );
}

class PlantSummary {
  final int id;
  final String name;
  final String species;
  final String? description;
  final String? location;
  final DateTime createdAt;
  final double? latestHealthScore;
  final String? latestHealthStatus;
  final int imageCount;

  const PlantSummary({
    required this.id,
    required this.name,
    required this.species,
    this.description,
    this.location,
    required this.createdAt,
    this.latestHealthScore,
    this.latestHealthStatus,
    required this.imageCount,
  });

  factory PlantSummary.fromJson(Map<String, dynamic> json) => PlantSummary(
    id: json['id'] as int,
    name: json['name'] as String,
    species: json['species'] as String,
    description: json['description'] as String?,
    location: json['location'] as String?,
    createdAt: DateTime.parse(json['created_at'] as String),
    latestHealthScore: json['latest_health_score'] != null
        ? (json['latest_health_score'] as num).toDouble()
        : null,
    latestHealthStatus: json['latest_health_status'] as String?,
    imageCount: json['image_count'] as int? ?? 0,
  );
}
