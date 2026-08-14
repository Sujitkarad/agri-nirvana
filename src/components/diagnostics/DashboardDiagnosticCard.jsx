import React from "react";
import { Sparkles, Camera, ShieldCheck, ArrowRight } from "lucide-react";

export default function DashboardDiagnosticCard({
  onOpenDiagnostics = () => {},
  isDark = true
}) {
  return (
    <div className={`relative overflow-hidden rounded-3xl border p-6 sm:p-7 transition-all duration-300 group hover:scale-[1.005] ${
      isDark
        ? "border-emerald-700/60 bg-gradient-to-br from-[#062419] via-[#072017] to-[#04160f] text-white shadow-2xl shadow-emerald-950/50"
        : "border-slate-200 bg-gradient-to-br from-emerald-50 via-white to-teal-50 text-slate-900 shadow-xl"
    }`}>
      {/* BACKGROUND DECORATIVE GLOW */}
      <div className="absolute -top-16 -right-16 h-48 w-48 rounded-full bg-emerald-500/10 blur-3xl group-hover:bg-emerald-500/20 transition-all" />

      <div className="relative flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
        <div className="space-y-2 max-w-xl">
          <div className="inline-flex items-center gap-2 rounded-full border border-emerald-500/30 bg-emerald-500/15 px-3.5 py-1 text-xs font-bold text-emerald-300">
            <Sparkles size={14} className="text-amber-400 animate-pulse" />
            <span>EfficientNet-B3 Vision Telemetry</span>
          </div>

          <h3 className="text-2xl font-black tracking-tight">
            Check Your Crop Health
          </h3>

          <p className={`text-xs sm:text-sm leading-relaxed ${isDark ? "text-emerald-100/80" : "text-slate-600"}`}>
            Upload a crop photo and get an instant AI-assisted preliminary health assessment, disease severity analysis, and verified treatment advisory.
          </p>

          <div className="flex flex-wrap items-center gap-4 text-xs font-mono text-emerald-400 pt-1">
            <span className="flex items-center gap-1"><ShieldCheck size={14} /> Preliminary Guidance Standard</span>
            <span className="flex items-center gap-1"><Camera size={14} /> Quality Pre-check</span>
          </div>
        </div>

        <div className="shrink-0 w-full md:w-auto">
          <button
            type="button"
            onClick={onOpenDiagnostics}
            className="w-full md:w-auto flex items-center justify-center gap-2.5 rounded-2xl bg-emerald-500 px-6 py-3.5 text-xs font-black text-slate-950 hover:bg-emerald-400 transition-all shadow-lg shadow-emerald-500/30 group-hover:translate-x-0.5"
          >
            <Camera size={18} />
            <span>Diagnose Crop</span>
            <ArrowRight size={16} />
          </button>
        </div>
      </div>
    </div>
  );
}
