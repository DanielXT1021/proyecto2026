from datetime import datetime, timedelta
from dataclasses import dataclass, field

from app.services.ml_analyzer import PlantAnalysisResult, HealthStatus


# Parámetros hídricos y de cuidado por especie
_SPECIES_CONFIG: dict[str, dict] = {
    "hortaliza": {
        "display_name": "Hortaliza",
        "base_water_ml": 450,
        "base_frequency_days": 1.0,
        "drought_tolerance": 0.2,
        "care_tips": [
            "Mantener el sustrato uniformemente húmedo en las primeras etapas.",
            "Regar preferentemente en horas de la mañana para reducir evaporación.",
            "Evitar encharcamiento: puede provocar pudrición radicular.",
            "En días muy calurosos, aumentar la frecuencia de riego.",
        ],
    },
    "quinoa": {
        "display_name": "Quinoa",
        "base_water_ml": 300,
        "base_frequency_days": 2.0,
        "drought_tolerance": 0.55,
        "care_tips": [
            "La quinoa tolera períodos moderados de sequía una vez establecida.",
            "Regar cuando el sustrato superficial (2-3 cm) esté seco al tacto.",
            "Incrementar riego en etapa de floración y llenado de grano.",
            "Reducir frecuencia durante la maduración para favorecer la cosecha.",
        ],
    },
    "quillay": {
        "display_name": "Quillay",
        "base_water_ml": 150,
        "base_frequency_days": 5.0,
        "drought_tolerance": 0.90,
        "care_tips": [
            "Especie nativa xerófita con alta tolerancia a la sequía.",
            "Evitar el riego excesivo una vez establecido el árbol.",
            "Regar profundamente pero con poca frecuencia para favorecer raíces profundas.",
            "No regar durante el invierno si hay lluvias regulares.",
        ],
    },
    "lavanda": {
        "display_name": "Lavanda",
        "base_water_ml": 200,
        "base_frequency_days": 3.0,
        "drought_tolerance": 0.70,
        "care_tips": [
            "La lavanda prefiere suelos bien drenados; evitar acumulación de agua.",
            "Regar directamente en la base, sin mojar el follaje.",
            "Reducir drásticamente el riego en invierno.",
            "En verano caluroso puede requerir riego cada 2 días si está recién plantada.",
        ],
    },
}


@dataclass
class WateringRecommendationData:
    water_amount_ml: int
    frequency_days: float
    next_watering: datetime
    urgency: str
    actions: list[str] = field(default_factory=list)
    care_tips: list[str] = field(default_factory=list)


def generate_recommendation(
    species: str,
    analysis: PlantAnalysisResult,
) -> WateringRecommendationData:
    """
    Genera recomendaciones de riego estimadas basadas en el análisis visual
    de la planta y los parámetros específicos de la especie.
    """
    cfg = _SPECIES_CONFIG.get(species, _SPECIES_CONFIG["hortaliza"])
    stress = analysis.hydric_stress_probability
    score = analysis.health_score

    # Ajuste de cantidad de agua según nivel de estrés
    if stress > 0.60:
        water_factor = 1.40
    elif stress > 0.35:
        water_factor = 1.20
    elif score > 80:
        water_factor = 0.90  # planta sana, ajuste conservador
    else:
        water_factor = 1.0

    water_amount_ml = int(cfg["base_water_ml"] * water_factor)

    # Ajuste de frecuencia según salud y tolerancia a sequía
    tolerance = cfg["drought_tolerance"]

    if analysis.health_status == HealthStatus.CRITICAL:
        freq_factor = 0.40
        urgency = "immediate"
    elif analysis.health_status == HealthStatus.STRESSED:
        freq_factor = 0.60
        urgency = "soon"
    elif analysis.health_status == HealthStatus.MODERATE:
        freq_factor = 0.85
        urgency = "normal"
    elif analysis.health_status == HealthStatus.EXCELLENT and tolerance > 0.5:
        freq_factor = 1.30
        urgency = "normal"
    else:
        freq_factor = 1.0
        urgency = "normal"

    frequency_days = max(0.5, cfg["base_frequency_days"] * freq_factor)
    next_watering = datetime.utcnow() + timedelta(days=frequency_days)

    actions = _build_action_list(species, analysis, urgency, water_amount_ml, frequency_days)

    return WateringRecommendationData(
        water_amount_ml=water_amount_ml,
        frequency_days=round(frequency_days, 1),
        next_watering=next_watering,
        urgency=urgency,
        actions=actions,
        care_tips=cfg["care_tips"],
    )


def _build_action_list(
    species: str,
    analysis: PlantAnalysisResult,
    urgency: str,
    water_ml: int,
    freq_days: float,
) -> list[str]:
    actions: list[str] = []
    cfg = _SPECIES_CONFIG.get(species, _SPECIES_CONFIG["hortaliza"])
    name = cfg["display_name"]

    if urgency == "immediate":
        actions.append(f"⚠️ Regar inmediatamente con aproximadamente {water_ml} ml.")
        actions.append("Revisar el sustrato: puede presentar sequedad severa.")
    elif urgency == "soon":
        actions.append(f"Regar pronto con aproximadamente {water_ml} ml.")
        actions.append(f"Próxima frecuencia recomendada: cada {freq_days:.1f} días.")
    else:
        actions.append(f"Regar según la frecuencia habitual para {name}: cada {freq_days:.1f} días.")
        actions.append(f"Cantidad estimada por sesión de riego: {water_ml} ml.")

    if analysis.yellow_coverage > 12:
        actions.append("Verificar posible carencia de nitrógeno o hierro (clorosis).")
    if analysis.brown_coverage > 8:
        actions.append("Revisar drenaje para descartar pudrición por exceso de humedad.")
    if analysis.green_coverage < 15 and analysis.growth_stage.value == "mature":
        actions.append("Evaluar el estado nutricional del sustrato (puede requerir fertilización).")

    return actions
