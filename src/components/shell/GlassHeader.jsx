import React, { useState } from "react";
import {
  Leaf,
  Globe,
  Sun,
  Moon,
  ChevronDown,
  Sparkles,
  Bot,
  Layers,
  Radar,
  LineChart,
  Calculator,
  TrendingUp,
  ShoppingCart,
  Zap,
  User,
  Check,
  Search
} from "lucide-react";

const LANGUAGES = [
  { code: "en", name: "English", flag: "🇬🇧" },
  { code: "hi", name: "हिन्दी", flag: "🇮🇳" },
  { code: "mr", name: "मराठी", flag: "🚩" },
  { code: "ja", name: "日本語", flag: "🇯🇵" },
];

export default function GlassHeader({
  isDark = true,
  theme = "dark",
  onToggleTheme,
  lang = "en",
  onChangeLang,
  activeTab = "workspace",
  onChangeTab,
  onOpenPricing
}) {
  const [langDropdownOpen, setLangDropdownOpen] = useState(false);

  const navItems = [
    { id: "workspace", label: "Workspace", icon: Bot, badge: "AI Core" },
    { id: "diag", label: "Diagnostics", icon: Leaf },
    { id: "sat", label: "3D Satellite", icon: Layers },
    { id: "map", label: "GIS Radar", icon: Radar },
    { id: "analytics", label: "Yield Analytics", icon: LineChart },
    { id: "calc", label: "NPK Calc", icon: Calculator },
    { id: "mandi", label: "Mandi Telemetry", icon: TrendingUp },
    { id: "market", label: "Marketplace", icon: ShoppingCart },
  ];

  return (
    <header
      className={`sticky top-0 z-40 border-b backdrop-blur-2xl transition-all duration-300 ${
        isDark
          ? "border-emerald-500/20 bg-[#030705]/85 shadow-[0_10px_35px_rgba(0,0,0,0.6)]"
          : "border-slate-200/80 bg-white/90 shadow-sm shadow-slate-100"
      }`}
    >
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6">
        {/* Left: Glowing AI Icon & Brand */}
        <div
          className="flex items-center gap-3 cursor-pointer group select-none"
          onClick={() => onChangeTab("workspace")}
        >
          <div
            className={`relative grid h-10 w-10 sm:h-11 sm:w-11 place-items-center rounded-2xl shadow-lg transition-transform duration-200 group-hover:scale-105 ${
              isDark
                ? "bg-gradient-to-br from-emerald-400 via-teal-500 to-cyan-500 text-slate-950 glow-emerald"
                : "bg-emerald-600 text-white shadow-emerald-600/30"
            }`}
          >
            <Leaf size={22} className="fill-current" />
            <div className="absolute -top-1 -right-1 h-3 w-3 rounded-full bg-cyan-400 animate-ping opacity-80" />
          </div>

          <div>
            <div className="flex items-center gap-2">
              <span
                className={`text-lg sm:text-xl font-black tracking-tight ${
                  isDark ? "ai-gradient-text" : "ai-gradient-text-light"
                }`}
              >
                Agri Nirvana
              </span>
              <span className="hidden sm:inline-flex items-center gap-1 rounded-full bg-emerald-500/20 px-2 py-0.5 text-[9px] font-mono font-bold text-emerald-300 border border-emerald-500/40 uppercase tracking-wider">
                <Sparkles size={10} className="text-amber-400" />
                Next-Gen AI
              </span>
            </div>
            <p className={`text-[11px] font-medium leading-none ${isDark ? "text-emerald-400/80" : "text-emerald-700"}`}>
              Precision Agronomy & 3D Telemetry
            </p>
          </div>
        </div>

        {/* Center: Segmented Luminous Pill Navigation (Desktop) */}
        <nav
          className={`hidden xl:flex items-center gap-1 rounded-2xl p-1 border backdrop-blur-md transition-colors ${
            isDark
              ? "bg-[#07170e]/80 border-emerald-500/20"
              : "bg-slate-100/90 border-slate-200"
          }`}
        >
          {navItems.map(({ id, label, icon: Icon, badge }) => {
            const isActive = activeTab === id;
            return (
              <button
                key={id}
                onClick={() => onChangeTab(id)}
                className={`relative flex items-center gap-1.5 rounded-xl px-3 py-1.5 text-xs font-bold transition-all duration-200 active:scale-[0.98] ${
                  isActive
                    ? isDark
                      ? "bg-gradient-to-r from-emerald-500 to-teal-400 text-slate-950 shadow-md glow-emerald font-black scale-[1.02]"
                      : "bg-emerald-600 text-white shadow-md shadow-emerald-600/25 font-black"
                    : isDark
                    ? "text-slate-300 hover:text-white hover:bg-emerald-950/40"
                    : "text-slate-600 hover:text-slate-900 hover:bg-white/80"
                }`}
              >
                <Icon size={14} />
                <span>{label}</span>
                {badge && (
                  <span className="rounded bg-amber-400/20 text-amber-400 px-1 py-0.2 text-[8px] font-mono">
                    {badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>

        {/* Right Controls: Command Menu, Tier, Theme, Language, Profile */}
        <div className="flex items-center gap-2 sm:gap-2.5">
          {/* Quick Command Palette Button */}
          <button
            onClick={() => onOpenCommandPalette?.()}
            title="Open Command Spotlight (⌘K / Ctrl+K)"
            className={`hidden md:flex items-center gap-1.5 rounded-xl border px-2.5 py-1.5 text-xs font-bold transition-all active:scale-[0.98] ${
              isDark
                ? "border-emerald-500/20 bg-[#071a10] text-slate-300 hover:border-emerald-400"
                : "border-slate-200 bg-slate-100 text-slate-700 hover:bg-slate-200 shadow-xs"
            }`}
          >
            <Search size={13} className="text-emerald-400" />
            <span className="text-[11px]">Command</span>
            <kbd className="rounded bg-emerald-500/20 text-emerald-400 px-1 text-[9px] font-mono border border-emerald-500/30">
              ⌘K
            </kbd>
          </button>

          <button
            onClick={onOpenPricing}
            className={`flex items-center gap-1.5 rounded-xl border px-3 py-1.5 text-xs font-extrabold transition-all active:scale-[0.98] ${
              isDark
                ? "border-emerald-500/30 bg-emerald-500/10 text-emerald-300 hover:bg-emerald-500/20"
                : "border-slate-300 bg-white text-slate-700 shadow-sm hover:bg-slate-50"
            }`}
          >
            <Zap size={13} className="text-amber-400 animate-pulse" />
            <span className="hidden sm:inline">Pro Tier</span>
          </button>

          {/* 3-Way Beast Theme Selector */}
          <div className="relative">
            <button
              onClick={() => {
                if (theme === "botanical" || theme === "light") onToggleTheme?.("cyber");
                else if (theme === "cyber" || theme === "dark") onToggleTheme?.("harvest");
                else onToggleTheme?.("botanical");
              }}
              title="Click to cycle themes: Botanical White → Cyber Obsidian → Golden Harvest"
              className={`flex items-center gap-1.5 rounded-xl border px-2.5 py-1.5 text-xs font-bold transition-all active:scale-[0.98] ${
                theme === "cyber" || isDark
                  ? "border-emerald-500/30 bg-[#071a10] text-emerald-300 hover:bg-[#0c2a1b] glow-emerald"
                  : theme === "harvest"
                  ? "border-amber-400 bg-amber-50 text-amber-900 shadow-sm hover:bg-amber-100"
                  : "border-slate-300 bg-white text-slate-700 hover:bg-slate-50 shadow-sm"
              }`}
            >
              {theme === "cyber" || isDark ? (
                <Moon size={14} className="text-emerald-400" />
              ) : theme === "harvest" ? (
                <Sparkles size={14} className="text-amber-500" />
              ) : (
                <Sun size={14} className="text-amber-500" />
              )}
              <span className="hidden md:inline font-mono">
                {theme === "cyber" || (isDark && theme !== "harvest") ? "Cyber" : theme === "harvest" ? "Harvest" : "Botanical"}
              </span>
            </button>
          </div>

          {/* Language Selector */}
          <div className="relative">
            <button
              onClick={() => setLangDropdownOpen((prev) => !prev)}
              aria-label="Select Language"
              className={`flex items-center gap-1.5 rounded-xl border px-2.5 py-1.5 text-xs font-bold transition-all active:scale-[0.98] ${
                isDark
                  ? "border-emerald-500/20 bg-[#071a10] text-slate-200 hover:bg-[#0c2a1b]"
                  : "border-slate-300 bg-white text-slate-800 shadow-sm hover:bg-slate-50"
              }`}
            >
              <Globe size={14} className={isDark ? "text-emerald-400" : "text-emerald-600"} />
              <span className="uppercase font-mono">{lang}</span>
              <ChevronDown size={13} className="text-slate-400" />
            </button>

            {langDropdownOpen && (
              <div
                className={`absolute right-0 mt-2 w-40 rounded-2xl border p-1 shadow-2xl z-50 animate-fade-in ${
                  isDark ? "border-emerald-500/30 bg-[#061910] text-slate-200" : "border-slate-200 bg-white text-slate-800"
                }`}
              >
                {LANGUAGES.map((l) => (
                  <button
                    key={l.code}
                    onClick={() => {
                      onChangeLang(l.code);
                      setLangDropdownOpen(false);
                    }}
                    className={`flex w-full items-center justify-between rounded-xl px-3 py-2 text-xs font-semibold transition ${
                      lang === l.code
                        ? isDark
                          ? "bg-emerald-500/20 text-emerald-300 font-bold"
                          : "bg-emerald-50 text-emerald-800 font-bold"
                        : isDark
                        ? "text-slate-300 hover:bg-emerald-950/60"
                        : "text-slate-700 hover:bg-slate-100"
                    }`}
                  >
                    <span>{l.name}</span>
                    <span>{l.flag}</span>
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
