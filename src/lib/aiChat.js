const API_BASE = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1").replace(/\/$/, "");

export async function sendAgriAIChat({ messages, crop = "Unknown", language = "en", model }) {
  const response = await fetch(`${API_BASE}/ai/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ messages, crop, language, model }),
  });

  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(payload.detail || `AI request failed (${response.status})`);
  }
  return payload;
}

export async function getAgriAIChatStatus() {
  const response = await fetch(`${API_BASE}/ai/chat/status`);
  if (!response.ok) throw new Error("Unable to check AI chat status");
  return response.json();
}
