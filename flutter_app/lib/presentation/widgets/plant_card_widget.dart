import 'package:flutter/material.dart';

import '../../core/constants/app_constants.dart';
import '../../core/theme/app_theme.dart';
import '../../data/models/plant_model.dart';

class PlantCardWidget extends StatelessWidget {
  final PlantSummary plant;
  final VoidCallback onTap;
  final VoidCallback? onDelete;

  const PlantCardWidget({
    super.key,
    required this.plant,
    required this.onTap,
    this.onDelete,
  });

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    final emoji = AppConstants.speciesEmojis[plant.species] ?? '🌿';
    final speciesLabel =
        AppConstants.speciesLabels[plant.species] ?? plant.species;
    final statusLabel = plant.latestHealthStatus != null
        ? AppConstants.healthStatusLabels[plant.latestHealthStatus!]
        : null;
    final healthColor = plant.latestHealthStatus != null
        ? AppTheme.healthColor(plant.latestHealthStatus!)
        : cs.outline;

    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
      child: InkWell(
        borderRadius: BorderRadius.circular(16),
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              // Especie icon
              Container(
                width: 56,
                height: 56,
                decoration: BoxDecoration(
                  color: cs.primaryContainer,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Center(
                  child: Text(emoji, style: const TextStyle(fontSize: 28)),
                ),
              ),
              const SizedBox(width: 14),
              // Info
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      plant.name,
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      speciesLabel,
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: cs.onSurfaceVariant,
                      ),
                    ),
                    if (plant.location != null) ...[
                      const SizedBox(height: 2),
                      Row(
                        children: [
                          Icon(
                            Icons.location_on_outlined,
                            size: 12,
                            color: cs.outline,
                          ),
                          const SizedBox(width: 2),
                          Text(
                            plant.location!,
                            style: Theme.of(
                              context,
                            ).textTheme.bodySmall?.copyWith(color: cs.outline),
                          ),
                        ],
                      ),
                    ],
                    const SizedBox(height: 6),
                    Row(
                      children: [
                        // Badge de salud
                        if (plant.latestHealthScore != null) ...[
                          Container(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 8,
                              vertical: 3,
                            ),
                            decoration: BoxDecoration(
                              color: healthColor.withOpacity(0.15),
                              borderRadius: BorderRadius.circular(8),
                              border: Border.all(
                                color: healthColor.withOpacity(0.4),
                              ),
                            ),
                            child: Text(
                              '${plant.latestHealthScore!.toStringAsFixed(0)}% · ${statusLabel ?? ""}',
                              style: TextStyle(
                                fontSize: 11,
                                fontWeight: FontWeight.w600,
                                color: healthColor,
                              ),
                            ),
                          ),
                          const SizedBox(width: 8),
                        ],
                        Icon(
                          Icons.photo_library_outlined,
                          size: 13,
                          color: cs.outline,
                        ),
                        const SizedBox(width: 3),
                        Text(
                          '${plant.imageCount}',
                          style: Theme.of(
                            context,
                          ).textTheme.bodySmall?.copyWith(color: cs.outline),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
              // Botones
              Column(
                children: [
                  Icon(Icons.chevron_right, color: cs.outline),
                  if (onDelete != null) ...[
                    const SizedBox(height: 8),
                    GestureDetector(
                      onTap: onDelete,
                      child: Icon(
                        Icons.delete_outline,
                        color: cs.error,
                        size: 20,
                      ),
                    ),
                  ],
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}
