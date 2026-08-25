import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Agri Nirvana - Crop AI Health Diagnostic API"
    VERSION: str = "3.0.0"
    API_V1_STR: str = "/api/v1"

    AI_MODEL_PROVIDER: str = os.getenv("AI_MODEL_PROVIDER", "real")
    AI_CONFIDENCE_THRESHOLD: float = float(os.getenv("AI_CONFIDENCE_THRESHOLD", "0.70"))
    HF_MODEL_ID: str = os.getenv(
        "HF_MODEL_ID",
        "linkanjarad/mobilenet_v2_1.0_224-plant-disease-identification",
    )

    MAX_IMAGE_SIZE_MB: int = int(os.getenv("MAX_IMAGE_SIZE_MB", "10"))
    ALLOWED_EXTENSIONS: set[str] = {"jpg", "jpeg", "png", "webp"}
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "backend/uploads")

    MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017/agri_nirvana")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "agri_nirvana")
    SQLITE_FALLBACK_DB: str = os.getenv("SQLITE_FALLBACK_DB", "backend/db/history.db")

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
