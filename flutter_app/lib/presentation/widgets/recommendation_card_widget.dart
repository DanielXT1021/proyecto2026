import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

import '../../core/constants/app_constants.dart';
import '../../core/theme/app_theme.dart';
import '../../data/models/analysis_model.dart';

class RecommendationCardWidget extends StatelessWidget {
  final WateringRecommendation recommendation;

  const RecommendationCardWidget({super.key, required this.recommendation});

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    final urgencyColor = AppTheme.urgencyColor(recommendation.urgency);
    final urgencyLabel =
        AppConstants.urgencyLabels[recommendation.urgency] ??
        recommendation.urgency;
    final dateFormatter = DateFormat('dd/MM/yyyy HH:mm');

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Encabezado
            Row(
              children: [
                Icon(Icons.water_drop, color: cs.primary),
                const SizedBox(width: 8),
                Text(
                  'Recomendación de Riego',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const Spacer(),
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 10,
                    vertical: 4,
                  ),
                  decoration: BoxDecoration(
                    color: urgencyColor.withOpacity(0.15),
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: urgencyColor.withOpacity(0.5)),
                  ),
                  child: Text(
                    urgencyLabel,
                    style: TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.w600,
                      color: urgencyColor,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            // Métricas principales
            Row(
              children: [
                _MetricChip(
                  icon: Icons.opacity,
                  label: '${recommendation.waterAmountMl} ml',
                  subtitle: 'Cantidad',
                  color: cs.primary,
                ),
                const SizedBox(width: 12),
                _MetricChip(
                  icon: Icons.schedule,
                  label:
                      'c/${recommendation.frequencyDays.toStringAsFixed(1)} días',
                  subtitle: 'Frecuencia',
                  color: cs.secondary,
                ),
              ],
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                Icon(Icons.event, size: 16, color: cs.outline),
                const SizedBox(width: 6),
                Text(
                  'Próximo riego: ${dateFormatter.format(recommendation.nextWatering.toLocal())}',
                  style: Theme.of(
                    context,
                  ).textTheme.bodySmall?.copyWith(color: cs.onSurfaceVariant),
                ),
              ],
            ),
            const SizedBox(height: 12),
            const Divider(),
            const SizedBox(height: 8),
            // Acciones
            Text(
              'Acciones recomendadas',
              style: Theme.of(context).textTheme.labelLarge,
            ),
            const SizedBox(height: 6),
            ...recommendation.actions.map(
              (a) => Padding(
                padding: const EdgeInsets.only(bottom: 4),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('• ', style: TextStyle(fontSize: 14)),
                    Expanded(
                      child: Text(
                        a,
                        style: Theme.of(context).textTheme.bodyMedium,
                      ),
                    ),
                  ],
                ),
              ),
            ),
            if (recommendation.careTips.isNotEmpty) ...[
              const SizedBox(height: 10),
              const Divider(),
              const SizedBox(height: 6),
              Text(
                'Consejos de cuidado',
                style: Theme.of(context).textTheme.labelLarge,
              ),
              const SizedBox(height: 6),
              ...recommendation.careTips.map(
                (tip) => Padding(
                  padding: const EdgeInsets.only(bottom: 4),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Icon(
                        Icons.tips_and_updates_outlined,
                        size: 14,
                        color: cs.primary,
                      ),
                      const SizedBox(width: 6),
                      Expanded(
                        child: Text(
                          tip,
                          style: Theme.of(context).textTheme.bodySmall,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}

class _MetricChip extends StatelessWidget {
  final IconData icon;
  final String label;
  final String subtitle;
  final Color color;

  const _MetricChip({
    required this.icon,
    required this.label,
    required this.subtitle,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
        decoration: BoxDecoration(
          color: color.withOpacity(0.08),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: color.withOpacity(0.3)),
        ),
        child: Row(
          children: [
            Icon(icon, color: color, size: 20),
            const SizedBox(width: 8),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  label,
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    color: color,
                    fontSize: 13,
                  ),
                ),
                Text(
                  subtitle,
                  style: TextStyle(fontSize: 11, color: color.withOpacity(0.7)),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
