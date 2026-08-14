import React from "react";
import { Activity, BarChart3, ShieldAlert, Leaf } from "lucide-react";

export default function LeafSpectrumHistogram({ disease, isDark = false }) {
  const metrics = disease?.metrics || {
    healthyPercent: 82,
    necroticPercent: 14,
    chlorosisPercent: 4,
    whitePercent: 0,
    rustPercent: 0,
    spadIndex: 42,
    plantStressScore: 18,
  };

  const spectrum = disease?.spectrumData || {
    rHistogram: [10, 15, 25, 40, 30, 20, 10, 5],
    gHistogram: [5, 10, 30, 65, 80, 50, 25, 10],
    bHistogram: [15, 20, 35, 30, 15, 10, 5, 2],
  };

  const spadPct = Math.min(100, Math.round((metrics.spadIndex / 60) * 100));

  return (
    <div
      className={`rounded-2xl p-4 border transition-all ${
        isDark ? "border-emerald-800/40 bg-[#04160f]" : "border-slate-200 bg-slate-50"
      }`}
    >
      <div className="flex items-center justify-between mb-3 border-b pb-2 border-slate-200/50">
        <div className="flex items-center gap-2">
          <BarChart3 size={16} className="text-emerald-500" />
          <h4 className={`text-xs font-black uppercase tracking-wider ${isDark ? "text-emerald-300" : "text-slate-800"}`}>
            Multi-Spectral Chromatic Histogram
          </h4>
        </div>
        <span className="text-[10px] font-mono font-bold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
          RGB & SPAD Analytics
        </span>
      </div>

      {/* TOP GAUGES: SPAD & PLANT STRESS */}
      <div className="grid grid-cols-2 gap-3 mb-4">
        {/* SPAD INDEX */}
        <div className={`p-3 rounded-xl border ${isDark ? "bg-emerald-950/40 border-emerald-900/50 text-white" : "bg-white border-slate-200 text-slate-800"}`}>
          <div className="flex items-center justify-between text-[11px] font-bold mb-1">
            <span className="flex items-center gap-1.5 text-emerald-600">
              <Leaf size={14} /> Chlorophyll SPAD
            </span>
            <span className="font-mono text-emerald-500 font-black">{metrics.spadIndex} SPAD</span>
          </div>
          <div className="h-2 rounded-full bg-slate-200/70 overflow-hidden relative">
            <div
              className="h-full bg-gradient-to-r from-emerald-500 to-green-400 transition-all duration-500"
              style={{ width: `${spadPct}%` }}
            />
          </div>
          <p className="text-[10px] text-slate-400 mt-1">Reflectance Nitrogen Proxy (12–60 standard)</p>
        </div>

        {/* PLANT STRESS SCORE */}
        <div className={`p-3 rounded-xl border ${isDark ? "bg-emerald-950/40 border-emerald-900/50 text-white" : "bg-white border-slate-200 text-slate-800"}`}>
          <div className="flex items-center justify-between text-[11px] font-bold mb-1">
            <span className="flex items-center gap-1.5 text-amber-600">
              <Activity size={14} /> Foliar Stress Rating
            </span>
            <span className={`font-mono font-black ${metrics.plantStressScore > 40 ? "text-amber-500" : "text-emerald-500"}`}>
              {metrics.plantStressScore}%
            </span>
          </div>
          <div className="h-2 rounded-full bg-slate-200/70 overflow-hidden relative">
            <div
              className={`h-full transition-all duration-500 ${
                metrics.plantStressScore > 50 ? "bg-red-500" : metrics.plantStressScore > 25 ? "bg-amber-500" : "bg-emerald-500"
              }`}
              style={{ width: `${metrics.plantStressScore}%` }}
            />
          </div>
          <p className="text-[10px] text-slate-400 mt-1">Tissue Necrotic & Chlorotic Index</p>
        </div>
      </div>

      {/* RGB SPECTRUM BARS */}
      <div className="space-y-2">
        <span className={`text-[10px] font-bold uppercase tracking-wide block ${isDark ? "text-slate-400" : "text-slate-500"}`}>
          RGB Wavelength Density Breakdown:
        </span>
        
        {/* GREEN CHANNEL (Healthy tissue) */}
        <div>
          <div className="flex justify-between text-[10px] font-mono font-bold mb-1">
            <span className="text-emerald-500">Green Channel (Chlorophyll Reflected 550nm)</span>
            <span className="text-emerald-400">{metrics.healthyPercent}%</span>
          </div>
          <div className="flex items-center gap-1 h-4">
            {spectrum.gHistogram.map((val, idx) => (
              <div key={idx} className="flex-1 h-full bg-emerald-950/40 rounded-sm overflow-hidden flex items-end">
                <div
                  className="w-full bg-emerald-500 transition-all duration-300"
                  style={{ height: `${Math.min(100, val * 1.5)}%` }}
                />
              </div>
            ))}
          </div>
        </div>

        {/* RED CHANNEL (Necrosis & Rust) */}
        <div>
          <div className="flex justify-between text-[10px] font-mono font-bold mb-1">
            <span className="text-amber-500">Red Channel (Necrotic / Rust Reflected 680nm)</span>
            <span className="text-amber-400">{metrics.necroticPercent + (metrics.rustPercent || 0)}%</span>
          </div>
          <div className="flex items-center gap-1 h-4">
            {spectrum.rHistogram.map((val, idx) => (
              <div key={idx} className="flex-1 h-full bg-amber-950/40 rounded-sm overflow-hidden flex items-end">
                <div
                  className="w-full bg-amber-500 transition-all duration-300"
                  style={{ height: `${Math.min(100, val * 1.5)}%` }}
                />
              </div>
            ))}
          </div>
        </div>

        {/* BLUE CHANNEL (Mildew & Water Absorption) */}
        <div>
          <div className="flex justify-between text-[10px] font-mono font-bold mb-1">
            <span className="text-cyan-500">Blue Channel (Water / Mildew Reflected 450nm)</span>
            <span className="text-cyan-400">{metrics.chlorosisPercent + (metrics.whitePercent || 0)}%</span>
          </div>
          <div className="flex items-center gap-1 h-4">
            {spectrum.bHistogram.map((val, idx) => (
              <div key={idx} className="flex-1 h-full bg-cyan-950/40 rounded-sm overflow-hidden flex items-end">
                <div
                  className="w-full bg-cyan-400 transition-all duration-300"
                  style={{ height: `${Math.min(100, val * 1.5)}%` }}
                />
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
