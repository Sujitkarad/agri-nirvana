import os
import base64
from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Query
from typing import Optional
from backend.config import settings
from backend.ml.config.ml_config import SUPPORTED_CROPS
from backend.ml.preprocessing.image_processor import validate_and_preprocess_image
from backend.ml.inference.engine import inference_engine
from backend.db.database import db

router = APIRouter(prefix="/diagnosis", tags=["Crop Diagnostics"])

@router.post("/analyze")
async def analyze_crop_leaf(
    image: UploadFile = File(...),
    cropType: str = Form("Tomato"),
    userId: Optional[str] = Form("anonymous_farmer")
):
    """
    Uploads a crop leaf image, validates quality (blur/darkness/resolution),
    runs computer-vision prediction, evaluates confidence against threshold, and saves result.
    """
    contents = await image.read()

    # 1. Quality Validation & Preprocessing
    val_result = validate_and_preprocess_image(contents, image.filename)
    if not val_result.is_valid:
        raise HTTPException(status_code=400, detail=val_result.error_message)

    # 2. Convert Image for Storage Preview
    encoded_b64 = base64.b64encode(contents).decode("utf-8")
    ext = image.filename.split(".")[-1].lower() if "." in image.filename else "jpeg"
    data_url = f"data:image/{ext};base64,{encoded_b64}"

    # 3. ML Computer Vision Inference
    prediction = inference_engine.analyze(val_result.pil_image, cropType)
    prediction["imageUrl"] = data_url
    prediction["userId"] = userId
    prediction["warnings"] = val_result.warnings

    # 4. Save Record to History Database
    saved_doc = db.save_diagnosis(prediction)

    return {
        "success": True,
        "diagnosis": saved_doc,
        "warnings": val_result.warnings
    }

@router.get("/history")
async def get_diagnosis_history(crop: Optional[str] = Query(None)):
    """
    Retrieves stored diagnosis records for the user. Supports optional crop filtering.
    """
    history = db.get_history(crop_filter=crop)
    return {
        "success": True,
        "total": len(history),
        "history": history
    }

@router.get("/{diag_id}")
async def get_diagnosis_item(diag_id: str):
    """
    Fetches detailed single diagnosis record by ID.
    """
    item = db.get_diagnosis_by_id(diag_id)
    if not item:
        raise HTTPException(status_code=404, detail=f"Diagnosis with ID '{diag_id}' not found.")
    return {"success": True, "diagnosis": item}

@router.delete("/{diag_id}")
async def delete_diagnosis_item(diag_id: str):
    """
    Deletes diagnosis item from history.
    """
    deleted = db.delete_diagnosis(diag_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Diagnosis with ID '{diag_id}' not found or already deleted.")
    return {"success": True, "message": f"Diagnosis '{diag_id}' successfully removed."}
