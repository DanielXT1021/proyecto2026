import os
import aiofiles
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.models import Plant, PlantImage, AnalysisResult, WateringRecommendation
from app.schemas.schemas import AnalysisResultOut, AnalysisResponse
from app.services.image_processor import save_upload
from app.services.ml_analyzer import analyze_plant_image
from app.services.recommendation_engine import generate_recommendation

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.post("/analyze", response_model=AnalysisResponse, status_code=201)
async def analyze_image(
    file: UploadFile = File(...),
    plant_id: int = Form(...),
    source: str = Form("mobile"),
    db: Session = Depends(get_db),
):
    plant = db.query(Plant).filter(Plant.id == plant_id).first()
    if not plant:
        raise HTTPException(status_code=404, detail="Planta no encontrada")

    filename, image_bytes = await save_upload(file)

    plant_image = PlantImage(plant_id=plant_id, image_filename=filename, source=source)
    db.add(plant_image)
    db.flush()

    result = analyze_plant_image(image_bytes, species=plant.species.value)

    # Guardar imagen con overlay de segmentación YOLO-seg si existe
    if result.annotated_image_bytes and settings.SAVE_SEGMENTATION_OVERLAY:
        try:
            seg_path = os.path.join(settings.UPLOADS_DIR, f"seg_{filename}")
            async with aiofiles.open(seg_path, "wb") as f:
                await f.write(result.annotated_image_bytes)
        except Exception:
            pass

    analysis_row = AnalysisResult(
        image_id=plant_image.id,
        health_score=result.health_score,
        health_status=result.health_status.value,
        growth_stage=result.growth_stage.value,
        green_coverage=result.green_coverage,
        yellow_coverage=result.yellow_coverage,
        brown_coverage=result.brown_coverage,
        estimated_leaf_count=result.estimated_leaf_count,
        hydric_stress_probability=result.hydric_stress_probability,
        vigor_index=result.vigor_index,
        notes=result.notes,
    )
    db.add(analysis_row)
    db.flush()

    rec = generate_recommendation(plant.species.value, result)
    rec_row = WateringRecommendation(
        analysis_id=analysis_row.id,
        water_amount_ml=rec.water_amount_ml,
        frequency_days=rec.frequency_days,
        next_watering=rec.next_watering,
        urgency=rec.urgency,
        actions=rec.actions,
        care_tips=rec.care_tips,
    )
    db.add(rec_row)
    db.commit()
    db.refresh(analysis_row)

    return AnalysisResponse(
        plant_id=plant_id,
        image_id=plant_image.id,
        analysis=AnalysisResultOut.model_validate(analysis_row),
    )


@router.get("/plant/{plant_id}", response_model=list[AnalysisResultOut])
def get_plant_history(plant_id: int, limit: int = 20, db: Session = Depends(get_db)):
    """Retorna el historial cronológico de análisis de una planta."""
    plant = db.query(Plant).filter(Plant.id == plant_id).first()
    if not plant:
        raise HTTPException(status_code=404, detail="Planta no encontrada")

    results = (
        db.query(AnalysisResult)
        .join(PlantImage)
        .filter(PlantImage.plant_id == plant_id)
        .order_by(AnalysisResult.analyzed_at.desc())
        .limit(limit)
        .all()
    )
    return results


@router.get("/{analysis_id}", response_model=AnalysisResultOut)
def get_analysis(analysis_id: int, db: Session = Depends(get_db)):
    analysis = db.query(AnalysisResult).filter(AnalysisResult.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Análisis no encontrado")
    return analysis
