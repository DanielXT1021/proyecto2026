import 'dart:io';

import 'package:dio/dio.dart';

import '../../core/network/api_client.dart';
import '../models/analysis_model.dart';

class AnalysisRepository {
  final _dio = ApiClient().dio;

  Future<PlantAnalysis> analyzeImage({
    required int plantId,
    required File imageFile,
    String source = 'mobile',
  }) async {
    final formData = FormData.fromMap({
      'file': await MultipartFile.fromFile(
        imageFile.path,
        filename: imageFile.path.split('/').last,
      ),
      'plant_id': plantId.toString(),
      'source': source,
    });

    final res = await _dio.post(
      '/analysis/analyze',
      data: formData,
      options: Options(contentType: 'multipart/form-data'),
    );

    final json = res.data as Map<String, dynamic>;
    return PlantAnalysis.fromJson(json['analysis'] as Map<String, dynamic>);
  }

  Future<List<PlantAnalysis>> getPlantHistory(int plantId) async {
    final res = await _dio.get('/analysis/plant/$plantId');
    return (res.data as List)
        .map((e) => PlantAnalysis.fromJson(e as Map<String, dynamic>))
        .toList();
  }
}
