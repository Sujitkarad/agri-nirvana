import React, { useState } from "react";
import {
  Bot,
  User,
  Volume2,
  Copy,
  Check,
  Share2,
  Sparkles,
  ChevronDown,
  ChevronUp,
  Cpu,
  ExternalLink,
  MessageSquare,
  ArrowRight,
  TrendingUp,
  Table,
  ShieldCheck
} from "lucide-react";

export default function AIWorkspaceStream({
  messages = [],
  isThinking = false,
  isDark = true,
  onPlayAudio,
  isPlayingAudio = false,
  onSelectFollowUp
}) {
  const [copiedIndex, setCopiedIndex] = useState(null);
  const [expandedReasoning, setExpandedReasoning] = useState({});

  const handleCopy = (text, idx) => {
    navigator.clipboard?.writeText(text);
    setCopiedIndex(idx);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  const toggleReasoning = (idx) => {
    setExpandedReasoning((prev) => ({
      ...prev,
      [idx]: !prev[idx]
    }));
  };

  if (messages.length === 0 && !isThinking) {
    return null;
  }

  return (
    <div className="w-full max-w-4xl mx-auto space-y-4 my-6">
      {messages.map((msg, idx) => {
        const isUser = msg.sender === "user";
        return (
          <div
            key={idx}
            className={`flex gap-3 sm:gap-4 items-start animate-fade-in ${
              isUser ? "flex-row-reverse" : "flex-row"
            }`}
          >
            {/* Avatar Pill */}
            <div
              className={`shrink-0 grid h-9 w-9 place-items-center rounded-2xl shadow-md ${
                isUser
                  ? "bg-slate-700 text-white"
                  : isDark
                  ? "bg-gradient-to-br from-emerald-400 via-teal-500 to-cyan-500 text-slate-950 glow-emerald"
                  : "bg-emerald-600 text-white shadow-emerald-600/30"
              }`}
            >
              {isUser ? <User size={16} /> : <Bot size={18} />}
            </div>

            {/* Message Bubble Card */}
            <div
              className={`relative max-w-[92%] sm:max-w-[84%] rounded-3xl p-4 sm:p-5 border transition shadow-xl text-left ${
                isUser
                  ? isDark
                    ? "bg-[#062014] border-emerald-500/30 text-slate-100"
                    : "bg-emerald-600 border-emerald-700 text-white"
                  : isDark
                  ? "glass-ai-panel border-emerald-500/20 text-slate-200"
                  : "glass-ai-panel-light border-slate-200 text-slate-900"
              }`}
            >
              {/* Optional Reasoning Chain Accordion for AI (DeepSeek-R1 / o1 Style) */}
              {!isUser && msg.reasoning && (
                <div className="mb-3 border-b border-emerald-500/15 pb-2.5">
                  <button
                    type="button"
                    onClick={() => toggleReasoning(idx)}
                    className="flex items-center gap-1.5 text-[11px] font-mono font-bold text-emerald-400 hover:text-emerald-300 transition"
                  >
                    <Cpu size={12} className="animate-pulse" />
                    <span>Deep Chain-of-Thought Reasoning ({msg.latency || "38ms · 110 tokens/s"})</span>
                    {expandedReasoning[idx] ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
                  </button>
                  {expandedReasoning[idx] && (
                    <div className="mt-2 text-xs font-mono text-slate-300 bg-black/50 p-3 rounded-2xl leading-relaxed border border-emerald-500/20 whitespace-pre-wrap">
                      {msg.reasoning}
                    </div>
                  )}
                </div>
              )}

              {/* Message Content */}
              <div className="text-xs sm:text-sm leading-relaxed whitespace-pre-wrap font-medium space-y-2">
                {msg.text}
              </div>

              {/* Data Table Preview if provided */}
              {msg.tableData && msg.tableData.length > 0 && (
                <div className="mt-4 rounded-2xl border border-emerald-500/20 overflow-hidden bg-black/30 text-xs">
                  <div className="p-2.5 bg-emerald-950/40 border-b border-emerald-500/20 font-bold text-emerald-300 flex items-center gap-1.5">
                    <Table size={13} /> Live APMC Price Telemetry Table
                  </div>
                  <div className="overflow-x-auto">
                    <table className="w-full text-left">
                      <thead>
                        <tr className="border-b border-emerald-500/15 text-[10px] uppercase text-slate-400">
                          <th className="p-2">Crop</th>
                          <th className="p-2">Mandi Yard</th>
                          <th className="p-2">Rate/kg</th>
                          <th className="p-2">Quintal Rate</th>
                          <th className="p-2">Trend</th>
                        </tr>
                      </thead>
                      <tbody>
                        {msg.tableData.map((row, rIdx) => (
                          <tr key={rIdx} className="border-b border-emerald-500/10 hover:bg-emerald-500/5">
                            <td className="p-2 font-bold text-emerald-200">{row.crop}</td>
                            <td className="p-2 text-slate-300">{row.mandi}</td>
                            <td className="p-2 font-mono font-bold text-emerald-400">₹{row.priceKg}</td>
                            <td className="p-2 font-mono text-slate-300">₹{row.priceQuintal}</td>
                            <td className="p-2 text-emerald-400 font-bold">{row.trend}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* Suggested Follow-up Action Chips */}
              {!isUser && msg.suggestedFollowUps && msg.suggestedFollowUps.length > 0 && (
                <div className="mt-4 pt-3 border-t border-emerald-500/15 space-y-1.5">
                  <span className="text-[10px] font-mono text-slate-400 flex items-center gap-1">
                    <Sparkles size={11} className="text-amber-400" /> Suggested Follow-ups:
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {msg.suggestedFollowUps.map((suggestion, sIdx) => (
                      <button
                        type="button"
                        key={sIdx}
                        onClick={() => onSelectFollowUp?.(suggestion)}
                        className={`flex items-center gap-1 rounded-xl px-2.5 py-1 text-[11px] font-bold transition-all active:scale-[0.98] ${
                          isDark
                            ? "bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 hover:bg-emerald-500/20 hover:border-emerald-400"
                            : "bg-emerald-50 border border-emerald-300 text-emerald-900 hover:bg-emerald-100"
                        }`}
                      >
                        <span>{suggestion}</span>
                        <ArrowRight size={11} />
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Sources Attribution & Actions Toolbar */}
              {!isUser && (
                <div className="mt-3.5 flex flex-wrap items-center justify-between gap-2 pt-2.5 border-t border-emerald-500/10 text-[11px] font-mono">
                  {/* Sources Chips */}
                  <div className="flex items-center gap-1.5 flex-wrap">
                    <span className="text-slate-400 text-[10px]">Model:</span>
                    <span className="rounded-md bg-emerald-500/15 border border-emerald-500/30 px-1.5 py-0.5 text-[9px] text-emerald-300 font-bold">
                      {msg.source || "DeepSeek-Agri Neural Engine"}
                    </span>
                  </div>

                  {/* Actions (Audio TTS, Copy) */}
                  <div className="flex items-center gap-2">
                    <button
                      type="button"
                      onClick={() => onPlayAudio?.(msg.text)}
                      title="Listen with voice synthesizer"
                      className={`flex items-center gap-1 rounded-lg px-2 py-1 transition ${
                        isPlayingAudio
                          ? "bg-cyan-400/20 text-cyan-300 animate-pulse"
                          : "hover:bg-emerald-500/10 text-emerald-400"
                      }`}
                    >
                      <Volume2 size={13} />
                      <span className="text-[10px]">Play Audio</span>
                    </button>

                    <button
                      type="button"
                      onClick={() => handleCopy(msg.text, idx)}
                      title="Copy response"
                      className="flex items-center gap-1 rounded-lg px-2 py-1 hover:bg-emerald-500/10 text-slate-400 hover:text-emerald-300 transition"
                    >
                      {copiedIndex === idx ? <Check size={13} className="text-emerald-400" /> : <Copy size={13} />}
                      <span className="text-[10px]">{copiedIndex === idx ? "Copied" : "Copy"}</span>
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        );
      })}

      {/* Real-time Thinking Skeleton Stream Indicator */}
      {isThinking && (
        <div className="flex gap-3 sm:gap-4 items-start animate-fade-in">
          <div className="shrink-0 grid h-9 w-9 place-items-center rounded-2xl bg-gradient-to-br from-amber-400 to-orange-500 text-slate-950 glow-emerald animate-pulse">
            <Bot size={18} />
          </div>
          <div
            className={`rounded-3xl p-4 sm:p-5 border transition shadow-xl w-full max-w-md ${
              isDark ? "glass-ai-panel border-amber-500/30 text-amber-300" : "glass-ai-panel-light border-amber-300 text-amber-900"
            }`}
          >
            <div className="flex items-center gap-2 text-xs font-mono font-bold">
              <span className="h-2 w-2 rounded-full bg-amber-400 animate-ping" />
              <span>AI REASONING · GENERATING TOKENS...</span>
            </div>
            <div className="mt-3 space-y-2">
              <div className="h-2.5 bg-amber-400/20 rounded-full animate-pulse w-3/4" />
              <div className="h-2.5 bg-amber-400/20 rounded-full animate-pulse w-1/2" />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
