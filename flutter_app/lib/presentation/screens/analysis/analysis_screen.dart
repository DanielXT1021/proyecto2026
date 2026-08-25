import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';
import 'package:image_picker/image_picker.dart';

import '../../../core/constants/app_constants.dart';
import '../../../core/theme/app_theme.dart';
import '../../../data/repositories/analysis_repository.dart';
import '../../widgets/health_gauge_widget.dart';
import '../../widgets/recommendation_card_widget.dart';
import 'cubit/analysis_cubit.dart';
import 'cubit/analysis_state.dart';

class AnalysisScreen extends StatelessWidget {
  final int plantId;
  final String plantName;

  const AnalysisScreen({
    super.key,
    required this.plantId,
    required this.plantName,
  });

  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      create: (_) => AnalysisCubit(AnalysisRepository()),
      child: _AnalysisView(plantId: plantId, plantName: plantName),
    );
  }
}

class _AnalysisView extends StatelessWidget {
  final int plantId;
  final String plantName;

  const _AnalysisView({required this.plantId, required this.plantName});

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;

    return Scaffold(
      appBar: AppBar(title: Text('Analizar: $plantName')),
      body: BlocConsumer<AnalysisCubit, AnalysisState>(
        listener: (ctx, state) {
          if (state is AnalysisError) {
            ScaffoldMessenger.of(ctx).showSnackBar(
              SnackBar(content: Text(state.message), backgroundColor: cs.error),
            );
          }
        },
        builder: (ctx, state) {
          if (state is AnalysisInitial) {
            return _PickerPrompt(plantId: plantId);
          }
          if (state is AnalysisImageSelected) {
            return _ImagePreview(image: state.image, plantId: plantId);
          }
          if (state is AnalysisLoading) {
            return const Center(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  CircularProgressIndicator(),
                  SizedBox(height: 16),
                  Text('Analizando imagen con IA...'),
                  SizedBox(height: 6),
                  Text('Procesando visión computacional'),
                ],
              ),
            );
          }
          if (state is AnalysisSuccess) {
            return _ResultView(
              analysis: state.analysis,
              image: state.image,
              onDone: () => ctx.pop(true),
              onRetry: () => ctx.read<AnalysisCubit>().reset(),
            );
          }
          if (state is AnalysisError) {
            return Center(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(Icons.error_outline, size: 48, color: cs.error),
                  const SizedBox(height: 12),
                  Text(state.message, textAlign: TextAlign.center),
                  const SizedBox(height: 16),
                  FilledButton(
                    onPressed: () => ctx.read<AnalysisCubit>().reset(),
                    child: const Text('Intentar de nuevo'),
                  ),
                ],
              ),
            );
          }
          return const SizedBox.shrink();
        },
      ),
    );
  }
}

class _PickerPrompt extends StatelessWidget {
  final int plantId;
  const _PickerPrompt({required this.plantId});

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text('📸', style: const TextStyle(fontSize: 64)),
            const SizedBox(height: 16),
            Text(
              'Selecciona una imagen',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 8),
            Text(
              'Toma una foto directa o elige una desde tu galería para analizar la planta.',
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.bodyMedium,
            ),
            const SizedBox(height: 32),
            FilledButton.icon(
              onPressed: () =>
                  context.read<AnalysisCubit>().pickImage(ImageSource.camera),
              icon: const Icon(Icons.camera_alt),
              label: const Text('Tomar Foto'),
            ),
            const SizedBox(height: 12),
            OutlinedButton.icon(
              onPressed: () =>
                  context.read<AnalysisCubit>().pickImage(ImageSource.gallery),
              icon: const Icon(Icons.photo_library_outlined),
              label: const Text('Galería'),
            ),
          ],
        ),
      ),
    );
  }
}

class _ImagePreview extends StatelessWidget {
  final File image;
  final int plantId;
  const _ImagePreview({required this.image, required this.plantId});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Expanded(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: ClipRRect(
              borderRadius: BorderRadius.circular(16),
              child: Image.file(image, fit: BoxFit.contain),
            ),
          ),
        ),
        Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            children: [
              FilledButton.icon(
                onPressed: () =>
                    context.read<AnalysisCubit>().analyze(plantId, image),
                icon: const Icon(Icons.analytics),
                label: const Text('Analizar con IA'),
              ),
              const SizedBox(height: 10),
              TextButton(
                onPressed: () => context.read<AnalysisCubit>().reset(),
                child: const Text('Cambiar imagen'),
              ),
            ],
          ),
        ),
      ],
    );
  }
}

class _ResultView extends StatelessWidget {
  final dynamic analysis;
  final File image;
  final VoidCallback onDone;
  final VoidCallback onRetry;

  const _ResultView({
    required this.analysis,
    required this.image,
    required this.onDone,
    required this.onRetry,
  });

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    final statusLabel =
        AppConstants.healthStatusLabels[analysis.healthStatus] ??
        analysis.healthStatus;
    final stageLabel =
        AppConstants.growthStageLabels[analysis.growthStage] ??
        analysis.growthStage;
    final healthColor = AppTheme.healthColor(analysis.healthStatus);

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Imagen y gauge
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Row(
                children: [
                  ClipRRect(
                    borderRadius: BorderRadius.circular(12),
                    child: Image.file(
                      image,
                      width: 100,
                      height: 100,
                      fit: BoxFit.cover,
                    ),
                  ),
                  const SizedBox(width: 16),
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      HealthGaugeWidget(
                        score: analysis.healthScore,
                        status: analysis.healthStatus,
                        size: 90,
                      ),
                    ],
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        _StatBadge(statusLabel, healthColor),
                        const SizedBox(height: 6),
                        _StatBadge(stageLabel, cs.secondary),
                        const SizedBox(height: 8),
                        Text(
                          '🍃 Hojas: ${analysis.estimatedLeafCount}\n'
                          '💧 Estrés: ${(analysis.hydricStressProbability * 100).toStringAsFixed(0)}%\n'
                          '⚡ Vigor: ${analysis.vigorIndex.toStringAsFixed(0)}',
                          style: Theme.of(context).textTheme.bodySmall,
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 8),

          // Cobertura de colores
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Análisis Colorimétrico',
                    style: Theme.of(context).textTheme.titleSmall?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 10),
                  _ColorRow(
                    '🟢 Verde (sano)',
                    analysis.greenCoverage,
                    const Color(0xFF388E3C),
                  ),
                  const SizedBox(height: 6),
                  _ColorRow(
                    '🟡 Amarillo (estrés)',
                    analysis.yellowCoverage,
                    const Color(0xFFF9A825),
                  ),
                  const SizedBox(height: 6),
                  _ColorRow(
                    '🟤 Marrón (daño)',
                    analysis.brownCoverage,
                    const Color(0xFF8D6E63),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 8),

          // Notas del análisis
          if (analysis.notes.isNotEmpty)
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Observaciones',
                      style: Theme.of(context).textTheme.titleSmall?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 8),
                    ...(analysis.notes as List<String>).map(
                      (n) => Padding(
                        padding: const EdgeInsets.only(bottom: 4),
                        child: Row(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text('• '),
                            Expanded(
                              child: Text(
                                n,
                                style: Theme.of(context).textTheme.bodyMedium,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          const SizedBox(height: 8),

          // Recomendación de riego
          if (analysis.recommendation != null)
            RecommendationCardWidget(recommendation: analysis.recommendation!),

          const SizedBox(height: 16),
          FilledButton.icon(
            onPressed: onDone,
            icon: const Icon(Icons.check_circle_outline),
            label: const Text('Guardar y volver'),
          ),
          const SizedBox(height: 8),
          OutlinedButton.icon(
            onPressed: onRetry,
            icon: const Icon(Icons.camera_alt),
            label: const Text('Analizar otra imagen'),
          ),
        ],
      ),
    );
  }
}

class _StatBadge extends StatelessWidget {
  final String label;
  final Color color;
  const _StatBadge(this.label, this.color);

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

class _ColorRow extends StatelessWidget {
  final String label;
  final double percent;
  final Color color;
  const _ColorRow(this.label, this.percent, this.color);

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        SizedBox(
          width: 130,
          child: Text(label, style: Theme.of(context).textTheme.bodySmall),
        ),
        Expanded(
          child: ClipRRect(
            borderRadius: BorderRadius.circular(4),
            child: LinearProgressIndicator(
              value: (percent / 100).clamp(0.0, 1.0),
              minHeight: 10,
              backgroundColor: color.withOpacity(0.12),
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
