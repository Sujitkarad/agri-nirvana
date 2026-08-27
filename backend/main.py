from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.ml.config.ml_config import SUPPORTED_CROPS
from backend.ml.inference.production_engine import inference_engine

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

configured_origins = [
    origin.strip()
    for origin in settings.ALLOWED_ORIGINS.split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=configured_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

from backend.routes.diagnosis import router as diagnosis_router
from backend.routes.field_intelligence import router as field_intelligence_router

app.include_router(diagnosis_router, prefix=settings.API_V1_STR)
app.include_router(field_intelligence_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["Health"])
async def root():
    return {
        "status": "online",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "model_provider": inference_engine.provider_type,
        "models_loaded": inference_engine.models_loaded,
        "model_name": inference_engine.model_name,
        "model_version": inference_engine.model_version,
        "confidence_threshold": inference_engine.threshold,
    }


@app.get("/health", tags=["Health"])
async def health():
    return {
        "status": "ok",
        "model_ready": inference_engine.models_loaded,
        "model_provider": inference_engine.provider_type,
    }


@app.get(f"{settings.API_V1_STR}/crops")
async def get_supported_crops():
    from backend.ml.models.disease_classifier import normalize_crop_name

    model_crops = set(inference_engine.supported_crops())
    normalized_model_crops = {normalize_crop_name(c).lower() for c in model_crops}
    crops = [
        crop
        for crop in SUPPORTED_CROPS
        if normalize_crop_name(crop["id"]).lower() in normalized_model_crops
    ]
    return {
        "success": True,
        "crops": crops,
        "model_supported_crops": sorted(model_crops),
    }


@app.get(f"{settings.API_V1_STR}/model/status")
async def get_model_status():
    return {
        "success": True,
        "model_name": inference_engine.model_name,
        "model_version": inference_engine.model_version,
        "provider_type": inference_engine.provider_type,
        "is_mock": inference_engine.is_mock,
        "models_loaded": inference_engine.models_loaded,
        "confidence_threshold": inference_engine.threshold,
        "max_image_size_mb": settings.MAX_IMAGE_SIZE_MB,
        "supported_crops": inference_engine.supported_crops(),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
