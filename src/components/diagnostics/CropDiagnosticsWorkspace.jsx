import React, { useState, useEffect } from "react";
import { Sparkles, History, Cpu, FileText, ShoppingCart, UserCheck, Landmark, MessageSquare, Mic, Send, RotateCw, AlertTriangle, XCircle, RefreshCw } from "lucide-react";

import {
  fetchModelStatus,
  fetchSupportedCrops,
  analyzeCropImageApi,
  analyzeCropSymptomsApi,
  fetchDiagnosisHistoryApi,
  initFarmerSessionApi
} from "../../services/diagnosisApi";

import CropSelector from "./CropSelector";
import CropImageUploader from "./CropImageUploader";
import AnalysisProgressScreen from "./AnalysisProgressScreen";
import DiagnosisResultCard from "./DiagnosisResultCard";
import LowConfidenceNotice from "./LowConfidenceNotice";
import DiagnosisHistoryView from "./DiagnosisHistoryView";
import DiseaseLeaf3DModel from "../DiseaseLeaf3DModel";

import LiveCameraModal from "../LiveCameraModal";
import DosageCalculatorModal from "../DosageCalculatorModal";
import DroneMissionGeneratorModal from "../DroneMissionGeneratorModal";
import AgronomistDispatchModal from "../AgronomistDispatchModal";

export default function CropDiagnosticsWorkspace({
  lang = "en",
  theme = "dark",
  t = {},
  selectedField = null,
  showToast = () => {},
  setMonthlyScansCount = () => {},
  handleSimulatePurchase = () => {}
}) {
  const isDark = theme === "cyber" || theme === "dark" || theme === "monochrome";

  // Tab: "diagnostic" | "history"
  const [activeSubTab, setActiveSubTab] = useState("diagnostic");

  // Input Mode: "vision" | "symptoms"
  const [inputMode, setInputMode] = useState("vision");
  const [symptomText, setSymptomText] = useState("");

  // Crop & Image State
  const [crops, setCrops] = useState([
    { id: "Tomato", name: "Tomato (टोमॅटो)", icon: "🍅" },
    { id: "Potato", name: "Potato (बटाटा)", icon: "🥔" },
    { id: "Corn", name: "Maize / Corn (मका)", icon: "🌽" },
    { id: "Soybean", name: "Soybean (सोयाबीन)", icon: "🌱" },
    { id: "Grape", name: "Grapes (द्राक्षे)", icon: "🍇" },
    { id: "Apple", name: "Apple (सफरचंद)", icon: "🍎" },
    { id: "Pepper", name: "Bell Pepper (ढोबळी मिरची)", icon: "🫑" },
    { id: "Cotton", name: "Cotton (कापूस)", icon: "☁️" },
    { id: "Rice", name: "Paddy / Rice (भात)", icon: "🌾" },
    { id: "Onion", name: "Onion (कांदा)", icon: "🧅" }
  ]);
  const [selectedCrop, setSelectedCrop] = useState("Tomato");
  const [selectedFile, setSelectedFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);

  // Workflow State: "idle" | "analyzing" | "result" | "invalid_image" | "error"
  const [workflowState, setWorkflowState] = useState("idle");
  const [currentDiagnosis, setCurrentDiagnosis] = useState(null);
  const [modelStatus, setModelStatus] = useState(null);
  const [analysisError, setAnalysisError] = useState(null);

  // Modals
  const [isCameraModalOpen, setIsCameraModalOpen] = useState(false);
  const [isDosageModalOpen, setIsDosageModalOpen] = useState(false);
  const [isDroneModalOpen, setIsDroneModalOpen] = useState(false);
  const [isAgronomistModalOpen, setIsAgronomistModalOpen] = useState(false);

  useEffect(() => {
    initFarmerSessionApi("farmer_default");
    fetchModelStatus().then((res) => {
      if (res) setModelStatus(res);
    });
    fetchSupportedCrops().then((res) => {
      if (res && res.crops && res.crops.length > 0) setCrops(res.crops);
    });
  }, []);

  const handleImageSelected = (file, dataUrl) => {
    setSelectedFile(file);
    setImagePreview(dataUrl);
  };

  const handleClearImage = () => {
    setSelectedFile(null);
    setImagePreview(null);
    setWorkflowState("idle");
  };

  const handleLoadPresetSample = async (crop, samplePath, label) => {
    setSelectedCrop(crop);
    setImagePreview(samplePath);
    setWorkflowState("idle");
    setAnalysisError(null);
    try {
      const resp = await fetch(samplePath);
      if (resp.ok) {
        const blob = await resp.blob();
        const file = new File([blob], `sample_${crop.toLowerCase()}.jpg`, { type: blob.type || "image/jpeg" });
        setSelectedFile(file);
      }
    } catch (_) {
      setSelectedFile(null);
    }
    showToast(`Loaded ${label}`);
  };

  const handleRunAnalysis = () => {
    if (!imagePreview && inputMode === "vision") {
      showToast("Please upload or capture a crop leaf photo first.");
      return;
    }
    setWorkflowState("analyzing");
  };

  const handleSymptomDiagnosisSubmit = (e) => {
    if (e) e.preventDefault();
    if (!symptomText.trim()) {
      showToast("Please describe the visible crop symptoms.");
      return;
    }
    setWorkflowState("analyzing");
  };

  const handleAnalysisProgressComplete = async () => {
    try {
      setAnalysisError(null);
      let res;
      if (inputMode === "symptoms") {
        res = await analyzeCropSymptomsApi(symptomText, selectedCrop);
      } else {
        res = await analyzeCropImageApi(selectedFile, selectedCrop, imagePreview);
      }

      if (res && res.diagnosis) {
        const diag = res.diagnosis;
        setCurrentDiagnosis(diag);

        // Check if the image was rejected as non-crop
        if (diag.is_valid_crop_image === false && diag.status === "invalid_image") {
          setWorkflowState("invalid_image");
          showToast("Image rejected — not a crop/leaf photo.");
          return;
        }

        setWorkflowState("result");
        setMonthlyScansCount((c) => c + 1);

        // Save to local storage history
        try {
          const local = localStorage.getItem("agri_nirvana_diag_history");
          let list = local ? JSON.parse(local) : [];
          list = [diag, ...list.filter((x) => x.id !== diag.id)];
          localStorage.setItem("agri_nirvana_diag_history", JSON.stringify(list));
        } catch (e) {}

        showToast(`AI diagnosis completed for ${selectedCrop}!`);
      }
    } catch (err) {
      setAnalysisError(err.message || "Analysis failed. Is the backend running?");
      showToast(`Analysis error: ${err.message}`);
      setWorkflowState("error");
    }
  };

  return (
    <div className="space-y-6">
      {/* MODEL PROVIDER STATUS BANNER */}
      <div className={`rounded-2xl p-4 border flex flex-wrap items-center justify-between gap-3 text-xs ${
        isDark ? "border-emerald-800/40 bg-[#072017]" : "border-slate-200 bg-white shadow-sm"
      }`}>
        <div className="flex items-center gap-2">
          <Cpu className="text-emerald-400" size={18} />
          <span className="font-black text-emerald-300">
            ML Model Engine: {modelStatus?.model_name || "Kisan AI Dr. Agri Multimodal Vision"}
          </span>
          <span className="rounded-full bg-emerald-500/20 text-emerald-300 text-[10px] font-mono font-bold px-2 py-0.5 border border-emerald-500/30">
            {modelStatus?.model_version || "v2.5-prod"}
          </span>
        </div>

        <div className="flex items-center gap-2">
          {/* TAB SWITCHER: DIAGNOSTIC WORKSPACE VS MY HISTORY */}
          <button
            type="button"
            onClick={() => setActiveSubTab("diagnostic")}
            className={`px-3 py-1.5 rounded-xl font-bold transition flex items-center gap-1.5 ${
              activeSubTab === "diagnostic"
                ? "bg-emerald-600 text-white shadow-sm"
                : isDark ? "text-slate-400 hover:text-white" : "text-slate-600 hover:text-slate-900"
            }`}
          >
            <Sparkles size={14} /> Diagnostic Hub
          </button>
          <button
            type="button"
            onClick={() => setActiveSubTab("history")}
            className={`px-3 py-1.5 rounded-xl font-bold transition flex items-center gap-1.5 ${
              activeSubTab === "history"
                ? "bg-emerald-600 text-white shadow-sm"
                : isDark ? "text-slate-400 hover:text-white" : "text-slate-600 hover:text-slate-900"
            }`}
          >
            <History size={14} /> My Health History
          </button>
        </div>
      </div>

      {/* SUB-TAB 1: DIAGNOSTIC HUB */}
      {activeSubTab === "diagnostic" && (
        <div className="space-y-6">
          {workflowState === "analyzing" ? (
            <AnalysisProgressScreen
              crop={selectedCrop}
              onComplete={handleAnalysisProgressComplete}
              isDark={isDark}
            />
          ) : workflowState === "error" ? (
            /* ERROR STATE — Backend offline or request failed */
            <div className={`rounded-3xl border p-6 sm:p-8 space-y-5 text-left animate-fade-in ${
              isDark ? "border-rose-800/60 bg-[#1a0a0a] text-white shadow-2xl" : "border-rose-200 bg-rose-50 text-slate-900 shadow-xl"
            }`}>
              <div className="flex items-center gap-3">
                <div className="h-12 w-12 rounded-2xl bg-rose-500/20 text-rose-400 border border-rose-500/40 flex items-center justify-center shrink-0">
                  <XCircle size={28} />
                </div>
                <div>
                  <span className="text-[10px] font-black uppercase tracking-wider text-rose-400 bg-rose-500/20 px-2.5 py-0.5 rounded-full border border-rose-500/30">
                    Analysis Failed
                  </span>
                  <h3 className="text-xl font-black text-rose-200 mt-1">Could Not Complete Diagnosis</h3>
                </div>
              </div>
              <p className="text-xs text-rose-100/90 leading-relaxed">
                {analysisError || "An unexpected error occurred. Please ensure the backend server is running."}
              </p>
              <div className="rounded-2xl border border-rose-500/30 bg-black/30 p-4 text-xs text-slate-300">
                <p className="font-bold text-rose-300 mb-1">Troubleshooting:</p>
                <ul className="space-y-1 list-disc list-inside text-slate-400">
                  <li>Ensure the FastAPI backend is running: <code className="text-emerald-300">python -m uvicorn backend.main:app --reload</code></li>
                  <li>Check that ML dependencies are installed: <code className="text-emerald-300">pip install -r backend/requirements.txt</code></li>
                  <li>Verify <code className="text-emerald-300">VITE_API_BASE_URL</code> in .env points to the correct backend URL</li>
                </ul>
              </div>
              <div className="flex flex-wrap items-center gap-3">
                <button
                  type="button"
                  onClick={() => handleLoadPresetSample("Tomato", "/samples/sample_tomato_early_blight.jpg", "Tomato Early Blight Sample")}
                  className="flex items-center gap-2 rounded-xl bg-emerald-500 px-6 py-3 text-xs font-black text-slate-950 hover:bg-emerald-400 transition shadow-lg"
                >
                  <Sparkles size={16} /> Load Demo Leaf Sample & Retry
                </button>
                <button
                  type="button"
                  onClick={() => { setWorkflowState("idle"); setAnalysisError(null); }}
                  className="flex items-center gap-2 rounded-xl border border-slate-600 bg-slate-800 px-6 py-3 text-xs font-bold text-slate-300 hover:bg-slate-700 transition"
                >
                  <RefreshCw size={16} /> Try Again
                </button>
              </div>
            </div>
          ) : workflowState === "invalid_image" && currentDiagnosis ? (
            /* INVALID IMAGE STATE — Not a crop/leaf photo */
            <div className={`rounded-3xl border p-6 sm:p-8 space-y-5 text-left animate-fade-in ${
              isDark ? "border-amber-800/60 bg-[#1e1406] text-white shadow-2xl" : "border-amber-200 bg-amber-50 text-slate-900 shadow-xl"
            }`}>
              <div className="flex items-center gap-3">
                <div className="h-12 w-12 rounded-2xl bg-amber-500/20 text-amber-400 border border-amber-500/40 flex items-center justify-center shrink-0">
                  <AlertTriangle size={28} />
                </div>
                <div>
                  <span className="text-[10px] font-black uppercase tracking-wider text-amber-400 bg-amber-500/20 px-2.5 py-0.5 rounded-full border border-amber-500/30">
                    Image Rejected
                  </span>
                  <h3 className="text-xl font-black text-amber-200 mt-1">Not a Crop / Leaf Image</h3>
                </div>
              </div>
              <p className="text-xs text-amber-100/90 leading-relaxed">
                {currentDiagnosis.rejection_reason || "This image does not appear to contain a plant or leaf. Please upload a clear photo of the affected crop part."}
              </p>
              {currentDiagnosis.top_imagenet_class && (
                <div className="rounded-2xl border border-amber-500/30 bg-black/30 p-4 text-xs">
                  <span className="text-amber-300 font-bold">AI detected: </span>
                  <span className="text-slate-300">
                    "{currentDiagnosis.top_imagenet_class}" ({Math.round((currentDiagnosis.top_imagenet_confidence || 0) * 100)}% confidence)
                  </span>
                </div>
              )}
              <div className="rounded-2xl border border-amber-500/30 bg-black/30 p-4 space-y-2 text-xs text-slate-300">
                <p className="font-bold text-amber-300">For best results:</p>
                <ul className="space-y-1 list-disc list-inside text-slate-400">
                  <li>Photograph a single leaf against a plain background</li>
                  <li>Ensure good natural lighting without harsh shadows</li>
                  <li>Focus on the affected area of the plant</li>
                  <li>Avoid photos of soil, equipment, or non-plant objects</li>
                </ul>
              </div>
              <button
                type="button"
                onClick={() => setWorkflowState("idle")}
                className="flex items-center gap-2 rounded-xl bg-amber-500 px-6 py-3 text-xs font-black text-slate-950 hover:bg-amber-400 transition shadow-lg shadow-amber-500/20"
              >
                <RefreshCw size={16} /> Upload Different Image
              </button>
            </div>
          ) : workflowState === "result" && currentDiagnosis ? (
            <div className="space-y-6">
              {/* LOW CONFIDENCE NOTICE BANNER (Informative while showing full crop report) */}
              {(currentDiagnosis.is_low_confidence || currentDiagnosis.confidence < 0.85) && (
                <div className={`p-4 rounded-2xl border flex items-start gap-3 text-xs text-left animate-fade-in ${
                  isDark ? "border-amber-500/40 bg-amber-950/30 text-amber-200" : "border-amber-300 bg-amber-50 text-amber-900"
                }`}>
                  <AlertTriangle size={18} className="text-amber-400 shrink-0 mt-0.5" />
                  <div>
                    <span className="font-bold text-amber-300">
                      Moderate / Field Confidence Score ({Math.round(currentDiagnosis.confidence > 1 ? currentDiagnosis.confidence : currentDiagnosis.confidence * 100)}%):
                    </span>
                    <p className="mt-0.5 text-slate-300 text-[11px] leading-relaxed">
                      AI identified primary symptoms with moderate confidence. Full pathology report, chemical dosages, and 3-tier treatment recommendations are provided below. Verify secondary physical signs before spraying.
                    </p>
                  </div>
                </div>
              )}

              {/* 3D WEBGL LEAF LESION INSPECTOR + DIAGNOSIS RESULT */}
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
                  <div className="lg:col-span-8">
                    <DiagnosisResultCard
                      diagnosis={currentDiagnosis}
                      onRetake={() => setWorkflowState("idle")}
                      onOpenDosage={() => setIsDosageModalOpen(true)}
                      onOpenDrone={() => setIsDroneModalOpen(true)}
                      onOpenAgronomist={() => setIsAgronomistModalOpen(true)}
                      isDark={isDark}
                    />
                  </div>

                  {/* 3D WEBGL LESION INSPECTOR SIDEBAR */}
                  <div className="lg:col-span-4 space-y-4">
                    <div className={`p-5 rounded-3xl border ${
                      isDark ? "border-emerald-800/40 bg-[#072017]" : "border-slate-200 bg-white"
                    } shadow-xl text-left`}>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-[11px] font-black uppercase tracking-wider text-emerald-400 flex items-center gap-1.5">
                          <RotateCw size={14} /> 3D Leaf Pathology Inspector
                        </span>
                        <span className="text-[10px] font-mono text-slate-400">Mouse Drag to Orbit</span>
                      </div>

                      <div className="h-64 w-full rounded-2xl overflow-hidden bg-slate-950/60 border border-emerald-900/40">
                        <DiseaseLeaf3DModel
                          disease={{
                            diseaseName: currentDiagnosis.condition,
                            severity: currentDiagnosis.severity,
                            confidence: Math.round(currentDiagnosis.confidence * 100)
                          }}
                          theme={theme}
                        />
                      </div>

                      <p className="text-[11px] text-slate-400 mt-2">
                        Pulsating orange/red zones correspond to predicted fungal/bacterial lesion coordinates on the foliar lamina.
                      </p>
                    </div>

                    {/* QUICK ACTION DOCK */}
                    <div className={`p-4 rounded-3xl border ${
                      isDark ? "border-emerald-800/40 bg-[#072017]" : "border-slate-200 bg-white"
                    } space-y-2 text-left`}>
                      <span className="text-[10px] font-black uppercase text-emerald-400 tracking-wider">
                        Integrated Field Workflow
                      </span>
                      <button
                        type="button"
                        onClick={() => setIsDosageModalOpen(true)}
                        className="w-full flex items-center justify-between p-3 rounded-2xl bg-amber-500/10 border border-amber-500/30 text-amber-300 hover:bg-amber-500/20 transition text-xs font-bold"
                      >
                        <span className="flex items-center gap-2"><ShoppingCart size={15} /> Chemical Dosage Calculator</span>
                        <span>→</span>
                      </button>
                      <button
                        type="button"
                        onClick={() => setIsDroneModalOpen(true)}
                        className="w-full flex items-center justify-between p-3 rounded-2xl bg-cyan-500/10 border border-cyan-500/30 text-cyan-300 hover:bg-cyan-500/20 transition text-xs font-bold"
                      >
                        <span className="flex items-center gap-2"><Cpu size={15} /> Spot-Spray Drone Mission (KML)</span>
                        <span>→</span>
                      </button>
                      <button
                        type="button"
                        onClick={() => setIsAgronomistModalOpen(true)}
                        className="w-full flex items-center justify-between p-3 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 hover:bg-emerald-500/20 transition text-xs font-bold"
                      >
                        <span className="flex items-center gap-2"><UserCheck size={15} /> Dispatch KVK Agronomist</span>
                        <span>→</span>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
          ) : (
            /* IDLE INPUT WORKSPACE */
            <div className={`rounded-3xl p-6 sm:p-8 border space-y-6 transition-all text-left ${
              isDark ? "border-emerald-800/40 bg-[#072017] shadow-2xl" : "border-slate-200 bg-white shadow-xl"
            }`}>
              <CropSelector
                crops={crops}
                selectedCrop={selectedCrop}
                onSelectCrop={(c) => setSelectedCrop(c)}
                isDark={isDark}
              />

              {/* MODE SELECTOR: LEAF PHOTO VS NATURAL LANGUAGE SYMPTOM PROMPT */}
              <div className="flex items-center gap-2 border-b border-emerald-900/40 pb-3">
                <button
                  type="button"
                  onClick={() => setInputMode("vision")}
                  className={`px-4 py-2 rounded-xl text-xs font-bold transition flex items-center gap-2 ${
                    inputMode === "vision"
                      ? "bg-emerald-600 text-white shadow-sm"
                      : isDark ? "text-slate-400 hover:text-white" : "text-slate-600 hover:text-slate-900"
                  }`}
                >
                  <Sparkles size={14} /> Multi-Modal Leaf Photo
                </button>
                <button
                  type="button"
                  onClick={() => setInputMode("symptoms")}
                  className={`px-4 py-2 rounded-xl text-xs font-bold transition flex items-center gap-2 ${
                    inputMode === "symptoms"
                      ? "bg-emerald-600 text-white shadow-sm"
                      : isDark ? "text-slate-400 hover:text-white" : "text-slate-600 hover:text-slate-900"
                  }`}
                >
                  <MessageSquare size={14} /> Natural Language / Voice Symptoms
                </button>
              </div>

              {inputMode === "vision" ? (
                <>
                  <CropImageUploader
                    imagePreview={imagePreview}
                    onImageSelected={handleImageSelected}
                    onClearImage={handleClearImage}
                    isDark={isDark}
                    maxSizeMb={modelStatus?.max_image_size_mb || 15}
                  />

                  {/* QUICK DEMO LEAF PRESETS */}
                  <div className="flex flex-wrap items-center gap-2 pt-1 text-xs">
                    <span className="text-slate-400 font-bold flex items-center gap-1">
                      <Sparkles size={12} className="text-amber-400" />
                      Quick Demo Samples:
                    </span>
                    <button
                      type="button"
                      onClick={() => handleLoadPresetSample("Tomato", "/samples/sample_tomato_early_blight.jpg", "Tomato Early Blight Sample")}
                      className="px-2.5 py-1 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 hover:bg-emerald-500/20 transition font-bold"
                    >
                      🍅 Tomato Sample
                    </button>
                    <button
                      type="button"
                      onClick={() => handleLoadPresetSample("Cotton", "/samples/sample_cotton_leaf.jpg", "Cotton Leaf Sample")}
                      className="px-2.5 py-1 rounded-lg bg-cyan-500/10 border border-cyan-500/30 text-cyan-300 hover:bg-cyan-500/20 transition font-bold"
                    >
                      ☁️ Cotton Sample
                    </button>
                    <button
                      type="button"
                      onClick={() => handleLoadPresetSample("Potato", "/samples/sample_potato_leaf.jpg", "Potato Blight Sample")}
                      className="px-2.5 py-1 rounded-lg bg-amber-500/10 border border-amber-500/30 text-amber-300 hover:bg-amber-500/20 transition font-bold"
                    >
                      🥔 Potato Sample
                    </button>
                  </div>

                  <div className="flex justify-end pt-2">
                    <button
                      type="button"
                      onClick={handleRunAnalysis}
                      disabled={!imagePreview}
                      className={`flex items-center gap-2 rounded-2xl px-8 py-3.5 text-xs font-black transition-all shadow-lg ${
                        imagePreview
                          ? "bg-emerald-500 text-slate-950 hover:bg-emerald-400 shadow-emerald-500/30"
                          : "bg-slate-800 text-slate-500 cursor-not-allowed border border-slate-700"
                      }`}
                    >
                      <Sparkles size={16} />
                      <span>Run AI Crop Pathology Diagnosis</span>
                    </button>
                  </div>
                </>
              ) : (
                <div className="space-y-4">
                  <div className="p-4 rounded-2xl bg-emerald-950/30 border border-emerald-900/40 text-xs text-slate-300">
                    <p className="font-bold text-emerald-300 mb-1">
                      Kisan AI Dr. Agri Symptom Pathology Prompt:
                    </p>
                    <p className="text-slate-400">
                      Describe the visible symptoms on your {selectedCrop} crop (e.g. leaf spots, mildew color, vein yellowing, leaf curling) in English, Hindi, or your regional language.
                    </p>
                  </div>

                  <form onSubmit={handleSymptomDiagnosisSubmit} className="space-y-3">
                    <textarea
                      value={symptomText}
                      onChange={(e) => setSymptomText(e.target.value)}
                      placeholder={`Describe ${selectedCrop} leaf spots, wilting, powder or lesions... e.g. 'Concentric dark brown circular rings on bottom leaves with yellow margins'`}
                      rows={4}
                      className={`w-full rounded-2xl p-4 text-xs font-medium border outline-none transition focus:ring-2 focus:ring-emerald-500 ${
                        isDark ? "bg-slate-950 border-emerald-800/60 text-white" : "bg-white border-slate-300 text-slate-900"
                      }`}
                    />

                    {/* QUICK SAMPLE PROMPTS */}
                    <div className="flex flex-wrap items-center gap-2 text-[11px]">
                      <span className="text-slate-400 font-bold">Quick Sample Symptoms:</span>
                      <button
                        type="button"
                        onClick={() => setSymptomText("Dark brown circular spots with target concentric rings on lower leaves")}
                        className="px-2.5 py-1 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 hover:bg-emerald-500/20"
                      >
                        Target-board rings (Early Blight)
                      </button>
                      <button
                        type="button"
                        onClick={() => setSymptomText("Water-soaked dark lesions with white downy growth on undersides in morning dew")}
                        className="px-2.5 py-1 rounded-lg bg-cyan-500/10 border border-cyan-500/30 text-cyan-300 hover:bg-cyan-500/20"
                      >
                        Water-soaked mold (Late Blight)
                      </button>
                      <button
                        type="button"
                        onClick={() => setSymptomText("Angular black water-soaked lesions bounded sharply by veins")}
                        className="px-2.5 py-1 rounded-lg bg-amber-500/10 border border-amber-500/30 text-amber-300 hover:bg-amber-500/20"
                      >
                        Angular vein spots (Bacterial Blight)
                      </button>
                    </div>

                    <div className="flex justify-end pt-2">
                      <button
                        type="submit"
                        className="flex items-center gap-2 rounded-2xl bg-emerald-500 px-8 py-3.5 text-xs font-black text-slate-950 hover:bg-emerald-400 transition shadow-lg shadow-emerald-500/30"
                      >
                        <Send size={15} /> Run Symptom Diagnosis
                      </button>
                    </div>
                  </form>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* SUB-TAB 2: MY HEALTH HISTORY */}
      {activeSubTab === "history" && (
        <DiagnosisHistoryView
          onSelectRecord={(rec) => {
            setCurrentDiagnosis(rec);
            setWorkflowState("result");
            setActiveSubTab("diagnostic");
          }}
          onStartNewDiagnosis={() => {
            setWorkflowState("idle");
            setActiveSubTab("diagnostic");
          }}
          isDark={isDark}
        />
      )}

      {/* MODALS */}
      <LiveCameraModal
        isOpen={isCameraModalOpen}
        onClose={() => setIsCameraModalOpen(false)}
        onCapture={(capturedImage) => {
          setImagePreview(capturedImage);
          setIsCameraModalOpen(false);
          showToast("Live Camera Snapshot Captured! Ready to analyze.");
        }}
        isDark={isDark}
      />

      <DosageCalculatorModal
        isOpen={isDosageModalOpen}
        onClose={() => setIsDosageModalOpen(false)}
        disease={currentDiagnosis || { crop: selectedCrop, diseaseName: "Early Blight" }}
        isDark={isDark}
      />

      <DroneMissionGeneratorModal
        isOpen={isDroneModalOpen}
        onClose={() => setIsDroneModalOpen(false)}
        disease={currentDiagnosis || { crop: selectedCrop, diseaseName: "Early Blight" }}
        isDark={isDark}
      />

      <AgronomistDispatchModal
        isOpen={isAgronomistModalOpen}
        onClose={() => setIsAgronomistModalOpen(false)}
        disease={currentDiagnosis || { crop: selectedCrop, diseaseName: "Early Blight" }}
        isDark={isDark}
      />
    </div>
  );
}

