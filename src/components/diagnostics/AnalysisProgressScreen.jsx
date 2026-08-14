import React, { useState, useEffect } from "react";
import { CheckCircle2, Loader2, Circle, Sparkles } from "lucide-react";

export default function AnalysisProgressScreen({
  crop = "Tomato",
  onComplete = () => {},
  isDark = true
}) {
  const [currentStep, setCurrentStep] = useState(0);

  const steps = [
    { label: "Image uploaded & validated", sub: "MIME type, file size and resolution checked" },
    { label: "Image quality checked", sub: "Checking brightness contrast & sharpness variance" },
    { label: `Crop context set to ${crop}`, sub: "Loading crop-specific disease taxonomy" },
    { label: "Analyzing leaf chromatic patterns", sub: "Extracting HSV vectors & necrotic spot density" },
    { label: "Estimating disease severity & confidence", sub: "Cross-referencing knowledge base threshold" },
    { label: "Preparing farmer-friendly recommendations", sub: "Structuring immediate action & preventative steps" }
  ];

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentStep((prev) => {
        if (prev >= steps.length - 1) {
          clearInterval(timer);
          setTimeout(() => onComplete(), 400);
          return steps.length - 1;
        }
        return prev + 1;
      });
    }, 450);

    return () => clearInterval(timer);
  }, []);

  return (
    <div className={`rounded-3xl border p-6 sm:p-8 text-center space-y-6 animate-fade-in ${
      isDark ? "border-emerald-800/60 bg-[#072017] shadow-2xl text-white" : "border-slate-200 bg-white shadow-xl text-slate-900"
    }`}>
      <div className="relative mx-auto h-20 w-20 flex items-center justify-center rounded-3xl bg-emerald-500/10 border border-emerald-500/30">
        <div className="absolute inset-0 rounded-3xl border-2 border-emerald-400 border-t-transparent animate-spin" />
        <Sparkles size={36} className="text-emerald-400 animate-pulse" />
      </div>

      <div>
        <h3 className="text-xl font-black">AI Computer Vision Analysis in Progress</h3>
        <p className="text-xs text-emerald-300/80 mt-1 font-mono">EfficientNet-B3 • Neural Inference Pipeline</p>
      </div>

      <div className="max-w-md mx-auto space-y-3 text-left">
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
                  : "border-slate-800/50 bg-black/20 text-slate-500 opacity-50"
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
