import React, { useState, useEffect } from "react";
import { CheckCircle2, Loader2, Circle, Sparkles, MessageSquare } from "lucide-react";

export default function AnalysisProgressScreen({
  crop = "Tomato",
  onComplete = () => {},
  isDark = true,
  inputMode = "vision",
}) {
  const [currentStep, setCurrentStep] = useState(0);

  const visionSteps = [
    { label: "Image loaded & resolution validated", sub: "File type, size, and minimum 150×150px quality check passed" },
    { label: "Stage A: Pre-Flight Image Quality Gate", sub: "Checking brightness, contrast, and focus to prevent blurry misdiagnoses" },
    { label: "Stage B: Dispatching to Neural Vision Engine", sub: `Evaluating ${crop} foliar patterns with trained pathology models` },
    { label: "Stage C: Confidence & Diagnostic Gating", sub: "Enforcing reliability thresholds and entropy checks" },
    { label: "Stage D: Differential diagnosis & IPM advisory", sub: "Validating against certified Krishi Vigyan Kendra protocols" },
    { label: "Preparing structured diagnostic report", sub: "Compiling verified recommendations and safety notices" },
  ];

  const symptomSteps = [
    { label: "Symptom text received", sub: "Input validated — English, Hindi, Marathi supported" },
    { label: "Tokenizing symptom keywords", sub: "Extracting individual symptom terms and phrases" },
    { label: `Scoring against ${crop} disease profiles`, sub: "Weighted NLP keyword matcher — 45+ crop disease entries" },
    { label: "Ranking differential diagnoses", sub: "Confidence gap analysis — separating primary from alternatives" },
    { label: "Fetching treatment & IPM advisory", sub: "Matching best-scoring diagnosis to agronomic knowledge base" },
    { label: "Preparing structured diagnostic report", sub: "Generating organic, chemical, preventive recommendations" },
  ];

  const steps = inputMode === "symptoms" ? symptomSteps : visionSteps;

  useEffect(() => {
    // Reset step when remounted
    setCurrentStep(0);
    let stepIdx = 0;
    const timer = setInterval(() => {
      stepIdx++;
      setCurrentStep(stepIdx);
      if (stepIdx >= steps.length - 1) {
        clearInterval(timer);
        setTimeout(() => onComplete(), 350);
      }
    }, 680);

    return () => clearInterval(timer);
  }, [inputMode]);

  const isVision = inputMode !== "symptoms";

  return (
    <div className={`rounded-3xl border p-6 sm:p-8 text-center space-y-6 animate-fade-in ${
      isDark ? "border-emerald-800/60 bg-[#072017] shadow-2xl text-white" : "border-slate-200 bg-white shadow-xl text-slate-900"
    }`}>
      <div className="relative mx-auto h-20 w-20 flex items-center justify-center rounded-3xl bg-emerald-500/10 border border-emerald-500/30">
        <div className="absolute inset-0 rounded-3xl border-2 border-emerald-400 border-t-transparent animate-spin" />
        {isVision
          ? <Sparkles size={36} className="text-emerald-400 animate-pulse" />
          : <MessageSquare size={32} className="text-emerald-400 animate-pulse" />
        }
      </div>

      <div>
        <h3 className="text-xl font-black">
          {isVision ? "Neural Vision Analysis Pipeline" : "NLP Symptom Pathology Engine"}
        </h3>
        <p className="text-xs text-emerald-300/80 mt-1 font-mono">
          {isVision
            ? "Canvas HSV Sampling • 45-Class Scoring • AgriNirvana v3.0"
            : "Weighted Keyword Matching • Multi-language NLP • AgriNirvana v3.0"
          }
        </p>
      </div>

      <div className="max-w-md mx-auto space-y-2.5 text-left">
        {steps.map((step, idx) => {
          const isDone = idx < currentStep;
          const isCurrent = idx === currentStep;

          return (
            <div
              key={idx}
              className={`flex items-start gap-3 p-3 rounded-2xl border transition-all duration-300 ${
                isCurrent
                  ? "border-emerald-500 bg-emerald-500/15 text-emerald-300 scale-[1.02] shadow-md shadow-emerald-500/10"
                  : isDone
                  ? "border-emerald-900/40 bg-emerald-950/40 text-emerald-400 opacity-90"
                  : "border-slate-800/50 bg-black/20 text-slate-500 opacity-40"
              }`}
            >
              <div className="mt-0.5 shrink-0">
                {isDone ? (
                  <CheckCircle2 size={18} className="text-emerald-400" />
                ) : isCurrent ? (
                  <Loader2 size={18} className="text-emerald-400 animate-spin" />
                ) : (
                  <Circle size={18} className="text-slate-600" />
                )}
              </div>

              <div>
                <div className="text-xs font-black">{step.label}</div>
                <div className="text-[10px] text-slate-400 mt-0.5 font-mono">{step.sub}</div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
