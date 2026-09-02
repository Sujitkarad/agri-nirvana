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


def _client() -> OpenAI:
    key = os.getenv("OPENAI_API_KEY", "").strip()
    if not key:
        raise RuntimeError("OPENAI_API_KEY is not configured")
    return OpenAI(api_key=key, timeout=30.0, max_retries=2)


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

    selected_model = model or os.getenv("OPENAI_CHAT_MODEL", "gpt-5.6-luna")
    response = _client().responses.create(
        model=selected_model,
        instructions=SYSTEM_PROMPT + "\n" + context,
        input=clean_messages,
        max_output_tokens=1200,
    )
    text = (response.output_text or "").strip()
    if not text:
        raise RuntimeError("OpenAI returned an empty response")
    return {"message": text, "model": selected_model, "provider": "openai"}
