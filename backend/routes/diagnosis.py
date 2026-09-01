import base64
from collections import defaultdict
import json
import logging
import re
import time
from typing import Optional, Dict, Any, List

from fastapi import APIRouter, File, Form, HTTPException, Query, UploadFile, Request, Header, Depends
from pydantic import BaseModel, Field
import httpx

from backend.config import settings
from backend.db.database import db
from backend.ml.config.disease_knowledge import DISEASE_KNOWLEDGE
from backend.ml.inference.production_engine import inference_engine
from backend.ml.models.disease_classifier import normalize_crop_name
from backend.ml.preprocessing.image_processor import validate_and_preprocess_image
from backend.routes.auth import get_current_user_optional

logger = logging.getLogger("agri_nirvana.diagnosis")
router = APIRouter(prefix="/diagnosis", tags=["Crop Diagnostics"])

# In-memory sliding-window rate limiter per client IP/User ID
_rate_limit_history = defaultdict(list)


def _check_rate_limit(client_id: str, max_requests: int = 15, window_seconds: int = 60) -> bool:
    now = time.time()
    valid_timestamps = [t for t in _rate_limit_history[client_id] if now - t < window_seconds]
    if len(valid_timestamps) >= max_requests:
        return False
    valid_timestamps.append(now)
    _rate_limit_history[client_id] = valid_timestamps
    return True


def _persist_without_image(record: dict) -> dict:
    """Persist metadata only; never store bulky base64 data URLs into SQLite history."""
    stored = dict(record)
    stored["imageUrl"] = ""
    return db.save_diagnosis(stored)


def _safe_user_id(user_id: Optional[str]) -> str:
    value = (user_id or "anonymous_farmer").strip()
    return value[:128] or "anonymous_farmer"


class GeminiAnalysisRequest(BaseModel):
    cropType: str = "Tomato"
    userId: Optional[str] = "anonymous_farmer"


class GeminiResponseSchema(BaseModel):
    disease_name: str
    pathogen: Optional[str] = "None"
    pathogen_category: Optional[str] = "Unknown"
    confidence: float = Field(ge=0.0, le=1.0)
    severity: str
    affected_surface: Optional[str] = "Foliar lamina"
    symptoms: List[str] = []
    likely_cause: Optional[str] = ""
    immediate_actions: List[str] = []
    organic_treatment: Optional[str] = None
    chemical_treatment: Optional[str] = None
    differential_diagnoses: List[Dict[str, Any]] = []


@router.post("/analyze")
async def analyze_crop_leaf(
    image: UploadFile = File(...),
    cropType: str = Form("Tomato"),
    userId: Optional[str] = Form("anonymous_farmer"),
    authorization: Optional[str] = Header(None)
):
    current_user = get_current_user_optional(authorization)
    effective_user_id = current_user.get("sub") if current_user else _safe_user_id(userId)

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

    # Strict Quality & Preprocessing Gate
    val_result = validate_and_preprocess_image(contents, image.filename)
    if not val_result.is_valid or val_result.pil_image is None:
        raise HTTPException(status_code=400, detail=val_result.error_message or "Unable to process image.")

    prediction = inference_engine.analyze(val_result.pil_image, cropType)
    confidence = max(0.0, min(float(prediction.get("confidence", 0.0)), 1.0))
    uncertainty = prediction.get("uncertainty") or {}
    abstain = bool(uncertainty.get("abstain", False))

    prediction["userId"] = effective_user_id
    prediction["warnings"] = list(val_result.warnings or [])
    prediction["is_low_confidence"] = abstain or confidence < settings.AI_CONFIDENCE_THRESHOLD
    prediction["condition_label"] = (
        "Uncertain Result" if prediction["is_low_confidence"] else prediction.get("condition", "Analyzed")
    )
    prediction["provenance"] = {
        "source": "real_ml_inference" if prediction.get("status") == "success" else "abstention",
        "confidence_is_calibrated": True if getattr(inference_engine, "_is_calibrated", False) else False,
        "treatment_allowed": prediction.get("status") == "success" and not prediction["is_low_confidence"],
    }

    if prediction["is_low_confidence"]:
        prediction["low_confidence_notice"] = (
            "The AI result is not reliable enough to use as a definitive diagnosis. "
            f"Model score: {round(confidence * 100)}%. Retake a sharp, well-lit close-up photo "
            "or consult a local agricultural expert."
        )

    mime = "jpeg" if ext == "jpg" else ext
    preview_url = f"data:image/{mime};base64,{base64.b64encode(contents).decode('utf-8')}"
    prediction["imageUrl"] = preview_url

    saved_doc = _persist_without_image(prediction)
    response_diagnosis = dict(saved_doc)
    response_diagnosis["imageUrl"] = preview_url

    return {"success": True, "diagnosis": response_diagnosis, "warnings": val_result.warnings}


@router.post("/gemini")
async def analyze_crop_leaf_gemini(
    request: Request,
    image: UploadFile = File(...),
    cropType: str = Form("Tomato"),
    userId: Optional[str] = Form("anonymous_farmer"),
    authorization: Optional[str] = Header(None)
):
    """Server-side Gemini 1.5 Flash Vision diagnosis.

    Enforces server-side API secret security, rate limiting (15 req/min),
    strict image quality gates, structured Pydantic response schema, and logging.
    """
    client_ip = request.client.host if request.client else "unknown_client"
    current_user = get_current_user_optional(authorization)
    effective_user_id = current_user.get("sub") if current_user else _safe_user_id(userId)

    # 1. Rate Limiting Check
    rate_limit_key = f"{client_ip}:{effective_user_id}"
    if not _check_rate_limit(rate_limit_key, max_requests=settings.GEMINI_RATE_LIMIT_PER_MINUTE, window_seconds=60):
        logger.warning("Rate limit exceeded for %s", rate_limit_key)
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded (maximum {settings.GEMINI_RATE_LIMIT_PER_MINUTE} requests/minute). Please wait before submitting another leaf photo."
        )

    # 2. Server Key Verification
    if not settings.GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY is not configured on the backend.")
        raise HTTPException(
            status_code=503,
            detail="Gemini Vision API is not configured on the server. Please set GEMINI_API_KEY in the backend environment."
        )

    # 3. Image Format & Size Validation
    if not image.filename:
        raise HTTPException(status_code=400, detail="Image filename is required.")

    ext = image.filename.rsplit(".", 1)[-1].lower() if "." in image.filename else ""
    if ext not in settings.ALLOWED_EXTENSIONS:
        allowed = ", ".join(sorted(settings.ALLOWED_EXTENSIONS))
        raise HTTPException(status_code=400, detail=f"Unsupported image type '.{ext}'. Allowed: {allowed}.")

    contents = await image.read()
    max_bytes = settings.MAX_IMAGE_SIZE_MB * 1024 * 1024
    if len(contents) > max_bytes:
        raise HTTPException(status_code=413, detail=f"Image exceeds the {settings.MAX_IMAGE_SIZE_MB} MB limit.")
    if not contents:
        raise HTTPException(status_code=400, detail="The uploaded image is empty.")

    # 4. Strict Image Quality Gate (Blur, Darkness, Resolution)
    val_result = validate_and_preprocess_image(contents, image.filename)
    if not val_result.is_valid:
        raise HTTPException(status_code=400, detail=val_result.error_message or "Image quality check failed.")

    # 5. Build Gemini Vision Payload
    base64_img = base64.b64encode(contents).decode("utf-8")
    mime_type = "image/jpeg" if ext in ["jpg", "jpeg"] else f"image/{ext}"

    prompt = f"""You are a certified senior plant pathologist and agronomist specializing in Indian cash crops.
Analyze this crop leaf image for a {cropType} plant.

Return ONLY a valid, single JSON object with these exact fields (no markdown, no code fencing, no explanation outside JSON):
{{
  "disease_name": "exact disease common name or 'Healthy Crop'",
  "pathogen": "scientific pathogen name or 'None'",
  "pathogen_category": "Fungal|Bacterial|Viral|Oomycete|Healthy",
  "confidence": 0.00 to 1.00,
  "severity": "Healthy|Low|Moderate|Severe",
  "affected_surface": "brief description of affected plant part",
  "symptoms": ["symptom 1", "symptom 2"],
  "likely_cause": "environmental or agronomic cause",
  "immediate_actions": ["action 1", "action 2"],
  "organic_treatment": "bio-organic treatment with dosage or null",
  "chemical_treatment": "chemical treatment with FRAC group and dosage or null",
  "differential_diagnoses": [{{"name": "alternative disease", "confidence_pct": 15, "key_distinguishing_feature": "feature"}}]
}}"""

    endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.GEMINI_MODEL}:generateContent?key={settings.GEMINI_API_KEY}"
    req_payload = {
        "contents": [{
            "parts": [
                {"text": prompt},
                {
                    "inline_data": {
                        "mime_type": mime_type,
                        "data": base64_img
                    }
                }
            ]
        }],
        "generationConfig": {
            "temperature": 0.1,
            "topK": 1,
            "topP": 0.95,
            "maxOutputTokens": 1024
        }
    }

    # 6. Execute Remote Vision Call
    start_time = time.time()
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(endpoint, json=req_payload)
    except Exception as exc:
        logger.error("Failed to connect to Gemini API: %s", exc)
        raise HTTPException(status_code=502, detail=f"Diagnostic vision provider connection failed: {exc}")

    elapsed_ms = int((time.time() - start_time) * 1000)
    logger.info("Gemini API call completed in %d ms with status %d", elapsed_ms, resp.status_code)

    if resp.status_code != 200:
        logger.error("Gemini API error (%d): %s", resp.status_code, resp.text[:400])
        raise HTTPException(
            status_code=502,
            detail=f"Diagnostic vision provider returned status {resp.status_code}."
        )

    # 7. Parse & Validate Response
    resp_data = resp.json()
    raw_text = ""
    try:
        parts = resp_data.get("candidates", [])[0].get("content", {}).get("parts", [])
        raw_text = parts[0].get("text", "").strip() if parts else ""
    except Exception:
        pass

    json_match = re.search(r"\{[\s\S]*\}", raw_text)
    if not json_match:
        logger.error("Gemini response did not contain JSON: %s", raw_text[:200])
        return {
            "success": True,
            "diagnosis": {
                "status": "uncertain",
                "condition": "Uncertain Result",
                "confidence": 0.0,
                "confidence_pct": 0,
                "severity": "Unknown",
                "severityPercentage": 0,
                "symptoms": [],
                "farmer_summary": "Vision provider returned non-JSON text. Please retake photo in clear lighting.",
                "recommendations": {
                    "immediate": "Retake a clear close-up image of the leaf.",
                    "expert_help": "Consult a local KVK/agriculture extension officer."
                },
                "is_low_confidence": True,
                "provenance": {"source": "gemini_backend", "confidence_is_calibrated": False, "treatment_allowed": False}
            },
            "warnings": ["Vision provider returned non-JSON output; returning safe uncertain fallback."]
        }

    try:
        parsed_json = json.loads(json_match.group(0))
        validated_gemini = GeminiResponseSchema(**parsed_json)
    except Exception as exc:
        logger.error("Failed to parse/validate Gemini response schema: %s. Raw: %s", exc, raw_text[:300])
        # Return structured uncertain result instead of unhandled crash
        return {
            "success": True,
            "diagnosis": {
                "status": "uncertain",
                "condition": "Uncertain Result",
                "confidence": 0.0,
                "confidence_pct": 0,
                "severity": "Unknown",
                "severityPercentage": 0,
                "symptoms": [],
                "farmer_summary": "Vision provider returned uncertain output. Please retake the photo under clear lighting.",
                "recommendations": {
                    "immediate": "Retake a clear close-up image of the leaf.",
                    "expert_help": "Consult a local KVK/agriculture extension officer."
                },
                "is_low_confidence": True,
                "provenance": {"source": "gemini_backend", "confidence_is_calibrated": False, "treatment_allowed": False}
            },
            "warnings": ["AI response validation check failed; returning uncertain safety fallback."]
        }

    # 8. Construct Verified Diagnosis Record
    confidence = float(validated_gemini.confidence)
    is_healthy = validated_gemini.pathogen_category == "Healthy" or "healthy" in validated_gemini.disease_name.lower()
    is_low_conf = confidence < settings.AI_CONFIDENCE_THRESHOLD or confidence <= 0.0
    treatment_allowed = not is_low_conf and not is_healthy and validated_gemini.disease_name != "Unknown Disease"

    diag_record = {
        "status": "uncertain" if is_low_conf else "success",
        "is_valid_crop_image": True,
        "crop": cropType,
        "cropType": cropType,
        "condition": "Uncertain Result" if is_low_conf else validated_gemini.disease_name,
        "diagnosis": "Uncertain Result" if is_low_conf else validated_gemini.disease_name,
        "confidence": round(confidence, 4),
        "confidence_pct": round(confidence * 100),
        "severity": "Unknown" if is_low_conf else validated_gemini.severity,
        "severityPercentage": 0 if is_healthy or is_low_conf else (50 if validated_gemini.severity == "Severe" else 30),
        "pathogen": validated_gemini.pathogen or "Unknown pathogen",
        "pathogenCategory": validated_gemini.pathogen_category or "Unknown",
        "affectedSurface": validated_gemini.affected_surface or "Foliar lamina",
        "symptoms": validated_gemini.symptoms,
        "symptoms_observed": validated_gemini.symptoms,
        "likely_cause": validated_gemini.likely_cause or "",
        "immediate_precautions": validated_gemini.immediate_actions,
        "treatment_organic": [validated_gemini.organic_treatment] if validated_gemini.organic_treatment else [],
        "treatment_chemical": [validated_gemini.chemical_treatment] if validated_gemini.chemical_treatment else [],
        "treatmentPlan": {
            "organic": {"name": validated_gemini.organic_treatment or "Not prescribed", "dosage": "Consult label"},
            "chemical": {"name": validated_gemini.chemical_treatment or "Not prescribed", "dosage": "Consult label"},
            "preventive": {"cultural": "Maintain field sanitation"}
        } if treatment_allowed else {},
        "recommendations": {
            "immediate": validated_gemini.immediate_actions[0] if validated_gemini.immediate_actions else "Monitor crop closely.",
            "monitoring": "Scout leaves twice weekly.",
            "prevention": "Maintain crop hygiene and sanitation.",
            "expert_help": "Consult local Krishi Vigyan Kendra (KVK) officer."
        },
        "differential_diagnoses": validated_gemini.differential_diagnoses,
        "is_low_confidence": is_low_conf,
        "provenance": {
            "source": "gemini_backend",
            "confidence_is_calibrated": False,
            "treatment_allowed": treatment_allowed
        },
        "userId": effective_user_id,
        "modelName": f"Gemini Pro Vision ({settings.GEMINI_MODEL})",
        "modelVersion": "v3.4-backend-secured",
        "isMock": False
    }

    if is_low_conf:
        diag_record["low_confidence_notice"] = (
            f"AI Vision confidence ({round(confidence * 100)}%) is below the reliability threshold ({round(settings.AI_CONFIDENCE_THRESHOLD * 100)}%). "
            "Retake a clear photo or consult a local KVK officer."
        )

    preview_url = f"data:{mime_type};base64,{base64_img}"
    diag_record["imageUrl"] = preview_url

    saved = _persist_without_image(diag_record)
    saved["imageUrl"] = preview_url
    return {"success": True, "diagnosis": saved, "warnings": val_result.warnings}


@router.post("/symptoms")
async def analyze_crop_symptoms(
    request: Request,
    authorization: Optional[str] = Header(None)
):
    """Unified Symptom Pathology Endpoint.

    Consistently accepts either application/json or multipart/form-data,
    normalizing both 'symptomText' and 'symptomsText'.
    """
    content_type = request.headers.get("content-type", "")

    if "application/json" in content_type:
        try:
            body = await request.json()
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid JSON body.")
        crop_type = body.get("cropType", "Tomato")
        text = (body.get("symptomText") or body.get("symptomsText") or "").strip()
        user_id = body.get("userId")
    else:
        form = await request.form()
        crop_type = form.get("cropType", "Tomato")
        text = (form.get("symptomText") or form.get("symptomsText") or "").strip()
        user_id = form.get("userId")

    current_user = get_current_user_optional(authorization)
    effective_user_id = current_user.get("sub") if current_user else _safe_user_id(user_id)

    if len(text) < 5:
        raise HTTPException(status_code=400, detail="Please provide a more detailed symptom description (at least 5 characters).")
    if len(text) > 2000:
        raise HTTPException(status_code=413, detail="Symptom description is too long (maximum 2000 characters).")

    STOP_WORDS = {
        "this", "that", "with", "from", "have", "also", "when", "some", "into",
        "over", "more", "than", "they", "them", "their", "been", "look", "very",
        "were", "what", "which", "will", "would", "about", "after", "again", "each",
        "only", "same", "such", "then", "there", "these", "those", "plant", "plants"
    }

    crop_name = normalize_crop_name(crop_type)
    candidates = []
    text_lower = text.lower()
    for key, info in DISEASE_KNOWLEDGE.items():
        if normalize_crop_name(info.get("crop", "")).lower() != crop_name.lower():
            continue
        score = 0
        for symptom in info.get("symptoms_observed", []):
            for word in symptom.lower().split():
                cleaned = word.strip(".,;:()[]{}")
                if len(cleaned) >= 4 and cleaned not in STOP_WORDS and cleaned in text_lower:
                    score += 1
        display_name = info.get("display_name", "")
        if display_name and display_name.lower() in text_lower:
            score += 3
        if score >= 2:
            candidates.append((score, key, info))

    candidates.sort(key=lambda item: item[0], reverse=True)

    if not candidates:
        prediction = {
            "status": "uncertain",
            "is_valid_crop_image": False,
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
                "expert_help": "Consult a local KVK/agriculture extension officer for confirmation."
            },
            "modelName": "Agri Nirvana Symptom Knowledge Matcher",
            "modelVersion": "v4",
            "isMock": False,
            "userId": effective_user_id,
            "warnings": ["Symptom-only matching is not a definitive diagnosis."],
            "is_low_confidence": True,
            "condition_label": "Uncertain Result",
            "provenance": {"source": "knowledge_base_matcher", "confidence_is_calibrated": False, "treatment_allowed": False},
        }
        saved = _persist_without_image(prediction)
        return {"success": True, "diagnosis": saved, "warnings": prediction["warnings"]}

    best_score, best_key, disease_info = candidates[0]
    confidence = min(0.89, 0.45 + best_score * 0.08)
    if len(candidates) > 1 and candidates[0][0] == candidates[1][0]:
        confidence = min(confidence, 0.59)

    is_low_confidence = confidence < settings.AI_CONFIDENCE_THRESHOLD
    differential = [
        {
            "name": info.get("display_name", key),
            "condition": info.get("display_name", key),
            "crop": info.get("crop", crop_name),
            "confidence_pct": round(min(0.89, 0.40 + score * 0.08) * 100)
        }
        for score, key, info in candidates[1:3]
    ]

    prediction = {
        "status": "possible_match",
        "is_valid_crop_image": False,
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
            "expert_help": "Consult a local KVK/agriculture extension officer before chemical application."
        },
        "modelName": "Agri Nirvana Symptom Knowledge Matcher",
        "modelVersion": "v4",
        "isMock": False,
        "userId": effective_user_id,
        "warnings": ["This is a symptom-based possible match, not a laboratory-confirmed diagnosis."],
        "is_low_confidence": is_low_confidence,
        "condition_label": "Possible Match — Confirm",
        "provenance": {"source": "knowledge_base_matcher", "confidence_is_calibrated": False, "treatment_allowed": False},
    }

    saved = _persist_without_image(prediction)
    return {"success": True, "diagnosis": saved, "warnings": prediction["warnings"]}


@router.get("/history")
async def get_diagnosis_history(
    crop: Optional[str] = Query(None),
    authorization: Optional[str] = Header(None),
    userId: Optional[str] = Query(None)
):
    """Retrieves diagnosis history with server-side farmer identity protection."""
    current_user = get_current_user_optional(authorization)
    effective_user_id = current_user.get("sub") if current_user else userId
    history = db.get_history(user_id=effective_user_id, crop_filter=crop)
    return {"success": True, "total": len(history), "history": history}


@router.get("/{diag_id}")
async def get_diagnosis_item(
    diag_id: str,
    authorization: Optional[str] = Header(None),
    userId: Optional[str] = Query(None)
):
    current_user = get_current_user_optional(authorization)
    effective_user_id = current_user.get("sub") if current_user else userId
    item = db.get_diagnosis_by_id(diag_id, user_id=effective_user_id)
    if not item:
        raise HTTPException(status_code=404, detail=f"Diagnosis with ID '{diag_id}' not found or access denied.")
    return {"success": True, "diagnosis": item}


@router.delete("/{diag_id}")
async def delete_diagnosis_item(
    diag_id: str,
    authorization: Optional[str] = Header(None),
    userId: Optional[str] = Query(None)
):
    current_user = get_current_user_optional(authorization)
    effective_user_id = current_user.get("sub") if current_user else userId
    deleted = db.delete_diagnosis(diag_id, user_id=effective_user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Diagnosis with ID '{diag_id}' not found or access denied.")
    return {"success": True, "message": f"Diagnosis '{diag_id}' successfully removed."}
