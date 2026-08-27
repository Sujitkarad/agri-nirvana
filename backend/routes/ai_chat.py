"""Real conversational AI endpoint for the Agri Nirvana assistant.

The browser never receives the Hugging Face token. Requests are proxied through
FastAPI and the model is selected server-side through Hugging Face Inference
Providers' OpenAI-compatible chat-completions endpoint.
"""

import json
import os
from typing import Any, Dict, List
from urllib import error, request

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.config import settings

router = APIRouter(prefix="/ai", tags=["AI Assistant"])


class ChatMessage(BaseModel):
    role: str = Field(pattern="^(user|assistant|system)$")
    content: str = Field(min_length=1, max_length=12000)


class ChatRequest(BaseModel):
    messages: List[ChatMessage] = Field(min_length=1, max_length=30)
    crop: str = Field(default="Unknown", max_length=80)
    language: str = Field(default="en", max_length=10)
    model: str | None = Field(default=None, max_length=160)


SYSTEM_PROMPT = """You are Agri Nirvana AI, a careful precision-agriculture assistant.
You help farmers with crop health, agronomy, irrigation, fertilizer concepts,
market interpretation and general farm decisions.

Rules:
- Be concise, practical and farmer-friendly.
- Never claim that an answer is real-time unless current data was actually supplied.
- Never invent mandi prices, satellite measurements, weather readings, disease confidence,
  chemical registrations, drone coordinates, or field measurements.
- For crop disease questions, distinguish education from a confirmed diagnosis.
- Do not turn a language-model guess into a definitive diagnosis.
- For pesticide/chemical advice, recommend checking the current registered product label
  and local KVK/agriculture extension guidance before application.
- If the user asks about the current field diagnosis, ask for or reference the actual
  diagnosis result rather than pretending to have inspected an image.
- Respond in the requested language when practical.
"""


def _model_id(requested: str | None) -> str:
    requested = (requested or "").strip()
    if requested:
        # Only allow known configured models; never let the browser choose arbitrary
        # upstream URLs or providers.
        allowed = set(settings.AI_CHAT_ALLOWED_MODELS.split(","))
        if requested in allowed:
            return requested
    return settings.AI_CHAT_MODEL


def _call_huggingface(messages: List[Dict[str, str]], model: str) -> Dict[str, Any]:
    token = os.getenv("HF_TOKEN", "").strip()
    if not token:
        raise HTTPException(
            status_code=503,
            detail="AI chat is not configured. Please configure an inference provider token on the backend.",
        )

    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.4,
        "max_tokens": 700,
    }
    body = json.dumps(payload).encode("utf-8")
    req = request.Request(
        "https://router.huggingface.co/v1/chat/completions",
        data=body,
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
        detail = exc.read().decode("utf-8", errors="replace")[:1000]
        raise HTTPException(status_code=502, detail=f"AI provider error: {detail}") from exc
    except error.URLError as exc:
        raise HTTPException(status_code=504, detail="AI provider could not be reached.") from exc


@router.post("/chat")
async def chat(request_body: ChatRequest):
    crop = request_body.crop.strip() or "Unknown"
    language = request_body.language.strip() or "en"
    model = _model_id(request_body.model)

    context = (
        f"Current selected crop: {crop}.\n"
        f"Requested response language: {language}.\n"
        "Treat the crop and language as context only; do not infer unprovided field facts."
    )

    messages: List[Dict[str, str]] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "system", "content": context},
    ]
    for message in request_body.messages:
        messages.append({"role": message.role, "content": message.content})

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
            "is_image_diagnosis": False,
        },
    }


@router.get("/chat/status")
async def chat_status():
    return {
        "configured": bool(os.getenv("HF_TOKEN", "").strip()),
        "provider": "Hugging Face Inference Providers",
        "model": settings.AI_CHAT_MODEL,
        "streaming": False,
    }
