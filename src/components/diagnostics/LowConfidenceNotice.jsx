import React from "react";
import { HelpCircle, RefreshCw, Sun, Focus, UserCheck, ShieldAlert } from "lucide-react";

export default function LowConfidenceNotice({
  confidence = 0.62,
  threshold = 0.70,
  onRetake = () => {},
  isDark = true
}) {
  return (
    <div className={`rounded-3xl border p-6 sm:p-8 space-y-6 text-left animate-fade-in ${
      isDark ? "border-amber-800/60 bg-[#1e1406] text-white shadow-2xl" : "border-amber-200 bg-amber-50 text-slate-900 shadow-xl"
    }`}>
      <div className="flex items-center gap-3">
        <div className="h-12 w-12 rounded-2xl bg-amber-500/20 text-amber-400 border border-amber-500/40 flex items-center justify-center shrink-0">
          <HelpCircle size={28} />
        </div>
        <div>
          <span className="text-[10px] font-black uppercase tracking-wider text-amber-400 bg-amber-500/20 px-2.5 py-0.5 rounded-full border border-amber-500/30">
            AI Confidence Threshold Notice
          </span>
          <h3 className="text-xl font-black text-amber-200 mt-1">
            Uncertain Result ({(confidence * 100).toFixed(0)}% Confidence)
          </h3>
        </div>
      </div>

      <p className="text-xs leading-relaxed text-amber-100/90">
        The image provided does not show enough clear leaf detail or chromatic contrast for a reliable AI diagnosis.
        Our confidence score is below our safe production threshold ({(threshold * 100).toFixed(0)}%).
      </p>

      <div className="rounded-2xl border border-amber-500/30 bg-black/30 p-4 space-y-3 text-xs">
        <div className="font-black text-amber-300 flex items-center gap-1.5">
          <ShieldAlert size={16} /> Recommended Next Steps for Best Accuracy:
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-slate-300">
          <div className="flex items-center gap-2">
            <Sun size={16} className="text-amber-400 shrink-0" />
            <span>Capture under clear, bright natural light</span>
          </div>
          <div className="flex items-center gap-2">
            <Focus size={16} className="text-amber-400 shrink-0" />
            <span>Ensure leaf surface is sharply in focus</span>
          </div>
          <div className="flex items-center gap-2">
            <UserCheck size={16} className="text-amber-400 shrink-0" />
            <span>Avoid shadows or severe blur</span>
          </div>
          <div className="flex items-center gap-2">
            <HelpCircle size={16} className="text-amber-400 shrink-0" />
            <span>Consult an agronomist if symptoms persist</span>
          </div>
        </div>
      </div>

      <div className="flex flex-wrap items-center justify-between gap-3 pt-2">
        <button
          type="button"
          onClick={onRetake}
          className="flex items-center gap-2 rounded-xl bg-amber-500 px-6 py-3 text-xs font-black text-slate-950 hover:bg-amber-400 transition shadow-lg shadow-amber-500/20"
        >
          <RefreshCw size={16} /> Retake / Upload Clearer Photo
        </button>
        <span className="text-[11px] italic text-amber-200/70">
          Preliminary AI guidance standard enforced.
        </span>
      </div>
    </div>
  );
}
