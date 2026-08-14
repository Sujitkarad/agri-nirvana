import React, { useState } from "react";
import {
  Sparkles, ShieldAlert, CheckCircle2, Info, AlertTriangle, Eye, ZoomIn, X,
  Clock, ArrowRight, UserCheck, Activity
} from "lucide-react";

export default function DiagnosisResultCard({
  diagnosis = {},
  onRetake = () => {},
  isDark = true
}) {
  const [zoomOpen, setZoomOpen] = useState(false);

  const {
    crop = "Tomato",
    condition = "Early Blight",
    confidence = 0.94,
    severity = "Moderate",
    pathogen = "Alternaria solani",
    imageUrl = "",
    symptoms = [],
    recommendations = {},
    modelName = "EfficientNet-B3",
    modelVersion = "v1.0",
    isMock = false,
    createdAt = new Date().toISOString()
  } = diagnosis;

  const confPercent = Math.round(confidence > 1 ? confidence : confidence * 100);

  const getSeverityStyle = (sev) => {
    switch (sev?.toLowerCase()) {
      case "healthy":
        return { bg: "bg-emerald-500/20 text-emerald-300 border-emerald-500/40", badge: "Healthy / Clear" };
      case "low":
        return { bg: "bg-cyan-500/20 text-cyan-300 border-cyan-500/40", badge: "Low Severity Watch" };
      case "moderate":
        return { bg: "bg-amber-500/20 text-amber-300 border-amber-500/40", badge: "Moderate Action Advisable" };
      case "severe":
        return { bg: "bg-rose-500/20 text-rose-300 border-rose-500/40", badge: "Severe Urgent Action Required" };
      default:
        return { bg: "bg-slate-500/20 text-slate-300 border-slate-500/40", badge: "Severity Assessment Pending" };
    }
  };

  const sevStyle = getSeverityStyle(severity);

  return (
    <div className={`rounded-3xl border p-5 sm:p-7 space-y-6 text-left animate-fade-in ${
      isDark ? "border-emerald-800/50 bg-[#072017] shadow-2xl text-white" : "border-slate-200 bg-white shadow-xl text-slate-900"
    }`}>
      {/* HEADER BAR */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b pb-4 border-emerald-900/40">
        <div>
          <span className="text-[10px] font-black uppercase tracking-wider text-emerald-400">
            AI-Assisted Preliminary Crop Health Assessment
          </span>
          <h2 className="text-2xl font-black mt-0.5">{crop} — {condition}</h2>
          {pathogen && <p className="text-xs italic text-slate-400 font-mono mt-0.5">{pathogen}</p>}
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <span className={`px-3 py-1 rounded-full text-xs font-black border ${sevStyle.bg}`}>
            {sevStyle.badge}
          </span>
          <span className="px-3 py-1 rounded-full text-xs font-black bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">
            {confPercent}% Confidence
          </span>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-12 items-start">
        {/* A. IMAGE CARD WITH PREVIEW & ZOOM */}
        <div className="lg:col-span-5 space-y-3">
          <div className="relative aspect-[16/11] overflow-hidden rounded-2xl border border-emerald-800/60 bg-slate-950 shadow-inner group">
            <img src={imageUrl} alt="Diagnosed Leaf Region" className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105" />
            <button
              onClick={() => setZoomOpen(true)}
              className="absolute bottom-3 right-3 flex items-center gap-1.5 rounded-xl bg-black/70 backdrop-blur-md px-3 py-1.5 text-xs font-bold text-white hover:bg-black/90 transition shadow"
            >
              <ZoomIn size={14} /> Zoom Image
            </button>
            {isMock && (
              <span className="absolute top-3 left-3 rounded-full bg-amber-500/90 text-slate-950 text-[10px] font-black px-2.5 py-0.5 shadow">
                Dev / Mock Provider
              </span>
            )}
          </div>

          <div className="flex items-center justify-between text-[11px] font-mono text-slate-400">
            <span className="flex items-center gap-1"><Clock size={12} /> {new Date(createdAt).toLocaleDateString()}</span>
            <span>Model: {modelName} ({modelVersion})</span>
          </div>
        </div>

        {/* B. CONFIDENCE & SYMPTOMS CARD */}
        <div className="lg:col-span-7 space-y-4">
          {/* CONFIDENCE VISUAL METER */}
          <div className={`p-4 rounded-2xl border ${isDark ? "bg-emerald-950/40 border-emerald-900/50" : "bg-slate-50 border-slate-200"}`}>
            <div className="flex items-center justify-between text-xs font-bold mb-1.5">
              <span className="flex items-center gap-1.5"><Activity size={14} className="text-emerald-400" /> AI Vision Confidence Score</span>
              <span className="text-emerald-400 font-mono font-black">{confPercent}%</span>
            </div>
            <div className="h-2.5 rounded-full bg-slate-950 border border-emerald-800/40 overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-emerald-500 via-teal-400 to-cyan-400 transition-all duration-1000 shadow-[0_0_10px_#10b981]"
                style={{ width: `${confPercent}%` }}
              />
            </div>
          </div>

          {/* C. DETECTED SYMPTOMS */}
          <div className={`p-4 rounded-2xl border ${isDark ? "bg-[#04160f] border-emerald-900/50" : "bg-slate-50 border-slate-200"}`}>
            <h4 className="text-xs font-black uppercase tracking-wider text-emerald-400 mb-2 flex items-center gap-1.5">
              <Eye size={14} /> Symptoms Identified in Visual Analysis
            </h4>
            <ul className="space-y-1.5 text-xs text-slate-300">
              {symptoms && symptoms.length > 0 ? (
                symptoms.map((sym, idx) => (
                  <li key={idx} className="flex items-start gap-2">
                    <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 shrink-0 mt-1.5" />
                    <span>{sym}</span>
                  </li>
                ))
              ) : (
                <li className="text-slate-400">No abnormal lesions or symptoms detected. Foliage displays healthy leaf matrix.</li>
              )}
            </ul>
          </div>
        </div>
      </div>

      {/* D. RECOMMENDED NEXT ACTIONS */}
      <div className="space-y-3 pt-2">
        <h4 className="text-xs font-black uppercase tracking-wider text-emerald-400 flex items-center gap-1.5">
          <ArrowRight size={14} /> Recommended Next Agronomic Actions
        </h4>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
          {recommendations.immediate && (
            <div className="p-4 rounded-2xl border border-rose-500/30 bg-rose-950/20 text-slate-200 space-y-1">
              <div className="font-bold text-rose-300 flex items-center gap-1.5">⚡ Immediate Action</div>
              <p className="text-slate-300">{recommendations.immediate}</p>
            </div>
          )}

          {recommendations.monitoring && (
            <div className="p-4 rounded-2xl border border-cyan-500/30 bg-cyan-950/20 text-slate-200 space-y-1">
              <div className="font-bold text-cyan-300 flex items-center gap-1.5">👁️ Monitoring Protocol</div>
              <p className="text-slate-300">{recommendations.monitoring}</p>
            </div>
          )}

          {recommendations.prevention && (
            <div className="p-4 rounded-2xl border border-emerald-500/30 bg-emerald-950/20 text-slate-200 space-y-1">
              <div className="font-bold text-emerald-300 flex items-center gap-1.5">🛡️ Preventative Measures</div>
              <p className="text-slate-300">{recommendations.prevention}</p>
            </div>
          )}

          {recommendations.expert_help && (
            <div className="p-4 rounded-2xl border border-amber-500/30 bg-amber-950/20 text-slate-200 space-y-1">
              <div className="font-bold text-amber-300 flex items-center gap-1.5">👨‍🌾 Agricultural Expert Guidance</div>
              <p className="text-slate-300">{recommendations.expert_help}</p>
            </div>
          )}
        </div>
      </div>

      {/* DISCLAIMER FOOTER */}
      <div className="pt-3 border-t border-emerald-900/40 flex flex-col sm:flex-row items-center justify-between gap-3 text-[11px] text-slate-400">
        <div className="flex items-center gap-2">
          <Info size={14} className="text-emerald-400 shrink-0" />
          <span>
            <strong>AI Preliminary Assessment Notice:</strong> AI-generated assessment for preliminary guidance. For severe or uncertain cases, consult a qualified agricultural expert.
          </span>
        </div>
        <button
          type="button"
          onClick={onRetake}
          className="shrink-0 rounded-xl bg-emerald-600 px-4 py-2 text-xs font-black text-white hover:bg-emerald-700 transition"
        >
          Diagnose Another Leaf
        </button>
      </div>

      {/* ZOOM MODAL */}
      {zoomOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/90 backdrop-blur-md">
          <div className="relative max-w-4xl max-h-[90vh] overflow-hidden rounded-3xl border border-emerald-800 bg-slate-950 p-2 shadow-2xl">
            <button
              onClick={() => setZoomOpen(false)}
              className="absolute top-4 right-4 rounded-full bg-slate-900/80 p-2 text-white hover:bg-rose-600 transition z-10"
            >
              <X size={20} />
            </button>
            <img src={imageUrl} alt="Zoomed Leaf Image" className="max-h-[85vh] w-auto object-contain rounded-2xl" />
          </div>
        </div>
      )}
    </div>
  );
}
