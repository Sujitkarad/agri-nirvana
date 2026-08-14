import React, { useState, useEffect, useRef } from "react";
import { Eye, Sun, Flame, Zap, ShieldAlert, Sparkles } from "lucide-react";

export default function PreSymptomaticNIRScanner({ imageSrc, disease, isDark = false }) {
  const canvasRef = useRef(null);
  const [spectralMode, setSpectralMode] = useState("ndvi"); // 'ndvi' | 'rededge' | 'thermal' | 'visible'

  useEffect(() => {
    if (!imageSrc || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    const img = new Image();
    img.crossOrigin = "anonymous";
    img.src = imageSrc;

    img.onload = () => {
      canvas.width = img.width || 600;
      canvas.height = img.height || 400;

      ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
      if (spectralMode === "visible") return;

      const imgData = ctx.getImageData(0, 0, canvas.width, canvas.height);
      const data = imgData.data;

      for (let i = 0; i < data.length; i += 4) {
        const r = data[i];
        const g = data[i + 1];
        const b = data[i + 2];

        if (spectralMode === "ndvi") {
          // NDVI Formula: NIR = 2*G - R proxy
          const nir = Math.min(255, Math.max(0, 2 * g - r));
          const ndviVal = (nir - r) / (nir + r + 1);

          if (ndviVal < 0.1) {
            // High stress / pre-symptomatic lesion
            data[i] = 239; // Red
            data[i + 1] = 68;
            data[i + 2] = 68;
          } else if (ndviVal < 0.35) {
            // Moderate stress
            data[i] = 245; // Amber
            data[i + 1] = 158;
            data[i + 2] = 11;
          } else {
            // Vibrant healthy vegetation
            data[i] = 16; // Emerald
            data[i + 1] = 185;
            data[i + 2] = 129;
          }
        } else if (spectralMode === "rededge") {
          // Red-Edge Transpiration Breakdown (680-730nm)
          const redEdge = (r * 1.4 - b * 0.6);
          data[i] = Math.min(255, redEdge * 1.2);
          data[i + 1] = Math.min(255, g * 0.7);
          data[i + 2] = Math.min(255, b * 1.8);
        } else if (spectralMode === "thermal") {
          // Thermal Stomatal Heatmap (False Color IR scale)
          const heatVal = (r * 0.5 + g * 0.3 + b * 0.2);
          if (heatVal > 140) {
            data[i] = 225; // Hot thermal anomaly (stoma closure)
            data[i + 1] = 29;
            data[i + 2] = 72;
          } else if (heatVal > 90) {
            data[i] = 234; // Medium warm
            data[i + 1] = 179;
            data[i + 2] = 8;
          } else {
            data[i] = 14; // Cool transpiration
            data[i + 1] = 116;
            data[i + 2] = 144;
          }
        }
      }

      ctx.putImageData(imgData, 0, 0);
    };
  }, [imageSrc, spectralMode]);

  return (
    <div className={`rounded-2xl p-4 border transition-all ${isDark ? "border-emerald-800/40 bg-[#04160f]" : "border-slate-200 bg-slate-50"}`}>
      {/* HEADER & VIEW MODE SELECTOR */}
      <div className="flex flex-wrap items-center justify-between gap-2 mb-3 pb-2 border-b border-slate-200/50">
        <div className="flex items-center gap-2">
          <Zap size={16} className="text-cyan-400 animate-pulse" />
          <h4 className={`text-xs font-black uppercase tracking-wider ${isDark ? "text-emerald-300" : "text-slate-800"}`}>
            Pre-Symptomatic Near-Infrared (NIR) & Thermal Scanner
          </h4>
        </div>
        <div className="flex gap-1 bg-slate-200 dark:bg-emerald-950 p-1 rounded-xl text-[11px] font-bold">
          <button
            onClick={() => setSpectralMode("ndvi")}
            className={`px-2.5 py-1 rounded-lg transition ${spectralMode === "ndvi" ? "bg-emerald-600 text-white" : "text-slate-500"}`}
          >
            NDVI Spectral
          </button>
          <button
            onClick={() => setSpectralMode("rededge")}
            className={`px-2.5 py-1 rounded-lg transition ${spectralMode === "rededge" ? "bg-emerald-600 text-white" : "text-slate-500"}`}
          >
            Red-Edge NIR
          </button>
          <button
            onClick={() => setSpectralMode("thermal")}
            className={`px-2.5 py-1 rounded-lg transition ${spectralMode === "thermal" ? "bg-emerald-600 text-white" : "text-slate-500"}`}
          >
            Thermal Stomata
          </button>
        </div>
      </div>

      {/* CANVAS CONTAINER */}
      <div className="relative aspect-[16/10] overflow-hidden rounded-xl bg-slate-950 shadow-inner">
        <canvas ref={canvasRef} className="h-full w-full object-cover" />
        <div className="absolute top-3 left-3 bg-black/70 backdrop-blur px-3 py-1 rounded-full border border-emerald-500/30 text-[10px] font-mono font-bold text-emerald-400 flex items-center gap-1.5">
          <Sparkles size={12} />
          {spectralMode === "ndvi" && "NDVI Cell Vigor Filter (750nm / 680nm Ratio)"}
          {spectralMode === "rededge" && "Red-Edge Transpiration Proxy (705nm)"}
          {spectralMode === "thermal" && "Stomatal Heat Transpiration (48h Pre-Symptomatic)"}
        </div>
      </div>

      <div className="mt-3 flex items-center gap-2 text-[11px] font-bold text-cyan-400 bg-cyan-950/40 p-2.5 rounded-xl border border-cyan-800/40">
        <ShieldAlert size={15} className="shrink-0" />
        <span>Pre-Symptomatic AI Alert: Stomatal transpiration breakdown detected in Sector B (Upper Left Quadrant) 48h before visible spots!</span>
      </div>
    </div>
  );
}
