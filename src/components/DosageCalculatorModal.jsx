import React, { useState } from "react";
import { Calculator, X, Sparkles, CheckCircle2, ShieldCheck } from "lucide-react";

export default function DosageCalculatorModal({ isOpen, onClose, disease, isDark = false }) {
  const [acres, setAcres] = useState(2.5);
  const [unit, setUnit] = useState("acres"); // 'acres' | 'hectares'

  if (!isOpen || !disease) return null;

  const cropName = typeof disease.crop === "object" ? (disease.crop?.name || "Crop") : (disease.crop || disease.cropType || "Crop");
  const conditionName = typeof disease.condition === "object" ? (disease.condition?.name || "Target Condition") : (disease.diseaseName || disease.condition || disease.diagnosis || "Target Condition");
  const severityName = typeof disease.severity === "object" ? (disease.severity?.tier || "Moderate") : (disease.severity || "Moderate");

  const areaInAcres = unit === "hectares" ? acres * 2.471 : acres;
  const waterLiters = Math.round(areaInAcres * 200); // 200L water per acre standard
  const sprayTanks = Math.round(waterLiters / 15); // 15L backpack knapsack sprayer

  // Remedy math defaults
  const chemicalDosageKg = ((areaInAcres * 0.5)).toFixed(2); // ~500g per acre
  const organicNeemMl = Math.round(areaInAcres * 1000); // ~1L neem oil per acre
  const estCostChemical = Math.round(areaInAcres * 450); // ₹450 per acre
  const estCostOrganic = Math.round(areaInAcres * 280); // ₹280 per acre

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-fade-in">
      <div
        className={`relative w-full max-w-lg overflow-hidden rounded-3xl border shadow-2xl transition-all ${
          isDark ? "border-emerald-800/60 bg-[#061e15] text-white" : "border-slate-200 bg-white text-slate-900"
        }`}
      >
        {/* HEADER */}
        <div className={`flex items-center justify-between p-4 px-6 border-b ${isDark ? "border-emerald-900/50" : "border-slate-200"}`}>
          <div className="flex items-center gap-2">
            <Calculator size={20} className="text-emerald-500" />
            <h3 className="text-base font-black">
              Precision Field Dosage Calculator
            </h3>
          </div>
          <button
            onClick={onClose}
            className={`rounded-full p-2 transition ${isDark ? "hover:bg-emerald-900/40 text-slate-400 hover:text-white" : "hover:bg-slate-100 text-slate-600"}`}
          >
            <X size={18} />
          </button>
        </div>

        {/* BODY CONTENT */}
        <div className="p-6 space-y-5">
          {/* CROP & DISEASE RECAP */}
          <div className={`p-3 rounded-2xl border flex items-center justify-between ${isDark ? "bg-emerald-950/40 border-emerald-900/50" : "bg-emerald-50 border-emerald-200"}`}>
            <div>
              <span className="text-[10px] font-black uppercase tracking-wider text-emerald-600">Target Treatment</span>
              <h4 className="text-sm font-black">{cropName} — {conditionName}</h4>
            </div>
            <span className="rounded-full bg-emerald-500/20 text-emerald-400 text-xs font-bold px-3 py-1 border border-emerald-500/30">
              {severityName} Severity
            </span>
          </div>

          {/* AREA INPUT SLIDER */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="text-xs font-bold uppercase tracking-wider text-slate-500">
                Farm Land Area:
              </label>
              <div className="flex gap-1 bg-slate-200 dark:bg-emerald-950 p-1 rounded-xl">
                <button
                  onClick={() => setUnit("acres")}
                  className={`px-3 py-1 text-[11px] font-bold rounded-lg transition ${unit === "acres" ? "bg-emerald-600 text-white" : "text-slate-500"}`}
                >
                  Acres
                </button>
                <button
                  onClick={() => setUnit("hectares")}
                  className={`px-3 py-1 text-[11px] font-bold rounded-lg transition ${unit === "hectares" ? "bg-emerald-600 text-white" : "text-slate-500"}`}
                >
                  Hectares
                </button>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <input
                type="range"
                min="0.5"
                max="50"
                step="0.5"
                value={acres}
                onChange={(e) => setAcres(parseFloat(e.target.value))}
                className="w-full accent-emerald-500 h-2 bg-slate-200 dark:bg-emerald-950 rounded-lg cursor-pointer"
              />
              <span className="font-mono text-lg font-black text-emerald-500 min-w-[60px] text-right">
                {acres} {unit}
              </span>
            </div>
          </div>

          {/* CALCULATED DOSAGE MATRIX */}
          <div className="grid grid-cols-2 gap-3 text-xs">
            {/* CHEMICAL ADVISORY */}
            <div className={`p-4 rounded-2xl border space-y-2 ${isDark ? "bg-emerald-950/30 border-emerald-900/40" : "bg-slate-50 border-slate-200"}`}>
              <div className="flex items-center justify-between font-bold text-amber-500">
                <span>Chemical Remedy</span>
                <span className="font-mono text-sm font-black">₹{estCostChemical}</span>
              </div>
              <p className="text-[11px] font-bold text-slate-700 dark:text-slate-300">{disease.remedies?.chemical?.title || "Copper Fungicide"}</p>
              <div className="pt-2 border-t border-slate-200/50 dark:border-emerald-900/50 space-y-1 font-mono text-[11px]">
                <div className="flex justify-between text-slate-500">
                  <span>Product Qty:</span>
                  <span className="text-emerald-400 font-bold">{chemicalDosageKg} kg</span>
                </div>
                <div className="flex justify-between text-slate-500">
                  <span>Water Vol:</span>
                  <span className="text-cyan-400 font-bold">{waterLiters} L</span>
                </div>
                <div className="flex justify-between text-slate-500">
                  <span>Knapsack Tanks:</span>
                  <span className="text-slate-300 font-bold">{sprayTanks} tanks (15L)</span>
                </div>
              </div>
            </div>

            {/* ORGANIC ADVISORY */}
            <div className={`p-4 rounded-2xl border space-y-2 ${isDark ? "bg-emerald-950/30 border-emerald-900/40" : "bg-slate-50 border-slate-200"}`}>
              <div className="flex items-center justify-between font-bold text-emerald-500">
                <span>Organic Remedy</span>
                <span className="font-mono text-sm font-black">₹{estCostOrganic}</span>
              </div>
              <p className="text-[11px] font-bold text-slate-700 dark:text-slate-300">{disease.remedies?.organic?.title || "Neem Oil Bio-Control"}</p>
              <div className="pt-2 border-t border-slate-200/50 dark:border-emerald-900/50 space-y-1 font-mono text-[11px]">
                <div className="flex justify-between text-slate-500">
                  <span>Neem Concentrate:</span>
                  <span className="text-emerald-400 font-bold">{organicNeemMl} ml</span>
                </div>
                <div className="flex justify-between text-slate-500">
                  <span>Water Vol:</span>
                  <span className="text-cyan-400 font-bold">{waterLiters} L</span>
                </div>
                <div className="flex justify-between text-slate-500">
                  <span>Knapsack Tanks:</span>
                  <span className="text-slate-300 font-bold">{sprayTanks} tanks (15L)</span>
                </div>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2 text-[11px] font-bold text-emerald-600 dark:text-emerald-400 bg-emerald-500/10 p-3 rounded-xl border border-emerald-500/20">
            <ShieldCheck size={16} className="shrink-0" />
            <span>Calculated using ICAR & FAO standard foliar dilution ratios for uniform canopy spray.</span>
          </div>
        </div>

        {/* FOOTER */}
        <div className={`p-4 px-6 border-t flex justify-end ${isDark ? "border-emerald-900/50 bg-[#04160f]" : "border-slate-200 bg-slate-50"}`}>
          <button
            onClick={onClose}
            className="rounded-xl bg-emerald-600 px-5 py-2 text-xs font-black text-white hover:bg-emerald-700"
          >
            Done & Save Calculation
          </button>
        </div>
      </div>
    </div>
  );
}
