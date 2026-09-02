import React, { useState, useEffect } from "react";
import {
  Search,
  Bot,
  Leaf,
  Layers,
  Radar,
  Calculator,
  TrendingUp,
  ShoppingCart,
  Zap,
  Sun,
  Moon,
  Sparkles,
  X,
  Command,
  Compass,
  Sliders,
  Home,
  CloudSun
} from "lucide-react";

export default function CommandPaletteModal({
  isOpen,
  onClose,
  isDark = true,
  onSelectNav,
  onChangeTheme,
  onRunDiagnosis,
  onQuickPrompt
}) {
  const [search, setSearch] = useState("");

  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        if (isOpen) onClose();
        else onClose(false); // toggle trigger
      }
      if (e.key === "Escape" && isOpen) {
        onClose();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const actions = [
    { id: "workspace", label: "Home — 3D AI Overview", icon: Home, category: "Navigation", badge: "Home", run: () => { onSelectNav("workspace"); onClose(); } },
    { id: "intel", label: "Drone Tech — Autonomous Avionics & Field Surveys", icon: Compass, category: "Drone & Avionics", badge: "Drone", run: () => { onSelectNav("intel"); onClose(); } },
    { id: "diag", label: "Run AI Crop Leaf Diagnostics", icon: Leaf, category: "Diagnostics", badge: "ResNet-50", run: () => { onSelectNav("diag"); onClose(); } },
    { id: "weather", label: "Open Farm Weather & Agricultural Forecast", icon: CloudSun, category: "Weather", badge: "Live", run: () => { onSelectNav("weather"); onClose(); } },
    { id: "map", label: "View 25km GIS Outbreak Radar", icon: Radar, category: "Telemetry", badge: "GIS", run: () => { onSelectNav("map"); onClose(); } },
    { id: "calc", label: "Calculate NPK Fertilizer Bags", icon: Calculator, category: "Tools", badge: "Agronomy", run: () => { onSelectNav("calc"); onClose(); } },
    { id: "mandi", label: "Live APMC Mandi Prices (e-NAM)", icon: TrendingUp, category: "Market", badge: "Live Feed", run: () => { onSelectNav("mandi"); onClose(); } },
    { id: "market", label: "Direct Harvest Produce Marketplace", icon: ShoppingCart, category: "Market", badge: "Trade", run: () => { onSelectNav("market"); onClose(); } },
    { id: "theme-harvest", label: "Switch to 🌾 Golden Harvest Theme (Warm Wheat Fields)", icon: Sparkles, category: "Appearance", badge: "Primary", run: () => { onChangeTheme("harvest"); onClose(); } },
    { id: "theme-botanical", label: "Switch to 🌿 Botanical Daylight Theme (Sunlit Orchard)", icon: Sun, category: "Appearance", badge: "Daylight", run: () => { onChangeTheme("botanical"); onClose(); } },
    { id: "theme-cyber", label: "Switch to 🌲 Living Canopy Theme (Deep Organic Forest)", icon: Leaf, category: "Appearance", badge: "Canopy", run: () => { onChangeTheme("cyber"); onClose(); } },
    { id: "theme-monochrome", label: "Switch to 📓 Botanical Noir Theme (Field Journal)", icon: Sliders, category: "Appearance", badge: "Noir", run: () => { onChangeTheme("monochrome"); onClose(); } }
  ];

  const filtered = actions.filter((a) =>
    a.label.toLowerCase().includes(search.toLowerCase()) ||
    a.category.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-20 px-4 bg-black/60 backdrop-blur-md animate-fade-in">
      <div
        className={`w-full max-w-2xl rounded-3xl border p-4 shadow-2xl transition-all ${
          isDark
            ? "glass-ai-panel border-emerald-500/30 text-white shadow-[0_25px_60px_rgba(0,0,0,0.8)]"
            : "glass-ai-panel-light border-slate-200 text-slate-900 shadow-2xl"
        }`}
      >
        {/* Search Input Bar */}
        <div className="relative flex items-center border-b border-emerald-500/20 pb-3">
          <Search size={18} className="text-emerald-400 ml-2 mr-3 shrink-0" />
          <input
            type="text"
            autoFocus
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Type a command or jump to feature (e.g., 'diagnostics', 'mandi', 'theme')..."
            className="w-full bg-transparent text-sm sm:text-base outline-none font-medium placeholder:text-slate-500"
          />
          <span className="hidden sm:inline-block rounded-md bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 px-2 py-0.5 text-[10px] font-mono">
            ESC to close
          </span>
          <button onClick={onClose} className="ml-2 hover:opacity-75 sm:hidden">
            <X size={18} />
          </button>
        </div>

        {/* Command Action List */}
        <div className="mt-3 max-h-80 overflow-y-auto space-y-1 no-scrollbar">
          {filtered.length > 0 ? (
            filtered.map((item) => {
              const Icon = item.icon;
              return (
                <button
                  key={item.id}
                  onClick={item.run}
                  className={`flex w-full items-center justify-between rounded-2xl p-3 text-left transition active:scale-[0.99] ${
                    isDark
                      ? "hover:bg-emerald-950/60 hover:text-emerald-300 text-slate-200"
                      : "hover:bg-emerald-50 text-slate-800 hover:text-emerald-900"
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <div className="grid h-8 w-8 place-items-center rounded-xl bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                      <Icon size={16} />
                    </div>
                    <div>
                      <p className="text-xs sm:text-sm font-bold">{item.label}</p>
                      <p className="text-[10px] opacity-70 font-mono">{item.category}</p>
                    </div>
                  </div>
                  <span className="rounded-md bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 px-2 py-0.5 text-[10px] font-mono font-bold">
                    {item.badge}
                  </span>
                </button>
              );
            })
          ) : (
            <div className="py-8 text-center text-xs text-slate-400 font-mono">
              No matching commands found for "{search}"
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
