import os
import uuid
from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Query, Header, Request
from typing import Optional
import hmac
import concurrent.futures
from backend.config import settings
from backend.ml.preprocessing.image_processor import validate_and_preprocess_image
from backend.ml.inference.engine import inference_engine
from backend.db.database import db

router = APIRouter(prefix="/diagnosis", tags=["Crop Diagnostics"])

def _enforce_api_key(x_api_key: Optional[str]) -> None:
    expected_key = (settings.API_ACCESS_KEY or "").strip()
    if not expected_key:
        return
    if not x_api_key or not hmac.compare_digest(x_api_key.strip(), expected_key):
        raise HTTPException(status_code=401, detail="Unauthorized API key.")

def _resolve_user_id(explicit_user_id: Optional[str], header_user_id: Optional[str]) -> str:
    user_id = (explicit_user_id or header_user_id or "").strip()
    if not user_id:
        raise HTTPException(status_code=400, detail="Missing user context. Provide userId.")
    return user_id

@router.post("/analyze")
async def analyze_crop_leaf(
    request: Request,
    image: UploadFile = File(...),
    cropType: str = Form("Tomato"),
    userId: Optional[str] = Form(None),
    x_api_key: Optional[str] = Header(default=None, alias="X-API-Key"),
    x_user_id: Optional[str] = Header(default=None, alias="X-User-Id")
):
    """
    Uploads a crop leaf image, validates quality (blur/darkness/resolution),
    runs computer-vision prediction, evaluates confidence against threshold, and saves result.
    """
    _enforce_api_key(x_api_key)
    resolved_user_id = _resolve_user_id(userId, x_user_id)
    contents = await image.read()

    # Basic Content-Type check to reject non-image uploads early
    if image.content_type and not image.content_type.lower().startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file is not an image.")

    # 1. Quality Validation & Preprocessing
    val_result = validate_and_preprocess_image(contents, image.filename)
    if not val_result.is_valid:
        raise HTTPException(status_code=400, detail=val_result.error_message)

    # 2. Persist upload as static file and store URL (avoids DB bloat from base64 blobs)
    ext = image.filename.split(".")[-1].lower() if image.filename and "." in image.filename else "jpeg"
    file_name = f"{uuid.uuid4()}.{ext}"
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(settings.UPLOAD_DIR, file_name)

    try:
        with open(file_path, "wb") as f:
            f.write(contents)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to save uploaded file.")

    image_url = f"{request.base_url}uploads/{file_name}"

    # 3. ML Computer Vision Inference + Save; ensure cleanup on failures to avoid orphan files
    try:
        # Run inference with timeout to protect long-running model operations
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(inference_engine.analyze, val_result.pil_image, cropType)
            try:
                prediction = future.result(timeout=settings.INFERENCE_TIMEOUT_SECS)
            except concurrent.futures.TimeoutError:
                # Attempt to remove uploaded file when inference times out
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                except Exception:
                    pass
                raise HTTPException(status_code=504, detail=f"Inference timed out after {settings.INFERENCE_TIMEOUT_SECS}s")

        prediction["imageUrl"] = image_url
        prediction["userId"] = resolved_user_id
        prediction["warnings"] = val_result.warnings

        # 4. Save Record to History Database
        saved_doc = db.save_diagnosis(prediction)
    except HTTPException:
        # Re-raise HTTP errors
        raise
    except Exception as e:
        # Attempt to remove file if something went wrong after the upload
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception:
            pass
        raise HTTPException(status_code=500, detail="Failed to analyze or persist diagnosis.")

    return {
        "success": True,
        "diagnosis": saved_doc,
        "warnings": val_result.warnings
    }

@router.get("/history")
async def get_diagnosis_history(
    crop: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    userId: Optional[str] = Query(None),
    x_api_key: Optional[str] = Header(default=None, alias="X-API-Key"),
    x_user_id: Optional[str] = Header(default=None, alias="X-User-Id")
):
    """
    Retrieves stored diagnosis records for the user. Supports optional crop filtering.
    """
    _enforce_api_key(x_api_key)
    resolved_user_id = _resolve_user_id(userId, x_user_id)
    history, total = db.get_history(
        user_id=resolved_user_id,
        crop_filter=crop,
        limit=limit,
        offset=offset
    )
    return {
        "success": True,
        "total": total,
        "limit": limit,
        "offset": offset,
        "history": history
    }

@router.get("/{diag_id}")
async def get_diagnosis_item(
    diag_id: str,
    userId: Optional[str] = Query(None),
    x_api_key: Optional[str] = Header(default=None, alias="X-API-Key"),
    x_user_id: Optional[str] = Header(default=None, alias="X-User-Id")
):
    """
    Fetches detailed single diagnosis record by ID.
    """
    _enforce_api_key(x_api_key)
    resolved_user_id = _resolve_user_id(userId, x_user_id)
    item = db.get_diagnosis_by_id(diag_id, resolved_user_id)
    if not item:
        raise HTTPException(status_code=404, detail=f"Diagnosis with ID '{diag_id}' not found.")
    return {"success": True, "diagnosis": item}

@router.delete("/{diag_id}")
async def delete_diagnosis_item(
    diag_id: str,
    userId: Optional[str] = Query(None),
    x_api_key: Optional[str] = Header(default=None, alias="X-API-Key"),
    x_user_id: Optional[str] = Header(default=None, alias="X-User-Id")
):
    """
    Deletes diagnosis item from history.
    """
    _enforce_api_key(x_api_key)
    resolved_user_id = _resolve_user_id(userId, x_user_id)
    deleted = db.delete_diagnosis(diag_id, resolved_user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Diagnosis with ID '{diag_id}' not found or already deleted.")
    return {"success": True, "message": f"Diagnosis '{diag_id}' successfully removed."}
