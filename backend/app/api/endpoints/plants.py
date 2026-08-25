from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import Plant, Species
from app.schemas.schemas import PlantCreate, PlantUpdate, PlantOut, PlantSummaryOut

router = APIRouter(prefix="/plants", tags=["plants"])


@router.get("/", response_model=list[PlantSummaryOut])
def list_plants(db: Session = Depends(get_db)):
    plants = db.query(Plant).order_by(Plant.created_at.desc()).all()
    result = []
    for plant in plants:
        latest_score = None
        latest_status = None
        images_sorted = sorted(plant.images, key=lambda i: i.captured_at, reverse=True)
        for img in images_sorted:
            if img.analysis:
                latest_score = img.analysis.health_score
                latest_status = img.analysis.health_status
                break
        result.append(PlantSummaryOut(
            id=plant.id,
            name=plant.name,
            species=plant.species,
            description=plant.description,
            location=plant.location,
            created_at=plant.created_at,
            latest_health_score=latest_score,
            latest_health_status=latest_status,
            image_count=len(plant.images),
        ))
    return result


@router.post("/", response_model=PlantOut, status_code=201)
def create_plant(data: PlantCreate, db: Session = Depends(get_db)):
    plant = Plant(**data.model_dump())
    db.add(plant)
    db.commit()
    db.refresh(plant)
    return plant


@router.get("/{plant_id}", response_model=PlantOut)
def get_plant(plant_id: int, db: Session = Depends(get_db)):
    plant = db.query(Plant).filter(Plant.id == plant_id).first()
    if not plant:
        raise HTTPException(status_code=404, detail="Planta no encontrada")
    return plant


@router.put("/{plant_id}", response_model=PlantOut)
def update_plant(plant_id: int, data: PlantUpdate, db: Session = Depends(get_db)):
    plant = db.query(Plant).filter(Plant.id == plant_id).first()
    if not plant:
        raise HTTPException(status_code=404, detail="Planta no encontrada")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(plant, field, value)
    db.commit()
    db.refresh(plant)
    return plant


@router.delete("/{plant_id}", status_code=204)
def delete_plant(plant_id: int, db: Session = Depends(get_db)):
    plant = db.query(Plant).filter(Plant.id == plant_id).first()
    if not plant:
        raise HTTPException(status_code=404, detail="Planta no encontrada")
    db.delete(plant)
    db.commit()
