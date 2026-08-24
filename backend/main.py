import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import settings
from backend.ml.config.ml_config import SUPPORTED_CROPS
from backend.ml.inference.engine import inference_engine

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "*"
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
from backend.routes.diagnosis import router as diagnosis_router
app.include_router(diagnosis_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {
        "status": "online",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "model_provider": inference_engine.provider_type,
        "models_loaded": inference_engine._models_loaded,
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
        "model_name": inference_engine.model_name,
        "model_version": inference_engine.model_version,
        "provider_type": inference_engine.provider_type,
        "is_mock": inference_engine.provider_type != "real" or not inference_engine._models_loaded,
        "models_loaded": inference_engine._models_loaded,
        "confidence_threshold": settings.AI_CONFIDENCE_THRESHOLD,
        "max_image_size_mb": settings.MAX_IMAGE_SIZE_MB
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
