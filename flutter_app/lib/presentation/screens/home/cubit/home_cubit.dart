import 'package:flutter_bloc/flutter_bloc.dart';

import '../../../../data/repositories/plant_repository.dart';
import 'home_state.dart';

class HomeCubit extends Cubit<HomeState> {
  final PlantRepository _repository;

  HomeCubit(this._repository) : super(HomeInitial());

  Future<void> loadPlants() async {
    emit(HomeLoading());
    try {
      final plants = await _repository.getPlants();
      emit(HomeLoaded(plants));
    } catch (e) {
      emit(HomeError('Error al cargar plantas: $e'));
    }
  }

  Future<void> deletePlant(int id) async {
    try {
      await _repository.deletePlant(id);
      await loadPlants();
    } catch (e) {
      emit(HomeError('Error al eliminar planta: $e'));
    }
  }
}
