import base64
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, Query, UploadFile

from backend.config import settings
from backend.ml.config.ml_config import SUPPORTED_CROPS
from backend.ml.preprocessing.image_processor import validate_and_preprocess_image
from backend.ml.inference.production_engine import inference_engine
from backend.db.database import db

router = APIRouter(prefix="/diagnosis", tags=["Crop Diagnostics"])


@router.post("/analyze")
async def analyze_crop_leaf(
    image: UploadFile = File(...),
    cropType: str = Form("Tomato"),
    userId: Optional[str] = Form("anonymous_farmer"),
):
    """Validate, diagnose, and persist a crop-leaf analysis.

    The endpoint never substitutes a fabricated disease for an unsupported crop
    or low-confidence prediction.
    """
    if not image.filename:
        raise HTTPException(status_code=400, detail="Image filename is required.")

    ext = image.filename.rsplit(".", 1)[-1].lower() if "." in image.filename else ""
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported image type '.{ext}'. Allowed: {', '.join(sorted(settings.ALLOWED_EXTENSIONS))}.",
        )

    contents = await image.read()
    max_bytes = settings.MAX_IMAGE_SIZE_MB * 1024 * 1024
    if len(contents) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"Image exceeds the {settings.MAX_IMAGE_SIZE_MB} MB upload limit.",
        )

    val_result = validate_and_preprocess_image(contents, image.filename)
    if not val_result.is_valid:
        raise HTTPException(status_code=400, detail=val_result.error_message)

    prediction = inference_engine.analyze(val_result.pil_image, cropType)

    mime = "jpeg" if ext == "jpg" else ext
    prediction["imageUrl"] = f"data:image/{mime};base64,{base64.b64encode(contents).decode('utf-8')}"
    prediction["userId"] = userId or "anonymous_farmer"
    prediction["warnings"] = val_result.warnings

    confidence = float(prediction.get("confidence", 0.0))
    abstain = bool(prediction.get("uncertainty", {}).get("abstain", False))
    prediction["is_low_confidence"] = abstain or confidence < settings.AI_CONFIDENCE_THRESHOLD
    prediction["condition_label"] = (
        "Uncertain Result" if prediction["is_low_confidence"] else prediction.get("condition", "Analyzed")
    )

    if prediction["is_low_confidence"]:
        prediction["low_confidence_notice"] = (
            f"The AI result is not reliable enough to use as a definitive diagnosis. "
            f"Current confidence: {round(confidence * 100)}%. "
            "Retake a sharp, well-lit close-up photo or consult a local agricultural expert."
        )

    # Do not persist a base64 image indefinitely when the database implementation
    # supports a record without the preview. Keep compatibility for the current UI.
    saved_doc = db.save_diagnosis(prediction)

    return {
        "success": True,
        "diagnosis": saved_doc,
        "warnings": val_result.warnings,
    }


@router.get("/history")
async def get_diagnosis_history(crop: Optional[str] = Query(None)):
    history = db.get_history(crop_filter=crop)
    return {"success": True, "total": len(history), "history": history}


@router.get("/{diag_id}")
async def get_diagnosis_item(diag_id: str):
    item = db.get_diagnosis_by_id(diag_id)
    if not item:
        raise HTTPException(status_code=404, detail=f"Diagnosis with ID '{diag_id}' not found.")
    return {"success": True, "diagnosis": item}


@router.delete("/{diag_id}")
async def delete_diagnosis_item(diag_id: str):
    deleted = db.delete_diagnosis(diag_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Diagnosis with ID '{diag_id}' not found or already deleted.")
    return {"success": True, "message": f"Diagnosis '{diag_id}' successfully removed."}
