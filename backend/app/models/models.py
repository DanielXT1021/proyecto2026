from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON, Enum as SAEnum
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class Species(str, enum.Enum):
    HORTALIZA = "hortaliza"
    QUINOA = "quinoa"
    QUILLAY = "quillay"
    LAVANDA = "lavanda"


class Plant(Base):
    __tablename__ = "plants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    species = Column(SAEnum(Species), nullable=False)
    description = Column(Text, nullable=True)
    location = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    images = relationship("PlantImage", back_populates="plant", cascade="all, delete-orphan")


class PlantImage(Base):
    __tablename__ = "plant_images"

    id = Column(Integer, primary_key=True, index=True)
    plant_id = Column(Integer, ForeignKey("plants.id"), nullable=False)
    image_filename = Column(String(255), nullable=False)
    captured_at = Column(DateTime, default=datetime.utcnow)
    source = Column(String(50), default="mobile")

    plant = relationship("Plant", back_populates="images")
    analysis = relationship("AnalysisResult", back_populates="image", uselist=False, cascade="all, delete-orphan")


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, index=True)
    image_id = Column(Integer, ForeignKey("plant_images.id"), nullable=False)
    health_score = Column(Float, nullable=False)
    health_status = Column(String(20), nullable=False)
    growth_stage = Column(String(20), nullable=False)
    green_coverage = Column(Float)
    yellow_coverage = Column(Float)
    brown_coverage = Column(Float)
    estimated_leaf_count = Column(Integer)
    hydric_stress_probability = Column(Float)
    vigor_index = Column(Float)
    notes = Column(JSON)
    analyzed_at = Column(DateTime, default=datetime.utcnow)

    image = relationship("PlantImage", back_populates="analysis")
    recommendation = relationship(
        "WateringRecommendation", back_populates="analysis", uselist=False, cascade="all, delete-orphan"
    )


class WateringRecommendation(Base):
    __tablename__ = "watering_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("analysis_results.id"), nullable=False)
    water_amount_ml = Column(Integer)
    frequency_days = Column(Float)
    next_watering = Column(DateTime)
    urgency = Column(String(20))
    actions = Column(JSON)
    care_tips = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    analysis = relationship("AnalysisResult", back_populates="recommendation")
