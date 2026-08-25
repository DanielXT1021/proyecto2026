from fastapi import APIRouter
from app.api.endpoints import plants, analysis

api_router = APIRouter()
api_router.include_router(plants.router)
api_router.include_router(analysis.router)
