import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from backend.config import settings
from backend.routes.diagnosis import router as diagnosis_router
from backend.ml.config.ml_config import SUPPORTED_CROPS
from backend.ml.inference.engine import inference_engine

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS configuration
cors_origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins or ["http://localhost:5173"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static uploads hosting
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Register routers
app.include_router(diagnosis_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {
        "status": "online",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "model_provider": inference_engine.provider_type,
        "confidence_threshold": inference_engine.threshold
    }

@app.get(f"{settings.API_V1_STR}/crops")
async def get_supported_crops():
    """
    Returns list of supported crops configuration.
    """
    return {
        "success": True,
        "crops": SUPPORTED_CROPS
    }

@app.get(f"{settings.API_V1_STR}/model/status")
async def get_model_status():
    """
    Returns active ML model status, version, and provider info.
    """
    return {
        "success": True,
        "model_name": inference_engine.model.model_name,
        "model_version": inference_engine.model.model_version,
        "provider_type": inference_engine.provider_type,
        "is_mock": getattr(inference_engine.model, "is_mock", True if inference_engine.provider_type == "mock" else False),
        "model_loaded": getattr(inference_engine.model, "model_loaded", None),
        "model_checkpoint_path": getattr(inference_engine.model, "checkpoint_path", None),
        "confidence_threshold": settings.AI_CONFIDENCE_THRESHOLD,
        "max_image_size_mb": settings.MAX_IMAGE_SIZE_MB
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
