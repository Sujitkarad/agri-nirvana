import React from "react";
import { Activity, Database, Radio, ShieldCheck } from "lucide-react";

/** Runtime status ribbon: intentionally avoids fabricated latency/uptime/security claims. */
export default function TelemetryRibbon({ isDark = false, selectedModel = "Model status pending" }) {
  return (
    <div role="status" aria-label="Agri Nirvana system status" className={`border-b px-4 py-1.5 text-[11px] font-mono transition-colors ${isDark ? "border-emerald-500/20 bg-[#020906]/90 text-emerald-300" : "border-slate-200 bg-white text-slate-600"}`}>
      <div className="mx-auto flex max-w-7xl items-center justify-between gap-4">
        <div className="flex min-w-0 items-center gap-4 sm:gap-6">
          <span className="flex items-center gap-1.5 font-semibold"><span className="h-2 w-2 shrink-0 rounded-full bg-emerald-500" />System ready</span>
          <span className="hidden md:flex items-center gap-1.5"><Activity size={12} className="text-emerald-600" /><span className="font-semibold">API:</span><span>status reported by service</span></span>
          <span className="hidden lg:flex items-center gap-1.5"><ShieldCheck size={12} className="text-emerald-600" /><span>Security transport depends on deployment configuration</span></span>
        </div>
        <div className="flex shrink-0 items-center gap-3">
          <span className="hidden sm:flex items-center gap-1.5"><Radio size={12} className="text-emerald-600" /><span className="font-semibold">Engine:</span><span className="max-w-40 truncate" title={selectedModel}>{selectedModel}</span></span>
          <span className="flex items-center gap-1.5 rounded-full border border-amber-300 bg-amber-50 px-2 py-0.5 text-[10px] font-bold text-amber-800"><Database size={11} />Demo data where marked</span>
        </div>
      </div>
    </div>
  );
}
