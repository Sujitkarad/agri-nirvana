const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

/**
 * Fetches the current ML model status from the backend.
 * Returns honest information — no more fake "multimodal vision" branding.
 */
export async function fetchModelStatus() {
  const endpoints = [
    `${API_BASE}/api/v1/model/status`,
    "/api/v1/model/status",
    "http://127.0.0.1:8000/api/v1/model/status"
  ];

  for (const ep of endpoints) {
    try {
      const res = await fetch(ep);
      if (res.ok) {
        return await res.json();
      }
    } catch (_) {}
  }

  return {
    success: false,
    model_name: "Backend Offline",
    model_version: "—",
    provider_type: "offline",
    is_mock: true,
    models_loaded: false,
    confidence_threshold: 0.50,
    max_image_size_mb: 10,
    error: "Cannot reach backend API. Please start the FastAPI server."
  };
}

/**
 * Fetches the list of supported crops from the backend.
 */
export async function fetchSupportedCrops() {
  const endpoints = [
    `${API_BASE}/api/v1/crops`,
    "/api/v1/crops",
    "http://127.0.0.1:8000/api/v1/crops"
  ];

  for (const ep of endpoints) {
    try {
      const res = await fetch(ep);
      if (res.ok) {
        return await res.json();
      }
    } catch (_) {}
  }

  return {
    success: true,
    crops: [
      { id: "Cotton", name: "Cotton (कापूस)", icon: "☁️" },
      { id: "Soybean", name: "Soybean (सोयाबीन)", icon: "🌱" },
      { id: "Sugarcane", name: "Sugarcane (ऊस)", icon: "🎋" },
      { id: "Onion", name: "Onion (कांदा)", icon: "🧅" },
      { id: "Grapes", name: "Grapes (द्राक्षे)", icon: "🍇" },
      { id: "Pomegranate", name: "Pomegranate (डाळिंब)", icon: "🍎" },
      { id: "Rice", name: "Paddy / Rice (भात)", icon: "🌾" },
      { id: "Tomato", name: "Tomato (टोमॅटो)", icon: "🍅" },
      { id: "Potato", name: "Potato (बटाटा)", icon: "🥔" },
      { id: "Maize", name: "Maize / Corn (मका)", icon: "🌽" }
    ]
  };
}

/**
 * Sends a crop leaf image to the real ML backend for diagnosis.
 *
 * NO MORE MOCK FALLBACK — if the backend is offline, this function
 * returns an honest error instead of fake hardcoded results.
 */
export async function analyzeCropImageApi(imageFile, cropType = "Tomato", userImageSrc = null) {
  const formData = new FormData();

  if (imageFile) {
    formData.append("image", imageFile);
  } else if (userImageSrc) {
    try {
      const response = await fetch(userImageSrc);
      const blob = await response.blob();
      formData.append("image", blob, `sample_${cropType.toLowerCase()}.jpg`);
    } catch (err) {
      throw new Error(`Could not load selected image: ${err.message}`);
    }
  } else {
    throw new Error("No image provided. Please upload or capture a crop leaf photo.");
  }

  formData.append("cropType", cropType);

  // Try direct backend API_BASE first, fallback to proxied /api
  const endpoints = [
    `${API_BASE}/api/v1/diagnosis/analyze`,
    "/api/v1/diagnosis/analyze",
    "http://127.0.0.1:8000/api/v1/diagnosis/analyze"
  ];

  let lastError = null;
  for (const endpoint of endpoints) {
    try {
      const res = await fetch(endpoint, {
        method: "POST",
        body: formData
      });

      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        const detail = errorData.detail || `Server error (HTTP ${res.status})`;
        throw new Error(detail);
      }

      const data = await res.json();
      if (!data || !data.diagnosis) {
        throw new Error("Invalid response from server — no diagnosis data returned.");
      }

      return data;
    } catch (err) {
      lastError = err;
      // If it's a network error (like failed to fetch), try the next fallback endpoint
      if (err.name === "TypeError" || err.message.includes("Failed to fetch") || err.message.includes("NetworkError")) {
        continue;
      }
      throw err;
    }
  }

  throw lastError || new Error("Failed to connect to ML backend server. Please verify FastAPI is running on port 8000.");
}

/**
 * Fetches diagnosis history from backend, falls back to localStorage.
 */
export async function fetchDiagnosisHistoryApi(cropFilter = null) {
  try {
    const url = cropFilter && cropFilter !== "All"
      ? `${API_BASE}/api/v1/diagnosis/history?crop=${encodeURIComponent(cropFilter)}`
      : `${API_BASE}/api/v1/diagnosis/history`;
    const res = await fetch(url);
    if (!res.ok) throw new Error("Failed to fetch history");
    return await res.json();
  } catch (err) {
    const local = localStorage.getItem("agri_nirvana_diag_history");
    let history = local ? JSON.parse(local) : [];
    if (cropFilter && cropFilter !== "All") {
      history = history.filter(h => h.crop === cropFilter || h.cropType === cropFilter);
    }
    return { success: true, total: history.length, history };
  }
}

/**
 * Deletes a diagnosis record by ID.
 */
export async function deleteDiagnosisItemApi(id) {
  try {
    const res = await fetch(`${API_BASE}/api/v1/diagnosis/${id}`, { method: "DELETE" });
    if (!res.ok) throw new Error("Failed to delete diagnosis item");
    return await res.json();
  } catch (err) {
    const local = localStorage.getItem("agri_nirvana_diag_history");
    if (local) {
      const history = JSON.parse(local).filter(item => item.id !== id);
      localStorage.setItem("agri_nirvana_diag_history", JSON.stringify(history));
    }
    return { success: true };
  }
}
