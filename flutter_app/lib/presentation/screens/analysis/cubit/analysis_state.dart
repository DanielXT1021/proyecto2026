import 'dart:io';

import 'package:equatable/equatable.dart';

import '../../../../data/models/analysis_model.dart';

abstract class AnalysisState extends Equatable {
  const AnalysisState();
  @override
  List<Object?> get props => [];
}

class AnalysisInitial extends AnalysisState {}

class AnalysisImageSelected extends AnalysisState {
  final File image;
  const AnalysisImageSelected(this.image);
  @override
  List<Object?> get props => [image];
}

class AnalysisLoading extends AnalysisState {}

class AnalysisSuccess extends AnalysisState {
  final PlantAnalysis analysis;
  final File image;
  const AnalysisSuccess(this.analysis, this.image);
  @override
  List<Object?> get props => [analysis, image];
}

class AnalysisError extends AnalysisState {
  final String message;
  const AnalysisError(this.message);
  @override
  List<Object?> get props => [message];
}
