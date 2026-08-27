import base64
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, Query, UploadFile

from backend.config import settings
from backend.db.database import db
from backend.ml.config.disease_knowledge import DISEASE_KNOWLEDGE
from backend.ml.inference.dynamic_advisor import generate_dynamic_advisory
from backend.ml.inference.production_engine import inference_engine
from backend.ml.models.disease_classifier import normalize_crop_name
from backend.ml.preprocessing.image_processor import validate_and_preprocess_image

router = APIRouter(prefix="/diagnosis", tags=["Crop Diagnostics"])


def _persist_without_image(record: dict) -> dict:
    """Persist metadata only; never put a base64 image into SQLite history."""
    stored = dict(record)
    stored["imageUrl"] = ""
    return db.save_diagnosis(stored)


def _safe_user_id(user_id: Optional[str]) -> str:
    """Avoid storing an empty or whitespace-only identity value."""
    value = (user_id or "anonymous_farmer").strip()
    return value[:128] or "anonymous_farmer"


@router.post("/analyze")
async def analyze_crop_leaf(
    image: UploadFile = File(...),
    cropType: str = Form("Tomato"),
    userId: Optional[str] = Form("anonymous_farmer"),
):
    if not image.filename:
        raise HTTPException(status_code=400, detail="Image filename is required.")

    ext = image.filename.rsplit(".", 1)[-1].lower() if "." in image.filename else ""
    if ext not in settings.ALLOWED_EXTENSIONS:
        allowed = ", ".join(sorted(settings.ALLOWED_EXTENSIONS))
        raise HTTPException(status_code=400, detail=f"Unsupported image type '.{ext}'. Allowed: {allowed}.")

    contents = await image.read()
    max_bytes = settings.MAX_IMAGE_SIZE_MB * 1024 * 1024
    if len(contents) > max_bytes:
        raise HTTPException(status_code=413, detail=f"Image exceeds the {settings.MAX_IMAGE_SIZE_MB} MB upload limit.")
    if not contents:
        raise HTTPException(status_code=400, detail="The uploaded image is empty.")

    val_result = validate_and_preprocess_image(contents, image.filename)
    if not val_result.is_valid or val_result.pil_image is None:
        raise HTTPException(status_code=400, detail=val_result.error_message or "Unable to process image.")

    prediction = inference_engine.analyze(val_result.pil_image, cropType)
    confidence = max(0.0, min(float(prediction.get("confidence", 0.0)), 1.0))
    uncertainty = prediction.get("uncertainty") or {}
    abstain = bool(uncertainty.get("abstain", False))

    prediction["userId"] = _safe_user_id(userId)
    prediction["warnings"] = list(val_result.warnings or [])
    prediction["is_low_confidence"] = abstain or confidence < settings.AI_CONFIDENCE_THRESHOLD
    prediction["condition_label"] = (
        "Uncertain Result" if prediction["is_low_confidence"] else prediction.get("condition", "Analyzed")
    )
    prediction["provenance"] = {
        "source": "real_ml_inference" if prediction.get("status") == "success" else "abstention",
        "confidence_is_calibrated": False,
        "severity_is_independent": bool((prediction.get("severity") or {}).get("reliable", False)) if isinstance(prediction.get("severity"), dict) else False,
        "treatment_allowed": prediction.get("status") == "success" and not prediction["is_low_confidence"],
    }

    if prediction["is_low_confidence"]:
        prediction["low_confidence_notice"] = (
            "The AI result is not reliable enough to use as a definitive diagnosis. "
            f"Model score: {round(confidence * 100)}%. Retake a sharp, well-lit close-up photo "
            "or consult a local agricultural expert."
        )

    # The image is returned only for the current response; it is never persisted in history.
    mime = "jpeg" if ext == "jpg" else ext
    preview_url = f"data:image/{mime};base64,{base64.b64encode(contents).decode('utf-8')}"
    prediction["imageUrl"] = preview_url

    saved_doc = _persist_without_image(prediction)
    response_diagnosis = dict(saved_doc)
    response_diagnosis["imageUrl"] = preview_url

    return {"success": True, "diagnosis": response_diagnosis, "warnings": val_result.warnings}


@router.post("/symptoms")
async def analyze_crop_symptoms(
    cropType: str = Form("Tomato"),
    symptomsText: str = Form(...),
    userId: Optional[str] = Form("anonymous_farmer"),
):
    """Return a possible knowledge-base match; never present it as image diagnosis."""
    text = (symptomsText or "").strip()
    if len(text) < 5:
        raise HTTPException(status_code=400, detail="Please provide a more detailed symptom description.")
    if len(text) > 2000:
        raise HTTPException(status_code=413, detail="Symptom description is too long.")

    crop_name = normalize_crop_name(cropType)
    candidates = []
    text_lower = text.lower()
    for key, info in DISEASE_KNOWLEDGE.items():
        if normalize_crop_name(info.get("crop", "")).lower() != crop_name.lower():
            continue
        score = 0
        for symptom in info.get("symptoms_observed", []):
            for word in symptom.lower().split():
                cleaned = word.strip(".,;:()[]{}")
                if len(cleaned) >= 4 and cleaned in text_lower:
                    score += 1
        display_name = info.get("display_name", "")
        if display_name and display_name.lower() in text_lower:
            score += 3
        if score:
            candidates.append((score, key, info))

    candidates.sort(key=lambda item: item[0], reverse=True)
    user_id = _safe_user_id(userId)

    if not candidates:
        prediction = {
            "status": "uncertain",
            "is_valid_crop_image": False,
            "validation": {"is_plant": None, "is_crop": True, "crop_supported": crop_name in inference_engine.supported_crops(), "rejection_reason": None},
            "crop": {"name": crop_name, "confidence_pct": 0},
            "cropType": crop_name,
            "condition": "Insufficient Evidence",
            "confidence": 0.0,
            "confidence_pct": 0,
            "severity": "Unknown",
            "severityPercentage": 0,
            "symptoms": [text],
            "symptoms_observed": [],
            "differential_diagnoses": [],
            "uncertainty": {"abstain": True, "reason": "The reported symptoms did not match a sufficiently specific knowledge-base pattern."},
            "recommendations": {
                "immediate": "Do not apply disease-specific chemicals based on this symptom report alone.",
                "monitoring": "Take clear photos of affected leaves and record whether symptoms are spreading.",
                "prevention": "Continue routine scouting and avoid unnecessary pesticide application.",
                "expert_help": "Consult a local KVK/agriculture extension officer for confirmation.",
            },
            "modelName": "Agri Nirvana Symptom Knowledge Matcher",
            "modelVersion": "v4",
            "isMock": False,
            "userId": user_id,
            "warnings": ["Symptom-only matching is not a definitive diagnosis."],
            "is_low_confidence": True,
            "condition_label": "Uncertain Result",
            "provenance": {"source": "knowledge_base_matcher", "confidence_is_calibrated": False, "treatment_allowed": False},
        }
        saved = _persist_without_image(prediction)
        return {"success": True, "diagnosis": saved, "warnings": prediction["warnings"]}

    best_score, best_key, disease_info = candidates[0]
    # Evidence score, deliberately capped below a definitive threshold.
    confidence = min(0.89, 0.45 + best_score * 0.08)
    if len(candidates) > 1 and candidates[0][0] == candidates[1][0]:
        confidence = min(confidence, 0.59)

    is_low_confidence = confidence < settings.AI_CONFIDENCE_THRESHOLD
    differential = [
        {"name": info.get("display_name", key), "condition": info.get("display_name", key), "crop": info.get("crop", crop_name), "confidence_pct": round(min(0.89, 0.40 + score * 0.08) * 100)}
        for score, key, info in candidates[1:3]
    ]

    # Symptoms alone never unlock disease-specific treatment.
    prediction = {
        "status": "possible_match",
        "is_valid_crop_image": False,
        "validation": {"is_plant": None, "is_crop": True, "crop_supported": crop_name in inference_engine.supported_crops(), "rejection_reason": None},
        "crop": {"name": disease_info.get("crop", crop_name), "confidence_pct": round(confidence * 100)},
        "cropType": disease_info.get("crop", crop_name),
        "condition": disease_info.get("display_name", "Possible Disease"),
        "confidence": round(confidence, 4),
        "confidence_pct": round(confidence * 100),
        "severity": "Unknown",
        "severityPercentage": 0,
        "symptoms": [text],
        "symptoms_observed": disease_info.get("symptoms_observed", [])[:5],
        "differential_diagnoses": differential,
        "uncertainty": {"abstain": True, "reason": "Symptom-only evidence is weaker than image-based diagnosis."},
        "farmer_summary": "Possible symptom match only. Confirm with a clear crop image or an agricultural expert before treatment.",
        "recommendations": {
            "immediate": "Confirm the condition with a clear leaf image before applying disease-specific treatment.",
            "monitoring": "Photograph the same affected area again in 48–72 hours to track progression.",
            "prevention": "Maintain field sanitation and routine scouting.",
            "expert_help": "Consult a local KVK/agriculture extension officer before chemical application.",
        },
        "treatmentPlan": {
            "organic": {"name": "Not prescribed", "dosage": "Confirm diagnosis first."},
            "chemical": {"name": "Not recommended from symptoms alone", "dosage": "Confirm diagnosis first."},
            "preventive": {"cultural": "Scout and remove severely affected material where appropriate."},
        },
        "modelName": "Agri Nirvana Symptom Knowledge Matcher",
        "modelVersion": "v4",
        "isMock": False,
        "userId": user_id,
        "warnings": ["This is a symptom-based possible match, not a laboratory-confirmed diagnosis."],
        "is_low_confidence": is_low_confidence,
        "condition_label": "Possible Match — Confirm",
        "provenance": {"source": "knowledge_base_matcher", "confidence_is_calibrated": False, "treatment_allowed": False},
    }

    saved = _persist_without_image(prediction)
    return {"success": True, "diagnosis": saved, "warnings": prediction["warnings"]}


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
