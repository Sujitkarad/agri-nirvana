/**
 * Agri Nirvana - Weather API Client & Location System.
 * 
 * Interacts with Agri Nirvana backend `/api/v1/weather/forecast`.
 * Includes direct Open-Meteo fallback if the backend proxy is offline,
 * ensuring high availability across both local and cloud environments.
 */

export const POPULAR_AGRI_LOCATIONS = [
  { name: "Kopargaon (अहिल्यानगर)", state: "Maharashtra", lat: 19.8864, lon: 74.4784, district: "Ahilyanagar" },
  { name: "Shirdi (शिर्डी)", state: "Maharashtra", lat: 19.7667, lon: 74.4764, district: "Ahilyanagar" },
  { name: "Nashik (नाशिक द्राक्ष / कांदा पट्टा)", state: "Maharashtra", lat: 19.9975, lon: 73.7898, district: "Nashik" },
  { name: "Pune (पुणे - मांजरी कृषी केंद्र)", state: "Maharashtra", lat: 18.5204, lon: 73.8567, district: "Pune" },
  { name: "Chhatrapati Sambhaji Nagar (औरंगाबाद)", state: "Maharashtra", lat: 19.8762, lon: 75.3433, district: "CSN" },
  { name: "Nagpur (नागपूर संत्रा पट्टा)", state: "Maharashtra", lat: 21.1458, lon: 79.0882, district: "Nagpur" },
  { name: "Solapur (सोलापूर डाळिंब पट्टा)", state: "Maharashtra", lat: 17.6599, lon: 75.9064, district: "Solapur" },
  { name: "Sangli (सांगली हळद / द्राक्ष)", state: "Maharashtra", lat: 16.8524, lon: 74.5815, district: "Sangli" },
  { name: "Kolhapur (कोल्हापूर ऊस पट्टा)", state: "Maharashtra", lat: 16.7050, lon: 74.2433, district: "Kolhapur" },
  { name: "Jalgaon (जळगाव केळी पट्टा)", state: "Maharashtra", lat: 21.0077, lon: 75.5626, district: "Jalgaon" },
  { name: "Akola (अकोला कापूस संशोधन केंद्र)", state: "Maharashtra", lat: 20.7002, lon: 77.0082, district: "Akola" },
  { name: "Amravati (अमरावती सोयाबीन)", state: "Maharashtra", lat: 20.9374, lon: 77.7796, district: "Amravati" },
  { name: "Baramati (बारामती कृषी विकास)", state: "Maharashtra", lat: 18.1517, lon: 74.5772, district: "Pune" },
  { name: "Indore (इंदौर सोयाबीन मंडी)", state: "Madhya Pradesh", lat: 22.7196, lon: 75.8577, district: "Indore" },
  { name: "Ludhiana (ਲੁਧਿਆਣਾ PAU Wheat)", state: "Punjab", lat: 30.9010, lon: 75.8573, district: "Ludhiana" },
  { name: "Karnal (करनाल Basmati / Wheat)", state: "Haryana", lat: 29.6857, lon: 76.9905, district: "Karnal" }
];

export const DEFAULT_LOCATION = POPULAR_AGRI_LOCATIONS[0]; // Kopargaon

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

/**
 * Maps WMO weather code to standard descriptive name and icon token.
 */
export function getWeatherConditionInfo(code = 0) {
  switch (Number(code)) {
    case 0:
      return { label: "Clear Sky", icon: "sun", severity: "clear" };
    case 1:
      return { label: "Mainly Clear", icon: "sun", severity: "clear" };
    case 2:
      return { label: "Partly Cloudy", icon: "cloud-sun", severity: "partly-cloudy" };
    case 3:
      return { label: "Overcast", icon: "cloud", severity: "cloudy" };
    case 45:
    case 48:
      return { label: "Fog / Depositing Rime Fog", icon: "cloud-fog", severity: "fog" };
    case 51:
    case 53:
    case 55:
      return { label: "Light Drizzle", icon: "cloud-drizzle", severity: "drizzle" };
    case 61:
      return { label: "Slight Rain", icon: "cloud-rain", severity: "rain-light" };
    case 63:
      return { label: "Moderate Rain", icon: "cloud-rain", severity: "rain-moderate" };
    case 65:
      return { label: "Heavy Rain", icon: "cloud-rain", severity: "rain-heavy" };
    case 80:
    case 81:
    case 82:
      return { label: "Rain Showers", icon: "cloud-rain", severity: "showers" };
    case 95:
      return { label: "Thunderstorm", icon: "cloud-lightning", severity: "storm" };
    case 96:
    case 99:
      return { label: "Severe Thunderstorm with Hail", icon: "cloud-lightning", severity: "hail" };
    default:
      return { label: "Variable Cloudiness", icon: "cloud-sun", severity: "cloudy" };
  }
}

/**
 * Fetch full agricultural weather forecast from backend or Open-Meteo fallback.
 */
export async function fetchFarmWeather(lat = DEFAULT_LOCATION.lat, lon = DEFAULT_LOCATION.lon, locationName = DEFAULT_LOCATION.name) {
  // 1. Try Backend Proxy Route first
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 6000);
    const url = `${API_BASE_URL}/api/v1/weather/forecast?lat=${lat}&lon=${lon}&location_name=${encodeURIComponent(locationName)}`;

    const res = await fetch(url, { signal: controller.signal });
    clearTimeout(timeoutId);

    if (res.ok) {
      const data = await res.json();
      if (data && data.success) {
        return data;
      }
    }
  } catch (err) {
    console.info("Backend weather proxy unreachable; falling back directly to Open-Meteo client API.", err);
  }

  // 2. Direct Open-Meteo Client Fallback (Guarantees uptime on static hosting)
  return await fetchOpenMeteoDirect(lat, lon, locationName);
}

/**
 * Direct Open-Meteo fetch with client-side agricultural rules calculation.
 */
async function fetchOpenMeteoDirect(latitude, longitude, locationName) {
  const url = `https://api.open-meteo.com/v1/forecast?latitude=${latitude}&longitude=${longitude}` +
    `&current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,rain,weather_code,wind_speed_10m,wind_direction_10m,wind_gusts_10m` +
    `&hourly=temperature_2m,relative_humidity_2m,precipitation_probability,precipitation,rain,weather_code,wind_speed_10m,wind_direction_10m,shortwave_radiation,et0_fao_evapotranspiration` +
    `&daily=temperature_2m_max,temperature_2m_min,apparent_temperature_max,apparent_temperature_min,precipitation_sum,rain_sum,precipitation_probability_max,wind_speed_10m_max,wind_gusts_10m_max,sunrise,sunset,weather_code,et0_fao_evapotranspiration` +
    `&timezone=auto&forecast_days=7`;

  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(`Open-Meteo API error: ${res.status}`);
  }
  const raw = await res.json();

  const currentRaw = raw.current || {};
  const hourlyRaw = raw.hourly || {};
  const dailyRaw = raw.daily || {};

  const current = {
    time: currentRaw.time,
    temperature_c: currentRaw.temperature_2m,
    apparent_temperature_c: currentRaw.apparent_temperature,
    relative_humidity_pct: currentRaw.relative_humidity_2m,
    precipitation_mm: currentRaw.precipitation || 0,
    rain_mm: currentRaw.rain || 0,
    weather_code: currentRaw.weather_code || 0,
    wind_speed_kmh: currentRaw.wind_speed_10m || 0,
    wind_direction_deg: currentRaw.wind_direction_10m || 0,
    wind_gusts_kmh: currentRaw.wind_gusts_10m || 0,
  };

  const hourly = (hourlyRaw.time || []).slice(0, 36).map((timeStr, i) => ({
    time: timeStr,
    temperature_c: hourlyRaw.temperature_2m?.[i],
    relative_humidity_pct: hourlyRaw.relative_humidity_2m?.[i],
    precipitation_probability_pct: hourlyRaw.precipitation_probability?.[i] || 0,
    precipitation_mm: hourlyRaw.precipitation?.[i] || 0,
    weather_code: hourlyRaw.weather_code?.[i] || 0,
    wind_speed_kmh: hourlyRaw.wind_speed_10m?.[i] || 0,
  }));

  const daily = (dailyRaw.time || []).map((dateStr, i) => ({
    date: dateStr,
    temp_max_c: dailyRaw.temperature_2m_max?.[i],
    temp_min_c: dailyRaw.temperature_2m_min?.[i],
    apparent_max_c: dailyRaw.apparent_temperature_max?.[i],
    precipitation_sum_mm: dailyRaw.precipitation_sum?.[i] || 0,
    rain_sum_mm: dailyRaw.rain_sum?.[i] || 0,
    precipitation_probability_max_pct: dailyRaw.precipitation_probability_max?.[i] || 0,
    wind_speed_max_kmh: dailyRaw.wind_speed_10m_max?.[i] || 0,
    wind_gusts_max_kmh: dailyRaw.wind_gusts_10m_max?.[i] || 0,
    sunrise: dailyRaw.sunrise?.[i],
    sunset: dailyRaw.sunset?.[i],
    weather_code: dailyRaw.weather_code?.[i] || 0,
    et0_fao_evapotranspiration_mm: dailyRaw.et0_fao_evapotranspiration?.[i] || 4.0,
  }));

  // Client-side rule evaluation matching backend engine
  const next24hRain = daily[0]?.rain_sum_mm || 0;
  const next24hPop = daily[0]?.precipitation_probability_max_pct || 0;
  const windKmh = current.wind_speed_kmh || 0;
  const gustKmh = current.wind_gusts_kmh || 0;
  const tempC = current.temperature_c || 25;
  const rhPct = current.relative_humidity_pct || 50;
  const et0 = daily[0]?.et0_fao_evapotranspiration_mm || 4.0;

  let activityWindow = "Good";
  let activityColor = "emerald";
  let activityRationale = `Gentle wind (${windKmh.toFixed(1)} km/h) and low shower probability (${next24hPop}%). Favorable for foliar spraying and field work.`;

  if (current.precipitation_mm > 0.5 || next24hPop >= 60 || windKmh >= 18.0 || gustKmh >= 25.0) {
    activityWindow = "Poor";
    activityColor = "red";
    activityRationale = `High wind (${windKmh.toFixed(1)} km/h) or rainfall risk (${next24hPop}%). Foliar applications will suffer droplet drift or wash-off.`;
  } else if (next24hPop >= 30 || windKmh >= 12.0) {
    activityWindow = "Caution";
    activityColor = "amber";
    activityRationale = `Moderate breeze (${windKmh.toFixed(1)} km/h) or shower risk (${next24hPop}%). Target calm early morning windows with coarse nozzles.`;
  }

  let diseaseLevel = "low";
  let diseaseNotice = "Ambient humidity and temperature are currently within normal baseline bounds. Continue standard agronomic scouting.";
  if (rhPct >= 80 && tempC >= 18 && tempC <= 28 && (current.precipitation_mm > 0 || next24hPop >= 45)) {
    diseaseLevel = "elevated";
    diseaseNotice = "Elevated humidity (80%+) and moderate temperatures (18–28°C) favor fungal pathogen sporulation. Scout crop leaves and use AI Crop Diagnostics to verify symptoms before taking action.";
  } else if (rhPct >= 70 && tempC >= 16 && tempC <= 30) {
    diseaseLevel = "moderate";
    diseaseNotice = "Mild canopy dew and humid air present. Monitor air circulation in dense crop stands.";
  }

  return {
    success: true,
    location: {
      name: locationName,
      latitude,
      longitude,
      elevation_m: raw.elevation || 0,
      timezone: raw.timezone || "UTC",
    },
    current,
    hourly,
    daily,
    agriculture: {
      rain_outlook: {
        status: next24hRain >= 12 ? "High Chance of Rainfall" : next24hPop >= 35 ? "Moderate Chance of Rain" : "Dry Conditions",
        level: next24hRain >= 12 ? "high" : next24hPop >= 35 ? "moderate" : "dry",
        summary: `Expected 24h precipitation: ~${next24hRain.toFixed(1)} mm (${next24hPop}% max probability).`,
        probability_pct: next24hPop,
        rain_sum_mm: next24hRain,
      },
      field_moisture: {
        status: next24hRain >= 10 ? "Increasing / Wet Soil Profile" : "Steady Depletion",
        summary: next24hRain >= 10 ? "Surface soil moisture will increase. Watch out for heavy machinery compaction." : `Standard crop transpiration demand (ET₀ ${et0.toFixed(1)} mm/day).`,
      },
      irrigation_check: {
        status: next24hRain >= 12 || next24hPop >= 70 ? "Delay Scheduled Irrigation" : "Normal Irrigation Cycle",
        badge: next24hRain >= 12 || next24hPop >= 70 ? "Hold" : "Normal",
        summary: next24hRain >= 12 || next24hPop >= 70 ? "Significant rain expected. Hold drip/furrow cycles to conserve water and prevent root rot." : `Atmospheric water loss is ~${et0.toFixed(1)} mm/day. Maintain regular crop irrigation.`,
        et0_mm: et0,
      },
      wind_conditions: {
        status: windKmh >= 22 ? "High Wind / Strong Gusts" : windKmh >= 14 ? "Moderate Breeze" : "Calm to Gentle Air",
        level: windKmh >= 22 ? "high" : windKmh >= 14 ? "moderate" : "calm",
        summary: `Sustained wind ${windKmh.toFixed(1)} km/h with gusts up to ${gustKmh.toFixed(1)} km/h.`,
        speed_kmh: windKmh,
        gusts_kmh: gustKmh,
      },
      field_activity_window: {
        status: activityWindow,
        level: activityColor,
        rationale: activityRationale,
      },
      heat_stress: {
        status: tempC >= 38 ? "Severe Heat Stress Alert" : tempC >= 33 ? "Moderate Thermal Load" : "Optimal Thermal Range",
        summary: tempC >= 38 ? `Extreme heat (${tempC.toFixed(1)}°C). Increase irrigation frequency to mitigate heat stress.` : `Ambient temperature is ${tempC.toFixed(1)}°C.`,
      },
      disease_favorable_weather: {
        status: diseaseLevel === "elevated" ? "Favorable for Fungal Sporulation" : diseaseLevel === "moderate" ? "Moderate Micro-Climatic Moisture" : "Low Disease-Favorable Weather Pressure",
        level: diseaseLevel,
        notice: diseaseNotice,
        disclaimer: "Weather conditions describe environmental suitability only. This is not a disease diagnosis.",
      },
    },
    source: {
      provider: "Open-Meteo",
      model: "ECMWF / GFS Hybrid Multi-Model",
      updated_at: new Date().toISOString(),
      documentation: "https://open-meteo.com/",
    },
    cached: false,
  };
}
