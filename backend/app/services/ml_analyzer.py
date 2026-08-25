import cv2
import numpy as np
from dataclasses import dataclass, field
from enum import Enum


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


def analyze_plant_image(image_bytes: bytes, species: str = "hortaliza") -> PlantAnalysisResult:
    """
    Analiza una imagen de planta usando visión computacional (OpenCV).
    Extrae métricas de color, cobertura vegetal y signos de estrés hídrico.
    """
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img is None:
        raise ValueError("No se pudo decodificar la imagen")

    # Redimensionar para análisis uniforme
    img = cv2.resize(img, (640, 480))
    total_pixels = img.shape[0] * img.shape[1]

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # ── Segmentación por color en espacio HSV ──────────────────────────────────
    # Verde (vegetación sana): H [35-85], S y V altos
    green_mask = cv2.inRange(hsv, (35, 30, 30), (85, 255, 255))

    # Amarillo (estrés hídrico temprano): H [20-35]
    yellow_mask = cv2.inRange(hsv, (20, 50, 50), (35, 255, 255))

    # Marrón/pardo (daño o necrosis): H [10-20]
    brown_mask = cv2.inRange(hsv, (8, 30, 20), (20, 200, 200))

    # Aplicar apertura morfológica para eliminar ruido
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    green_mask = cv2.morphologyEx(green_mask, cv2.MORPH_OPEN, kernel)
    yellow_mask = cv2.morphologyEx(yellow_mask, cv2.MORPH_OPEN, kernel)
    brown_mask = cv2.morphologyEx(brown_mask, cv2.MORPH_OPEN, kernel)

    green_pct = np.count_nonzero(green_mask) / total_pixels * 100
    yellow_pct = np.count_nonzero(yellow_mask) / total_pixels * 100
    brown_pct = np.count_nonzero(brown_mask) / total_pixels * 100

    # ── Cobertura total de vegetación ─────────────────────────────────────────
    plant_mask = cv2.bitwise_or(green_mask, cv2.bitwise_or(yellow_mask, brown_mask))
    coverage_pct = np.count_nonzero(plant_mask) / total_pixels * 100

    # ── Índice de textura (varianza Laplaciana = vigor foliar) ─────────────────
    plant_gray = cv2.bitwise_and(gray, gray, mask=plant_mask)
    laplacian = cv2.Laplacian(plant_gray.astype(np.float64), cv2.CV_64F)
    texture_var = float(np.var(laplacian[plant_mask > 0])) if np.any(plant_mask > 0) else 0.0

    # Normalizar vigor: escala 0-100
    vigor_index = min(texture_var / 80.0, 100.0)

    # ── Conteo estimado de hojas por análisis de contornos ────────────────────
    edges = cv2.Canny(plant_gray, 25, 90)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    min_area = total_pixels * 0.0015
    leaf_like = [c for c in contours if cv2.contourArea(c) > min_area]
    estimated_leaf_count = min(len(leaf_like), 200)

    # ── Puntaje de salud (0-100) ───────────────────────────────────────────────
    green_contribution = min(green_pct * 1.4, 55.0)
    stress_penalty = yellow_pct * 1.8 + brown_pct * 2.5
    vigor_contribution = vigor_index * 0.20
    coverage_contribution = min(coverage_pct * 0.25, 20.0)

    health_score = max(0.0, min(100.0,
        green_contribution - stress_penalty + vigor_contribution + coverage_contribution
    ))

    # ── Probabilidad de estrés hídrico ────────────────────────────────────────
    hydric_stress = min(1.0, yellow_pct * 0.035 + brown_pct * 0.045 + max(0, (30 - green_pct) * 0.015))

    # ── Estadio de crecimiento ────────────────────────────────────────────────
    if coverage_pct < 10:
        growth_stage = GrowthStage.SEEDLING
    elif coverage_pct < 30:
        growth_stage = GrowthStage.GROWING
    elif health_score < 35:
        growth_stage = GrowthStage.DECLINING
    else:
        growth_stage = GrowthStage.MATURE

    # ── Estado de salud ───────────────────────────────────────────────────────
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

    notes = _generate_notes(
        species, health_score, green_pct, yellow_pct, brown_pct,
        hydric_stress, coverage_pct, growth_stage
    )

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
) -> list[str]:
    notes: list[str] = []

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
        notes.append("Alto riesgo de estrés hídrico detectado por análisis colorimétrico.")
    elif hydric_stress > 0.30:
        notes.append("Signos leves a moderados de estrés hídrico.")

    if yellow_pct > 15:
        notes.append(f"Amarillamiento notable ({yellow_pct:.1f}%): posible déficit hídrico o carencia nutricional.")
    if brown_pct > 10:
        notes.append(f"Follaje pardo ({brown_pct:.1f}%): puede indicar necrosis o daño por exceso de agua.")
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
