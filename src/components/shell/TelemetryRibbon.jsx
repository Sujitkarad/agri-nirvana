import React, { useState, useEffect } from "react";
import { Activity, ShieldCheck, Cpu, Radio, Sparkles } from "lucide-react";

export default function TelemetryRibbon({ isDark = true, selectedModel = "Mistral-7B" }) {
  const [latency, setLatency] = useState(42);

  // Subtle realistic latency fluctuation simulation: 42ms -> 38ms -> 41ms -> 37ms
  useEffect(() => {
    const interval = setInterval(() => {
      const delta = (Math.random() * 6 - 3); // -3 to +3
      setLatency((prev) => {
        const next = Math.round(prev + delta);
        return Math.min(48, Math.max(34, next));
      });
    }, 2800);
    return () => clearInterval(interval);
  }, []);

  return (
    <div
      className={`border-b text-[11px] font-mono py-1.5 px-4 overflow-hidden whitespace-nowrap select-none transition-colors duration-300 ${
        isDark
          ? "border-emerald-500/20 bg-[#020906]/90 text-emerald-400/90 backdrop-blur-md"
          : "border-slate-200 bg-slate-900 text-emerald-300"
      }`}
    >
      <div className="mx-auto max-w-7xl flex items-center justify-between gap-4">
        {/* Left Telemetry Cluster */}
        <div className="flex items-center gap-5 sm:gap-6">
          <span className="flex items-center gap-1.5 font-bold">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500" />
            </span>
            <span className="tracking-tight">&lt;{latency}ms</span>
            <span className="opacity-70 font-normal">Neural Inference</span>
          </span>

          <span className="hidden md:flex items-center gap-1.5 text-cyan-400">
            <Activity size={12} className="text-cyan-400" />
            <span className="font-bold">API Health:</span>
            <span className="text-emerald-400">Operational (99.99%)</span>
          </span>

          <span className="hidden lg:flex items-center gap-1.5 text-slate-300">
            <ShieldCheck size={12} className="text-emerald-400" />
            <span className="opacity-70">TLS 1.3 End-to-End Encrypted</span>
          </span>
        </div>

        {/* Right Telemetry Cluster */}
        <div className="flex items-center gap-3">
          <span className="flex items-center gap-1.5 text-emerald-300 font-semibold">
            <Radio size={12} className="text-emerald-400 animate-pulse" />
            <span className="hidden sm:inline">Engine:</span>
            <span className="text-white font-bold">{selectedModel}</span>
          </span>

          <span className="rounded-full bg-emerald-500/20 px-2 py-0.5 text-[10px] text-emerald-300 border border-emerald-500/40 font-bold">
            Live Telemetry
          </span>
        </div>
      </div>
    </div>
  );
}
