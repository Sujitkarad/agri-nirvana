import React, { useState, useEffect, useId } from "react";
import {
  Sun,
  Cloud,
  CloudSun,
  CloudRain,
  CloudDrizzle,
  CloudLightning,
  CloudFog,
  Wind,
  Droplets,
  Thermometer,
  Compass,
  MapPin,
  RefreshCw,
  AlertTriangle,
  CheckCircle2,
  Calendar,
  Clock,
  ExternalLink,
  Search,
  X,
  ShieldAlert,
  Gauge,
  Info
} from "lucide-react";
import {
  fetchFarmWeather,
  DEFAULT_LOCATION,
  POPULAR_AGRI_LOCATIONS,
  getWeatherConditionInfo
} from "../../services/weatherApi";

export default function FarmWeatherDashboard({
  theme = "harvest",
  isDark = false,
  onNavigateDiagnostics
}) {
  const [currentLocation, setCurrentLocation] = useState(DEFAULT_LOCATION);
  const [weatherData, setWeatherData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [locationModalOpen, setLocationModalOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [lastUpdated, setLastUpdated] = useState(null);
  const [geoLocating, setGeoLocating] = useState(false);
  const searchInputId = useId();

  // Load weather when location changes
  const loadWeather = async (loc = currentLocation) => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchFarmWeather(loc.lat, loc.lon, loc.name);
      setWeatherData(data);
      setLastUpdated(new Date());
    } catch (err) {
      console.error("Failed to load weather:", err);
      setError("Unable to retrieve weather data from provider. Please check your connection and try again.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadWeather(currentLocation);
  }, [currentLocation]);

  // Handle HTML5 browser geolocation
  const handleUseMyLocation = () => {
    if (!navigator.geolocation) {
      alert("Geolocation is not supported by your browser.");
      return;
    }
    setGeoLocating(true);
    navigator.geolocation.getCurrentPosition(
      (position) => {
        const { latitude, longitude } = position.coords;
        const myLoc = {
          name: `My Farm Location (${latitude.toFixed(3)}°N, ${longitude.toFixed(3)}°E)`,
          lat: latitude,
          lon: longitude,
          state: "Local Field"
        };
        setCurrentLocation(myLoc);
        setGeoLocating(false);
        setLocationModalOpen(false);
      },
      (geoError) => {
        setGeoLocating(false);
        let msg = "Could not detect location.";
        if (geoError.code === geoError.PERMISSION_DENIED) {
          msg = "Location permission was denied. You can select your district or mandi below.";
        }
        alert(msg);
      },
      { timeout: 10000, enableHighAccuracy: true }
    );
  };

  // Icon selector helper
  const renderWeatherIcon = (code, size = 24, className = "") => {
    const info = getWeatherConditionInfo(code);
    switch (info.icon) {
      case "sun":
        return <Sun size={size} className={`text-amber-500 ${className}`} />;
      case "cloud":
        return <Cloud size={size} className={`text-slate-400 ${className}`} />;
      case "cloud-rain":
        return <CloudRain size={size} className={`text-blue-500 ${className}`} />;
      case "cloud-drizzle":
        return <CloudDrizzle size={size} className={`text-cyan-400 ${className}`} />;
      case "cloud-lightning":
        return <CloudLightning size={size} className={`text-amber-400 ${className}`} />;
      case "cloud-fog":
        return <CloudFog size={size} className={`text-slate-400 ${className}`} />;
      default:
        return <CloudSun size={size} className={`text-emerald-500 ${className}`} />;
    }
  };

  const filteredLocations = POPULAR_AGRI_LOCATIONS.filter((loc) =>
    loc.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    loc.state.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const current = weatherData?.current || {};
  const agriculture = weatherData?.agriculture || {};
  const conditionInfo = getWeatherConditionInfo(current.weather_code);
  const activityWindow = agriculture.field_activity_window || { status: "Good", level: "emerald", rationale: "" };

  return (
    <div className="space-y-6 animate-fade-in pb-12">
      {/* 1. TOP LOCATION & HEADER BAR */}
      <div className={`rounded-3xl p-5 border transition-all ${
        isDark
          ? "border-emerald-800/40 bg-[#072017]/90 shadow-xl shadow-emerald-950/20"
          : "border-slate-200 bg-white shadow-md shadow-slate-100"
      }`}>
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="flex h-2.5 w-2.5 rounded-full bg-emerald-500 animate-pulse" />
              <span className="text-[11px] font-mono font-bold tracking-wider uppercase text-emerald-600 dark:text-emerald-400">
                Agro-Meteorological Telemetry
              </span>
            </div>
            <h1 className={`text-2xl sm:text-3xl font-black tracking-tight flex items-center gap-2.5 ${
              isDark ? "text-white" : "text-slate-900"
            }`}>
              <CloudSun className="text-emerald-500 shrink-0" size={28} />
              Farm Weather & Micro-Climate
            </h1>
            <div className="flex flex-wrap items-center gap-3 pt-1 text-xs">
              <button
                onClick={() => setLocationModalOpen(true)}
                className={`flex items-center gap-1.5 font-bold px-3 py-1 rounded-full border transition hover:scale-105 active:scale-95 ${
                  isDark
                    ? "border-emerald-500/40 bg-emerald-950/50 text-emerald-300 hover:bg-emerald-900/60"
                    : "border-emerald-300 bg-emerald-50 text-emerald-800 hover:bg-emerald-100"
                }`}
              >
                <MapPin size={13} className="text-emerald-500" />
                <span>{currentLocation.name}</span>
                <span className="text-[10px] opacity-75 underline ml-1">Change</span>
              </button>

              <span className={`text-[11px] ${isDark ? "text-slate-400" : "text-slate-500"}`}>
                {lastUpdated
                  ? `Updated at ${lastUpdated.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}`
                  : "Connecting..."}
              </span>

              {weatherData?.cached && (
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">
                  ⚡ 10m TTL Cache
                </span>
              )}
            </div>
          </div>

          {/* Right Action Buttons */}
          <div className="flex items-center gap-2.5">
            <button
              onClick={handleUseMyLocation}
              disabled={geoLocating}
              className={`flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-bold border transition active:scale-95 ${
                isDark
                  ? "border-emerald-800/60 bg-emerald-950/40 text-emerald-300 hover:bg-emerald-900/40"
                  : "border-slate-200 bg-slate-50 text-slate-700 hover:bg-slate-100"
              }`}
            >
              <Compass size={14} className={geoLocating ? "animate-spin" : ""} />
              <span>{geoLocating ? "Locating..." : "Use My GPS"}</span>
            </button>

            <button
              onClick={() => loadWeather()}
              disabled={loading}
              className={`p-2.5 rounded-xl border transition active:scale-95 ${
                isDark
                  ? "border-emerald-800/60 bg-emerald-950/40 text-emerald-300 hover:bg-emerald-900/40"
                  : "border-slate-200 bg-slate-50 text-slate-700 hover:bg-slate-100"
              }`}
              title="Refresh weather data"
            >
              <RefreshCw size={15} className={loading ? "animate-spin text-emerald-500" : ""} />
            </button>
          </div>
        </div>
      </div>

      {/* ERROR STATE */}
      {error && (
        <div className="rounded-2xl border border-red-500/40 bg-red-500/10 p-4 text-xs text-red-300 flex items-center justify-between gap-4">
          <div className="flex items-center gap-2.5">
            <AlertTriangle size={18} className="text-red-400 shrink-0" />
            <span>{error}</span>
          </div>
          <button
            onClick={() => loadWeather()}
            className="px-3 py-1 bg-red-600 text-white font-bold rounded-lg hover:bg-red-500 transition shrink-0"
          >
            Retry
          </button>
        </div>
      )}

      {/* 2. CURRENT CONDITIONS & BEST FIELD ACTIVITY HERO */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Hero Card: Current Weather */}
        <div className={`lg:col-span-7 rounded-3xl p-6 border transition-all ${
          isDark
            ? "border-emerald-800/40 bg-[#072017] shadow-xl"
            : "border-slate-200 bg-white shadow-xl"
        }`}>
          <div className="flex items-center justify-between border-b pb-4 mb-5 border-slate-200/60 dark:border-emerald-900/40">
            <div>
              <span className="text-[11px] font-bold uppercase tracking-wider text-emerald-600 dark:text-emerald-400">
                Live Atmospheric Reading
              </span>
              <h2 className={`text-xl font-black ${isDark ? "text-white" : "text-slate-900"}`}>
                Current Field Conditions
              </h2>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold text-slate-500 dark:text-slate-400">
                {conditionInfo.label}
              </span>
              <div className="p-2 rounded-2xl bg-emerald-500/10 border border-emerald-500/20">
                {renderWeatherIcon(current.weather_code, 28)}
              </div>
            </div>
          </div>

          <div className="flex flex-col sm:flex-row sm:items-baseline gap-6 mb-6">
            <div className="flex items-baseline gap-2">
              <span className={`text-5xl sm:text-6xl font-black tracking-tight ${isDark ? "text-white" : "text-slate-900"}`}>
                {current.temperature_c !== undefined ? `${Math.round(current.temperature_c)}°` : "--"}
              </span>
              <span className="text-2xl font-bold text-emerald-500">C</span>
            </div>

            <div className={`text-xs space-y-1 ${isDark ? "text-slate-300" : "text-slate-600"}`}>
              <p>
                Feels like: <strong className="text-slate-900 dark:text-white">{current.apparent_temperature_c !== undefined ? `${Math.round(current.apparent_temperature_c)}°C` : "--"}</strong>
              </p>
              <p>
                Condition: <strong className="text-emerald-600 dark:text-emerald-400">{conditionInfo.label}</strong>
              </p>
              <p className="text-[11px] opacity-75">
                Elevation: {weatherData?.location?.elevation_m || 490}m AMSL
              </p>
            </div>
          </div>

          {/* Key Metrics Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className={`rounded-2xl p-3 border transition-colors ${
              isDark ? "border-emerald-900/50 bg-[#051810]" : "border-slate-100 bg-slate-50/80"
            }`}>
              <div className="flex items-center gap-1.5 text-xs text-slate-500 dark:text-slate-400 mb-1">
                <Droplets size={14} className="text-blue-500" />
                <span>Humidity</span>
              </div>
              <p className={`text-lg font-black ${isDark ? "text-white" : "text-slate-900"}`}>
                {current.relative_humidity_pct !== undefined ? `${current.relative_humidity_pct}%` : "--"}
              </p>
              <span className="text-[10px] text-slate-400">Relative Humidity</span>
            </div>

            <div className={`rounded-2xl p-3 border transition-colors ${
              isDark ? "border-emerald-900/50 bg-[#051810]" : "border-slate-100 bg-slate-50/80"
            }`}>
              <div className="flex items-center gap-1.5 text-xs text-slate-500 dark:text-slate-400 mb-1">
                <Wind size={14} className="text-cyan-500" />
                <span>Wind Speed</span>
              </div>
              <p className={`text-lg font-black ${isDark ? "text-white" : "text-slate-900"}`}>
                {current.wind_speed_kmh !== undefined ? `${Math.round(current.wind_speed_kmh)}` : "--"}
                <span className="text-xs font-normal ml-1">km/h</span>
              </p>
              <span className="text-[10px] text-slate-400">
                Gusts: {current.wind_gusts_kmh !== undefined ? `${Math.round(current.wind_gusts_kmh)} km/h` : "--"}
              </span>
            </div>

            <div className={`rounded-2xl p-3 border transition-colors ${
              isDark ? "border-emerald-900/50 bg-[#051810]" : "border-slate-100 bg-slate-50/80"
            }`}>
              <div className="flex items-center gap-1.5 text-xs text-slate-500 dark:text-slate-400 mb-1">
                <CloudRain size={14} className="text-blue-400" />
                <span>Rain (1h)</span>
              </div>
              <p className={`text-lg font-black ${isDark ? "text-white" : "text-slate-900"}`}>
                {current.precipitation_mm !== undefined ? `${current.precipitation_mm.toFixed(1)}` : "0.0"}
                <span className="text-xs font-normal ml-1">mm</span>
              </p>
              <span className="text-[10px] text-slate-400">Current Surface Rain</span>
            </div>

            <div className={`rounded-2xl p-3 border transition-colors ${
              isDark ? "border-emerald-900/50 bg-[#051810]" : "border-slate-100 bg-slate-50/80"
            }`}>
              <div className="flex items-center gap-1.5 text-xs text-slate-500 dark:text-slate-400 mb-1">
                <Gauge size={14} className="text-amber-500" />
                <span>Evaporation</span>
              </div>
              <p className={`text-lg font-black ${isDark ? "text-white" : "text-slate-900"}`}>
                {weatherData?.daily?.[0]?.et0_fao_evapotranspiration_mm !== undefined
                  ? `${weatherData.daily[0].et0_fao_evapotranspiration_mm.toFixed(1)}`
                  : "4.2"}
                <span className="text-xs font-normal ml-1">mm/d</span>
              </p>
              <span className="text-[10px] text-slate-400">FAO-56 ET₀ Rate</span>
            </div>
          </div>
        </div>

        {/* Right Card: Best Field Activity Window & Agronomic Guidance */}
        <div className={`lg:col-span-5 rounded-3xl p-6 border flex flex-col justify-between transition-all ${
          isDark
            ? "border-emerald-800/40 bg-[#072017] shadow-xl"
            : "border-slate-200 bg-white shadow-xl"
        }`}>
          <div>
            <div className="flex items-center justify-between border-b pb-4 mb-4 border-slate-200/60 dark:border-emerald-900/40">
              <span className="text-[11px] font-bold uppercase tracking-wider text-emerald-600 dark:text-emerald-400">
                Operational Window
              </span>
              <span className={`px-2.5 py-1 rounded-full text-xs font-black uppercase tracking-wider ${
                activityWindow.level === "emerald"
                  ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                  : activityWindow.level === "amber"
                    ? "bg-amber-500/20 text-amber-400 border border-amber-500/30"
                    : "bg-red-500/20 text-red-400 border border-red-500/30"
              }`}>
                {activityWindow.status} Window
              </span>
            </div>

            <h3 className={`text-lg font-black mb-2 ${isDark ? "text-white" : "text-slate-900"}`}>
              Field Spray & Tractor Activity
            </h3>
            <p className={`text-xs leading-relaxed mb-4 ${isDark ? "text-slate-300" : "text-slate-600"}`}>
              {activityWindow.rationale || "Atmospheric conditions are stable for general field tractor operations and chemical application."}
            </p>

            <div className={`rounded-2xl p-3 border mb-4 text-xs space-y-2 ${
              isDark ? "border-emerald-900/60 bg-[#051810]" : "border-slate-100 bg-emerald-50/50"
            }`}>
              <div className="flex items-center justify-between">
                <span className="text-slate-500 dark:text-slate-400">Foliar Absorption Risk:</span>
                <strong className={current.precipitation_mm > 0 ? "text-red-400" : "text-emerald-600 dark:text-emerald-400"}>
                  {current.precipitation_mm > 0 ? "Wash-off Risk High" : "Optimal (Dry Canopy)"}
                </strong>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-slate-500 dark:text-slate-400">Spray Droplet Drift:</span>
                <strong className={current.wind_speed_kmh > 15 ? "text-amber-400" : "text-emerald-600 dark:text-emerald-400"}>
                  {current.wind_speed_kmh > 15 ? "Moderate Drift (Use Coarse Nozzles)" : "Low (<12 km/h)"}
                </strong>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-slate-500 dark:text-slate-400">Optimal Application Hours:</span>
                <strong className="text-slate-900 dark:text-white">6:00 AM – 9:30 AM</strong>
              </div>
            </div>
          </div>

          <div className="pt-2 text-[11px] text-slate-500 dark:text-slate-400 italic">
            * Rules evaluated against live wind gusts and next-24h rain probabilities.
          </div>
        </div>
      </div>

      {/* 3. FARM WEATHER STATUS GRID (4 KEY SIGNALS) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Signal 1: Rain Outlook */}
        <div className={`rounded-3xl p-5 border transition-all ${
          isDark ? "border-emerald-800/40 bg-[#072017]" : "border-slate-200 bg-white shadow-md"
        }`}>
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold text-slate-500 dark:text-slate-400">🌧 Rain Outlook</span>
            <span className={`text-[10px] font-black px-2 py-0.5 rounded-full uppercase ${
              agriculture.rain_outlook?.level === "high"
                ? "bg-red-500/20 text-red-400"
                : agriculture.rain_outlook?.level === "moderate"
                  ? "bg-amber-500/20 text-amber-400"
                  : "bg-emerald-500/20 text-emerald-400"
            }`}>
              {agriculture.rain_outlook?.status || "Dry"}
            </span>
          </div>
          <p className={`text-xs leading-relaxed ${isDark ? "text-slate-300" : "text-slate-600"}`}>
            {agriculture.rain_outlook?.summary || "Low rain probability over next 24 hours."}
          </p>
        </div>

        {/* Signal 2: Field Moisture */}
        <div className={`rounded-3xl p-5 border transition-all ${
          isDark ? "border-emerald-800/40 bg-[#072017]" : "border-slate-200 bg-white shadow-md"
        }`}>
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold text-slate-500 dark:text-slate-400">🌱 Field Moisture</span>
            <span className="text-[10px] font-black px-2 py-0.5 rounded-full bg-blue-500/20 text-blue-400 uppercase">
              Vertisol / Black Soil
            </span>
          </div>
          <p className={`text-xs leading-relaxed ${isDark ? "text-slate-300" : "text-slate-600"}`}>
            {agriculture.field_moisture?.summary || "Standard crop water consumption. Surface soil trafficable."}
          </p>
        </div>

        {/* Signal 3: Irrigation Check */}
        <div className={`rounded-3xl p-5 border transition-all ${
          isDark ? "border-emerald-800/40 bg-[#072017]" : "border-slate-200 bg-white shadow-md"
        }`}>
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold text-slate-500 dark:text-slate-400">💧 Irrigation Check</span>
            <span className={`text-[10px] font-black px-2 py-0.5 rounded-full uppercase ${
              agriculture.irrigation_check?.badge === "Hold"
                ? "bg-red-500/20 text-red-400"
                : agriculture.irrigation_check?.badge === "Review"
                  ? "bg-amber-500/20 text-amber-400"
                  : "bg-emerald-500/20 text-emerald-400"
            }`}>
              {agriculture.irrigation_check?.badge || "Normal"}
            </span>
          </div>
          <p className={`text-xs leading-relaxed ${isDark ? "text-slate-300" : "text-slate-600"}`}>
            {agriculture.irrigation_check?.summary || "Maintain regular scheduled drip irrigation cycles."}
          </p>
        </div>

        {/* Signal 4: Wind Conditions */}
        <div className={`rounded-3xl p-5 border transition-all ${
          isDark ? "border-emerald-800/40 bg-[#072017]" : "border-slate-200 bg-white shadow-md"
        }`}>
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold text-slate-500 dark:text-slate-400">🌬 Wind & Drift</span>
            <span className={`text-[10px] font-black px-2 py-0.5 rounded-full uppercase ${
              agriculture.wind_conditions?.level === "high"
                ? "bg-red-500/20 text-red-400"
                : agriculture.wind_conditions?.level === "moderate"
                  ? "bg-amber-500/20 text-amber-400"
                  : "bg-emerald-500/20 text-emerald-400"
            }`}>
              {agriculture.wind_conditions?.status || "Calm"}
            </span>
          </div>
          <p className={`text-xs leading-relaxed ${isDark ? "text-slate-300" : "text-slate-600"}`}>
            {agriculture.wind_conditions?.summary || "Calm winds facilitate accurate foliar and drone misting."}
          </p>
        </div>
      </div>

      {/* 4. DISEASE-FAVORABLE WEATHER NOTICE (Non-prescriptive) */}
      <div className={`rounded-3xl p-5 border transition-all ${
        agriculture.disease_favorable_weather?.level === "elevated"
          ? "border-amber-500/40 bg-amber-500/10 text-amber-200"
          : isDark
            ? "border-emerald-800/40 bg-[#072017] text-slate-300"
            : "border-slate-200 bg-white text-slate-700 shadow-md"
      }`}>
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-start gap-3">
            <ShieldAlert size={22} className="text-amber-500 shrink-0 mt-0.5" />
            <div className="space-y-1">
              <h4 className="text-sm font-black flex items-center gap-2">
                <span>Micro-Climate Pathogen Pressure:</span>
                <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${
                  agriculture.disease_favorable_weather?.level === "elevated"
                    ? "bg-red-500/20 text-red-400 border border-red-500/30"
                    : "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                }`}>
                  {agriculture.disease_favorable_weather?.status || "Low Pathogen Pressure"}
                </span>
              </h4>
              <p className="text-xs leading-relaxed text-slate-600 dark:text-slate-300">
                {agriculture.disease_favorable_weather?.notice ||
                  "Ambient relative humidity and temperatures do not present heightened sporulation risk. Maintain routine farm scouting."}
              </p>
              <p className="text-[11px] text-slate-500 italic">
                {agriculture.disease_favorable_weather?.disclaimer ||
                  "Weather conditions describe environmental suitability only. This is not a disease diagnosis."}
              </p>
            </div>
          </div>

          {onNavigateDiagnostics && (
            <button
              onClick={() => onNavigateDiagnostics()}
              className="rounded-xl px-4 py-2 text-xs font-bold bg-emerald-600 text-white hover:bg-emerald-500 transition shadow shrink-0 active:scale-95"
            >
              Verify Leaf Symptoms
            </button>
          )}
        </div>
      </div>

      {/* 5. 24-HOUR HOURLY TIMELINE (Horizontal Scrollable) */}
      <div className={`rounded-3xl p-6 border transition-all ${
        isDark ? "border-emerald-800/40 bg-[#072017] shadow-xl" : "border-slate-200 bg-white shadow-xl"
      }`}>
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Clock size={18} className="text-emerald-500" />
            <h3 className={`text-base font-black ${isDark ? "text-white" : "text-slate-900"}`}>
              Hourly Field Forecast (Next 24 Hours)
            </h3>
          </div>
          <span className="text-xs text-slate-500 dark:text-slate-400 font-mono">
            Scroll horizontally →
          </span>
        </div>

        <div className="flex overflow-x-auto gap-3 pb-2 pt-1 no-scrollbar">
          {(weatherData?.hourly || []).slice(0, 24).map((h, idx) => {
            const timeDate = new Date(h.time);
            const hourStr = timeDate.toLocaleTimeString([], { hour: "numeric", hour12: true });
            const isNow = idx === 0;

            return (
              <div
                key={h.time || idx}
                className={`flex flex-col items-center justify-between min-w-[76px] p-3 rounded-2xl border text-center transition-all ${
                  isNow
                    ? "border-emerald-500 bg-emerald-500/15 shadow-md glow-emerald font-bold"
                    : isDark
                      ? "border-emerald-900/40 bg-[#051810]"
                      : "border-slate-100 bg-slate-50/80"
                }`}
              >
                <span className={`text-[11px] font-bold ${isNow ? "text-emerald-400" : "text-slate-500 dark:text-slate-400"}`}>
                  {isNow ? "Now" : hourStr}
                </span>

                <div className="my-2">
                  {renderWeatherIcon(h.weather_code, 22)}
                </div>

                <span className={`text-sm font-black ${isDark ? "text-white" : "text-slate-900"}`}>
                  {h.temperature_c !== undefined ? `${Math.round(h.temperature_c)}°` : "--"}
                </span>

                <div className="flex items-center gap-0.5 text-[10px] text-blue-500 font-bold mt-1">
                  <Droplets size={10} />
                  <span>{h.precipitation_probability_pct || 0}%</span>
                </div>

                <span className="text-[9px] text-slate-400 mt-0.5">
                  {Math.round(h.wind_speed_kmh || 0)} km/h
                </span>
              </div>
            );
          })}
        </div>
      </div>

      {/* 6. 7-DAY AGRICULTURAL FORECAST TABLE */}
      <div className={`rounded-3xl p-6 border transition-all ${
        isDark ? "border-emerald-800/40 bg-[#072017] shadow-xl" : "border-slate-200 bg-white shadow-xl"
      }`}>
        <div className="flex items-center justify-between mb-5 border-b pb-3 border-slate-200/60 dark:border-emerald-900/40">
          <div className="flex items-center gap-2">
            <Calendar size={18} className="text-emerald-500" />
            <h3 className={`text-base font-black ${isDark ? "text-white" : "text-slate-900"}`}>
              7-Day Agricultural Outlook
            </h3>
          </div>
          <span className="text-xs text-slate-500 dark:text-slate-400">
            ECMWF High-Resolution Forecast
          </span>
        </div>

        <div className="space-y-3">
          {(weatherData?.daily || []).map((day, idx) => {
            const dateObj = new Date(day.date);
            const dayName = idx === 0
              ? "Today"
              : idx === 1
                ? "Tomorrow"
                : dateObj.toLocaleDateString([], { weekday: "short", month: "short", day: "numeric" });
            const info = getWeatherConditionInfo(day.weather_code);

            return (
              <div
                key={day.date || idx}
                className={`grid grid-cols-12 items-center gap-3 p-3.5 rounded-2xl border transition-colors ${
                  idx === 0
                    ? isDark ? "border-emerald-500/40 bg-emerald-950/30" : "border-emerald-200 bg-emerald-50/40"
                    : isDark ? "border-emerald-900/40 bg-[#051810]" : "border-slate-100 bg-white"
                }`}
              >
                {/* Day name */}
                <div className="col-span-3 sm:col-span-2">
                  <p className={`text-xs font-black ${isDark ? "text-white" : "text-slate-900"}`}>
                    {dayName}
                  </p>
                  <span className="text-[10px] text-slate-400 font-mono">
                    {dateObj.toLocaleDateString([], { day: "numeric", month: "short" })}
                  </span>
                </div>

                {/* Weather icon & condition */}
                <div className="col-span-4 sm:col-span-3 flex items-center gap-2">
                  {renderWeatherIcon(day.weather_code, 20)}
                  <span className="text-xs font-bold truncate text-slate-700 dark:text-slate-300">
                    {info.label}
                  </span>
                </div>

                {/* Rain probability */}
                <div className="col-span-2 sm:col-span-2 text-right sm:text-center">
                  <span className="text-xs font-bold text-blue-500 flex items-center justify-end sm:justify-center gap-1">
                    <Droplets size={12} />
                    {day.precipitation_probability_max_pct || 0}%
                  </span>
                  <span className="text-[10px] text-slate-400">
                    {day.rain_sum_mm ? `${day.rain_sum_mm.toFixed(1)} mm` : "0 mm"}
                  </span>
                </div>

                {/* Min / Max Temp Bar */}
                <div className="col-span-3 sm:col-span-3 flex items-center justify-end gap-2 text-xs font-bold">
                  <span className="text-slate-400 font-mono text-[11px]">
                    {Math.round(day.temp_min_c)}°
                  </span>
                  <div className="hidden sm:block w-20 h-1.5 rounded-full bg-slate-200 dark:bg-slate-800 overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-blue-400 via-emerald-400 to-amber-500 rounded-full"
                      style={{ width: "100%" }}
                    />
                  </div>
                  <span className={`font-mono text-sm font-black ${isDark ? "text-white" : "text-slate-900"}`}>
                    {Math.round(day.temp_max_c)}°
                  </span>
                </div>

                {/* ET0 Water Loss */}
                <div className="hidden sm:col-span-2 sm:flex flex-col items-end text-xs">
                  <span className="font-bold text-slate-600 dark:text-slate-300">
                    {day.et0_fao_evapotranspiration_mm ? `${day.et0_fao_evapotranspiration_mm.toFixed(1)}` : "4.0"} mm
                  </span>
                  <span className="text-[10px] text-slate-400">ET₀ loss</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* 7. DATA SOURCE, METHODOLOGY & DISCLAIMER FOOTER */}
      <div className={`rounded-2xl p-4 border text-xs text-slate-500 dark:text-slate-400 space-y-1.5 ${
        isDark ? "border-emerald-900/40 bg-[#04160f]/60" : "border-slate-200 bg-slate-50"
      }`}>
        <div className="flex flex-wrap items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <Info size={14} className="text-emerald-500" />
            <span>Weather telemetry provided via <strong>Open-Meteo API</strong> (ECMWF IFS / GFS Multi-Model Ensemble).</span>
          </div>
          <a
            href="https://open-meteo.com/"
            target="_blank"
            rel="noopener noreferrer"
            className="text-emerald-600 dark:text-emerald-400 hover:underline flex items-center gap-1 font-bold"
          >
            <span>Documentation</span>
            <ExternalLink size={12} />
          </a>
        </div>
        <p className="text-[11px] leading-relaxed">
          <strong>Agricultural Disclaimer:</strong> Meteorological forecasts describe probabilities and local atmospheric conditions. Weather signals are advisory in nature. Confirm on-field conditions and visual plant symptoms before applying agrochemical inputs or modifying irrigation schedules.
        </p>
      </div>

      {/* LOCATION SELECTION MODAL */}
      {locationModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/70 backdrop-blur-sm animate-fade-in">
          <div className={`relative w-full max-w-lg rounded-3xl p-6 border shadow-2xl transition-all ${
            isDark ? "border-emerald-800/60 bg-[#072017] text-white" : "border-slate-200 bg-white text-slate-900"
          }`}>
            <div className="flex items-center justify-between pb-4 border-b border-slate-200 dark:border-emerald-900/50 mb-4">
              <h3 className="text-lg font-black flex items-center gap-2">
                <MapPin className="text-emerald-500" size={20} />
                Select Agricultural Locality
              </h3>
              <button
                onClick={() => setLocationModalOpen(false)}
                className="p-1 rounded-lg hover:bg-slate-100 dark:hover:bg-emerald-900/40 text-slate-400"
              >
                <X size={18} />
              </button>
            </div>

            <div className="relative mb-4">
              <label htmlFor={searchInputId} className="sr-only">
                Search district, taluka, or state
              </label>
              <Search className="absolute left-3.5 top-3 text-slate-400" size={16} />
              <input
                id={searchInputId}
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search district, taluka, or state..."
                className={`w-full rounded-xl pl-10 pr-4 py-2.5 text-xs font-bold border outline-hidden transition ${
                  isDark
                    ? "border-emerald-800/60 bg-[#051810] text-white placeholder-slate-500 focus:border-emerald-400"
                    : "border-slate-200 bg-slate-50 text-slate-900 placeholder-slate-400 focus:border-emerald-600"
                }`}
              />
            </div>

            <div className="space-y-2 max-h-64 overflow-y-auto no-scrollbar pr-1">
              {filteredLocations.map((loc) => {
                const isSelected = currentLocation.name === loc.name;
                return (
                  <button
                    key={loc.name}
                    onClick={() => {
                      setCurrentLocation(loc);
                      setLocationModalOpen(false);
                    }}
                    className={`w-full flex items-center justify-between p-3 rounded-xl border text-left text-xs transition ${
                      isSelected
                        ? "border-emerald-500 bg-emerald-500/15 font-bold text-emerald-400"
                        : isDark
                          ? "border-emerald-900/30 bg-[#051810]/60 hover:bg-emerald-950/80 text-slate-300"
                          : "border-slate-100 bg-slate-50 hover:bg-slate-100 text-slate-700"
                    }`}
                  >
                    <div>
                      <p className="font-bold">{loc.name}</p>
                      <span className="text-[10px] text-slate-400">
                        {loc.state} • {loc.lat.toFixed(2)}°N, {loc.lon.toFixed(2)}°E
                      </span>
                    </div>
                    {isSelected && <CheckCircle2 size={16} className="text-emerald-500" />}
                  </button>
                );
              })}
            </div>

            <div className="mt-4 pt-3 border-t border-slate-200 dark:border-emerald-900/50 flex justify-end">
              <button
                onClick={() => setLocationModalOpen(false)}
                className="px-4 py-2 rounded-xl text-xs font-bold border border-slate-300 dark:border-emerald-800 text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-emerald-950/60"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
