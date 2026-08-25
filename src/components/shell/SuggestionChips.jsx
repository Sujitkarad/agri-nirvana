import React from "react";
import { Sparkles, Leaf, TrendingUp, Layers, Calculator, ShieldAlert, Cpu } from "lucide-react";

export const SUGGESTIONS = [
  {
    icon: Leaf,
    label: "Diagnose Leaf Blight",
    prompt: "Diagnose this uploaded tomato leaf image for early and late blight infection and suggest chemical & organic treatments."
  },
  {
    icon: TrendingUp,
    label: "Katol APMC Mandi Rate",
    prompt: "What is the real-time modal price of Tomato, Onion, and Soybean at Katol Mandi today?"
  },
  {
    icon: Calculator,
    label: "NPK Fertilizer Dosage",
    prompt: "Calculate the exact NPK 120:60:40 kg/ha dosage in Urea, DAP, and MOP bags for 4.5 acres of Wheat."
  },
  {
    icon: Layers,
    label: "Sentinel-2 NDVI Analysis",
    prompt: "Show the latest Sentinel-2 NDVI vegetative health map and autonomous drone flight plan for Plot 14-B."
  },
  {
    icon: ShieldAlert,
    label: "GIS Outbreak Radar",
    prompt: "Are there any active Fall Armyworm or Whitefly disease outbreak clusters within a 25km radius?"
  },
  {
    icon: Cpu,
    label: "Explain Simply",
    prompt: "Explain how to prevent powdery mildew in grape vineyards using drip irrigation in simple terms."
  }
];

export default function SuggestionChips({ isDark = true, onSelectPrompt }) {
  return (
    <div className="w-full max-w-4xl mx-auto overflow-x-auto no-scrollbar py-2">
      <div className="flex items-center gap-2.5 sm:justify-center min-w-max px-2">
        {SUGGESTIONS.map((item, idx) => {
          const Icon = item.icon;
          return (
            <button
              key={idx}
              onClick={() => onSelectPrompt(item.prompt)}
              className={`group flex items-center gap-2 rounded-2xl border px-3.5 py-2 text-xs font-semibold transition-all duration-200 active:scale-[0.98] ${
                isDark
                  ? "border-emerald-500/20 bg-[#05180f]/80 text-slate-200 hover:border-emerald-400 hover:bg-[#072416] hover:text-white hover:-translate-y-0.5 shadow-md shadow-black/40"
                  : "border-slate-200 bg-white/90 text-slate-700 hover:border-emerald-500 hover:bg-emerald-50/50 hover:text-emerald-900 hover:-translate-y-0.5 shadow-xs"
              }`}
            >
              <Icon size={14} className={isDark ? "text-emerald-400 transition-transform group-hover:scale-110" : "text-emerald-600"} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
