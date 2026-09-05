from __future__ import annotations

import os
from typing import Any

from openai import OpenAI


SYSTEM_PROMPT = """You are Agri Nirvana's agricultural assistant.

Be precise, practical, and safety-conscious. Never invent live prices, weather,
registrations, field measurements, disease confidence, or chemical approvals.
A crop diagnosis is authoritative only when it comes from Agri Nirvana's
production diagnostic pipeline; do not create a diagnosis from a chat message
or image attachment. If diagnostic evidence is absent, say so clearly.

For pesticides or fertilizers, give only general educational guidance and tell
the user to follow the product label and local agricultural/KVK advice. Avoid
unsafe dosing claims. Prefer integrated pest management and non-chemical steps.
"""


from backend.config import settings


def _get_client_and_model(requested_model: str | None = None) -> tuple[OpenAI, str, str]:
    """
    Returns (client, model_name, provider_name).
    Supports Google Gemini (via GEMINI_API_KEY) and OpenAI (via OPENAI_API_KEY).
    """
    gemini_key = (os.getenv("GEMINI_API_KEY", "") or settings.GEMINI_API_KEY or "").strip()
    openai_key = os.getenv("OPENAI_API_KEY", "").strip()

    if gemini_key:
        client = OpenAI(
            api_key=gemini_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            timeout=30.0,
            max_retries=2,
        )
        model = requested_model or settings.AI_CHAT_DEFAULT_GEMINI_MODEL
        if not ("gemini" in (model or "").lower()):
            model = settings.AI_CHAT_DEFAULT_GEMINI_MODEL
        return client, model, "gemini"

    if openai_key:
        client = OpenAI(api_key=openai_key, timeout=30.0, max_retries=2)
        model = requested_model or settings.AI_CHAT_MODEL
        return client, model, "openai"

    raise RuntimeError("AI assistant is not configured. Add GEMINI_API_KEY or OPENAI_API_KEY to the backend environment.")


def generate_chat(
    messages: list[dict[str, str]],
    *,
    crop: str = "Unknown",
    language: str = "en",
    model: str | None = None,
    diagnosis: dict[str, Any] | None = None,
) -> dict[str, Any]:
    clean_messages: list[dict[str, str]] = []
    for message in messages:
        role = message.get("role")
        content = (message.get("content") or "").strip()
        if role not in {"user", "assistant"} or not content:
            continue
        clean_messages.append({"role": role, "content": content})

    context = f"Current crop context: {crop}. Respond in language: {language}."
    if diagnosis:
        context += (
            "\nVerified diagnostic pipeline context (do not strengthen or alter it): "
            + str(diagnosis)
        )

    client, selected_model, provider = _get_client_and_model(model)
    full_instruction = SYSTEM_PROMPT + "\n" + context

    if provider == "gemini":
        chat_messages = [{"role": "system", "content": full_instruction}] + clean_messages
        completion = client.chat.completions.create(
            model=selected_model,
            messages=chat_messages,
            max_tokens=1200,
        )
        text = (completion.choices[0].message.content or "").strip()
    else:
        try:
            response = client.responses.create(
                model=selected_model,
                instructions=full_instruction,
                input=clean_messages,
                max_output_tokens=1200,
            )
            text = (response.output_text or "").strip()
        except Exception:
            chat_messages = [{"role": "system", "content": full_instruction}] + clean_messages
            completion = client.chat.completions.create(
                model=selected_model,
                messages=chat_messages,
                max_tokens=1200,
            )
            text = (completion.choices[0].message.content or "").strip()

    if not text:
        raise RuntimeError(f"{provider} returned an empty response")
    return {"message": text, "model": selected_model, "provider": provider}

