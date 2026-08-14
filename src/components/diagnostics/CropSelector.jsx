import React from "react";
import { Check, Leaf } from "lucide-react";

export default function CropSelector({
  crops = [],
  selectedCrop = "Tomato",
  onSelectCrop = () => {},
  isDark = true
}) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <label className={`text-xs font-black uppercase tracking-wider flex items-center gap-1.5 ${isDark ? "text-emerald-400" : "text-emerald-700"}`}>
          <Leaf size={14} />
          Select Target Crop Type
        </label>
        <span className="text-[10px] font-bold text-slate-400">
          {crops.length} AI-Supported Crops
        </span>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-2.5">
        {crops.map((crop) => {
          const isSelected = selectedCrop === crop.id || selectedCrop === crop.name;
          return (
            <button
              key={crop.id}
              type="button"
              onClick={() => onSelectCrop(crop.id)}
              className={`relative flex items-center justify-between rounded-xl p-3 text-left transition-all border ${
                isSelected
                  ? "border-emerald-500 bg-emerald-500/15 text-emerald-300 shadow-md shadow-emerald-500/10 ring-1 ring-emerald-500/50"
                  : isDark
                  ? "border-emerald-900/50 bg-[#04160f] text-slate-300 hover:border-emerald-700 hover:bg-emerald-950/40"
                  : "border-slate-200 bg-white text-slate-700 hover:border-emerald-400 hover:bg-emerald-50/50"
              }`}
            >
              <div className="flex items-center gap-2 overflow-hidden">
                <span className="text-lg shrink-0">{crop.icon || "🌱"}</span>
                <span className="text-xs font-bold truncate">{crop.name}</span>
              </div>
              {isSelected && (
                <div className="h-4 w-4 rounded-full bg-emerald-500 text-slate-950 flex items-center justify-center shrink-0">
                  <Check size={10} strokeWidth={3} />
                </div>
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
}
