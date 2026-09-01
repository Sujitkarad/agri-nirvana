const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
const API_KEY = import.meta.env.VITE_API_KEY || "";
const USER_ID_KEY = "agri_nirvana_user_id";

function getOrCreateUserId() {
  const existing = localStorage.getItem(USER_ID_KEY);
  if (existing) return existing;
  const generated = typeof crypto !== "undefined" && crypto.randomUUID
    ? crypto.randomUUID()
    : `anon_${Date.now()}_${Math.round(Math.random() * 1e6)}`;
  localStorage.setItem(USER_ID_KEY, generated);
  return generated;
}

function buildHeaders() {
  const headers = {
    "X-User-Id": getOrCreateUserId()
  };
  if (API_KEY) {
    headers["X-API-Key"] = API_KEY;
  }
  return headers;
}

async function parseError(res, fallbackMessage) {
  const errData = await res.json().catch(() => null);
  throw new Error(errData?.detail || fallbackMessage);
}

export async function fetchModelStatus() {
  try {
    const res = await fetch(`${API_BASE}/api/v1/model/status`, {
      headers: buildHeaders()
    });
    if (!res.ok) await parseError(res, "Failed to fetch model status");
    return await res.json();
  } catch {
    return {
      success: true,
      model_name: "Offline Model Status (API unavailable)",
      model_version: "offline-fallback",
      provider_type: "unknown",
      is_mock: true,
      confidence_threshold: 0.70,
      max_image_size_mb: 10
    };
  }
}

export async function fetchSupportedCrops() {
  try {
    const res = await fetch(`${API_BASE}/api/v1/crops`, {
      headers: buildHeaders()
    });
    if (!res.ok) await parseError(res, "Failed to fetch supported crops");
    return await res.json();
  } catch {
    return {
      success: true,
      crops: [
        { id: "Tomato", name: "Tomato", icon: "🍅" },
        { id: "Potato", name: "Potato", icon: "🥔" },
        { id: "Cotton", name: "Cotton", icon: "☁️" },
        { id: "Rice", name: "Paddy / Rice", icon: "🌾" },
        { id: "Wheat", name: "Wheat", icon: "🌾" },
        { id: "Maize", name: "Maize / Corn", icon: "🌽" },
        { id: "Onion", name: "Onion", icon: "🧅" },
        { id: "Soybean", name: "Soybean", icon: "🌱" },
        { id: "Chilli", name: "Chilli", icon: "🌶️" },
        { id: "Grapes", name: "Grapes", icon: "🍇" }
      ]
    };
  }
}

export async function analyzeCropImageApi(imageFile, cropType = "Tomato", userImageSrc = null) {
  const formData = new FormData();
  if (imageFile) {
    formData.append("image", imageFile);
  } else if (userImageSrc && userImageSrc.startsWith("data:")) {
    const blob = await (await fetch(userImageSrc)).blob();
    formData.append("image", blob, `sample_${cropType.toLowerCase()}.jpg`);
  } else {
    throw new Error("No image file provided for analysis.");
  }
  formData.append("cropType", cropType);
  formData.append("userId", getOrCreateUserId());

  const res = await fetch(`${API_BASE}/api/v1/diagnosis/analyze`, {
    method: "POST",
    headers: buildHeaders(),
    body: formData
  });

  if (!res.ok) await parseError(res, "Image analysis failed");
  return await res.json();
}

export async function fetchDiagnosisHistoryApi(cropFilter = null, limit = 20, offset = 0) {
  const params = new URLSearchParams({
    userId: getOrCreateUserId(),
    limit: String(limit),
    offset: String(offset)
  });
  if (cropFilter && cropFilter !== "All") {
    params.set("crop", cropFilter);
  }

  const res = await fetch(`${API_BASE}/api/v1/diagnosis/history?${params.toString()}`, {
    headers: buildHeaders()
  });
  if (!res.ok) await parseError(res, "Failed to fetch diagnosis history");
  return await res.json();
}

export async function deleteDiagnosisItemApi(id) {
  const params = new URLSearchParams({ userId: getOrCreateUserId() });
  const res = await fetch(`${API_BASE}/api/v1/diagnosis/${id}?${params.toString()}`, {
    method: "DELETE",
    headers: buildHeaders()
  });
  if (!res.ok) await parseError(res, "Failed to delete diagnosis item");
  return await res.json();
}

