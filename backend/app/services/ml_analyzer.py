import cv2
import numpy as np
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List

from app.services.yolo_segmenter import yolo_segmenter, YOLOSegmentationResult


class HealthStatus(str, Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    MODERATE = "moderate"
    STRESSED = "stressed"
    CRITICAL = "critical"


class GrowthStage(str, Enum):
    SEEDLING = "seedling"
    GROWING = "growing"
    MATURE = "mature"
    DECLINING = "declining"


@dataclass
class PlantAnalysisResult:
    health_score: float
    health_status: HealthStatus
    growth_stage: GrowthStage
    green_coverage: float
    yellow_coverage: float
    brown_coverage: float
    estimated_leaf_count: int
    hydric_stress_probability: float
    vigor_index: float
    notes: list[str] = field(default_factory=list)
    annotated_image_bytes: Optional[bytes] = None
    segmentation_used: bool = False
    instances_count: int = 0


def analyze_plant_image(image_bytes: bytes, species: str = "hortaliza") -> PlantAnalysisResult:
    """
    Analiza una imagen de planta usando visión computacional avanzada y YOLO-seg.
    Aísla la vegetación del fondo mediante segmentación de instancias neuronales
    y extrae métricas de color, vigor foliar y estrés hídrico.
    """
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img is None:
        raise ValueError("No se pudo decodificar la imagen")

    # Redimensionar para análisis uniforme y óptimo
    img = cv2.resize(img, (640, 480))
    total_pixels = img.shape[0] * img.shape[1]

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # ── Segmentación por IA con YOLO-seg ───────────────────────────────────────
    seg_res = yolo_segmenter.segment(img)

    # ── Máscaras de color en espacio HSV ───────────────────────────────────────
    # Verde (vegetación sana): H [35-85], S y V moderados/altos
    green_mask_raw = cv2.inRange(hsv, (35, 30, 30), (85, 255, 255))
    # Amarillo (clorosis / estrés hídrico): H [20-35]
    yellow_mask_raw = cv2.inRange(hsv, (20, 50, 50), (35, 255, 255))
    # Marrón/pardo (necrosis o daño foliar): H [8-20]
    brown_mask_raw = cv2.inRange(hsv, (8, 30, 20), (20, 200, 200))

    # Limpieza morfológica para reducir ruido
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    green_mask_clean = cv2.morphologyEx(green_mask_raw, cv2.MORPH_OPEN, kernel)
    yellow_mask_clean = cv2.morphologyEx(yellow_mask_raw, cv2.MORPH_OPEN, kernel)
    brown_mask_clean = cv2.morphologyEx(brown_mask_raw, cv2.MORPH_OPEN, kernel)

    segmentation_used = False
    instances_count = seg_res.num_instances

    if seg_res.has_detections and np.count_nonzero(seg_res.combined_mask) > 0:
        # Usar la máscara generada por la red YOLO-seg
        plant_mask = seg_res.combined_mask
        segmentation_used = True

        # Restringir las detecciones de color a los píxeles de la vegetación segmentada
        green_mask = cv2.bitwise_and(green_mask_clean, green_mask_clean, mask=plant_mask)
        yellow_mask = cv2.bitwise_and(yellow_mask_clean, yellow_mask_clean, mask=plant_mask)
        brown_mask = cv2.bitwise_and(brown_mask_clean, brown_mask_clean, mask=plant_mask)
    else:
        # Respaldo adaptativo por color si el modelo YOLO no detectó objetos específicos
        plant_mask = cv2.bitwise_or(green_mask_clean, cv2.bitwise_or(yellow_mask_clean, brown_mask_clean))
        green_mask = green_mask_clean
        yellow_mask = yellow_mask_clean
        brown_mask = brown_mask_clean

    plant_pixels = int(np.count_nonzero(plant_mask))
    coverage_pct = (plant_pixels / total_pixels) * 100.0 if total_pixels > 0 else 0.0

    green_pct = (np.count_nonzero(green_mask) / total_pixels) * 100.0
    yellow_pct = (np.count_nonzero(yellow_mask) / total_pixels) * 100.0
    brown_pct = (np.count_nonzero(brown_mask) / total_pixels) * 100.0

    # ── Índice de textura y vigor foliar (Varianza Laplaciana sobre la planta) ──
    plant_gray = cv2.bitwise_and(gray, gray, mask=plant_mask)
    if plant_pixels > 0:
        laplacian = cv2.Laplacian(plant_gray.astype(np.float64), cv2.CV_64F)
        texture_var = float(np.var(laplacian[plant_mask > 0]))
    else:
        texture_var = 0.0

    vigor_index = min(texture_var / 80.0, 100.0)

    # ── Conteo estimado de hojas / instancias ──────────────────────────────────
    if segmentation_used and instances_count > 1:
        estimated_leaf_count = instances_count
    else:
        # Conteo morfológico en la región segmentada
        edges = cv2.Canny(plant_gray, 25, 90)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        min_area = total_pixels * 0.0015
        leaf_like = [c for c in contours if cv2.contourArea(c) > min_area]
        estimated_leaf_count = max(instances_count, min(len(leaf_like), 200))

    # ── Puntaje de salud (0-100) ───────────────────────────────────────────────
    # Proporción de verde dentro del follaje real
    if plant_pixels > 0:
        green_ratio_in_plant = (np.count_nonzero(green_mask) / plant_pixels) * 100.0
        yellow_ratio_in_plant = (np.count_nonzero(yellow_mask) / plant_pixels) * 100.0
        brown_ratio_in_plant = (np.count_nonzero(brown_mask) / plant_pixels) * 100.0
    else:
        green_ratio_in_plant = 0.0
        yellow_ratio_in_plant = 0.0
        brown_ratio_in_plant = 0.0

    green_contribution = min(green_ratio_in_plant * 0.60, 55.0)
    stress_penalty = yellow_ratio_in_plant * 0.45 + brown_ratio_in_plant * 0.70
    vigor_contribution = vigor_index * 0.20
    coverage_contribution = min(coverage_pct * 0.25, 20.0)

    health_score = max(0.0, min(100.0,
        green_contribution - stress_penalty + vigor_contribution + coverage_contribution
    ))

    # ── Probabilidad de estrés hídrico ────────────────────────────────────────
    hydric_stress = min(1.0, (
        yellow_pct * 0.035 +
        brown_pct * 0.045 +
        max(0.0, (25.0 - green_pct) * 0.015)
    ))

    # ── Estadio de crecimiento ────────────────────────────────────────────────
    if coverage_pct < 10:
        growth_stage = GrowthStage.SEEDLING
    elif coverage_pct < 30:
        growth_stage = GrowthStage.GROWING
    elif health_score < 35:
        growth_stage = GrowthStage.DECLINING
    else:
        growth_stage = GrowthStage.MATURE

    # ── Estado de salud categórico ────────────────────────────────────────────
    if health_score >= 80:
        status = HealthStatus.EXCELLENT
    elif health_score >= 62:
        status = HealthStatus.GOOD
    elif health_score >= 42:
        status = HealthStatus.MODERATE
    elif health_score >= 22:
        status = HealthStatus.STRESSED
    else:
        status = HealthStatus.CRITICAL

    # ── Generación de notas agronómicas ───────────────────────────────────────
    notes = _generate_notes(
        species=species,
        health_score=health_score,
        green_pct=green_pct,
        yellow_pct=yellow_pct,
        brown_pct=brown_pct,
        hydric_stress=hydric_stress,
        coverage=coverage_pct,
        growth_stage=growth_stage,
        seg_res=seg_res,
        segmentation_used=segmentation_used,
    )

    # ── Codificación de imagen anotada (overlay) ──────────────────────────────
    annotated_bytes: Optional[bytes] = None
    if seg_res.annotated_image is not None:
        success, enc = cv2.imencode(".jpg", seg_res.annotated_image, [int(cv2.IMWRITE_JPEG_QUALITY), 88])
        if success:
            annotated_bytes = enc.tobytes()

    return PlantAnalysisResult(
        health_score=round(health_score, 1),
        health_status=status,
        growth_stage=growth_stage,
        green_coverage=round(green_pct, 1),
        yellow_coverage=round(yellow_pct, 1),
        brown_coverage=round(brown_pct, 1),
        estimated_leaf_count=estimated_leaf_count,
        hydric_stress_probability=round(hydric_stress, 3),
        vigor_index=round(vigor_index, 1),
        notes=notes,
        annotated_image_bytes=annotated_bytes,
        segmentation_used=segmentation_used,
        instances_count=instances_count,
    )


def _generate_notes(
    species: str,
    health_score: float,
    green_pct: float,
    yellow_pct: float,
    brown_pct: float,
    hydric_stress: float,
    coverage: float,
    growth_stage: GrowthStage,
    seg_res: YOLOSegmentationResult,
    segmentation_used: bool,
) -> list[str]:
    notes: list[str] = []

    # Información sobre el modelo de IA YOLO-seg
    if segmentation_used:
        notes.append(
            f"🧠 YOLO-seg ({seg_res.model_name}): {seg_res.num_instances} instancia(s) segmentada(s) con confianza promedio del {seg_res.avg_confidence * 100:.1f}%."
        )
    else:
        notes.append("ℹ️ Análisis adaptativo por segmentación colorimétrica y contraste.")

    if health_score >= 80:
        notes.append("Planta en excelente estado fitosanitario.")
    elif health_score >= 62:
        notes.append("Planta con buena salud general.")
    elif health_score >= 42:
        notes.append("Estado de salud moderado, monitorear de cerca.")
    elif health_score >= 22:
        notes.append("Planta bajo estrés significativo, requiere atención.")
    else:
        notes.append("Estado crítico: intervención inmediata necesaria.")

    if hydric_stress > 0.55:
        notes.append("Alto riesgo de estrés hídrico detectado por análisis foliar.")
    elif hydric_stress > 0.30:
        notes.append("Signos leves a moderados de estrés hídrico.")

    if yellow_pct > 15:
        notes.append(f"Amarillamiento notable ({yellow_pct:.1f}%): posible déficit hídrico o clorosis.")
    if brown_pct > 10:
        notes.append(f"Follaje pardo ({brown_pct:.1f}%): puede indicar necrosis o daño radicular.")
    if green_pct < 10 and coverage > 5:
        notes.append("Baja proporción de follaje verde activo.")

    stage_labels = {
        GrowthStage.SEEDLING: "Plántula/semilla en estadio temprano.",
        GrowthStage.GROWING: "Planta en fase de crecimiento activo.",
        GrowthStage.MATURE: "Planta en estadio maduro.",
        GrowthStage.DECLINING: "Posible senescencia o deterioro.",
    }
    notes.append(stage_labels[growth_stage])

    return notes
