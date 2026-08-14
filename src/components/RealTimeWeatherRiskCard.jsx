import React, { useState, useEffect } from "react";
import { CloudSun, Droplets, Wind, ShieldAlert, CheckCircle2, RefreshCw, MapPin } from "lucide-react";
import { calculateFungalRisk } from "../data/agriData";

export default function RealTimeWeatherRiskCard({ diseaseId = "tomato-late-blight", isDark = false }) {
  const [weather, setWeather] = useState({
    tempC: 28,
    humidityPct: 76,
    windKm: 11,
    condition: "Partly Humid",
    locationName: "Nagpur AgTech Field Zone (21.14°N, 79.08°E)",
    isLive: false,
  });

  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchLiveWeather();
  }, []);

  const fetchLiveWeather = async () => {
    setLoading(true);
    try {
      // Default to Nagpur AgTech Zone coordinates if geolocation not available immediately
      let lat = 21.1458;
      let lon = 79.0882;

      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
          (pos) => {
            lat = pos.coords.latitude;
            lon = pos.coords.longitude;
            queryOpenMeteo(lat, lon);
          },
          () => {
            queryOpenMeteo(lat, lon);
          },
          { timeout: 4000 }
        );
      } else {
        queryOpenMeteo(lat, lon);
      }
    } catch (e) {
      console.warn("Weather fetch fallback:", e);
      setLoading(false);
    }
  };

  const queryOpenMeteo = async (lat, lon) => {
    try {
      const res = await fetch(
        `https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}&current=temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code`
      );
      if (!res.ok) throw new Error("OpenMeteo network error");
      const data = await res.json();
      if (data.current) {
        setWeather({
          tempC: Math.round(data.current.temperature_2m),
          humidityPct: Math.round(data.current.relative_humidity_2m),
          windKm: Math.round(data.current.wind_speed_10m),
          condition: data.current.relative_humidity_2m > 80 ? "High Humidity / Rain Risk" : "Partly Sunny",
          locationName: `Live Coordinates (${lat.toFixed(2)}°N, ${lon.toFixed(2)}°E)`,
          isLive: true,
        });
      }
    } catch (err) {
      console.warn("Using offline fallback telemetry:", err);
    } finally {
      setLoading(false);
    }
  };

  const riskAnalysis = calculateFungalRisk(weather.tempC, weather.humidityPct, diseaseId);

  return (
    <div
      className={`rounded-2xl p-4 border transition-all ${
        isDark ? "border-emerald-800/40 bg-[#04160f]" : "border-slate-200 bg-white shadow-sm"
      }`}
    >
      <div className="flex items-center justify-between mb-3 border-b pb-2.5 border-slate-200/50">
        <div>
          <div className="flex items-center gap-2">
            <CloudSun size={18} className="text-amber-500" />
            <h4 className={`text-xs font-black uppercase tracking-wider ${isDark ? "text-emerald-300" : "text-slate-800"}`}>
              Real-Time Canopy & Microclimate Telemetry
            </h4>
          </div>
          <p className={`text-[10px] flex items-center gap-1 mt-0.5 ${isDark ? "text-emerald-200/60" : "text-slate-500"}`}>
            <MapPin size={10} className="text-emerald-500" /> {weather.locationName}
          </p>
        </div>

        <button
          onClick={fetchLiveWeather}
          disabled={loading}
          className={`flex items-center gap-1 rounded-lg px-2.5 py-1 text-[10px] font-bold border transition ${
            weather.isLive
              ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/30"
              : isDark
              ? "bg-slate-800 text-slate-300 border-slate-700"
              : "bg-slate-100 text-slate-700 border-slate-200"
          }`}
        >
          <RefreshCw size={11} className={loading ? "animate-spin" : ""} />
          {weather.isLive ? "Open-Meteo Live API" : "Refresh Weather"}
        </button>
      </div>

      {/* METRIC CARDS */}
      <div className="grid grid-cols-3 gap-2 mb-3 text-center">
        <div className={`p-2 rounded-xl border ${isDark ? "bg-emerald-950/30 border-emerald-900/40" : "bg-slate-50 border-slate-200"}`}>
          <span className="text-[10px] font-bold text-slate-500 block">Temperature</span>
          <span className="text-sm font-black text-slate-900 dark:text-white font-mono">{weather.tempC}°C</span>
        </div>
        <div className={`p-2 rounded-xl border ${isDark ? "bg-emerald-950/30 border-emerald-900/40" : "bg-slate-50 border-slate-200"}`}>
          <span className="text-[10px] font-bold text-slate-500 block flex items-center justify-center gap-1">
            <Droplets size={10} className="text-cyan-500" /> Humidity
          </span>
          <span className="text-sm font-black text-cyan-600 dark:text-cyan-400 font-mono">{weather.humidityPct}%</span>
        </div>
        <div className={`p-2 rounded-xl border ${isDark ? "bg-emerald-950/30 border-emerald-900/40" : "bg-slate-50 border-slate-200"}`}>
          <span className="text-[10px] font-bold text-slate-500 block flex items-center justify-center gap-1">
            <Wind size={10} className="text-emerald-500" /> Wind
          </span>
          <span className="text-sm font-black text-slate-900 dark:text-white font-mono">{weather.windKm} km/h</span>
        </div>
      </div>

      {/* DYNAMIC FUNGAL RISK BANNER */}
      <div className={`p-3 rounded-xl border flex items-center justify-between ${
        riskAnalysis.riskScore >= 80 
          ? "bg-red-500/10 border-red-500/30 text-red-700 dark:text-red-300"
          : riskAnalysis.riskScore >= 60
          ? "bg-amber-500/10 border-amber-500/30 text-amber-800 dark:text-amber-300"
          : "bg-emerald-500/10 border-emerald-500/30 text-emerald-800 dark:text-emerald-300"
      }`}>
        <div className="flex items-center gap-2.5">
          <ShieldAlert size={18} className="shrink-0" />
          <div>
            <div className="text-xs font-black">{riskAnalysis.riskLevel} ({riskAnalysis.riskScore}% Fungal Index)</div>
            <p className="text-[10px] opacity-90 mt-0.5">{riskAnalysis.idealSprayWindow}</p>
          </div>
        </div>
      </div>
    </div>
  );
}
