from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./vivero_ia.db"
    UPLOADS_DIR: str = "uploads"
    MAX_IMAGE_SIZE_MB: int = 10
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = True

    model_config = {"env_file": ".env", "case_sensitive": True}


settings = Settings()
