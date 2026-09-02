"""Production conversational AI endpoint for Agri Nirvana.

The browser never receives the provider token. FastAPI validates the request,
adds the safety policy and diagnosis context, then calls the configured
Hugging Face OpenAI-compatible inference endpoint.
"""

import json
import os
import time
from collections import defaultdict, deque
from typing import Any, Dict, List
from urllib import error, request

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from backend.config import settings

router = APIRouter(prefix="/ai", tags=["AI Assistant"])

# Small in-process limiter. This protects a single API instance from accidental
# request storms; production deployments should also enforce a platform/WAF limit.
_RATE_WINDOW_SECONDS = 60
_RATE_LIMIT = 30
_request_log: dict[str, deque[float]] = defaultdict(deque)


class ChatMessage(BaseModel):
    role: str = Field(pattern="^(user|assistant)$")
    content: str = Field(min_length=1, max_length=12000)


class ChatRequest(BaseModel):
    messages: List[ChatMessage] = Field(min_length=1, max_length=30)
    crop: str = Field(default="Unknown", max_length=80)
    language: str = Field(default="en", max_length=20)
    model: str | None = Field(default=None, max_length=160)
    diagnosis: Dict[str, Any] | None = None


SYSTEM_PROMPT = """You are Agri Nirvana AI, a careful precision-agriculture assistant.
You help farmers and agronomists with crop health, disease education, pests,
irrigation, soil and nutrient concepts, farm planning and general agronomy.

Safety and truthfulness rules:
- Be practical, concise and easy to understand.
- Never invent current weather, mandi prices, market arrivals, satellite values,
  field measurements, registrations, product labels, disease confidence or test results.
- Never present an LLM opinion as a confirmed plant disease diagnosis.
- If diagnosis context is supplied, explain it faithfully and preserve its confidence
  and uncertainty; do not increase or reinterpret the confidence.
- If the user asks for a diagnosis without an actual diagnostic result/image analysis,
  ask them to use the Crop Diagnosis feature and provide the result.
- For pesticide/fungicide/herbicide advice, avoid inventing product-specific doses.
  Tell the user to follow the current registered product label and local agriculture
  department/KVK guidance. Mention PPE and pre-harvest interval when relevant.
- Do not recommend mixing chemicals unless compatibility is verified from labels.
- For fertilizer rates, clearly state that soil test, crop stage, variety and local
  recommendations can change the prescription.
- If information is insufficient, say what is missing instead of guessing.
- Respond in the requested language when practical.
"""


def _model_id(requested: str | None) -> str:
    allowed = {m.strip() for m in settings.AI_CHAT_ALLOWED_MODELS.split(",") if m.strip()}
    requested = (requested or "").strip()
    return requested if requested in allowed else settings.AI_CHAT_MODEL


def _check_rate_limit(client_key: str) -> None:
    now = time.monotonic()
    bucket = _request_log[client_key]
    while bucket and now - bucket[0] >= _RATE_WINDOW_SECONDS:
        bucket.popleft()
    if len(bucket) >= _RATE_LIMIT:
        raise HTTPException(status_code=429, detail="Too many AI chat requests. Please try again shortly.")
    bucket.append(now)


def _call_huggingface(messages: List[Dict[str, str]], model: str) -> Dict[str, Any]:
    token = os.getenv("HF_TOKEN", "").strip()
    if not token:
        raise HTTPException(
            status_code=503,
            detail="AI chat is not configured. Add HF_TOKEN to the backend environment.",
        )

    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.25,
        "max_tokens": 900,
    }
    req = request.Request(
        "https://router.huggingface.co/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with request.urlopen(req, timeout=45) as response:
            return json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:1200]
        raise HTTPException(status_code=502, detail=f"AI provider error: {detail}") from exc
    except error.URLError as exc:
        raise HTTPException(status_code=504, detail="AI provider could not be reached.") from exc
    except (TimeoutError, json.JSONDecodeError) as exc:
        raise HTTPException(status_code=504, detail="AI provider timed out or returned invalid data.") from exc


def _diagnosis_context(diagnosis: Dict[str, Any] | None) -> str:
    if not diagnosis:
        return "No verified crop diagnosis is attached to this conversation."

    # Allow only diagnosis fields that are useful to the assistant. This prevents
    # arbitrary client text from becoming a fake system instruction.
    allowed = {
        "crop": diagnosis.get("crop"),
        "disease": diagnosis.get("disease"),
        "confidence": diagnosis.get("confidence"),
        "severity": diagnosis.get("severity"),
        "crop_match": diagnosis.get("crop_match"),
        "warnings": diagnosis.get("warnings"),
        "treatment_allowed": diagnosis.get("treatment_allowed"),
    }
    safe = {k: v for k, v in allowed.items() if v is not None}
    return "Verified diagnostic context (use exactly as evidence, not as a new prediction):\n" + json.dumps(safe, ensure_ascii=False)


@router.post("/chat")
async def chat(request_body: ChatRequest, request_context: Request):
    client_key = request_context.client.host if request_context.client else "unknown"
    _check_rate_limit(client_key)

    crop = request_body.crop.strip() or "Unknown"
    language = request_body.language.strip() or "en"
    model = _model_id(request_body.model)

    messages: List[Dict[str, str]] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "system",
            "content": (
                f"Selected crop: {crop}. Requested language: {language}.\n"
                "Treat these as context only; do not infer unprovided field facts.\n\n"
                + _diagnosis_context(request_body.diagnosis)
            ),
        },
    ]
    # System messages from the browser are deliberately not accepted by the schema.
    messages.extend({"role": m.role, "content": m.content.strip()} for m in request_body.messages)

    result = _call_huggingface(messages, model)
    choices = result.get("choices") or []
    if not choices:
        raise HTTPException(status_code=502, detail="AI provider returned no response choices.")

    message = choices[0].get("message") or {}
    text = (message.get("content") or "").strip()
    if not text:
        raise HTTPException(status_code=502, detail="AI provider returned an empty response.")

    usage = result.get("usage") or {}
    return {
        "success": True,
        "message": text,
        "model": result.get("model", model),
        "provider": "Hugging Face Inference Providers",
        "usage": usage,
        "provenance": {
            "source": "llm_chat_completion",
            "is_mock": False,
            "is_real_time_market_data": False,
            "is_image_diagnosis": bool(request_body.diagnosis),
            "diagnosis_context_attached": bool(request_body.diagnosis),
        },
    }


@router.get("/chat/status")
async def chat_status():
    configured = bool(os.getenv("HF_TOKEN", "").strip())
    return {
        "configured": configured,
        "provider": "Hugging Face Inference Providers",
        "model": settings.AI_CHAT_MODEL,
        "allowed_models": [m.strip() for m in settings.AI_CHAT_ALLOWED_MODELS.split(",") if m.strip()],
        "streaming": False,
        "rate_limit_per_minute": _RATE_LIMIT,
    }
