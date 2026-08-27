import React, { useState, useEffect, useRef } from "react";
import {
  Leaf,
  Camera,
  Globe,
  Wifi,
  WifiOff,
  Volume2,
  Sparkles,
  ShieldAlert,
  ChevronDown,
  Layers,
  Sun,
  Moon,
  Calculator,
  MapPin,
  X,
  TrendingUp,
  ShoppingCart,
  Zap,
  Check,
  Award,
  Bot,
  Send,
  Search,
  PlusCircle,
  Clock,
  Coins,
  Radar,
  LineChart,
  Target,
  Maximize2,
  Minimize2,
  ChevronUp,
  Mic,
  MicOff,
  Paperclip,
  ArrowUpRight,
  Cpu,
  Radio,
  Activity
} from "lucide-react";

import {
  LANGUAGES,
  TRANSLATIONS,
  CROP_DISEASE_DATASETS,
  SATELLITE_FIELDS,
  CROPS_CONFIG,
  OUTBREAK_CLUSTERS,
  SUBSCRIPTION_PLANS,
  AGRI_PRODUCTS,
  MANDI_PRICES_FEED,
  KAGGLE_VEGETABLE_PRICES,
  queryHuggingFaceAgriBot,
  classifyCropLeafImage
} from "./data/agriData";

import Hero3DCropModel from "./components/Hero3DCropModel";
import DiseaseLeaf3DModel from "./components/DiseaseLeaf3DModel";
import NDVITerrain3DModel from "./components/NDVITerrain3DModel";
import DiseaseHeatmapCanvas from "./components/DiseaseHeatmapCanvas";
import CropDiagnosticsWorkspace from "./components/diagnostics/CropDiagnosticsWorkspace";
import DashboardDiagnosticCard from "./components/diagnostics/DashboardDiagnosticCard";
import PrecisionFieldIntelligenceWorkspace from "./components/field-intelligence/PrecisionFieldIntelligenceWorkspace";

// Enterprise Shell Components
import TelemetryRibbon from "./components/shell/TelemetryRibbon";
import GlassHeader from "./components/shell/GlassHeader";
import HolographicAIAvatar from "./components/shell/HolographicAIAvatar";
import OmniPromptStudio from "./components/shell/OmniPromptStudio";
import SuggestionChips from "./components/shell/SuggestionChips";
import AIWorkspaceStream from "./components/shell/AIWorkspaceStream";
import CommandPaletteModal from "./components/shell/CommandPaletteModal";

// 3D ANIMATED AI BOT AVATAR COMPONENT (MiniMax / Hailuo Style)
function AgriBot3DAvatar({ isThinking, isSpeaking, selectedModel }) {
  return (
    <div className="relative flex flex-col items-center justify-center py-2">
      <div className="relative h-40 w-40 [perspective:1000px] flex items-center justify-center">
        {/* Ambient Halo */}
        <div className="absolute inset-0 rounded-full bg-gradient-to-tr from-emerald-500/20 via-cyan-500/10 to-transparent blur-xl animate-pulse" />

        {/* Orbit Ring 1 */}
        <div className={`absolute inset-0 rounded-full border-2 border-emerald-500/40 border-t-emerald-300 border-b-cyan-400 animate-spin ${
          isThinking ? "duration-700 border-amber-400" : "duration-3000"
        }`} style={{ transformStyle: "preserve-3d", transform: "rotateX(65deg) rotateY(15deg)" }} />

        {/* Orbit Ring 2 */}
        <div className={`absolute inset-2 rounded-full border-2 border-cyan-500/40 border-r-emerald-300 border-l-teal-200 animate-spin ${
          isSpeaking ? "duration-500 border-emerald-300 shadow-[0_0_20px_#10b981]" : "duration-4000"
        }`} style={{ transformStyle: "preserve-3d", transform: "rotateX(25deg) rotateY(65deg)" }} />

        {/* Orbit Ring 3 (Particle Dashes) */}
        <div className="absolute inset-4 rounded-full border border-dashed border-emerald-400/50 animate-spin duration-7000"
             style={{ transformStyle: "preserve-3d", transform: "rotateX(45deg) rotateZ(45deg)" }} />

        {/* Central Core Holographic Sphere */}
        <div className={`relative h-20 w-20 rounded-full bg-gradient-to-tr from-emerald-600 via-teal-400 to-cyan-300 shadow-[0_0_35px_#10b981] flex items-center justify-center transition-all duration-500 ${
          isThinking ? "scale-110 shadow-[0_0_50px_#f59e0b] from-amber-500 via-orange-400 to-yellow-300" : ""
        } ${
          isSpeaking ? "scale-105 shadow-[0_0_50px_#34d399] from-emerald-400 via-teal-300 to-cyan-200" : ""
        }`}>
          {isSpeaking ? (
            <div className="flex items-center gap-1">
              <span className="w-1 bg-white rounded-full audio-wave-bar" />
              <span className="w-1 bg-white rounded-full audio-wave-bar" />
              <span className="w-1 bg-white rounded-full audio-wave-bar" />
              <span className="w-1 bg-white rounded-full audio-wave-bar" />
              <span className="w-1 bg-white rounded-full audio-wave-bar" />
            </div>
          ) : (
            <div className="flex items-center gap-2.5">
              <div className={`h-3 w-3 rounded-full bg-slate-950 shadow-inner transition-all ${
                isThinking ? "animate-ping bg-amber-200" : ""
              }`} />
              <div className={`h-3 w-3 rounded-full bg-slate-950 shadow-inner transition-all ${
                isThinking ? "animate-ping bg-amber-200" : ""
              }`} />
            </div>
          )}
          <div className="absolute -inset-1 rounded-full border border-emerald-300/50 animate-ping opacity-75" />
        </div>

        {/* Holographic Satellite Particles */}
        <div className="absolute -top-2 -left-2 h-2.5 w-2.5 rounded-full bg-emerald-400 animate-bounce opacity-90 shadow-[0_0_10px_#34d399]" />
        <div className="absolute -bottom-1 -right-2 h-2 w-2 rounded-full bg-cyan-400 animate-ping opacity-90 shadow-[0_0_10px_#22d3ee]" />
        <div className="absolute top-1/2 -right-4 h-2 w-2 rounded-full bg-amber-400 animate-pulse opacity-90 shadow-[0_0_10px_#f59e0b]" />
      </div>

      <div className="mt-2 flex items-center gap-2 rounded-full border border-emerald-500/40 bg-emerald-950/90 backdrop-blur-md px-3.5 py-1 text-[10px] font-mono font-bold text-emerald-300 shadow-lg">
        <span className={`h-2 w-2 rounded-full ${
          isThinking ? "bg-amber-400 animate-ping" : isSpeaking ? "bg-cyan-400 animate-pulse" : "bg-emerald-400"
        }`} />
        <span>
          {isThinking ? "3D AI REASONING..." : isSpeaking ? "AUDIO STREAMING ACTIVE" : "3D AI ONLINE (42ms)"}
        </span>
      </div>
      <p className="text-[10px] text-emerald-400/90 font-mono mt-0.5 font-bold">{selectedModel}</p>
    </div>
  );
}

export default function App() {
  // Theme & Navigation State
  const [theme, setTheme] = useState("botanical");
  const isDark = theme === "cyber" || theme === "dark" || theme === "monochrome";
  const [lang, setLang] = useState("en");
  const [langMenuOpen, setLangMenuOpen] = useState(false);
  const [offline, setOffline] = useState(false);
  const [activeNav, setActiveNav] = useState("workspace");
  const [heroExpanded, setHeroExpanded] = useState(true);
  const [avatarState, setAvatarState] = useState("idle");
  const [isCommandPaletteOpen, setIsCommandPaletteOpen] = useState(false);

  // Subscription Features State
  const [userPlan, setUserPlan] = useState("pro");
  const [monthlyScansCount, setMonthlyScansCount] = useState(12);
  const [selectedProductCategory, setSelectedProductCategory] = useState("all");
  const [totalCommissionEarnedINR, setTotalCommissionEarnedINR] = useState(4820);

  // 3D AI Bot & Hugging Face Model State
  const [selectedHfModel, setSelectedHfModel] = useState("Mistral-7B");
  const [chatMessages, setChatMessages] = useState([
    {
      sender: "bot",
      text: "👋 Namaste! I am your 3D Animated Hugging Face AI Agri Assistant (powered by Mistral-7B & pre-processed Kaggle Ag-Datasets). Ask me about real-time vegetable market prices, mandi trends, fertilizer ratios, or crop disease remedies!",
      source: "Hugging Face API (mistralai/Mistral-7B-Instruct-v0.2)"
    }
  ]);
  const [botInputText, setBotInputText] = useState("");
  const [botLoading, setBotLoading] = useState(false);
  const [vegSearchQuery, setVegSearchQuery] = useState("");
  const [vegCategoryFilter, setVegCategoryFilter] = useState("All");

  // Market Linkage State
  const [listedProduce, setListedProduce] = useState([
    { id: "p-1", crop: "Tomato (Hybrid A-Grade)", qtyQuintals: 40, expectedPriceINR: 3300, status: "Active Listing" }
  ]);
  const [produceFormCrop, setProduceFormCrop] = useState("Tomato");
  const [produceFormQty, setProduceFormQty] = useState(25);
  const [produceFormPrice, setProduceFormPrice] = useState(3200);

  // Parametric Insurance State
  const [insuranceClaimTriggered, setInsuranceClaimTriggered] = useState(false);

  // Diagnostic State
  const [selectedDisease, setSelectedDisease] = useState(CROP_DISEASE_DATASETS[0]);
  const [userImage, setUserImage] = useState(null);
  const [scanState, setScanState] = useState("idle");
  const [remedyTab, setRemedyTab] = useState("organic");
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [audioSpeechRate, setAudioSpeechRate] = useState(1.0);
  const [scanProgress, setScanProgress] = useState(0);
  const [diagCrop, setDiagCrop] = useState("Tomato");
  const [diagViewMode, setDiagViewMode] = useState("heatmap"); // "heatmap" | "3d" | "timelapse" | "nir" | "radar" | "spectrum" | "original"
  const [scanStatusStep, setScanStatusStep] = useState("Extracting Leaf RGB & HSV Chromaticity Vectors...");
  const [isCameraModalOpen, setIsCameraModalOpen] = useState(false);
  const [isDosageModalOpen, setIsDosageModalOpen] = useState(false);
  const [isDroneModalOpen, setIsDroneModalOpen] = useState(false);
  const [isClaimModalOpen, setIsClaimModalOpen] = useState(false);
  const [isAgronomistModalOpen, setIsAgronomistModalOpen] = useState(false);

  // Satellite Telemetry State
  const [selectedField, setSelectedField] = useState(SATELLITE_FIELDS[0]);

  // NPK Calculator State
  const [calcCrop, setCalcCrop] = useState("wheat");
  const [calcAcres, setCalcAcres] = useState(5);
  const [soilN, setSoilN] = useState("medium");

  // Outbreak Radar State
  const [outbreakList, setOutbreakList] = useState(OUTBREAK_CLUSTERS);
  const [reportModalOpen, setReportModalOpen] = useState(false);
  const [reportCrop, setReportCrop] = useState("Tomato");
  const [reportDisease, setReportDisease] = useState("Late Blight");
  const [reportPincode, setReportPincode] = useState("440001");
  const [toastMessage, setToastMessage] = useState(null);

  const fileInputRef = useRef(null);
  const chatBottomRef = useRef(null);
  const t = TRANSLATIONS[lang] || TRANSLATIONS.en;
  const isLandingPage = activeNav === "workspace" || activeNav === "bot";

  // Scanning Animation Timer & Real Pixel Classification
  useEffect(() => {
    let interval;
    if (scanState === "scanning") {
      setScanProgress(0);
      setScanStatusStep("Extracting Leaf RGB & HSV Chromaticity Vectors...");

      interval = setInterval(() => {
        setScanProgress((prev) => {
          if (prev === 25) setScanStatusStep("Calculating Chlorophyll & Necrotic Spot Density...");
          if (prev === 50) setScanStatusStep("Matching Pathogen Spectrum Database...");
          if (prev === 75) setScanStatusStep("Generating Precision Treatment Advisory...");
          if (prev >= 100) {
            clearInterval(interval);
            classifyCropLeafImage(userImage || selectedDisease.imageUrl, diagCrop).then((classified) => {
              setSelectedDisease(classified);
              setScanState("result");
              setMonthlyScansCount((c) => c + 1);
            });
            return 100;
          }
          return prev + 25;
        });
      }, 250);
    }
    return () => clearInterval(interval);
  }, [scanState, userImage, selectedDisease.imageUrl, diagCrop]);

  const handlePrintCertificate = () => {
    const printWin = window.open("", "_blank");
    if (!printWin) return;
    const content = `
      <!DOCTYPE html>
      <html>
      <head>
        <title>Kisan AI Crop Diagnostic Certificate - Agri Nirvana</title>
        <style>
          body { font-family: 'Segoe UI', Arial, sans-serif; padding: 24px; color: #1e293b; max-width: 800px; margin: 0 auto; }
          .header { border-bottom: 3px solid #10b981; padding-bottom: 12px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; }
          .title { font-size: 22px; font-weight: 900; color: #065f46; margin: 0; }
          .badge { background: #d1fae5; color: #065f46; padding: 6px 12px; border-radius: 20px; font-size: 12px; font-weight: bold; }
          .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 20px; }
          .box { border: 1px solid #cbd5e1; padding: 14px; border-radius: 12px; background: #f8fafc; }
          .label { font-size: 11px; text-transform: uppercase; color: #64748b; font-weight: bold; }
          .value { font-size: 16px; font-weight: bold; color: #0f172a; margin-top: 4px; }
          .remedy { border: 1px solid #10b981; background: #f0fdf4; padding: 14px; border-radius: 12px; margin-top: 16px; }
          .footer { font-size: 10px; color: #94a3b8; text-align: center; margin-top: 30px; border-top: 1px solid #e2e8f0; padding-top: 12px; }
        </style>
      </head>
      <body>
        <div class="header">
          <div>
            <h1 class="title">AGRI NIRVANA • AI CROP DIAGNOSTIC REPORT</h1>
            <p style="margin: 4px 0 0; font-size: 12px; color: #64748b;">Verified ResNet-50 Vision Telemetry • ...</p>
          </div>
          <div class="badge">AI ANALYZED</div>
        </div>
        <div class="grid">
          <div class="box"><div class="label">Crop</div><div class="value">${selectedDisease.crop || selectedDisease.cropType || diagCrop}</div></div>
          <div class="box"><div class="label">Condition</div><div class="value">${selectedDisease.diseaseName || selectedDisease.condition || "Analysis"}</div></div>
          <div class="box"><div class="label">Confidence</div><div class="value">${selectedDisease.confidence_pct ?? Math.round((selectedDisease.confidence || 0) * 100)}%</div></div>
          <div class="box"><div class="label">Severity</div><div class="value">${selectedDisease.severity?.tier || selectedDisease.severity || "Unknown"}</div></div>
        </div>
        <div class="remedy"><strong>Recommended Action</strong><p>${selectedDisease.farmer_summary || selectedDisease.recommendations?.immediate || "Monitor the crop and consult an agriculture expert for uncertain cases."}</p></div>
        <div class="footer">Agri Nirvana • AI-assisted decision support. Confirm crop protection products and local recommendations with a qualified agricultural professional.</div>
      </body>
      </html>`;
    printWin.document.write(content);
    printWin.document.close();
    printWin.focus();
    printWin.print();
  };

  const showToast = (message) => {
    setToastMessage(message);
    window.setTimeout(() => setToastMessage(null), 2800);
  };

  const handleSpeechToggle = (text) => {
    if (!text || !("speechSynthesis" in window)) return;
    if (isSpeaking) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
      return;
    }
    const utterance = new SpeechSynthesisUtterance(text.replace(/[*#]/g, ""));
    utterance.rate = audioSpeechRate;
    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = () => setIsSpeaking(false);
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(utterance);
    setIsSpeaking(true);
  };

  const handleSendBotMessage = async (text, attachments = []) => {
    const prompt = (text || botInputText || "").trim();
    if (!prompt || botLoading) return;
    setBotInputText("");
    setBotLoading(true);
    setAvatarState("thinking");
    setChatMessages((prev) => [...prev, { sender: "user", text: prompt }]);
    try {
      const result = await queryHuggingFaceAgriBot(prompt, lang, selectedHfModel, attachments);
      setChatMessages((prev) => [...prev, { sender: "bot", text: result?.text || "I could not generate a response right now.", source: result?.source || "Agri Nirvana AI" }]);
    } catch (error) {
      setChatMessages((prev) => [...prev, { sender: "bot", text: "I couldn't complete that request. Please try again.", source: "Agri Nirvana" }]);
    } finally {
      setBotLoading(false);
      setAvatarState("idle");
    }
  };

  const totalN_kg = (calcAcres * 50) * (soilN === "low" ? 1.25 : soilN === "high" ? 0.75 : 1);
  const totalK_kg = calcAcres * 40;
  const dapBags = Math.max(0, Math.round((calcAcres * 30) / 50));
  const nitrogenFromDap = dapBags * 50 * 0.18;
  const remainingN = Math.max(0, totalN_kg - nitrogenFromDap);
  const ureaBags = Math.round((remainingN / 0.46) / 50);
  const mopBags = Math.round((totalK_kg / 0.60) / 50);

  const estimatedCostINR = Math.round(ureaBags * 266 + dapBags * 1350 + mopBags * 1700);

  const filteredKaggleVegs = KAGGLE_VEGETABLE_PRICES.filter((item) => {
    const matchesCategory = vegCategoryFilter === "All" || item.category === vegCategoryFilter;
    const matchesSearch = item.crop.toLowerCase().includes(vegSearchQuery.toLowerCase()) ||
                          item.mandi.toLowerCase().includes(vegSearchQuery.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  const filteredProducts = AGRI_PRODUCTS.filter((p) => {
    if (selectedProductCategory === "all") return true;
    return p.category.toLowerCase().includes(selectedProductCategory.toLowerCase());
  });

  const bestMandiItem = MANDI_PRICES_FEED.find((m) => m.isBestPrice) || MANDI_PRICES_FEED[0];

  return (
    <div className={`min-h-screen font-sans transition-colors duration-500 ${
      isLandingPage
        ? "agri-landing-light text-slate-900"
        : theme === "monochrome"
        ? "ai-mesh-bg-monochrome text-white"
        : theme === "cyber"
        ? "ai-mesh-bg-dark text-slate-100"
        : theme === "harvest"
        ? "ai-mesh-bg-harvest text-slate-900"
        : "ai-mesh-bg-botanical text-slate-900"
    } selection:bg-emerald-500 selection:text-white`}>
      
      {/* 1. TOP TELEMETRY RIBBON */}
      <TelemetryRibbon isDark={isDark} selectedModel={selectedHfModel} />

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
            theme === "botanical" ? "cyber" :
            theme === "cyber" ? "monochrome" :
            theme === "monochrome" ? "harvest" : "botanical"
          );
          setTheme(newTheme);
          const themeLabels = {
            botanical: "Botanical Glass (Apple / Stripe AgTech)",
            cyber: "Cyber Obsidian (MiniMax AI)",
            monochrome: "Monochrome Noir (Black & White Minimalist)",
            harvest: "Golden Harvest (Anthropic Claude)"
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
        onOpenPricing={() => setActiveNav("pricing")}
        onOpenCommandPalette={() => setIsCommandPaletteOpen(true)}
      />

      {/* GLOBAL ⌘K COMMAND SPOTLIGHT PALETTE */}
      <CommandPaletteModal
        isOpen={isCommandPaletteOpen}
        onClose={() => setIsCommandPaletteOpen(false)}
        isDark={isDark}
        onSelectNav={(navId) => setActiveNav(navId)}
        onChangeTheme={(nextTheme) => {
          setTheme(nextTheme);
          showToast(`Theme updated to ${nextTheme.toUpperCase()}`);
        }}
      />

      {/* 3. HERO SECTION (Collapsible) */}
      {heroExpanded ? (
        <section className={`relative overflow-hidden border-b py-8 px-4 sm:px-6 transition-all duration-300 ${
          isLandingPage
            ? "border-slate-200 bg-white"
            : isDark
            ? "border-emerald-500/20 bg-gradient-to-b from-[#062419] via-[#041911] to-[#030705]"
            : "border-slate-200/70 bg-gradient-to-b from-emerald-50/90 via-teal-50/40 to-slate-50"
        }`}>
          <div className="relative mx-auto max-w-7xl grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
            <div className="lg:col-span-7 text-center lg:text-left space-y-4">
              <div className={`inline-flex items-center gap-2 rounded-full border px-3.5 py-1.5 text-xs font-bold backdrop-blur-md ${
                isDark
                  ? "border-emerald-500/40 bg-emerald-500/10 text-emerald-300 glow-emerald"
                  : "border-emerald-300 bg-white/80 text-emerald-900 shadow-sm"
              }`}>
                <Sparkles size={14} className="text-amber-400 animate-pulse" />
                <span>Next-Gen AgTech Intelligence • Free Open Access</span>
              </div>

              <h1 className={`text-3xl font-black tracking-tight sm:text-4xl lg:text-5xl ${
                isDark ? "ai-gradient-text" : "ai-gradient-text-light"
              }`}>
                Build. Think. Discover.
              </h1>
              <p className={`max-w-xl text-xs sm:text-sm leading-relaxed ${
                isDark ? "text-emerald-100/70" : "text-slate-600"
              }`}>
                {t.heroSub}
              </p>

              <div className="flex flex-wrap items-center justify-center lg:justify-start gap-3 pt-2">
                <button
                  onClick={() => setActiveNav("diag")}
                  className="rounded-2xl bg-gradient-to-r from-emerald-500 to-teal-400 px-6 py-3 text-xs font-black text-slate-950 shadow-lg glow-emerald hover:brightness-110 flex items-center gap-2 transition hover:scale-[1.02] active:scale-[0.98]"
                >
                  <Camera size={16} /> Run AI Leaf Diagnostics
                </button>
                <button
                  onClick={() => setActiveNav("sat")}
                  className={`rounded-2xl px-6 py-3 text-xs font-bold flex items-center gap-2 transition active:scale-[0.98] ${
                    isLandingPage
                      ? "border border-slate-300 bg-white text-emerald-800 shadow-sm hover:border-emerald-400 hover:bg-emerald-50"
                      : "border border-emerald-500/40 bg-emerald-500/10 text-emerald-300 hover:bg-emerald-500/20"
                  }`}
                >
                  <Layers size={16} /> Open 3D NDVI Terrain
                </button>
              </div>
            </div>

            <div className="lg:col-span-5 flex flex-col items-center justify-center">
              <div className={`relative rounded-3xl p-4 border transition-all ${
                isLandingPage
                  ? "border-slate-200 bg-white shadow-[0_20px_60px_rgba(15,23,42,0.10)]"
                  : isDark ? "border-emerald-500/30 bg-[#072017]/80 shadow-2xl glow-emerald" : "border-slate-200 bg-white/90 shadow-xl"
              }`}>
                <div className="flex items-center justify-between mb-1 px-2">
                  <span className="text-[11px] font-mono font-bold text-emerald-400 uppercase tracking-wider flex items-center gap-1.5">
                    <span className="h-2 w-2 rounded-full bg-emerald-400 animate-ping" />
                    Interactive 3D Crop Model
                  </span>
                  <span className="text-[10px] text-slate-400 font-mono">Three.js WebGL</span>
                </div>
                
                <Hero3DCropModel theme={theme} />

                <div className="mt-2 text-center text-[11px] font-mono text-slate-400">
                  Low-Poly Wheat Stalk • Auto-Rotating Three.js Render
                </div>
              </div>
            </div>
          </div>
        </section>
      ) : (
        <div className={`border-b py-2 px-4 transition-colors ${isDark ? "border-emerald-900/40 bg-[#061912]/60" : "border-slate-200 bg-emerald-50/50"}`}>
          <div className="mx-auto max-w-7xl flex items-center justify-between text-xs">
            <span className="font-bold text-emerald-500 flex items-center gap-1.5">
              <Sparkles size={14} /> 3D Agronomy Dashboard Active
            </span>
            <button
              onClick={() => setHeroExpanded(true)}
              className="text-xs font-bold text-emerald-600 hover:underline flex items-center gap-1"
            >
              <Maximize2 size={13} /> Expand 3D Hero
            </button>
          </div>
        </div>
      )}

      {/* Main Content Area */}
      <main className="mx-auto max-w-7xl px-4 py-6 sm:px-6">
        {/* Mobile Navigation Bar */}
        <div className="flex xl:hidden overflow-x-auto gap-2 mb-6 pb-2 no-scrollbar">
          {[
            { id: "workspace", label: "Workspace", icon: Bot, badge: "AI Core" },
            { id: "diag", label: t.navDiag, icon: Leaf },
            { id: "sat", label: t.navSat, icon: Layers },
            { id: "map", label: t.navMap, icon: Radar, badge: "GIS" },
            { id: "analytics", label: t.navAnalytics, icon: LineChart },
            { id: "calc", label: t.navCalc, icon: Calculator },
            { id: "mandi", label: t.navMandi, icon: TrendingUp },
            { id: "market", label: t.navMarket, icon: ShoppingCart },
            { id: "pricing", label: t.navPricing, icon: Zap },
          ].map(({ id, label, icon: Icon, badge }) => (
            <button
              key={id}
              onClick={() => setActiveNav(id)}
              className={`flex shrink-0 items-center gap-2 rounded-xl px-3.5 py-2.5 text-xs font-bold transition ${
                activeNav === id || (activeNav === "bot" && id === "workspace")
                  ? isDark ? "bg-emerald-500 text-slate-950 shadow-md glow-emerald font-black" : "bg-emerald-600 text-white shadow-md font-black"
                  : isDark
                    ? "border border-emerald-900/60 bg-emerald-950/60 text-slate-300"
                    : "border border-slate-200 bg-white text-slate-600 shadow-xs"
              }`}
            >
              <Icon size={14} />
              {label}
              {badge && <span className="rounded bg-amber-400/20 text-amber-400 px-1 text-[9px] font-mono">{badge}</span>}
            </button>
          ))}
        </div>

        {/* SECTION: 3D HOLOGRAPHIC AI WORKSPACE (Default Main Studio) */}
        {(activeNav === "workspace" || activeNav === "bot") && (
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
              isThinking={botLoading}
              isDark={isDark}
              isPlayingAudio={isSpeaking}
              onPlayAudio={(text) => handleSpeechToggle(text)}
            />

            {/* Quick Dashboard Diagnostic Trigger Card */}
            <div className="mt-8">
              <DashboardDiagnosticCard
                onOpenDiagnostics={() => setActiveNav("diag")}
                isDark={isDark}
              />
            </div>
          </div>
        )}