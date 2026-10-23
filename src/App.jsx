import { useState } from "react";
import {
  Leaf,
  Camera,
  Sparkles,
  Sun,
  Calculator,
  X,
  TrendingUp,
  Compass,
  Home
} from "lucide-react";

import {
  TRANSLATIONS,
  CROPS_CONFIG
} from "./data/agriData";
import { generateAIChatResponse } from "./services/aiChatbotEngine";

import Hero3DCropModel from "./components/Hero3DCropModel";
import DiseaseLeaf3DModel from "./components/DiseaseLeaf3DModel";
import FarmWeatherDashboard from "./components/weather/FarmWeatherDashboard";
import DiseaseHeatmapCanvas from "./components/DiseaseHeatmapCanvas";
import CropDiagnosticsWorkspace from "./components/diagnostics/CropDiagnosticsWorkspace";
import PrecisionFieldIntelligenceWorkspace from "./components/field-intelligence/PrecisionFieldIntelligenceWorkspace";
import LiveMandiMarketView from "./components/mandi/LiveMandiMarketView";

// Enterprise Shell Components
import GlassHeader from "./components/shell/GlassHeader";
import HolographicAIAvatar from "./components/shell/HolographicAIAvatar";
import OmniPromptStudio from "./components/shell/OmniPromptStudio";
import SuggestionChips from "./components/shell/SuggestionChips";
import AIWorkspaceStream from "./components/shell/AIWorkspaceStream";
import CommandPaletteModal from "./components/shell/CommandPaletteModal";

// 3D ANIMATED AI BOT AVATAR COMPONENT (MiniMax / Hailuo Style)
export default function App() {
  // Keep the app shell focused on supported, connected workflows.
  const [theme, setTheme] = useState("harvest");
  const isDark = theme === "cyber" || theme === "dark" || theme === "monochrome";
  const [lang, setLang] = useState("en");
  const [activeNav, setActiveNav] = useState("workspace");
  const [avatarState, setAvatarState] = useState("idle");
  const [isCommandPaletteOpen, setIsCommandPaletteOpen] = useState(false);
  const [selectedHfModel, setSelectedHfModel] = useState("gemini-2.5-flash");
  const [chatMessages, setChatMessages] = useState([
    {
      sender: "bot",
      text: "Namaste! I'm the Agri Nirvana AI Assistant. I can help explain crop-diagnostic results, farm weather, and market information. For a crop-image assessment, open Crop Diagnostics.",
      source: "Agri Nirvana Assistant"
    }
  ]);
  const [botLoading, setBotLoading] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [calcCrop, setCalcCrop] = useState("wheat");
  const [calcAcres, setCalcAcres] = useState(5);
  const [soilN, setSoilN] = useState("medium");
  const [toastMessage, setToastMessage] = useState(null);
  const t = TRANSLATIONS[lang] || TRANSLATIONS.en;



  const handleSpeechToggle = (textToSpeak) => {
    if (!("speechSynthesis" in window)) {
      showToast("Speech synthesis not supported in this browser.");
      return;
    }

    if (isSpeaking) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
    } else {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(textToSpeak || "No message is available to read aloud.");
      utterance.onend = () => setIsSpeaking(false);
      utterance.onerror = () => setIsSpeaking(false);
      window.speechSynthesis.speak(utterance);
      setIsSpeaking(true);
    }
  };

  const showToast = (msg) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 4000);
  };

  const handleSendBotMessage = async (queryText, attachedFiles = []) => {
    const prompt = queryText || "";
    if (!prompt.trim() && attachedFiles.length === 0) return;

    let displayPrompt = prompt;
    if (attachedFiles.length > 0) {
      displayPrompt += `\n📎 [Attached: ${attachedFiles.map(f => f.name).join(", ")}]`;
    }

    const userMsg = { sender: "user", text: displayPrompt };
    setChatMessages((prev) => [...prev, userMsg]);
    setBotLoading(true);
    setAvatarState("thinking");

    try {
      setTimeout(() => {
        setAvatarState((current) => (current === "thinking" ? "processing" : current));
      }, 500);

      const botResponse = await generateAIChatResponse({
        userPrompt: prompt || "Analyze attached crop leaf image",
        attachments: attachedFiles,
        selectedModel: selectedHfModel,
        userLang: lang
      });
      
      setAvatarState("speaking");
      setChatMessages((prev) => [
        ...prev,
        {
          sender: "bot",
          text: botResponse.text,
          source: botResponse.source,
          tableData: botResponse.tableData,
          reasoning: botResponse.reasoning,
          latency: botResponse.latency,
          suggestedFollowUps: botResponse.suggestedFollowUps
        }
      ]);

      // Automatically speak summary
      handleSpeechToggle(botResponse.text.slice(0, 160));
      setTimeout(() => {
        setAvatarState("idle");
      }, 4000);
    } catch (err) {
      setAvatarState("error");
      setChatMessages((prev) => [
        ...prev,
        {
          sender: "bot",
          text: "The Agri Nirvana AI service is unavailable right now. No AI answer or diagnosis was generated. Please try again later.",
          source: "AI service unavailable",
          reasoning: "The request failed; no offline inference was performed."
        }
      ]);
      setTimeout(() => {
        setAvatarState("idle");
      }, 3000);
    } finally {
      setBotLoading(false);
    }
  };

  // NPK Calculation Logic
  const currentCropConfig = CROPS_CONFIG.find((c) => c.id === calcCrop) || CROPS_CONFIG[0];
  const multN = soilN === "low" ? 1.25 : soilN === "high" ? 0.75 : 1.0;
  
  const totalN_kg = Math.round(currentCropConfig.defaultN * calcAcres * multN);
  const totalP_kg = Math.round(currentCropConfig.defaultP * calcAcres);
  const totalK_kg = Math.round(currentCropConfig.defaultK * calcAcres);

  const dapBags = Math.round((totalP_kg / 0.46) / 50);
  const nitrogenFromDap = dapBags * 50 * 0.18;
  const remainingN = Math.max(0, totalN_kg - nitrogenFromDap);
  const ureaBags = Math.round((remainingN / 0.46) / 50);
  const mopBags = Math.round((totalK_kg / 0.60) / 50);


  return (
    <div className={`min-h-screen font-sans transition-colors duration-500 ${
      theme === "cyber"
        ? "ai-mesh-bg-dark text-slate-100"
        : theme === "monochrome"
        ? "ai-mesh-bg-monochrome text-slate-100"
        : theme === "harvest"
        ? "ai-mesh-bg-harvest text-slate-900"
        : "ai-mesh-bg-botanical text-slate-900"
    } selection:bg-emerald-500 selection:text-white`}>
      
      {/* Toast Notification Bar */}
      {toastMessage && (
        <div className="fixed top-20 right-5 z-50 flex items-center gap-3 rounded-2xl bg-emerald-600 px-4 py-3 text-sm font-bold text-white shadow-2xl transition-all animate-bounce glow-emerald">
          <Sparkles size={18} />
          <span>{toastMessage}</span>
          <button onClick={() => setToastMessage(null)} className="ml-2 hover:opacity-75"><X size={16} /></button>
        </div>
      )}

      {/* 2. FLOATING GLASS HEADER */}
      <GlassHeader
        isDark={isDark}
        theme={theme}
        onToggleTheme={(targetTheme) => {
          const newTheme = targetTheme || (
            theme === "harvest" ? "botanical" :
            theme === "botanical" ? "cyber" :
            theme === "cyber" ? "monochrome" : "harvest"
          );
          setTheme(newTheme);
          const themeLabels = {
            harvest: "🌾 Golden Harvest (Sun-Drenched Wheat Fields)",
            botanical: "🌿 Botanical Daylight (Sunlit Orchard & Soil)",
            cyber: "🌲 Living Canopy (Organic Forest & Night Sky)",
            monochrome: "📓 Botanical Noir (Minimalist Field Study)"
          };
          showToast(`Switched to ${themeLabels[newTheme] || newTheme}`);
        }}
        lang={lang}
        onChangeLang={(newLang) => {
          setLang(newLang);
          showToast(`Language set to ${newLang.toUpperCase()}`);
        }}
        activeTab={activeNav}
        onChangeTab={(tab) => setActiveNav(tab)}
        onOpenCommandPalette={() => setIsCommandPaletteOpen(true)}
      />

      {/* GLOBAL ⌘K COMMAND SPOTLIGHT PALETTE */}
      <CommandPaletteModal
        isOpen={isCommandPaletteOpen}
        onClose={() => setIsCommandPaletteOpen(false)}
        onToggle={() => setIsCommandPaletteOpen((open) => !open)}
        isDark={isDark}
        onSelectNav={(navId) => setActiveNav(navId)}
        onChangeTheme={(nextTheme) => {
          setTheme(nextTheme);
          showToast(`Theme updated to ${nextTheme.toUpperCase()}`);
        }}
      />

      {/* 3. HERO SECTION (Only displayed on Home / Landing Page) */}
      {activeNav === "workspace" && (
        <section className={`relative overflow-hidden border-b py-12 px-4 sm:px-6 transition-all duration-300 ${
          isDark
            ? "border-emerald-500/20 bg-gradient-to-b from-[#062419] via-[#041911] to-[#030705]"
            : "border-slate-200/70 bg-gradient-to-b from-emerald-50/90 via-teal-50/40 to-slate-50"
        }`}>

          {/* Subtle background dots */}
          <div className={`absolute inset-0 opacity-[0.035] pointer-events-none ${isDark ? "bg-[radial-gradient(#10b981_1px,transparent_1px)]" : "bg-[radial-gradient(#047857_1px,transparent_1px)]"}`}
            style={{backgroundSize: "24px 24px"}} />

          {/* Single soft glow orb */}
          <div className={`absolute -top-24 -left-24 w-80 h-80 rounded-full blur-3xl pointer-events-none opacity-15 ${isDark ? "bg-emerald-500" : "bg-emerald-300"}`} />

          <div className="relative mx-auto max-w-7xl grid grid-cols-1 lg:grid-cols-12 gap-10 items-center">
            {/* LEFT: Text */}
            <div className="lg:col-span-7 text-center lg:text-left space-y-5">
              <h1 className={`text-4xl font-black tracking-tight sm:text-5xl lg:text-6xl ${
                isDark ? "ai-gradient-text" : "ai-gradient-text-light"
              }`}>
                Scan. Diagnose. Grow.
              </h1>

              <p className={`max-w-xl text-sm sm:text-base leading-relaxed ${
                isDark ? "text-emerald-100/70" : "text-slate-600"
              }`}>
                {t.heroSub}
              </p>

              <div className="flex flex-wrap items-center justify-center lg:justify-start gap-3 pt-1">
                <button
                  onClick={() => setActiveNav("diag")}
                  className="rounded-2xl bg-gradient-to-r from-emerald-500 to-teal-400 px-6 py-3 text-xs font-black text-slate-950 shadow-lg glow-emerald hover:brightness-110 flex items-center gap-2 transition hover:scale-[1.02] active:scale-[0.98]"
                >
                  <Camera size={16} /> Run AI Leaf Diagnostics
                </button>
                <button
                  onClick={() => setActiveNav("weather")}
                  className={`rounded-2xl border px-6 py-3 text-xs font-bold flex items-center gap-2 transition active:scale-[0.98] hover:scale-[1.02] ${
                    isDark ? "border-emerald-500/40 bg-emerald-500/10 text-emerald-300 hover:bg-emerald-500/20" : "border-emerald-500/40 bg-white text-emerald-700 hover:bg-emerald-50 shadow-sm"
                  }`}
                >
                  <CloudSun size={16} /> View Farm Weather
                </button>
              </div>
            </div>

            {/* RIGHT: 3D Model */}
            <div className="lg:col-span-5 flex items-center justify-center">
              <div className={`relative w-full rounded-3xl overflow-hidden transition-all ${
                isDark
                  ? "border border-emerald-500/20 bg-[#040f08] shadow-[0_0_80px_-20px_rgba(16,185,129,0.35)]"
                  : "border border-emerald-200/60 bg-gradient-to-br from-emerald-50 to-white shadow-2xl"
              }`} style={{minHeight: "460px", maxWidth: "480px"}}>
                <Hero3DCropModel theme={theme} />
              </div>
            </div>

          </div>
        </section>
      )}

      {/* Main Content Area */}

      <main className="mx-auto max-w-7xl px-4 py-6 sm:px-6">
        {/* Mobile Navigation Bar */}
        <div className="flex xl:hidden overflow-x-auto gap-2 mb-6 pb-2 no-scrollbar">
          {[
            { id: "workspace", label: "Home", icon: Home },
            { id: "intel", label: "Field Scenario", icon: Compass },
            { id: "diag", label: t.navDiag, icon: Leaf },
            { id: "weather", label: "Weather", icon: CloudSun },

            { id: "calc", label: t.navCalc, icon: Calculator },
            { id: "mandi", label: t.navMandi, icon: TrendingUp },


          ].map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              onClick={() => setActiveNav(id)}
              className={`flex shrink-0 items-center gap-2 rounded-xl px-3 py-2 text-xs font-bold whitespace-nowrap transition ${
                activeNav === id
                  ? isDark ? "bg-emerald-500 text-slate-950 shadow-md glow-emerald font-black" : "bg-emerald-600 text-white shadow-md font-black"
                  : isDark
                    ? "border border-emerald-900/60 bg-emerald-950/60 text-slate-300"
                    : "border border-slate-200 bg-white text-slate-600 shadow-xs"
              }`}
            >
              <Icon size={14} />
              <span>{label}</span>
            </button>
          ))}
        </div>

        {/* SECTION: 3D HOLOGRAPHIC AI WORKSPACE (Default Main Studio) */}
        {activeNav === "workspace" && (
          <div className="space-y-6 animate-fade-in">
            {/* 3D Holographic AI Avatar */}
            <HolographicAIAvatar
              state={avatarState}
              selectedModel={selectedHfModel}
              isDark={isDark}
            />

            {/* Omni Multi-Modal Prompt Studio */}
            <OmniPromptStudio
              isDark={isDark}
              selectedModel={selectedHfModel}
              onSelectModel={(model) => setSelectedHfModel(model)}
              isLoading={botLoading}
              onSubmitPrompt={(text, attachments) => handleSendBotMessage(text, attachments)}
              onTriggerVoice={(isRec) => {
                if (isRec) {
                  setAvatarState("speaking");
                } else {
                  setAvatarState("idle");
                }
              }}
            />

            {/* Quick Prompt Suggestion Chips */}
            <SuggestionChips
              isDark={isDark}
              onSelectPrompt={(prompt) => handleSendBotMessage(prompt)}
            />

            {/* Live Streaming AI Messages Workspace */}
            <AIWorkspaceStream
              messages={chatMessages}
              isDiagnoseing={botLoading}
              isDark={isDark}
              isPlayingAudio={isSpeaking}
              onPlayAudio={(text) => handleSpeechToggle(text)}
              onSelectFollowUp={(followUp) => handleSendBotMessage(followUp)}
            />
          </div>
        )}

        {/* SECTION: PRECISION 3D FIELD INTELLIGENCE & DRONE AVIONICS */}
        {activeNav === "intel" && (
          <div className="animate-fade-in">
            <PrecisionFieldIntelligenceWorkspace
              isDark={isDark}
              theme={theme}
              showToast={showToast}
            />
          </div>
        )}

        {/* SECTION: AI DIAGNOSTICS MODULE (ONE-STOP WORKSPACE) */}
        {activeNav === "diag" && (
          <CropDiagnosticsWorkspace
            lang={lang}
            theme={theme}
            t={t}
            showToast={showToast}
          />
        )}

        {/* SECTION: FARM WEATHER & AGRO-METEOROLOGY INTELLIGENCE */}
        {activeNav === "weather" && (
          <FarmWeatherDashboard
            theme={theme}
            isDark={isDark}
            onNavigateDiagnostics={() => setActiveNav("diag")}
          />
        )}

        {activeNav === "calc" && (
          <div className="space-y-6">
            <div className={`rounded-3xl p-6 border transition-all ${
              isDark ? "border-emerald-800/40 bg-[#072017]" : "border-slate-200 bg-white shadow-xl"
            }`}>
              <h2 className={`text-2xl font-black flex items-center gap-2 mb-2 ${isDark ? "text-white" : "text-slate-900"}`}>
                <Calculator className="text-emerald-500" size={26} />
                {t.npkTitle}
              </h2>
              <p className={`text-xs mb-3 ${isDark ? "text-slate-400" : "text-slate-600"}`}>{t.npkSub}</p>
              <p role="note" className={`mb-6 rounded-xl border px-4 py-3 text-xs leading-relaxed ${isDark ? "border-amber-500/30 bg-amber-500/10 text-amber-200" : "border-amber-300 bg-amber-50 text-amber-900"}`}>Planning estimate only: this uses generic crop nutrient defaults, not a soil-test-based recommendation. Actual nutrient needs depend on soil tests, crop variety, yield goals, and local conditions. Confirm fertilizer decisions with your local KVK or agricultural-extension officer.</p>

              <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
                <div className="lg:col-span-6 space-y-4 text-xs">
                  <div>
                    <label className="block font-bold mb-1">Select Crop Type</label>
                    <select
                      value={calcCrop}
                      onChange={(e) => setCalcCrop(e.target.value)}
                      className={`w-full rounded-xl border p-3 outline-none font-bold ${
                        isDark ? "border-emerald-800 bg-[#04160f] text-white" : "border-slate-300 bg-slate-50 text-slate-800"
                      }`}
                    >
                      {CROPS_CONFIG.map((c) => (
                        <option key={c.id} value={c.id}>{c.name} (NPK Ratio: {c.defaultN}:{c.defaultP}:{c.defaultK})</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block font-bold mb-1">Land Parcel Area (Acres): {calcAcres} Acres</label>
                    <input type="range" min="1" max="25" value={calcAcres} onChange={(e) => setCalcAcres(Number(e.target.value))} className="w-full accent-emerald-500" />
                  </div>

                  <div>
                    <label className="block font-bold mb-1">Soil Nitrogen Testing Level</label>
                    <div className="flex gap-2">
                      {["low", "medium", "high"].map((lvl) => (
                        <button key={lvl} onClick={() => setSoilN(lvl)} className={`flex-1 rounded-xl py-2 font-bold uppercase border transition ${
                          soilN === lvl
                            ? "border-emerald-500 bg-emerald-500/20 text-emerald-300"
                            : isDark ? "border-slate-800 text-slate-400" : "border-slate-300 text-slate-600"
                        }`}>{lvl}</button>
                      ))}
                    </div>
                  </div>
                </div>

                <div className={`lg:col-span-6 rounded-3xl border p-6 space-y-4 transition-all ${
                  isDark ? "border-emerald-500/30 bg-[#04160f] text-white" : "border-emerald-200 bg-emerald-50/70 text-slate-900 shadow-sm"
                }`}>
                  <h3 className="text-lg font-black text-emerald-500">Nutrient Bag Estimate</h3>
                  <div className="grid grid-cols-3 gap-3 text-center">
                    <div className={`rounded-xl border p-3 ${
                      isDark ? "border-emerald-500/30 bg-emerald-500/10 text-white" : "border-emerald-300 bg-white text-slate-900 shadow-xs"
                    }`}>
                      <p className="text-2xl font-black">{ureaBags}</p>
                      <p className={`text-[10px] font-bold ${isDark ? "text-emerald-300" : "text-emerald-700"}`}>Urea Bags (50kg)</p>
                    </div>
                    <div className={`rounded-xl border p-3 ${
                      isDark ? "border-cyan-500/30 bg-cyan-500/10 text-white" : "border-cyan-300 bg-white text-slate-900 shadow-xs"
                    }`}>
                      <p className="text-2xl font-black">{dapBags}</p>
                      <p className={`text-[10px] font-bold ${isDark ? "text-cyan-300" : "text-cyan-700"}`}>DAP Bags (50kg)</p>
                    </div>
                    <div className={`rounded-xl border p-3 ${
                      isDark ? "border-amber-500/30 bg-amber-500/10 text-white" : "border-amber-300 bg-white text-slate-900 shadow-xs"
                    }`}>
                      <p className="text-2xl font-black">{mopBags}</p>
                      <p className={`text-[10px] font-bold ${isDark ? "text-amber-300" : "text-amber-700"}`}>MOP Bags (50kg)</p>
                    </div>
                  </div>

                </div>
              </div>
            </div>
          </div>
        )}

        {/* SECTION: MANDI PRICE INTELLIGENCE */}
        {activeNav === "mandi" && (
          <LiveMandiMarketView
            isDark={isDark}
            t={t}
          />
        )}

      </main>

      {/* Footer */}
      <footer className={`mt-16 border-t py-8 text-center text-xs transition-colors ${
        isDark ? "border-emerald-900/40 bg-[#03100a] text-slate-400" : "border-slate-200 bg-slate-100 text-slate-600"
      }`}>
        <div className="mx-auto max-w-7xl px-4 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className={`flex items-center gap-3 font-extrabold ${isDark ? "text-white" : "text-slate-900"}`}>
            <img
              src={isDark ? "/logo-dark.png" : "/logo-light.png"}
              alt="Agri Nirvana Logo"
              className="h-8 w-auto object-contain"
            />
            <span className="text-xs font-semibold text-slate-400">| Crop diagnostics · Weather · Market intelligence</span>
          </div>
          <p>© 2026 Agri Nirvana. AI guidance and field scenarios require real-world verification.</p>
        </div>
      </footer>
    </div>
  );
}
