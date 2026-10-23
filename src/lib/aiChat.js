const CONFIGURED_API_BASE = (import.meta.env.VITE_API_BASE_URL || "").replace(/\/$/, "");
const API_BASE = CONFIGURED_API_BASE.replace(/\/api\/v1$/, "");
const API_PREFIX = `${API_BASE}/api/v1`;

export async function sendAgriAIChat({
  messages,
  crop = "Unknown",
  language = "en",
  model,
  diagnosis = null,
}) {
  const response = await fetch(`${API_PREFIX}/ai/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ messages, crop, language, model, diagnosis }),
  });

  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(payload.detail || `AI request failed (${response.status})`);
  }
  return payload;
}

export async function getAgriAIChatStatus() {
  const response = await fetch(`${API_PREFIX}/ai/chat/status`);
  if (!response.ok) throw new Error("Unable to check AI chat status");
  return response.json();
}
