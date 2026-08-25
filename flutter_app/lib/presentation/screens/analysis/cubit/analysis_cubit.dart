import 'dart:io';

import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:image_picker/image_picker.dart';

import '../../../../data/repositories/analysis_repository.dart';
import 'analysis_state.dart';

class AnalysisCubit extends Cubit<AnalysisState> {
  final AnalysisRepository _repository;
  final ImagePicker _picker = ImagePicker();

  AnalysisCubit(this._repository) : super(AnalysisInitial());

  Future<void> pickImage(ImageSource source) async {
    final picked = await _picker.pickImage(
      source: source,
      imageQuality: 85,
      maxWidth: 1280,
    );
    if (picked == null) return;
    emit(AnalysisImageSelected(File(picked.path)));
  }

  Future<void> analyze(int plantId, File image) async {
    emit(AnalysisLoading());
    try {
      final result = await _repository.analyzeImage(
        plantId: plantId,
        imageFile: image,
      );
      emit(AnalysisSuccess(result, image));
    } catch (e) {
      emit(AnalysisError('Error al analizar imagen: $e'));
    }
  }

  void reset() => emit(AnalysisInitial());
}
