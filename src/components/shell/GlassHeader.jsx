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
  Calculator,
  TrendingUp,
  ShoppingCart,
  Zap,
  Search,
  Compass,
  Home,
  CloudSun
} from "lucide-react";

const LANGUAGES = [
  { code: "en", name: "English", flag: "🇬🇧" },
  { code: "hi", name: "हिन्दी", flag: "🇮🇳" },
  { code: "mr", name: "मराठी", flag: "🇮🇳" },
  { code: "te", name: "తెలుగు", flag: "🇮🇳" },
  { code: "ta", name: "தமிழ்", flag: "🇮🇳" },
  { code: "pa", name: "ਪੰਜਾਬੀ", flag: "🇮🇳" }
];

export default function GlassHeader({
  isDark = true,
  theme = "harvest",
  onToggleTheme,
  lang = "en",
  onChangeLang,
  activeTab = "workspace",
  onChangeTab,
  onOpenPricing,
  onOpenCommandPalette
}) {
  const [langDropdownOpen, setLangDropdownOpen] = useState(false);

  const navItems = [
    { id: "workspace", label: "Home", icon: Home },
    { id: "intel", label: "Drone Tech", icon: Compass },
    { id: "diag", label: "Diagnostics", icon: Leaf },
    { id: "weather", label: "Weather", icon: CloudSun },
    { id: "map", label: "Radar", icon: Radar },
    { id: "calc", label: "Soil NPK", icon: Calculator },
    { id: "mandi", label: "Mandi", icon: TrendingUp },
    { id: "market", label: "Market", icon: ShoppingCart },
  ];

  return (
    <header
      className={`sticky top-0 z-40 border-b backdrop-blur-2xl transition-all duration-300 ${
        isDark
          ? "border-emerald-500/20 bg-[#030705]/85 shadow-[0_10px_35px_rgba(0,0,0,0.6)]"
          : "border-slate-200/80 bg-white/90 shadow-sm shadow-slate-100"
      }`}
    >
      <div className="mx-auto flex max-w-7xl items-center justify-between px-3 sm:px-5 py-2.5">
        {/* Left: Official Agri Nirvana Logo */}
        <button
          type="button"
          className="flex items-center text-left group select-none cursor-pointer shrink-0 mr-2"
          onClick={() => onChangeTab("workspace")}
          aria-label="Open Agri Nirvana workspace"
        >
          <img
            src={isDark ? "/logo-dark.png" : "/logo-light.png"}
            alt="Agri Nirvana"
            className="h-11 sm:h-12 w-auto max-w-[180px] sm:max-w-[210px] object-contain transition-transform duration-200 group-hover:scale-105"
          />
        </button>

        {/* Center: Segmented Pill Navigation */}
        <nav
          aria-label="Primary navigation"
          className={`hidden xl:flex items-center gap-0.5 rounded-2xl p-1 border backdrop-blur-md transition-colors ${
            isDark
              ? "bg-[#07170e]/80 border-emerald-500/20"
              : "bg-slate-100/90 border-slate-200"
          }`}
        >
          {navItems.map(({ id, label, icon: Icon }) => {
            const isActive = activeTab === id;
            return (
              <button
                type="button"
                key={id}
                onClick={() => onChangeTab(id)}
                aria-current={isActive ? "page" : undefined}
                className={`relative flex items-center gap-1.5 rounded-xl px-2.5 py-1.5 text-xs font-bold whitespace-nowrap transition-all duration-200 active:scale-[0.98] ${
                  isActive
                    ? isDark
                      ? "bg-gradient-to-r from-emerald-500 to-teal-400 text-slate-950 shadow-md glow-emerald font-black"
                      : "bg-emerald-600 text-white shadow-md shadow-emerald-600/25 font-black"
                    : isDark
                    ? "text-slate-300 hover:text-white hover:bg-emerald-950/40"
                    : "text-slate-600 hover:text-slate-900 hover:bg-white/80"
                }`}
              >
                <Icon size={14} className="shrink-0" />
                <span>{label}</span>
              </button>
            );
          })}
        </nav>

        {/* Right Controls */}
        <div className="flex items-center gap-1.5 sm:gap-2 shrink-0">
          <button
            type="button"
            onClick={() => onOpenCommandPalette?.()}
            title="Open Command Spotlight (⌘K / Ctrl+K)"
            aria-label="Open command palette"
            className={`hidden lg:flex items-center gap-1.5 rounded-xl border px-2.5 py-1.5 text-xs font-bold transition-all active:scale-[0.98] ${
              isDark
                ? "border-emerald-500/20 bg-[#071a10] text-slate-300 hover:border-emerald-400"
                : "border-slate-200 bg-slate-100 text-slate-700 hover:bg-slate-200 shadow-xs"
            }`}
          >
            <Search size={13} className="text-emerald-400" />
            <span className="text-[11px] hidden xl:inline">Command</span>
            <kbd className="rounded bg-emerald-500/20 text-emerald-400 px-1 text-[9px] font-mono border border-emerald-500/30">
              ⌘K
            </kbd>
          </button>

          <button
            type="button"
            onClick={onOpenPricing}
            className={`flex items-center gap-1.5 rounded-xl border px-2.5 py-1.5 text-xs font-extrabold transition-all active:scale-[0.98] ${
              isDark
                ? "border-emerald-500/30 bg-emerald-500/10 text-emerald-300 hover:bg-emerald-500/20"
                : "border-slate-300 bg-white text-slate-700 shadow-sm hover:bg-slate-50"
            }`}
          >
            <Zap size={13} className="text-amber-400 animate-pulse shrink-0" />
            <span className="hidden sm:inline">Pro Tier</span>
          </button>

          {/* 4-Way Natural & Realistic Theme Selector */}
          <div className="relative">
            <button
              type="button"
              onClick={() => {
                if (theme === "harvest") onToggleTheme?.("botanical");
                else if (theme === "botanical" || theme === "light") onToggleTheme?.("cyber");
                else if (theme === "cyber" || theme === "dark") onToggleTheme?.("monochrome");
                else onToggleTheme?.("harvest");
              }}
              title="Cycle theme: 🌾 Golden Harvest → 🌿 Botanical → 🌲 Living Canopy → 📓 Noir"
              aria-label="Cycle visual theme"
              className={`flex items-center gap-1.5 rounded-xl border px-2.5 py-1.5 text-xs font-bold transition-all active:scale-[0.98] ${
                theme === "monochrome"
                  ? "border-white/40 bg-black text-white hover:bg-neutral-900 shadow-md shadow-white/10 font-black"
                  : theme === "cyber" || (isDark && theme !== "harvest")
                  ? "border-emerald-500/30 bg-[#061c11] text-emerald-300 hover:bg-[#0a2e1d] glow-emerald"
                  : theme === "harvest"
                  ? "border-amber-400 bg-amber-50 text-amber-900 shadow-sm hover:bg-amber-100"
                  : "border-emerald-300 bg-white text-emerald-950 hover:bg-emerald-50 shadow-sm"
              }`}
            >
              {theme === "monochrome" ? (
                <span className="h-3.5 w-3.5 rounded-full border border-white bg-gradient-to-r from-white to-black inline-block" />
              ) : theme === "cyber" || (isDark && theme !== "harvest") ? (
                <Leaf size={14} className="text-emerald-400 fill-emerald-500/30 shrink-0" />
              ) : theme === "harvest" ? (
                <Sparkles size={14} className="text-amber-500 shrink-0" />
              ) : (
                <Sun size={14} className="text-amber-500 shrink-0" />
              )}
              <span className="hidden 2xl:inline font-semibold text-[11px]">
                {theme === "monochrome" ? "Noir" : theme === "cyber" || (isDark && theme !== "harvest") ? "Canopy" : theme === "harvest" ? "Harvest" : "Daylight"}
              </span>
            </button>
          </div>

          {/* Language Selector */}
          <div className="relative">
            <button
              type="button"
              onClick={() => setLangDropdownOpen((prev) => !prev)}
              aria-expanded={langDropdownOpen}
              aria-haspopup="menu"
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
                role="menu"
                className={`absolute right-0 mt-2 w-40 rounded-2xl border p-1 shadow-2xl z-50 animate-fade-in ${
                  isDark ? "border-emerald-500/30 bg-[#061910] text-slate-200" : "border-slate-200 bg-white text-slate-800"
                }`}
              >
                {LANGUAGES.map((l) => (
                  <button
                    type="button"
                    role="menuitem"
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
