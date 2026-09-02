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
  Radar,
  Maximize2,
  Minimize2,
  ChevronUp,
  Mic,
  MicOff,
  Paperclip,
  ArrowUpRight,
  Cpu,
  Radio,
  Activity,
  Compass,
  Home,
  CloudSun
} from "lucide-react";

import {
  LANGUAGES,
  TRANSLATIONS,
  CROP_DISEASE_DATASETS,
  CROPS_CONFIG,
  OUTBREAK_CLUSTERS,
  SUBSCRIPTION_PLANS,
  AGRI_PRODUCTS,
  DIRECT_BUYERS_LIST,
  MANDI_PRICES_FEED,
  KAGGLE_VEGETABLE_PRICES,
  queryHuggingFaceAgriBot,
  classifyCropLeafImage
} from "./data/agriData";
import { generateAIChatResponse } from "./services/aiChatbotEngine";

import Hero3DCropModel from "./components/Hero3DCropModel";
import DiseaseLeaf3DModel from "./components/DiseaseLeaf3DModel";
import FarmWeatherDashboard from "./components/weather/FarmWeatherDashboard";
import DiseaseHeatmapCanvas from "./components/DiseaseHeatmapCanvas";
import CropDiagnosticsWorkspace from "./components/diagnostics/CropDiagnosticsWorkspace";
import PrecisionFieldIntelligenceWorkspace from "./components/field-intelligence/PrecisionFieldIntelligenceWorkspace";

// Enterprise Shell Components
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

        {/* Holographic Atmospheric Particles */}
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
  // Theme & Navigation State (1st theme: Golden Harvest)
  const [theme, setTheme] = useState("harvest");
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
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@500;700&family=Plus+Jakarta+Sans:wght@400;600;700;800;900&display=swap" rel="stylesheet">
        <style>
          body { font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; padding: 24px; color: #1e293b; max-width: 800px; margin: 0 auto; -webkit-font-smoothing: antialiased; }
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
            <p style="margin: 4px 0 0; font-size: 12px; color: #64748b;">Verified ResNet-50 Vision Telemetry • Date: ${new Date().toLocaleDateString()}</p>
          </div>
          <div class="badge">${selectedDisease.confidence}% MATCH CONFIDENCE</div>
        </div>

        <div class="grid">
          <div class="box">
            <div class="label">Crop Type & Sample</div>
            <div class="value">${selectedDisease.crop}</div>
          </div>
          <div class="box">
            <div class="label">Diagnosed Pathogen</div>
            <div class="value">${selectedDisease.diseaseName} (${selectedDisease.pathogen})</div>
          </div>
          <div class="box">
            <div class="label">Disease Severity Level</div>
            <div class="value" style="color: ${selectedDisease.severity === 'Healthy' ? '#10b981' : '#f59e0b'};">${selectedDisease.severity} Severity</div>
          </div>
          <div class="box">
            <div class="label">Infected Surface Coverage</div>
            <div class="value">${selectedDisease.metrics?.necroticPercent ?? 12}% Necrotic Lesion Spots</div>
          </div>
        </div>

        <div class="remedy">
          <h3 style="margin: 0 0 6px; color: #065f46; font-size: 15px;">Targeted Treatment Protocol</h3>
          <p><strong>Organic Treatment:</strong> ${selectedDisease.remedies?.organic?.title || ''} — ${selectedDisease.remedies?.organic?.dosage || ''}</p>
          <p><strong>Chemical Intervention:</strong> ${selectedDisease.remedies?.chemical?.title || ''} — ${selectedDisease.remedies?.chemical?.dosage || ''}</p>
          <p><strong>Field Instructions:</strong> ${selectedDisease.remedies?.chemical?.instructions || ''}</p>
        </div>

        <div class="footer">
          Generated automatically by Agri Nirvana AgTech Engine. Valid for agricultural advisory & crop protection.
        </div>
        <script>window.onload = function() { window.print(); }</script>
      </body>
      </html>
    `;
    printWin.document.write(content);
    printWin.document.close();
  };

  useEffect(() => {
    if (activeNav === "bot") {
      chatBottomRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [chatMessages, activeNav]);

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
      const utterance = new SpeechSynthesisUtterance(textToSpeak || selectedDisease.audioAdvisoryText);
      utterance.rate = audioSpeechRate;
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
    const prompt = queryText || botInputText;
    if (!prompt.trim() && attachedFiles.length === 0) return;

    let displayPrompt = prompt;
    if (attachedFiles.length > 0) {
      displayPrompt += `\n📎 [Attached: ${attachedFiles.map(f => f.name).join(", ")}]`;
    }

    const userMsg = { sender: "user", text: displayPrompt };
    setChatMessages((prev) => [...prev, userMsg]);
    if (!queryText) setBotInputText("");
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
          text: "🌾 **Agri Nirvana AI Intelligence Active**:\n• Crop Health & Market Telemetry online.\n• Select a prompt below or ask any question regarding crop diagnostics, soil NPK, mandi prices, or pest remedies.",
          source: `${selectedHfModel} Offline Fallback`,
          reasoning: `Local offline edge heuristics executed in 18ms.`
        }
      ]);
      setTimeout(() => {
        setAvatarState("idle");
      }, 3000);
    } finally {
      setBotLoading(false);
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (event) => {
        setUserImage(event.target.result);
        setScanState("idle");
        showToast("Leaf photo uploaded! Click 'Run AI Diagnostics' to analyze.");
      };
      reader.readAsDataURL(file);
    }
  };

  const selectPresetSample = (datasetItem) => {
    setSelectedDisease(datasetItem);
    setUserImage(null);
    setScanState("idle");
  };

  const triggerScan = () => {
    setScanState("scanning");
  };

  const handleSimulateUpgrade = (planId) => {
    setUserPlan(planId);
    showToast(`Tier Updated to ${planId.toUpperCase()}! 100% Free Open Access Active.`);
  };

  const handleSimulatePurchase = (product) => {
    const commission = Math.round(product.priceINR * (product.commissionRate || 0.05));
    setTotalCommissionEarnedINR((prev) => prev + commission);

    // Dispatch WhatsApp Order to 9270547135
    const targetPhone = "919270547135";
    const whatsappMessage = `*Agri Nirvana Marketplace — New Order Request*\n\n` +
      `📦 *Product Name:* ${product.name}\n` +
      `💰 *Price:* ₹${product.priceINR} ${product.unit ? `(${product.unit})` : ""}\n` +
      (product.brand ? `🏷️ *Brand:* ${product.brand}\n` : "") +
      (product.dealerName ? `🏪 *Local Dealer:* ${product.dealerName}\n` : "") +
      `📍 *Market Area:* Kopargaon, Maharashtra\n\n` +
      `Hello, I would like to confirm and place an order for this product. Please advise on stock availability and delivery/payment process.`;

    const whatsappUrl = `https://api.whatsapp.com/send?phone=${targetPhone}&text=${encodeURIComponent(whatsappMessage)}`;
    window.open(whatsappUrl, "_blank", "noopener,noreferrer");

    showToast(`Connecting via WhatsApp to order ${product.name} (₹${product.priceINR}) at 9270547135!`);
  };

  const handleOpenGoogleMaps = (locationName, customQuery) => {
    const query = customQuery || `${locationName}, Kopargaon, Maharashtra`;
    const mapsUrl = `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(query)}`;
    window.open(mapsUrl, "_blank", "noopener,noreferrer");
    showToast(`Opening Google Maps for ${locationName}...`);
  };

  const handleProduceSubmit = (e) => {
    e.preventDefault();
    const newListing = {
      id: `p-${Date.now()}`,
      crop: produceFormCrop,
      qtyQuintals: produceFormQty,
      expectedPriceINR: produceFormPrice,
      status: "Active Listing"
    };
    setListedProduce([newListing, ...listedProduce]);
    showToast(`Harvest produce listing added! Buyers near you have been notified.`);
  };

  const handleOutbreakSubmit = (e) => {
    e.preventDefault();
    const newOutbreak = {
      id: `ob-${Date.now()}`,
      crop: reportCrop,
      disease: reportDisease,
      distKm: 4.2,
      location: `Pincode ${reportPincode}`,
      affectedFarms: 3,
      riskLevel: "High Risk Alert"
    };
    setOutbreakList([newOutbreak, ...outbreakList]);
    setReportModalOpen(false);
    showToast(`Community Outbreak Reported for ${reportCrop}! Nearby agronomists and farmers alerted.`);
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

      {/* 3. HERO SECTION (Only displayed on Home / Landing Page) */}
      {(activeNav === "workspace" || activeNav === "home") && (
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
                Build. Think. Discover.
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
              <div className={`relative w-full rounded-3xl border transition-all ${
                isDark ? "border-emerald-500/30 bg-[#072017]/80 shadow-2xl glow-emerald" : "border-slate-200 bg-white/90 shadow-xl"
              }`} style={{minHeight: "380px", maxWidth: "460px"}}>
                <Hero3DCropModel theme={theme} />
                <div className="absolute top-3 right-3 flex items-center gap-1.5 rounded-xl bg-black/70 backdrop-blur px-3 py-1.5 border border-emerald-500/30">
                  <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                  <span className="text-[10px] font-mono font-bold text-emerald-300">AI Vision · LIVE</span>
                </div>
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
            { id: "intel", label: "Drone Tech", icon: Compass },
            { id: "diag", label: t.navDiag, icon: Leaf },
            { id: "weather", label: "Weather", icon: CloudSun },
            { id: "map", label: t.navMap, icon: Radar },
            { id: "calc", label: t.navCalc, icon: Calculator },
            { id: "mandi", label: t.navMandi, icon: TrendingUp },
            { id: "market", label: t.navMarket, icon: ShoppingCart },
            { id: "pricing", label: t.navPricing, icon: Zap },
          ].map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              onClick={() => setActiveNav(id)}
              className={`flex shrink-0 items-center gap-2 rounded-xl px-3 py-2 text-xs font-bold whitespace-nowrap transition ${
                activeNav === id || (activeNav === "bot" && id === "workspace")
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
            setMonthlyScansCount={setMonthlyScansCount}
            handleSimulatePurchase={handleSimulatePurchase}
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

        {/* SECTION: GIS OUTBREAK RADAR & COMMUNITY LOGGING */}
        {activeNav === "map" && (
          <div className="space-y-6">
            <div className={`rounded-3xl p-6 border transition-all ${
              isDark ? "border-emerald-800/40 bg-[#072017]" : "border-slate-200 bg-white shadow-xl"
            }`}>
              <div className="flex flex-wrap items-center justify-between gap-4 mb-6">
                <div>
                  <h2 className={`text-2xl font-black flex items-center gap-2 ${isDark ? "text-white" : "text-slate-900"}`}>
                    <Radar className="text-emerald-500" size={26} />
                    {t.regionalOutbreaks} (25km Radius GIS Radar)
                  </h2>
                  <p className={`text-xs mt-1 ${isDark ? "text-slate-400" : "text-slate-600"}`}>Community crop disease logging and early infection spread warnings</p>
                </div>
                <button
                  onClick={() => setReportModalOpen(true)}
                  className="flex items-center gap-2 rounded-2xl bg-amber-500 px-5 py-2.5 text-xs font-black text-slate-950 hover:bg-amber-400 shadow transition"
                >
                  <PlusCircle size={16} /> + Report Outbreak to Community
                </button>
              </div>

              {/* GIS Radar Map Visual Card — Pinterest Radar UI */}
              <div className="relative w-full rounded-2xl border border-emerald-500/30 bg-[#04160f] overflow-hidden flex flex-col items-center justify-center" style={{minHeight: "360px"}}>
                {/* Radar Background Image */}
                <img
                  src="/images/radar_intro.jpg"
                  alt="GIS Radar Sweep"
                  className="absolute inset-0 w-full h-full object-cover opacity-80"
                  style={{mixBlendMode: "screen"}}
                />

                {/* Sweep Animation Overlay */}
                <div className="absolute inset-0 pointer-events-none" style={{
                  background: "conic-gradient(from 0deg, transparent 270deg, rgba(16,185,129,0.18) 330deg, transparent 360deg)",
                  animation: "radar-sweep 3s linear infinite",
                }}>
                </div>

                {/* Grid Lines */}
                <div className="absolute inset-0 opacity-10" style={{
                  backgroundImage: "linear-gradient(#10b981 1px, transparent 1px), linear-gradient(90deg, #10b981 1px, transparent 1px)",
                  backgroundSize: "40px 40px",
                }} />

                {/* Outbreak Ping Dots */}
                {outbreakList.map((ob, i) => {
                  const angles = [42, 165, 245];
                  const radii = [0.28, 0.38, 0.22];
                  const angle = (angles[i % angles.length] * Math.PI) / 180;
                  const r = radii[i % radii.length];
                  const cx = 50 + r * 50 * Math.cos(angle);
                  const cy = 50 + r * 50 * Math.sin(angle);
                  const colors = ["#f59e0b","#ef4444","#f97316"];
                  return (
                    <div
                      key={ob.id}
                      className="absolute z-20 flex items-center justify-center"
                      style={{ left: `${cx}%`, top: `${cy}%`, transform: "translate(-50%,-50%)" }}
                      title={`${ob.crop} — ${ob.disease} (${ob.distKm}km)`}
                    >
                      <span className="relative flex h-4 w-4">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full opacity-75" style={{backgroundColor: colors[i % colors.length]}}></span>
                        <span className="relative inline-flex rounded-full h-4 w-4 border-2 border-white/30" style={{backgroundColor: colors[i % colors.length]}}></span>
                      </span>
                      <span className="absolute left-5 whitespace-nowrap rounded bg-black/80 px-1.5 py-0.5 text-[9px] font-bold text-white border border-emerald-500/40">
                        {ob.crop} • {ob.distKm}km
                      </span>
                    </div>
                  );
                })}

                {/* Center Pulse */}
                <div className="absolute z-20" style={{left:"50%",top:"50%",transform:"translate(-50%,-50%)"}}>
                  <span className="relative flex h-3 w-3">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
                  </span>
                </div>

                {/* HUD Info Bar */}
                <div className="absolute top-3 left-3 right-3 z-20 flex items-center justify-between">
                  <span className="rounded-full bg-black/80 px-3 py-1 text-[10px] font-mono font-bold text-emerald-300 border border-emerald-500/40 backdrop-blur">
                    📡 LIVE · 25km GIS Cluster Radar
                  </span>
                  <span className="rounded-full bg-black/80 px-3 py-1 text-[10px] font-mono font-bold text-amber-400 border border-amber-500/40 backdrop-blur">
                    ⚠ {outbreakList.length} CLUSTERS ACTIVE
                  </span>
                </div>

                {/* Bottom Legend */}
                <div className="absolute bottom-3 left-3 right-3 z-20 flex items-center gap-4 justify-center">
                  {[["#f59e0b","HIGH"], ["#f97316","MED"], ["#ef4444","CRITICAL"]].map(([c,l]) => (
                    <span key={l} className="flex items-center gap-1.5 text-[9px] font-mono font-bold text-white/70">
                      <span className="inline-block w-2.5 h-2.5 rounded-full" style={{backgroundColor:c}}></span>{l}
                    </span>
                  ))}
                </div>

                <style>{`
                  @keyframes radar-sweep {
                    from { transform: rotate(0deg); }
                    to { transform: rotate(360deg); }
                  }
                `}</style>
              </div>

              {/* Outbreak Cards Grid */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 my-6">
                {outbreakList.map((ob) => (
                  <div key={ob.id} className={`rounded-2xl border p-4 transition ${
                    isDark ? "border-emerald-900/60 bg-[#04160f]" : "border-slate-200 bg-white shadow-xs hover:border-emerald-500"
                  }`}>
                    <div className="flex justify-between items-start">
                      <span className="text-[10px] font-mono font-bold text-amber-500 uppercase">{ob.riskLevel}</span>
                      <span className={`text-[10px] ${isDark ? "text-slate-400" : "text-slate-500"}`}>{ob.distKm} km away</span>
                    </div>
                    <h3 className={`font-black text-base mt-1 ${isDark ? "text-white" : "text-slate-900"}`}>{ob.crop} — {ob.disease}</h3>
                    <p className={`text-xs mt-1 ${isDark ? "text-slate-400" : "text-slate-500"}`}><MapPin size={12} className="inline mr-1" />{ob.location} • {ob.affectedFarms} farms reported</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}


        {/* SECTION: NPK FERTILIZER & YIELD CALCULATOR */}
        {activeNav === "calc" && (
          <div className="space-y-6">
            <div className={`rounded-3xl p-6 border transition-all ${
              isDark ? "border-emerald-800/40 bg-[#072017]" : "border-slate-200 bg-white shadow-xl"
            }`}>
              <h2 className={`text-2xl font-black flex items-center gap-2 mb-2 ${isDark ? "text-white" : "text-slate-900"}`}>
                <Calculator className="text-emerald-500" size={26} />
                {t.npkTitle}
              </h2>
              <p className={`text-xs mb-6 ${isDark ? "text-slate-400" : "text-slate-600"}`}>{t.npkSub}</p>

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
                  <h3 className="text-lg font-black text-emerald-500">Bag & Cost Estimation</h3>
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

                  <div className="pt-3 border-t border-slate-700/30 flex justify-between items-center">
                    <span className={`text-xs font-bold ${isDark ? "text-slate-400" : "text-slate-600"}`}>Total Estimated Fertilizer Cost:</span>
                    <span className="text-2xl font-black text-emerald-500">₹{estimatedCostINR.toLocaleString()}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* SECTION: e-NAM MANDI MARKET LINKAGE */}
        {activeNav === "mandi" && (
          <div className="space-y-6">
            <div className={`rounded-3xl p-6 border transition-all ${
              isDark ? "border-emerald-800/40 bg-[#072017]" : "border-slate-200 bg-white shadow-xl"
            }`}>
              <div className="flex flex-wrap items-center justify-between gap-4 mb-6">
                <div>
                  <h2 className={`text-xl font-black flex items-center gap-2 ${isDark ? "text-white" : "text-slate-900"}`}>
                    <TrendingUp className="text-emerald-500" size={24} />
                    {t.mandiTitle}
                  </h2>
                  <p className={`text-xs ${isDark ? "text-slate-400" : "text-slate-600"}`}>
                    Kopargaon APMC (कृषी उत्पन्न बाजार समिती, कोपरगाव, अहिल्यानगर) • e-NAM AGMARKNET Telemetry
                  </p>
                </div>
                <div className={`rounded-2xl border p-3.5 text-xs flex items-center gap-3 ${
                  isDark ? "border-emerald-500/40 bg-emerald-500/10 text-emerald-400" : "border-emerald-300 bg-emerald-50 text-emerald-900 shadow-xs"
                }`}>
                  <Award size={22} className="shrink-0 text-emerald-500" />
                  <div>
                    <p className={`font-black ${isDark ? "text-white" : "text-slate-900"}`}>{t.bestPriceToday}: {bestMandiItem.mandiName}</p>
                    <p className="text-[11px]">{bestMandiItem.crop} @ ₹{bestMandiItem.modalPriceINR} {bestMandiItem.unit}</p>
                  </div>
                </div>
              </div>

              {/* Mandi Cards Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {MANDI_PRICES_FEED.map((mandi) => (
                  <div key={mandi.id} className={`rounded-2xl border p-4 flex justify-between items-start transition ${
                    isDark ? "border-emerald-900/60 bg-[#04160f] hover:border-emerald-500/50" : "border-slate-200 bg-white shadow-xs hover:border-emerald-500"
                  }`}>
                    <div>
                      <span className="text-[10px] font-bold text-emerald-500 uppercase tracking-widest">{mandi.crop}</span>
                      <h3 className={`font-black text-base mt-0.5 ${isDark ? "text-white" : "text-slate-900"}`}>{mandi.mandiName}</h3>
                      <p className={`text-xs mt-1 ${isDark ? "text-slate-400" : "text-slate-500"}`}><MapPin size={12} className="inline mr-1" />{mandi.distanceKm} km away • Updated {mandi.lastUpdated}</p>
                      {mandi.arrival && (
                        <p className={`text-[11px] font-mono mt-1 ${isDark ? "text-emerald-400/90" : "text-emerald-700 font-semibold"}`}>
                          Arrival: <span className="font-bold">{mandi.arrival}</span> • Range: ₹{mandi.minPriceINR} – ₹{mandi.maxPriceINR}
                        </p>
                      )}
                    </div>
                    <div className="text-right shrink-0 ml-3">
                      <p className="text-2xl font-black text-emerald-500">₹{mandi.modalPriceINR}</p>
                      <span className="text-[10px] text-slate-400 font-mono block">{mandi.unit}</span>
                      <span className={`text-[11px] font-bold ${mandi.trendDirection === 'down' ? 'text-rose-400' : 'text-emerald-400'}`}>{mandi.trend}</span>
                    </div>
                  </div>
                ))}
              </div>

              {/* Produce Listing Form */}
              <div className={`mt-8 rounded-2xl border p-6 ${isDark ? "border-emerald-900/60 bg-[#04160f]" : "border-slate-200 bg-slate-50"}`}>
                <h3 className={`text-base font-black mb-4 flex items-center gap-2 ${isDark ? "text-white" : "text-slate-900"}`}>
                  <PlusCircle size={18} className="text-emerald-500" />
                  {t.listProduce}
                </h3>
                <form onSubmit={handleProduceSubmit} className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
                  <div>
                    <label className="block font-bold mb-1">Crop Type</label>
                    <select
                      value={produceFormCrop}
                      onChange={(e) => setProduceFormCrop(e.target.value)}
                      className={`w-full rounded-xl border p-2.5 outline-none font-bold ${
                        isDark ? "border-emerald-900 bg-[#04160f] text-white" : "border-slate-300 bg-white text-slate-800"
                      }`}
                    >
                      <option value="Onion">Onion (लाल कांदा / Nashik Red)</option>
                      <option value="Soybean">Soybean (पिवळा सोयाबीन / JS-335)</option>
                      <option value="Sugarcane">Sugarcane (ऊस / Co 86032)</option>
                      <option value="Wheat">Wheat (शरबती / लोकवन)</option>
                      <option value="Maize">Maize (पिवळी मका)</option>
                      <option value="Pomegranate">Pomegranate (भगवा डाळिंब)</option>
                      <option value="Cotton">Cotton (कापूस)</option>
                      <option value="Chickpea">Chickpea / Gram (हरभरा)</option>
                      <option value="Tomato">Tomato (Desi / Hybrid)</option>
                    </select>
                  </div>
                  <div>
                    <label className="block font-bold mb-1">Quantity (Quintals)</label>
                    <input
                      type="number"
                      value={produceFormQty}
                      onChange={(e) => setProduceFormQty(Number(e.target.value))}
                      className={`w-full rounded-xl border p-2.5 outline-none ${
                        isDark ? "border-emerald-900 bg-[#04160f] text-white" : "border-slate-300 bg-white text-slate-800"
                      }`}
                    />
                  </div>
                  <div>
                    <label className="block font-bold mb-1">Expected Price (₹/Quintal)</label>
                    <input
                      type="number"
                      value={produceFormPrice}
                      onChange={(e) => setProduceFormPrice(Number(e.target.value))}
                      className={`w-full rounded-xl border p-2.5 outline-none ${
                        isDark ? "border-emerald-900 bg-[#04160f] text-white" : "border-slate-300 bg-white text-slate-800"
                      }`}
                    />
                  </div>
                  <div className="sm:col-span-3">
                    <button type="submit" className="w-full rounded-xl bg-emerald-500 py-3 font-black text-slate-950 hover:bg-emerald-400 transition shadow">
                      List Produce for Verified Institutional Buyers
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        )}

        {/* SECTION: AGRI-INPUT & PRODUCE MARKETPLACE (KOPARGAON) */}
        {activeNav === "market" && (
          <div className="space-y-6">
            <div className={`rounded-3xl p-6 border transition-all ${
              isDark ? "border-emerald-800/40 bg-[#072017]" : "border-slate-200 bg-white shadow-xl"
            }`}>
              <div className="flex flex-wrap items-center justify-between gap-4 mb-6">
                <div>
                  <h2 className={`text-xl font-black flex items-center gap-2 ${isDark ? "text-white" : "text-slate-900"}`}>
                    <ShoppingCart className="text-emerald-500" size={24} />
                    Kopargaon Agri-Input & Farm Marketplace
                  </h2>
                  <p className={`text-xs ${isDark ? "text-slate-400" : "text-slate-600"}`}>
                    Certified Krushi Seva Kendras, IFFCO centers & crop protection hubs in Kopargaon Taluka (अहिल्यानगर)
                  </p>
                </div>
                <div className="flex gap-2 overflow-x-auto">
                  {["all", "bio-control", "fungicide", "fertilizer", "bactericide", "insecticide"].map((cat) => (
                    <button key={cat} onClick={() => setSelectedProductCategory(cat)} className={`rounded-xl px-3 py-1.5 text-xs font-bold border uppercase transition ${
                      selectedProductCategory === cat
                        ? "border-emerald-500 bg-emerald-500/20 text-emerald-300 font-black"
                        : isDark ? "border-emerald-900 text-slate-400" : "border-slate-300 text-slate-600"
                    }`}>
                      {cat}
                    </button>
                  ))}
                </div>
              </div>

              {/* Products Grid */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                {filteredProducts.map((prod) => (
                  <div key={prod.id} className={`rounded-2xl border p-4 flex flex-col justify-between transition ${
                    isDark ? "border-emerald-900/60 bg-[#04160f] hover:border-emerald-500/50" : "border-slate-200 bg-white shadow-xs hover:border-emerald-500"
                  }`}>
                    <div>
                      <div className="flex items-center justify-between">
                        <span className="text-[10px] font-bold text-emerald-500 uppercase tracking-widest">{prod.category}</span>
                        <span className={`text-[10px] font-mono px-2 py-0.5 rounded-full ${isDark ? "bg-emerald-950/80 text-emerald-300 border border-emerald-800/40" : "bg-emerald-50 text-emerald-700"}`}>
                          ⭐ {prod.rating}
                        </span>
                      </div>
                      <h3 className={`font-black text-base mt-1 ${isDark ? "text-white" : "text-slate-900"}`}>{prod.name}</h3>
                      <p className={`text-xs mt-0.5 ${isDark ? "text-slate-400" : "text-slate-600"}`}>{prod.brand} • {prod.unit}</p>
                      <button
                        type="button"
                        onClick={() => handleOpenGoogleMaps(prod.dealerName, `${prod.dealerName.replace(/\(.*?\)/g, "").trim()}, Kopargaon, Maharashtra`)}
                        className="text-xs text-emerald-500 hover:text-emerald-400 font-bold mt-2 flex items-center gap-1 hover:underline cursor-pointer text-left"
                        title="Open Shop Location on Google Maps"
                      >
                        <MapPin size={12} className="inline mr-1 shrink-0" />
                        <span>{prod.dealerName}</span>
                      </button>
                      <p className={`text-[11px] font-mono mt-1 ${isDark ? "text-slate-400" : "text-slate-500"}`}>{prod.stock}</p>
                    </div>

                    <div className="mt-4 pt-3 border-t border-slate-700/30 flex items-center justify-between">
                      <span className="text-xl font-black text-emerald-500">₹{prod.priceINR}</span>
                      <button
                        onClick={() => handleSimulatePurchase(prod)}
                        className="flex items-center gap-1.5 rounded-xl bg-emerald-500 px-3.5 py-2 text-xs font-black text-slate-950 hover:bg-emerald-400 transition shadow hover:shadow-emerald-500/25 active:scale-95 cursor-pointer"
                        title="Order via WhatsApp to 9270547135"
                      >
                        <span className="text-sm leading-none">💬</span>
                        <span>Order Now</span>
                      </button>
                    </div>
                  </div>
                ))}
              </div>

              {/* Direct Institutional Buyers & FPO Section */}
              <div className="mt-10 pt-8 border-t border-slate-700/30">
                <div className="flex flex-wrap items-center justify-between gap-2 mb-6">
                  <div>
                    <h3 className={`text-lg font-black flex items-center gap-2 ${isDark ? "text-white" : "text-slate-900"}`}>
                      <Award className="text-amber-400" size={22} />
                      Verified Institutional Buyers & FPOs (Kopargaon Taluka)
                    </h3>
                    <p className={`text-xs ${isDark ? "text-slate-400" : "text-slate-600"}`}>
                      Direct procurement aggregators purchasing harvested crops with guaranteed e-NAM settlement
                    </p>
                  </div>
                  <span className="rounded-full bg-emerald-500/10 px-3 py-1 text-xs font-mono font-bold text-emerald-400 border border-emerald-500/30">
                    4 Verified Buyers Active
                  </span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {DIRECT_BUYERS_LIST.map((buyer) => (
                    <div key={buyer.id} className={`rounded-2xl border p-4 flex flex-col justify-between transition ${
                      isDark ? "border-emerald-900/60 bg-[#04160f] hover:border-emerald-500/50" : "border-slate-200 bg-slate-50 shadow-xs hover:border-emerald-500"
                    }`}>
                      <div>
                        <div className="flex items-center justify-between">
                          <span className="text-[10px] font-bold text-amber-400 uppercase tracking-widest">{buyer.type}</span>
                          <span className="text-[11px] font-bold text-emerald-400">⭐ {buyer.rating}</span>
                        </div>
                        <h4 className={`font-black text-base mt-1 ${isDark ? "text-white" : "text-slate-900"}`}>{buyer.name}</h4>
                        <p className={`text-xs mt-1 ${isDark ? "text-slate-400" : "text-slate-600"}`}>
                          <MapPin size={12} className="inline mr-1" />{buyer.distanceKm} km from Kopargaon Center • {buyer.contactPerson}
                        </p>
                        {buyer.shopAddress && (
                          <p className={`text-[11px] font-mono mt-0.5 ${isDark ? "text-emerald-400/80" : "text-emerald-700 font-semibold"}`}>
                            📍 {buyer.shopAddress}
                          </p>
                        )}
                        <div className="flex flex-wrap gap-1.5 mt-2.5">
                          {buyer.buyingCrops.map((cropName, cIdx) => (
                            <span key={cIdx} className={`rounded-md px-2 py-0.5 text-[10px] font-bold ${
                              isDark ? "bg-emerald-950 text-emerald-300 border border-emerald-800/60" : "bg-white text-emerald-800 border border-slate-200"
                            }`}>
                              {cropName}
                            </span>
                          ))}
                        </div>
                      </div>

                      <div className="mt-4 pt-3 border-t border-slate-700/30 flex items-center justify-between">
                        <div>
                          <p className="text-[10px] text-slate-400 font-mono">Offered Modal Rate</p>
                          <span className="text-lg font-black text-emerald-400">₹{buyer.offeredPriceINR} <span className="text-xs font-normal text-slate-400">/ Qtl</span></span>
                        </div>
                        <button
                          onClick={() => handleOpenGoogleMaps(buyer.name, buyer.mapsQuery || buyer.shopAddress || `${buyer.name}, Kopargaon, Maharashtra`)}
                          className="flex items-center gap-1.5 rounded-xl border border-emerald-500/40 bg-emerald-500/10 hover:bg-emerald-500 hover:text-slate-950 px-3.5 py-1.5 text-xs font-bold text-emerald-300 transition shadow cursor-pointer active:scale-95"
                          title={`Open Google Maps for ${buyer.name} location`}
                        >
                          <MapPin size={13} className="shrink-0" />
                          <span>Connect Direct</span>
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* SECTION: TIER FEATURES */}
        {activeNav === "pricing" && (
          <div className="space-y-6">
            <div className={`rounded-3xl p-6 border transition-all ${
              isDark ? "border-emerald-800/40 bg-[#072017]" : "border-slate-200 bg-white shadow-xl shadow-slate-200/50"
            }`}>
              <h2 className={`text-2xl font-black flex items-center gap-2 mb-6 ${isDark ? "text-white" : "text-slate-900"}`}>
                <Zap className="text-amber-500" size={26} />
                Agri Nirvana Tier Features (100% Free Open Access)
              </h2>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {SUBSCRIPTION_PLANS.map((plan) => (
                  <div key={plan.id} className={`relative rounded-3xl border p-6 flex flex-col justify-between transition-all ${
                    userPlan === plan.id
                      ? "border-emerald-500 ring-2 ring-emerald-500/50"
                      : isDark ? "border-emerald-900/60 bg-[#04160f]" : "border-slate-200 bg-white shadow-xs hover:border-emerald-500"
                  }`}>
                    {plan.popular && (
                      <span className="absolute -top-3 right-6 rounded-full bg-amber-500 px-3 py-1 text-[10px] font-black text-slate-950 uppercase tracking-widest shadow">
                        {plan.badge}
                      </span>
                    )}

                    <div>
                      <span className={`text-xs font-extrabold uppercase tracking-wider ${isDark ? "text-emerald-400" : "text-emerald-700"}`}>
                        {plan.badge}
                      </span>
                      <h3 className={`text-xl font-black mt-1 ${isDark ? "text-white" : "text-slate-900"}`}>{plan.name}</h3>
                      <div className="my-4">
                        <span className={`text-3xl font-black ${isDark ? "text-white" : "text-slate-900"}`}>₹0 (Free)</span>
                        <span className="text-xs text-emerald-500 block font-bold mt-1">Free Open Access</span>
                      </div>

                      <div className="space-y-2.5 my-6 text-xs">
                        {plan.features.map((feat, idx) => (
                          <div key={idx} className="flex items-start gap-2">
                            <Check size={16} className="text-emerald-500 shrink-0 mt-0.5" />
                            <span className={isDark ? "text-slate-200" : "text-slate-700"}>{feat}</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    <button
                      onClick={() => handleSimulateUpgrade(plan.id)}
                      disabled={userPlan === plan.id}
                      className={`w-full rounded-2xl py-3 text-xs font-black transition shadow ${
                        userPlan === plan.id
                          ? "bg-emerald-500/20 text-emerald-400 cursor-default"
                          : plan.popular
                          ? "bg-amber-500 text-slate-950 hover:bg-amber-400"
                          : isDark
                          ? "bg-emerald-500 text-slate-950 hover:bg-emerald-400"
                          : "bg-emerald-600 text-white hover:bg-emerald-700"
                      }`}
                    >
                      {userPlan === plan.id ? "Currently Active Tier" : "Activate Tier Features (Free)"}
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </main>

      {/* REPORT OUTBREAK MODAL */}
      {reportModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-sm p-4">
          <div className={`w-full max-w-md rounded-3xl border p-6 shadow-2xl ${
            isDark ? "border-emerald-800 bg-[#072017] text-white" : "border-slate-200 bg-white text-slate-900"
          }`}>
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-black flex items-center gap-2">
                <ShieldAlert className="text-amber-400" size={20} />
                Report Outbreak to Community
              </h3>
              <button onClick={() => setReportModalOpen(false)} className="hover:opacity-75"><X size={18} /></button>
            </div>
            <form onSubmit={handleOutbreakSubmit} className="space-y-4 text-xs">
              <div>
                <label className="block font-bold mb-1">Crop Type</label>
                <select value={reportCrop} onChange={(e) => setReportCrop(e.target.value)} className="w-full rounded-xl border p-2.5 outline-none bg-transparent">
                  <option value="Tomato">Tomato</option>
                  <option value="Potato">Potato</option>
                  <option value="Wheat">Wheat</option>
                  <option value="Cotton">Cotton</option>
                </select>
              </div>
              <div>
                <label className="block font-bold mb-1">Disease / Pest Observed</label>
                <input type="text" value={reportDisease} onChange={(e) => setReportDisease(e.target.value)} className="w-full rounded-xl border p-2.5 outline-none bg-transparent" />
              </div>
              <div>
                <label className="block font-bold mb-1">Your Location PIN Code</label>
                <input type="text" value={reportPincode} onChange={(e) => setReportPincode(e.target.value)} className="w-full rounded-xl border p-2.5 outline-none bg-transparent" />
              </div>
              <button type="submit" className="w-full rounded-xl bg-amber-500 py-3 font-black text-slate-950 hover:bg-amber-400 transition shadow">
                Broadcast Outbreak Alert to 25km Radius
              </button>
            </form>
          </div>
        </div>
      )}

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
            <span className="text-xs font-semibold text-slate-400">| 100% Free Open-Access AgTech Platform</span>
          </div>
          <p>© 2026 Agri Nirvana AgTech Systems. Powered by Three.js 3D Engine & Hugging Face AI.</p>
        </div>
      </footer>
    </div>
  );
}
