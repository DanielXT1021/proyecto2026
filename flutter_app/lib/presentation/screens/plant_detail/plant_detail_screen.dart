import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';

import '../../../core/constants/app_constants.dart';
import '../../../core/theme/app_theme.dart';
import '../../../data/models/plant_model.dart';
import '../../../data/repositories/plant_repository.dart';
import '../../widgets/health_gauge_widget.dart';

class PlantDetailScreen extends StatefulWidget {
  final int plantId;
  const PlantDetailScreen({super.key, required this.plantId});

  @override
  State<PlantDetailScreen> createState() => _PlantDetailScreenState();
}

class _PlantDetailScreenState extends State<PlantDetailScreen> {
  final _repo = PlantRepository();
  late Future<Plant> _future;

  @override
  void initState() {
    super.initState();
    _future = _repo.getPlant(widget.plantId);
  }

  void _refresh() => setState(() => _future = _repo.getPlant(widget.plantId));

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    final fmt = DateFormat('dd/MM/yyyy HH:mm');

    return Scaffold(
      body: FutureBuilder<Plant>(
        future: _future,
        builder: (context, snap) {
          if (snap.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snap.hasError) {
            return Center(child: Text('Error: ${snap.error}'));
          }
          final plant = snap.data!;
          final emoji = AppConstants.speciesEmojis[plant.species] ?? '🌿';
          final speciesLabel =
              AppConstants.speciesLabels[plant.species] ?? plant.species;

          // Ordenar imágenes más recientes primero
          final images = [...plant.images]
            ..sort((a, b) => b.capturedAt.compareTo(a.capturedAt));

          return CustomScrollView(
            slivers: [
              SliverAppBar.large(
                title: Text(plant.name),
                actions: [
                  IconButton(
                    icon: const Icon(Icons.camera_alt),
                    tooltip: 'Analizar nueva imagen',
                    onPressed: () async {
                      final done = await context.push<bool>(
                        '/plant/${plant.id}/analyze',
                        extra: plant.name,
                      );
                      if (done == true && mounted) _refresh();
                    },
                  ),
                ],
              ),
              SliverToBoxAdapter(
                child: Padding(
                  padding: const EdgeInsets.all(20),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // Info de la planta
                      Row(
                        children: [
                          Text(emoji, style: const TextStyle(fontSize: 40)),
                          const SizedBox(width: 14),
                          Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                speciesLabel,
                                style: Theme.of(context).textTheme.titleMedium
                                    ?.copyWith(
                                      color: cs.primary,
                                      fontWeight: FontWeight.bold,
                                    ),
                              ),
                              if (plant.location != null)
                                Text(
                                  plant.location!,
                                  style: Theme.of(context).textTheme.bodySmall
                                      ?.copyWith(color: cs.outline),
                                ),
                              Text(
                                'Registrada: ${DateFormat('dd/MM/yyyy').format(plant.createdAt)}',
                                style: Theme.of(context).textTheme.bodySmall
                                    ?.copyWith(color: cs.outline),
                              ),
                            ],
                          ),
                        ],
                      ),
                      if (plant.description != null) ...[
                        const SizedBox(height: 12),
                        Text(
                          plant.description!,
                          style: Theme.of(context).textTheme.bodyMedium,
                        ),
                      ],
                      const SizedBox(height: 20),
                      const Divider(),
                      const SizedBox(height: 12),
                      Text(
                        'Historial de Análisis (${images.length})',
                        style: Theme.of(context).textTheme.titleMedium
                            ?.copyWith(fontWeight: FontWeight.bold),
                      ),
                      if (images.isEmpty)
                        Padding(
                          padding: const EdgeInsets.symmetric(vertical: 24),
                          child: Center(
                            child: Column(
                              children: [
                                Text(
                                  '📷',
                                  style: const TextStyle(fontSize: 48),
                                ),
                                const SizedBox(height: 10),
                                const Text(
                                  'Sin análisis todavía.\nToca el ícono de cámara para analizar.',
                                ),
                              ],
                            ),
                          ),
                        ),
                    ],
                  ),
                ),
              ),
              // Lista de análisis
              SliverList.builder(
                itemCount: images.length,
                itemBuilder: (ctx, i) {
                  final img = images[i];
                  final analysis = img.analysis;
                  if (analysis == null) return const SizedBox.shrink();

                  final healthColor = AppTheme.healthColor(
                    analysis.healthStatus,
                  );
                  final statusLabel =
                      AppConstants.healthStatusLabels[analysis.healthStatus] ??
                      analysis.healthStatus;
                  final stageLabel =
                      AppConstants.growthStageLabels[analysis.growthStage] ??
                      analysis.growthStage;

                  return Card(
                    margin: const EdgeInsets.symmetric(
                      horizontal: 16,
                      vertical: 6,
                    ),
                    child: Padding(
                      padding: const EdgeInsets.all(14),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              HealthGaugeWidget(
                                score: analysis.healthScore,
                                status: analysis.healthStatus,
                                size: 72,
                              ),
                              const SizedBox(width: 14),
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    _Badge(statusLabel, healthColor),
                                    const SizedBox(height: 4),
                                    _Badge(stageLabel, cs.secondary),
                                    const SizedBox(height: 6),
                                    Text(
                                      fmt.format(analysis.analyzedAt.toLocal()),
                                      style: Theme.of(context)
                                          .textTheme
                                          .bodySmall
                                          ?.copyWith(color: cs.outline),
                                    ),
                                  ],
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 10),
                          // Barras de color
                          _ColorBar(
                            'Verde',
                            analysis.greenCoverage,
                            const Color(0xFF388E3C),
                          ),
                          const SizedBox(height: 4),
                          _ColorBar(
                            'Amarillo',
                            analysis.yellowCoverage,
                            const Color(0xFFF9A825),
                          ),
                          const SizedBox(height: 4),
                          _ColorBar(
                            'Marrón',
                            analysis.brownCoverage,
                            const Color(0xFF8D6E63),
                          ),
                          const SizedBox(height: 8),
                          Row(
                            children: [
                              Icon(
                                Icons.filter_tilt_shift,
                                size: 13,
                                color: cs.outline,
                              ),
                              const SizedBox(width: 4),
                              Text(
                                'Hojas estimadas: ${analysis.estimatedLeafCount}  •  '
                                'Estrés hídrico: ${(analysis.hydricStressProbability * 100).toStringAsFixed(0)}%',
                                style: Theme.of(context).textTheme.bodySmall
                                    ?.copyWith(color: cs.onSurfaceVariant),
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),
                  );
                },
              ),
              const SliverPadding(padding: EdgeInsets.only(bottom: 40)),
            ],
          );
        },
      ),
    );
  }
}

class _Badge extends StatelessWidget {
  final String label;
  final Color color;
  const _Badge(this.label, this.color);

  @override
  Widget build(BuildContext context) => Container(
    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
    decoration: BoxDecoration(
      color: color.withOpacity(0.12),
      borderRadius: BorderRadius.circular(6),
      border: Border.all(color: color.withOpacity(0.4)),
    ),
    child: Text(
      label,
      style: TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: color),
    ),
  );
}

class _ColorBar extends StatelessWidget {
  final String label;
  final double percent;
  final Color color;

  const _ColorBar(this.label, this.percent, this.color);

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        SizedBox(
          width: 60,
          child: Text(label, style: Theme.of(context).textTheme.bodySmall),
        ),
        const SizedBox(width: 8),
        Expanded(
          child: ClipRRect(
            borderRadius: BorderRadius.circular(4),
            child: LinearProgressIndicator(
              value: (percent / 100).clamp(0.0, 1.0),
              minHeight: 8,
              backgroundColor: color.withOpacity(0.15),
              valueColor: AlwaysStoppedAnimation(color),
            ),
          ),
        ),
        const SizedBox(width: 8),
        Text(
          '${percent.toStringAsFixed(1)}%',
          style: Theme.of(context).textTheme.bodySmall,
        ),
      ],
    );
  }
}
