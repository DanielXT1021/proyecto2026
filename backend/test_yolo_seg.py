import sys
import os
import cv2
import numpy as np

# Añadir backend al sys.path
sys.path.insert(0, os.path.dirname(__file__))

from app.services.yolo_segmenter import yolo_segmenter
from app.services.ml_analyzer import analyze_plant_image


def create_sample_plant_image() -> bytes:
    """Crea una imagen sintética de una planta para pruebas."""
    img = np.full((480, 640, 3), (230, 230, 230), dtype=np.uint8)

    # Dibujar maceta marrón en la parte inferior
    cv2.rectangle(img, (260, 360), (380, 460), (30, 60, 100), -1)

    # Dibujar hojas verdes con elipses
    cv2.ellipse(img, (320, 260), (70, 40), 30, 0, 360, (35, 160, 45), -1)
    cv2.ellipse(img, (280, 220), (60, 35), -40, 0, 360, (40, 180, 50), -1)
    cv2.ellipse(img, (360, 200), (65, 38), 50, 0, 360, (30, 150, 40), -1)
    cv2.ellipse(img, (310, 150), (55, 30), -10, 0, 360, (45, 190, 60), -1)

    # Pequeña zona amarilla (estrés/clorosis leve)
    cv2.ellipse(img, (260, 240), (25, 15), -20, 0, 360, (20, 200, 220), -1)

    # Tallo
    cv2.line(img, (320, 360), (315, 160), (25, 110, 35), 6)

    success, encoded = cv2.imencode(".jpg", img)
    return encoded.tobytes()


def main():
    print("=== Iniciando prueba de YOLO-seg ===")
    sample_bytes = create_sample_plant_image()
    print(f"Imagen sintética generada ({len(sample_bytes)} bytes)")

    # 1. Probar YOLOSegmenter directamente
    nparr = np.frombuffer(sample_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    print("Ejecutando inferencia directa de segmentación con YOLO-seg...")
    seg_res = yolo_segmenter.segment(img)

    print(f"Modelo cargado: {seg_res.model_name}")
    print(f"Detecciones encontradas: {seg_res.has_detections}")
    print(f"Número de instancias: {seg_res.num_instances}")
    print(f"Confianza promedio: {seg_res.avg_confidence}")
    print(f"Píxeles segmentados en máscara: {np.count_nonzero(seg_res.combined_mask)}")

    # 2. Probar analyze_plant_image
    print("\nEjecutando pipeline completo de análisis agronómico...")
    result = analyze_plant_image(sample_bytes, species="quinoa")

    print("\n--- Resultados del Análisis ---")
    print(f"Puntaje de salud: {result.health_score}/100")
    print(f"Estado de salud: {result.health_status.value}")
    print(f"Estadio de crecimiento: {result.growth_stage.value}")
    print(f"Cobertura verde: {result.green_coverage}%")
    print(f"Amarillamiento: {result.yellow_coverage}%")
    print(f"Necrosis/Pardo: {result.brown_coverage}%")
    print(f"Conteo estimado de hojas/instancias: {result.estimated_leaf_count}")
    print(f"Índice de vigor: {result.vigor_index}")
    print(f"Estrés hídrico: {result.hydric_stress_probability}")
    print(f"Segmentación IA usada: {result.segmentation_used}")
    print(f"Overlay generado: {result.annotated_image_bytes is not None}")
    print(f"Notas:")
    for note in result.notes:
        print(f"  • {note}")

    # 3. Probar con foto real de planta
    test_photo_path = os.path.join(os.path.dirname(__file__), "uploads", "test_plant.jpg")
    if os.path.exists(test_photo_path):
        print(f"\n--- Probando con foto real de planta: {test_photo_path} ---")
        with open(test_photo_path, "rb") as f:
            photo_bytes = f.read()
        photo_result = analyze_plant_image(photo_bytes, species="hortaliza")
        print(f"Puntaje de salud: {photo_result.health_score}/100")
        print(f"Estado de salud: {photo_result.health_status.value}")
        print(f"Estadio de crecimiento: {photo_result.growth_stage.value}")
        print(f"Cobertura verde: {photo_result.green_coverage}%")
        print(f"Amarillamiento: {photo_result.yellow_coverage}%")
        print(f"Necrosis/Pardo: {photo_result.brown_coverage}%")
        print(f"Segmentación IA usada: {photo_result.segmentation_used}")
        print(f"Instancias / Hojas: {photo_result.estimated_leaf_count}")
        print(f"Índice de vigor: {photo_result.vigor_index}")
        print(f"Estrés hídrico: {photo_result.hydric_stress_probability}")
        print("Notas:")
        for note in photo_result.notes:
            print(f"  • {note}")

        if photo_result.annotated_image_bytes:
            out_overlay_path = os.path.join(os.path.dirname(__file__), "uploads", "test_plant_segmented.jpg")
            with open(out_overlay_path, "wb") as f:
                f.write(photo_result.annotated_image_bytes)
            print(f"Imagen con segmentación guardada en: {out_overlay_path}")

    print("\n=== Prueba completada con éxito ===")


if __name__ == "__main__":
    main()
