"""Production conversational AI endpoint for Agri Nirvana."""

import os
import time
from collections import defaultdict, deque
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from backend.config import settings
from backend.services.chat_service import generate_chat

router = APIRouter(prefix="/ai", tags=["AI Assistant"])

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


def _model_id(requested: str | None) -> str | None:
    if not requested:
        return None
    allowed = {m.strip().lower() for m in settings.AI_CHAT_ALLOWED_MODELS.split(",") if m.strip()}
    requested_clean = requested.strip()
    if requested_clean.lower() in allowed:
        return requested_clean
    return None


def _check_rate_limit(client_key: str) -> None:
    now = time.monotonic()
    bucket = _request_log[client_key]
    while bucket and now - bucket[0] >= _RATE_WINDOW_SECONDS:
        bucket.popleft()
    if len(bucket) >= _RATE_LIMIT:
        raise HTTPException(status_code=429, detail="Too many AI chat requests. Please try again shortly.")
    bucket.append(now)


@router.post("/chat")
async def chat(request_body: ChatRequest, request_context: Request):
    client_key = request_context.client.host if request_context.client else "unknown"
    _check_rate_limit(client_key)

    messages = [
        {"role": message.role, "content": message.content.strip()}
        for message in request_body.messages
        if message.content.strip()
    ]
    if not messages:
        raise HTTPException(status_code=422, detail="At least one non-empty chat message is required.")

    try:
        result = generate_chat(
            messages,
            crop=request_body.crop.strip() or "Unknown",
            language=request_body.language.strip() or "en",
            model=_model_id(request_body.model),
            diagnosis=request_body.diagnosis,
        )
    except RuntimeError as exc:
        detail = str(exc)
        if "not configured" in detail:
            raise HTTPException(status_code=503, detail="AI chat is not configured. Add GEMINI_API_KEY or OPENAI_API_KEY to the backend environment.") from exc
        raise HTTPException(status_code=502, detail="AI provider returned an unusable response.") from exc
    except Exception as exc:
        # Do not expose provider internals or credentials to the browser.
        raise HTTPException(status_code=502, detail="AI provider request failed. Please try again shortly.") from exc

    provider_source = "google_gemini_api" if result.get("provider") == "gemini" else "openai_responses_api"

    return {
        "success": True,
        "message": result["message"],
        "model": result["model"],
        "provider": result["provider"],
        "usage": None,
        "provenance": {
            "source": provider_source,
            "is_mock": False,
            "is_real_time_market_data": False,
            "is_image_diagnosis": False,
            "diagnosis_context_attached": bool(request_body.diagnosis),
        },
    }


@router.get("/chat/status")
async def chat_status():
    gemini_key = (os.getenv("GEMINI_API_KEY", "") or settings.GEMINI_API_KEY or "").strip()
    openai_key = os.getenv("OPENAI_API_KEY", "").strip()
    configured = bool(gemini_key or openai_key)
    provider = "Google Gemini API" if gemini_key else "OpenAI Responses API"
    active_model = settings.AI_CHAT_DEFAULT_GEMINI_MODEL if gemini_key else settings.AI_CHAT_MODEL
    return {
        "configured": configured,
        "provider": provider,
        "model": active_model,
        "allowed_models": [m.strip() for m in settings.AI_CHAT_ALLOWED_MODELS.split(",") if m.strip()],
        "streaming": False,
        "rate_limit_per_minute": _RATE_LIMIT,
    }

