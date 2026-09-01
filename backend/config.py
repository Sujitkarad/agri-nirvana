import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Agri Nirvana - Crop AI Health Diagnostic API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "http://localhost:5173,https://agri-nirvana.vercel.app")
    
    # ML Model Configuration
    AI_MODEL_PROVIDER: str = os.getenv("AI_MODEL_PROVIDER", "mock")  # "mock" | "efficientnet"
    AI_MODEL_PATH: str = os.getenv("AI_MODEL_PATH", "backend/ml/models/checkpoints/efficientnet_b3.pth")
    AI_CONFIDENCE_THRESHOLD: float = float(os.getenv("AI_CONFIDENCE_THRESHOLD", "0.70"))
    API_ACCESS_KEY: str = os.getenv("API_ACCESS_KEY", "")
    
    # Image Upload Configuration
    MAX_IMAGE_SIZE_MB: int = int(os.getenv("MAX_IMAGE_SIZE_MB", "10"))
    ALLOWED_EXTENSIONS: set = {"jpg", "jpeg", "png", "webp"}
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "backend/uploads")
    
    # Inference / Observability
    INFERENCE_TIMEOUT_SECS: int = int(os.getenv("INFERENCE_TIMEOUT_SECS", "10"))
    METRICS_PORT: int = int(os.getenv("METRICS_PORT", "8001"))

    # Database Configuration
    MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017/agri_nirvana")
    DATABASE_NAME: str = "agri_nirvana"
    SQLITE_FALLBACK_DB: str = "backend/db/history.db"

    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "ignore"

settings = Settings()
