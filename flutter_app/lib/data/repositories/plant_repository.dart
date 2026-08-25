import '../../core/network/api_client.dart';
import '../models/plant_model.dart';

class PlantRepository {
  final _dio = ApiClient().dio;

  Future<List<PlantSummary>> getPlants() async {
    final res = await _dio.get('/plants/');
    return (res.data as List)
        .map((e) => PlantSummary.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<Plant> getPlant(int id) async {
    final res = await _dio.get('/plants/$id');
    return Plant.fromJson(res.data as Map<String, dynamic>);
  }

  Future<PlantSummary> createPlant({
    required String name,
    required String species,
    String? description,
    String? location,
  }) async {
    final res = await _dio.post(
      '/plants/',
      data: {
        'name': name,
        'species': species,
        if (description != null) 'description': description,
        if (location != null) 'location': location,
      },
    );
    // La respuesta es PlantOut que tiene 'images', devolvemos como summary
    final json = res.data as Map<String, dynamic>;
    return PlantSummary(
      id: json['id'] as int,
      name: json['name'] as String,
      species: json['species'] as String,
      description: json['description'] as String?,
      location: json['location'] as String?,
      createdAt: DateTime.parse(json['created_at'] as String),
      imageCount: 0,
    );
  }

  Future<void> deletePlant(int id) async {
    await _dio.delete('/plants/$id');
  }
}
