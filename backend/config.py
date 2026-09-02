from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Agri Nirvana - Crop AI Health Diagnostic API"
    VERSION: str = "4.1.0"
    API_V1_STR: str = "/api/v1"

    AI_MODEL_PROVIDER: str = "real"
    AI_CONFIDENCE_THRESHOLD: float = Field(default=0.70, ge=0.50, le=0.95)
    AI_MIN_TOP2_MARGIN: float = Field(default=0.10, ge=0.0, le=0.50)
    AI_MAX_NORMALIZED_ENTROPY: float = Field(default=0.90, ge=0.0, le=1.0)
    AI_MIN_CROP_PROBABILITY_MASS: float = Field(default=0.45, ge=0.0, le=1.0)
    AI_REQUIRE_LOCAL_CHECKPOINT: bool = True

    # Single production architecture/checkpoint. No silent model substitution.
    LOCAL_TRAINED_MODEL_PATH: str = "backend/ml/models/weights/agri_nirvana_efficientnet_v2_s.pt"

    AI_CHAT_MODEL: str = "openai/gpt-oss-120b:fastest"
    AI_CHAT_ALLOWED_MODELS: str = "openai/gpt-oss-120b:fastest,deepseek-ai/DeepSeek-V3-0324:fastest,Qwen/Qwen2.5-7B-Instruct-1M:fastest"

    MAX_IMAGE_SIZE_MB: int = Field(default=10, ge=1, le=25)
    ALLOWED_EXTENSIONS: set[str] = {"jpg", "jpeg", "png", "webp"}
    UPLOAD_DIR: str = "backend/uploads"

    MONGODB_URI: str = "mongodb://localhost:27017/agri_nirvana"
    DATABASE_NAME: str = "agri_nirvana"
    SQLITE_FALLBACK_DB: str = "backend/db/history.db"

    ALLOWED_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173,https://agri-nirvana.vercel.app"

    GEMINI_API_KEY: Optional[str] = None
    GEMINI_RATE_LIMIT_PER_MINUTE: int = 15
    GEMINI_MODEL: str = "gemini-1.5-flash"

    # Never ship a reusable production signing secret in source control.
    JWT_SECRET: str = ""
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
