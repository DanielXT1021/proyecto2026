class WateringRecommendation {
  final int id;
  final int waterAmountMl;
  final double frequencyDays;
  final DateTime nextWatering;
  final String urgency;
  final List<String> actions;
  final List<String> careTips;
  final DateTime createdAt;

  const WateringRecommendation({
    required this.id,
    required this.waterAmountMl,
    required this.frequencyDays,
    required this.nextWatering,
    required this.urgency,
    required this.actions,
    required this.careTips,
    required this.createdAt,
  });

  factory WateringRecommendation.fromJson(Map<String, dynamic> json) =>
      WateringRecommendation(
        id: json['id'] as int,
        waterAmountMl: json['water_amount_ml'] as int,
        frequencyDays: (json['frequency_days'] as num).toDouble(),
        nextWatering: DateTime.parse(json['next_watering'] as String),
        urgency: json['urgency'] as String,
        actions: List<String>.from(json['actions'] as List),
        careTips: List<String>.from(json['care_tips'] as List),
        createdAt: DateTime.parse(json['created_at'] as String),
      );
}

class PlantAnalysis {
  final int id;
  final int imageId;
  final double healthScore;
  final String healthStatus;
  final String growthStage;
  final double greenCoverage;
  final double yellowCoverage;
  final double brownCoverage;
  final int estimatedLeafCount;
  final double hydricStressProbability;
  final double vigorIndex;
  final List<String> notes;
  final DateTime analyzedAt;
  final WateringRecommendation? recommendation;

  const PlantAnalysis({
    required this.id,
    required this.imageId,
    required this.healthScore,
    required this.healthStatus,
    required this.growthStage,
    required this.greenCoverage,
    required this.yellowCoverage,
    required this.brownCoverage,
    required this.estimatedLeafCount,
    required this.hydricStressProbability,
    required this.vigorIndex,
    required this.notes,
    required this.analyzedAt,
    this.recommendation,
  });

  factory PlantAnalysis.fromJson(Map<String, dynamic> json) => PlantAnalysis(
    id: json['id'] as int,
    imageId: json['image_id'] as int,
    healthScore: (json['health_score'] as num).toDouble(),
    healthStatus: json['health_status'] as String,
    growthStage: json['growth_stage'] as String,
    greenCoverage: (json['green_coverage'] as num).toDouble(),
    yellowCoverage: (json['yellow_coverage'] as num).toDouble(),
    brownCoverage: (json['brown_coverage'] as num).toDouble(),
    estimatedLeafCount: json['estimated_leaf_count'] as int,
    hydricStressProbability: (json['hydric_stress_probability'] as num)
        .toDouble(),
    vigorIndex: (json['vigor_index'] as num).toDouble(),
    notes: List<String>.from(json['notes'] as List),
    analyzedAt: DateTime.parse(json['analyzed_at'] as String),
    recommendation: json['recommendation'] != null
        ? WateringRecommendation.fromJson(
            json['recommendation'] as Map<String, dynamic>,
          )
        : null,
  );
}
