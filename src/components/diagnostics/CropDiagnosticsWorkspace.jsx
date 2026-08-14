import React, { useState, useEffect } from "react";
import { Sparkles, History, Cpu, FileText, ShoppingCart, UserCheck, Landmark } from "lucide-react";

import {
  fetchModelStatus,
  fetchSupportedCrops,
  analyzeCropImageApi,
  fetchDiagnosisHistoryApi
} from "../../services/diagnosisApi";

import CropSelector from "./CropSelector";
import CropImageUploader from "./CropImageUploader";
import AnalysisProgressScreen from "./AnalysisProgressScreen";
import DiagnosisResultCard from "./DiagnosisResultCard";
import LowConfidenceNotice from "./LowConfidenceNotice";
import DiagnosisHistoryView from "./DiagnosisHistoryView";

import LiveCameraModal from "../LiveCameraModal";
import DosageCalculatorModal from "../DosageCalculatorModal";
import DroneMissionGeneratorModal from "../DroneMissionGeneratorModal";
import ParametricClaimModal from "../ParametricClaimModal";
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
  const isDark = theme === "dark";

  // Tab: "diagnostic" | "history"
  const [activeSubTab, setActiveSubTab] = useState("diagnostic");

  // Crop & Image State
  const [crops, setCrops] = useState([
    { id: "Tomato", name: "Tomato", icon: "🍅" },
    { id: "Potato", name: "Potato", icon: "🥔" },
    { id: "Cotton", name: "Cotton", icon: "☁️" },
    { id: "Rice", name: "Paddy / Rice", icon: "🌾" },
    { id: "Wheat", name: "Wheat", icon: "🌾" },
    { id: "Maize", name: "Maize / Corn", icon: "🌽" },
    { id: "Onion", name: "Onion", icon: "🧅" },
    { id: "Soybean", name: "Soybean", icon: "🌱" },
    { id: "Chilli", name: "Chilli", icon: "🌶️" },
    { id: "Grapes", name: "Grapes", icon: "🍇" }
  ]);
  const [selectedCrop, setSelectedCrop] = useState("Tomato");
  const [selectedFile, setSelectedFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);

  // Workflow State: "idle" | "analyzing" | "result"
  const [workflowState, setWorkflowState] = useState("idle");
  const [currentDiagnosis, setCurrentDiagnosis] = useState(null);
  const [modelStatus, setModelStatus] = useState(null);

  // Modals
  const [isCameraModalOpen, setIsCameraModalOpen] = useState(false);
  const [isDosageModalOpen, setIsDosageModalOpen] = useState(false);
  const [isDroneModalOpen, setIsDroneModalOpen] = useState(false);
  const [isClaimModalOpen, setIsClaimModalOpen] = useState(false);
  const [isAgronomistModalOpen, setIsAgronomistModalOpen] = useState(false);

  useEffect(() => {
    fetchModelStatus().then((res) => {
      if (res && res.success) setModelStatus(res);
    });
    fetchSupportedCrops().then((res) => {
      if (res && res.crops) setCrops(res.crops);
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

  const handleRunAnalysis = () => {
    if (!imagePreview) {
      showToast("Please upload or capture a crop leaf photo first.");
      return;
    }
    setWorkflowState("analyzing");
  };

  const handleAnalysisProgressComplete = async () => {
    try {
      const res = await analyzeCropImageApi(selectedFile, selectedCrop, imagePreview);
      if (res && res.diagnosis) {
        setCurrentDiagnosis(res.diagnosis);
        setWorkflowState("result");
        setMonthlyScansCount((c) => c + 1);

        // Save to local storage history as well for instant client availability
        try {
          const local = localStorage.getItem("agri_nirvana_diag_history");
          let list = local ? JSON.parse(local) : [];
          list = [res.diagnosis, ...list.filter((x) => x.id !== res.diagnosis.id)];
          localStorage.setItem("agri_nirvana_diag_history", JSON.stringify(list));
        } catch (e) {}

        showToast(`AI diagnosis completed for ${selectedCrop}!`);
      }
    } catch (err) {
      showToast(`Analysis error: ${err.message}`);
      setWorkflowState("idle");
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
            ML Model Engine: {modelStatus?.model_name || "EfficientNet-B3 Transfer Learning"}
          </span>
          <span className="rounded-full bg-emerald-500/20 text-emerald-300 text-[10px] font-mono font-bold px-2 py-0.5 border border-emerald-500/30">
            {modelStatus?.model_version || "v1.0-prod"}
          </span>
          {modelStatus?.is_mock && (
            <span className="rounded-full bg-amber-500/20 text-amber-300 text-[10px] font-mono font-bold px-2 py-0.5 border border-amber-500/30">
              Dev Mock Provider
            </span>
          )}
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
          ) : workflowState === "result" && currentDiagnosis ? (
            currentDiagnosis.is_low_confidence || (currentDiagnosis.confidence < 0.70) ? (
              <LowConfidenceNotice
                confidence={currentDiagnosis.confidence}
                threshold={modelStatus?.confidence_threshold || 0.70}
                onRetake={() => setWorkflowState("idle")}
                isDark={isDark}
              />
            ) : (
              <div className="space-y-6">
                {/* ACTION BAR */}
                <div className="flex flex-wrap items-center justify-between gap-2 bg-emerald-950/40 p-3 rounded-2xl border border-emerald-900/50">
                  <span className="text-xs font-bold text-emerald-300">
                    Integrated Field Action Dock:
                  </span>
                  <div className="flex flex-wrap items-center gap-2">
                    <button onClick={() => setIsDroneModalOpen(true)} className="flex items-center gap-1 text-xs font-bold text-cyan-400 bg-cyan-950/60 px-3 py-1.5 rounded-xl border border-cyan-800/60 hover:bg-cyan-900/60">
                      <Cpu size={14} /> Drone Mission
                    </button>
                    <button onClick={() => setIsClaimModalOpen(true)} className="flex items-center gap-1 text-xs font-bold text-emerald-400 bg-emerald-950/60 px-3 py-1.5 rounded-xl border border-emerald-800/60 hover:bg-emerald-900/60">
                      <Landmark size={14} /> Auto-Claim Payout
                    </button>
                    <button onClick={() => setIsAgronomistModalOpen(true)} className="flex items-center gap-1 text-xs font-bold text-emerald-300 bg-emerald-900/60 px-3 py-1.5 rounded-xl border border-emerald-700/60 hover:bg-emerald-800/60">
                      <UserCheck size={14} /> Dispatch Agronomist
                    </button>
                    <button onClick={() => setIsDosageModalOpen(true)} className="flex items-center gap-1 text-xs font-bold text-amber-400 bg-amber-950/60 px-3 py-1.5 rounded-xl border border-amber-800/60 hover:bg-amber-900/60">
                      <ShoppingCart size={14} /> Dosage & Buy
                    </button>
                  </div>
                </div>

                <DiagnosisResultCard
                  diagnosis={currentDiagnosis}
                  onRetake={() => setWorkflowState("idle")}
                  isDark={isDark}
                />
              </div>
            )
          ) : (
            /* IDLE INPUT WORKSPACE */
            <div className={`rounded-3xl p-6 sm:p-8 border space-y-6 transition-all ${
              isDark ? "border-emerald-800/40 bg-[#072017] shadow-2xl" : "border-slate-200 bg-white shadow-xl"
            }`}>
              <CropSelector
                crops={crops}
                selectedCrop={selectedCrop}
                onSelectCrop={(c) => setSelectedCrop(c)}
                isDark={isDark}
              />

              <CropImageUploader
                imagePreview={imagePreview}
                onImageSelected={handleImageSelected}
                onClearImage={handleClearImage}
                isDark={isDark}
                maxSizeMb={modelStatus?.max_image_size_mb || 10}
              />

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
                  <span>Analyze Crop Leaf AI</span>
                </button>
              </div>
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

      <ParametricClaimModal
        isOpen={isClaimModalOpen}
        onClose={() => setIsClaimModalOpen(false)}
        disease={currentDiagnosis || { crop: selectedCrop, diseaseName: "Early Blight" }}
        selectedField={selectedField}
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
