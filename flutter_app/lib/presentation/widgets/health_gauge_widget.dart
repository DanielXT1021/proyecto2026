import 'package:flutter/material.dart';

import '../../core/theme/app_theme.dart';

class HealthGaugeWidget extends StatelessWidget {
  final double score;
  final String status;
  final double size;

  const HealthGaugeWidget({
    super.key,
    required this.score,
    required this.status,
    this.size = 120,
  });

  @override
  Widget build(BuildContext context) {
    final color = AppTheme.healthColor(status);
    return SizedBox(
      width: size,
      height: size,
      child: Stack(
        alignment: Alignment.center,
        children: [
          CircularProgressIndicator(
            value: score / 100,
            strokeWidth: 10,
            backgroundColor: color.withOpacity(0.15),
            valueColor: AlwaysStoppedAnimation<Color>(color),
            strokeCap: StrokeCap.round,
          ),
          Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                score.toStringAsFixed(0),
                style: TextStyle(
                  fontSize: size * 0.28,
                  fontWeight: FontWeight.bold,
                  color: color,
                ),
              ),
              Text(
                '%',
                style: TextStyle(
                  fontSize: size * 0.13,
                  color: color.withOpacity(0.7),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
