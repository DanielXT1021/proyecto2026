from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from app.models.models import Species


# ── Plant schemas ──────────────────────────────────────────────────────────────

class PlantCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    species: Species
    description: Optional[str] = None
    location: Optional[str] = None


class PlantUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    location: Optional[str] = None


class WateringRecommendationOut(BaseModel):
    id: int
    water_amount_ml: int
    frequency_days: float
    next_watering: datetime
    urgency: str
    actions: list[str]
    care_tips: list[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class AnalysisResultOut(BaseModel):
    id: int
    image_id: int
    health_score: float
    health_status: str
    growth_stage: str
    green_coverage: float
    yellow_coverage: float
    brown_coverage: float
    estimated_leaf_count: int
    hydric_stress_probability: float
    vigor_index: float
    notes: list[str]
    analyzed_at: datetime
    recommendation: Optional[WateringRecommendationOut] = None

    model_config = {"from_attributes": True}


class PlantImageOut(BaseModel):
    id: int
    image_filename: str
    captured_at: datetime
    source: str
    analysis: Optional[AnalysisResultOut] = None

    model_config = {"from_attributes": True}


class PlantOut(BaseModel):
    id: int
    name: str
    species: Species
    description: Optional[str]
    location: Optional[str]
    created_at: datetime
    images: list[PlantImageOut] = []

    model_config = {"from_attributes": True}


class PlantSummaryOut(BaseModel):
    id: int
    name: str
    species: Species
    description: Optional[str]
    location: Optional[str]
    created_at: datetime
    latest_health_score: Optional[float] = None
    latest_health_status: Optional[str] = None
    image_count: int = 0

    model_config = {"from_attributes": True}


# ── Analysis response ──────────────────────────────────────────────────────────

class AnalysisResponse(BaseModel):
    plant_id: int
    image_id: int
    analysis: AnalysisResultOut
