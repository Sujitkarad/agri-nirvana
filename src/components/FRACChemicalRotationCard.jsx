import React, { useState } from "react";
import { ShieldAlert, RefreshCw, CheckCircle2, Calendar, Layers } from "lucide-react";
import { FRAC_CHEMICAL_REGISTRY } from "../data/agriData";

export default function FRACChemicalRotationCard({ isDark = false }) {
  const [selectedFrac, setSelectedFrac] = useState(FRAC_CHEMICAL_REGISTRY[0]);

  return (
    <div className={`rounded-2xl p-4 border transition-all ${isDark ? "border-emerald-800/40 bg-[#04160f]" : "border-slate-200 bg-white shadow-sm"}`}>
      <div className="flex items-center justify-between mb-3 pb-2 border-b border-slate-200/50">
        <div className="flex items-center gap-2">
          <RefreshCw size={16} className="text-amber-500" />
          <h4 className={`text-xs font-black uppercase tracking-wider ${isDark ? "text-emerald-300" : "text-slate-800"}`}>
            FRAC Fungicide Resistance & Chemical Rotation Advisory
          </h4>
        </div>
        <span className="text-[10px] font-mono font-bold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
          Anti-Mutation Protocol
        </span>
      </div>

      {/* FRAC GROUP SELECTOR */}
      <div className="grid grid-cols-4 gap-2 mb-3">
        {FRAC_CHEMICAL_REGISTRY.map((frac) => (
          <button
            key={frac.groupCode}
            onClick={() => setSelectedFrac(frac)}
            className={`p-2 rounded-xl border text-center transition ${
              selectedFrac.groupCode === frac.groupCode
                ? "border-amber-500 bg-amber-500/20 text-amber-300 font-bold"
                : isDark
                ? "border-emerald-900/50 bg-emerald-950/30 text-slate-400"
                : "border-slate-200 bg-slate-50 text-slate-700"
            }`}
          >
            <div className="text-xs font-black">{frac.groupCode}</div>
            <div className="text-[9px] opacity-75 truncate">{frac.activeIngredients[0]}</div>
          </button>
        ))}
      </div>

      {/* SELECTED FRAC DETAILS */}
      <div className={`p-3 rounded-xl border space-y-2 mb-3 ${isDark ? "bg-emerald-950/30 border-emerald-900/40" : "bg-slate-50 border-slate-200"}`}>
        <div className="flex items-center justify-between text-xs font-bold">
          <span className="text-amber-500">{selectedFrac.groupName}</span>
          <span className="text-[10px] text-slate-400 font-mono">Max {selectedFrac.maxSpraysPerSeason} sprays/season</span>
        </div>
        <p className="text-[11px] text-slate-300 font-mono">
          <strong>Mode of Action:</strong> {selectedFrac.modeOfAction}
        </p>
        <p className="text-[10px] text-amber-400 font-bold">
          ⚠️ {selectedFrac.resistanceRisk}
        </p>
      </div>

      {/* ALTERNATING SPRAY CALENDAR */}
      <div className="space-y-1.5 text-[11px] font-mono">
        <span className="text-[10px] font-bold uppercase text-slate-400 block">Recommended 6-Week Resistance-Break Spray Schedule:</span>
        <div className="grid grid-cols-3 gap-2 text-center">
          <div className="p-2 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-400">
            <div className="text-[9px] text-slate-400 font-bold">Week 1</div>
            <div className="font-bold">FRAC 11</div>
            <div className="text-[8px] opacity-80">Azoxystrobin</div>
          </div>
          <div className="p-2 rounded-lg bg-amber-500/10 border border-amber-500/30 text-amber-400">
            <div className="text-[9px] text-slate-400 font-bold">Week 3</div>
            <div className="font-bold">FRAC M05</div>
            <div className="text-[8px] opacity-80">Copper Oxychloride</div>
          </div>
          <div className="p-2 rounded-lg bg-cyan-500/10 border border-cyan-500/30 text-cyan-400">
            <div className="text-[9px] text-slate-400 font-bold">Week 5</div>
            <div className="font-bold">FRAC 3</div>
            <div className="text-[8px] opacity-80">Tebuconazole</div>
          </div>
        </div>
      </div>
    </div>
  );
}
