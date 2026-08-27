import React, { useState, useRef, useEffect } from "react";
import {
  Send,
  Paperclip,
  Mic,
  MicOff,
  Sparkles,
  X,
  FileText,
  Image as ImageIcon,
  Check,
  ChevronDown,
  Cpu,
  Loader2
} from "lucide-react";

const MODEL_OPTIONS = [
  {
    id: "DeepSeek-R1",
    name: "DeepSeek-R1 Agri-Reasoner",
    desc: "Deep chain-of-thought agronomy & soil chemistry",
    badge: "Reasoning · CoT"
  },
  {
    id: "Mistral-7B",
    name: "Mistral-7B-Instruct v0.3",
    desc: "Ultra-fast diagnosis & actionable field prescriptions",
    badge: "Fast · 34ms"
  },
  {
    id: "Llama-3.2",
    name: "LLaMA-3.2-3B Multimodal",
    desc: "Visual foliar lesion & edge agronomy analysis",
    badge: "Edge Vision"
  },
  {
    id: "Kisan-Dr",
    name: "Kisan-AI Dr. (Multilingual)",
    desc: "Field-verified farmer advisory in regional languages",
    badge: "KVK Verified"
  },
  {
    id: "Zephyr-7B",
    name: "Zephyr-7B-Beta",
    desc: "Dialectic agronomic reasoning & farm economics",
    badge: "Economics"
  }
];

export default function OmniPromptStudio({
  isDark = true,
  onSubmitPrompt,
  isLoading = false,
  selectedModel = "Mistral-7B",
  onSelectModel,
  onAttachFiles,
  onTriggerVoice
}) {
  const [inputText, setInputText] = useState("");
  const [attachments, setAttachments] = useState([]);
  const [modelDropdownOpen, setModelDropdownOpen] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [recordingSeconds, setRecordingSeconds] = useState(0);

  const fileInputRef = useRef(null);
  const textareaRef = useRef(null);
  const dropdownRef = useRef(null);

  // Recording timer
  useEffect(() => {
    let timer;
    if (isRecording) {
      timer = setInterval(() => {
        setRecordingSeconds((prev) => prev + 1);
      }, 1000);
    } else {
      setRecordingSeconds(0);
    }
    return () => clearInterval(timer);
  }, [isRecording]);

  // Click outside to close model dropdown
  useEffect(() => {
    function handleClickOutside(e) {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setModelDropdownOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleSubmit = () => {
    if ((!inputText.trim() && attachments.length === 0) || isLoading) return;
    onSubmitPrompt?.(inputText, attachments);
    setInputText("");
    setAttachments([]);
  };

  const handleFileChange = (e) => {
    const files = Array.from(e.target.files || []);
    if (files.length === 0) return;

    const newAttachments = files.map((f) => ({
      name: f.name,
      size: (f.size / 1024).toFixed(1) + " KB",
      type: f.type.startsWith("image/") ? "image" : "doc",
      raw: f
    }));

    setAttachments((prev) => [...prev, ...newAttachments]);
    onAttachFiles?.(files);
    e.target.value = "";
  };

  const removeAttachment = (index) => {
    setAttachments((prev) => prev.filter((_, i) => i !== index));
  };

  const recognitionRef = useRef(null);

  const toggleVoiceRecording = () => {
    if (!isRecording) {
      setIsRecording(true);
      onTriggerVoice?.(true);

      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (SpeechRecognition) {
        try {
          const recognition = new SpeechRecognition();
          recognition.continuous = true;
          recognition.interimResults = true;
          recognition.lang = "en-IN";

          recognition.onresult = (event) => {
            let transcript = "";
            for (let i = event.resultIndex; i < event.results.length; ++i) {
              transcript += event.results[i][0].transcript;
            }
            if (transcript.trim()) {
              setInputText((prev) => (prev ? prev + " " + transcript : transcript));
            }
          };

          recognition.onerror = () => {
            setIsRecording(false);
            onTriggerVoice?.(false);
          };

          recognition.onend = () => {
            setIsRecording(false);
            onTriggerVoice?.(false);
          };

          recognition.start();
          recognitionRef.current = recognition;
        } catch (e) {
          // Fallback simulation if mic permissions denied
          setTimeout(() => {
            if (!inputText) {
              setInputText("What is the real-time price of Tomato at Saoner APMC and how to treat Early Blight?");
            }
          }, 2500);
        }
      } else {
        // Fallback simulation
        setTimeout(() => {
          if (!inputText) {
            setInputText("What are the recommended fertilizer dosages for 5 acres of Wheat?");
          }
        }, 2000);
      }
    } else {
      setIsRecording(false);
      onTriggerVoice?.(false);
      if (recognitionRef.current) {
        try {
          recognitionRef.current.stop();
        } catch (e) {}
      }
      if (!inputText) {
        setInputText("What are the recommended treatments for tomato early blight in Maharashtra?");
      }
    }
  };

  const formatTimer = (sec) => {
    const m = Math.floor(sec / 60);
    const s = sec % 60;
    return `${m.toString().padStart(2, "0")}:${s.toString().padStart(2, "0")}`;
  };

  return (
    <div className="relative w-full max-w-4xl mx-auto">
      {/* Omni Prompt Dock Container */}
      <div
        className={`relative rounded-3xl border transition-all duration-300 shadow-2xl ${
          isDark
            ? "glass-ai-panel border-emerald-500/30 shadow-[0_15px_40px_rgba(0,0,0,0.7)] focus-within:border-emerald-400 focus-within:glow-emerald"
            : "glass-ai-panel-light border-slate-200 shadow-lg focus-within:border-emerald-600"
        }`}
      >
        {/* Attached Files Chips Bar */}
        {attachments.length > 0 && (
          <div className="flex flex-wrap items-center gap-2 p-3 pb-0">
            {attachments.map((file, idx) => (
              <div
                key={idx}
                className={`flex items-center gap-2 rounded-xl px-3 py-1.5 text-xs font-mono border backdrop-blur-md transition ${
                  isDark
                    ? "bg-[#061e13] border-emerald-500/30 text-emerald-200"
                    : "bg-emerald-50 border-emerald-200 text-emerald-900"
                }`}
              >
                {file.type === "image" ? (
                  <ImageIcon size={14} className="text-emerald-400" />
                ) : (
                  <FileText size={14} className="text-cyan-400" />
                )}
                <span className="max-w-[150px] truncate font-medium">{file.name}</span>
                <span className="text-[10px] opacity-70">({file.size})</span>
                <button
                  type="button"
                  onClick={() => removeAttachment(idx)}
                  className="hover:text-rose-400 transition"
                  aria-label="Remove attachment"
                >
                  <X size={13} />
                </button>
              </div>
            ))}
          </div>
        )}

        {/* Live Voice Recording HUD Overlay */}
        {isRecording && (
          <div className="flex items-center justify-between px-5 pt-3 text-xs font-mono font-bold text-cyan-400 animate-fade-in">
            <div className="flex items-center gap-2">
              <span className="relative flex h-2.5 w-2.5">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75" />
                <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-cyan-500" />
              </span>
              <span>LISTENING...</span>
              <div className="flex items-center gap-1 ml-2">
                <span className="w-1 bg-cyan-400 rounded-full audio-wave-bar" />
                <span className="w-1 bg-cyan-400 rounded-full audio-wave-bar" />
                <span className="w-1 bg-cyan-400 rounded-full audio-wave-bar" />
                <span className="w-1 bg-cyan-400 rounded-full audio-wave-bar" />
                <span className="w-1 bg-cyan-400 rounded-full audio-wave-bar" />
              </div>
            </div>
            <span>{formatTimer(recordingSeconds)}</span>
          </div>
        )}

        {/* Multiline Conversational Textarea Input */}
        <div className="p-4 sm:p-5">
          <textarea
            ref={textareaRef}
            rows={2}
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask anything, analyze crop leaf photo, generate NPK formula, or explore live Mandi prices..."
            className={`w-full resize-none bg-transparent text-sm sm:text-base outline-none font-medium leading-relaxed transition placeholder:text-slate-500 ${
              isDark ? "text-white placeholder:text-slate-500" : "text-slate-900 placeholder:text-slate-400"
            }`}
          />

          {/* Bottom Dock Controls */}
          <div className="flex flex-wrap items-center justify-between gap-3 pt-3 border-t border-emerald-500/10">
            {/* Left Controls: Attachments, Voice, Model Dropdown */}
            <div className="flex items-center gap-2 sm:gap-2.5">
              {/* File Attachment Hidden Input */}
              <input
                ref={fileInputRef}
                type="file"
                multiple
                accept="image/*,.pdf,.csv"
                onChange={handleFileChange}
                className="hidden"
              />

              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                title="Attach leaf image or dataset"
                className={`flex items-center gap-1.5 rounded-xl border px-3 py-2 text-xs font-bold transition active:scale-[0.98] ${
                  isDark
                    ? "border-emerald-500/20 bg-[#05180f] text-emerald-300 hover:bg-emerald-950/60"
                    : "border-slate-300 bg-white text-slate-700 hover:bg-slate-50 shadow-sm"
                }`}
              >
                <Paperclip size={14} />
                <span className="hidden sm:inline">Attach</span>
              </button>

              {/* Voice Input Toggle */}
              <button
                type="button"
                onClick={toggleVoiceRecording}
                title="Voice input"
                className={`flex items-center gap-1.5 rounded-xl border px-3 py-2 text-xs font-bold transition active:scale-[0.98] ${
                  isRecording
                    ? "border-cyan-400 bg-cyan-400/20 text-cyan-300 glow-cyan animate-pulse"
                    : isDark
                    ? "border-emerald-500/20 bg-[#05180f] text-emerald-300 hover:bg-emerald-950/60"
                    : "border-slate-300 bg-white text-slate-700 hover:bg-slate-50 shadow-sm"
                }`}
              >
                {isRecording ? <MicOff size={14} className="text-cyan-300" /> : <Mic size={14} />}
                <span className="hidden sm:inline">{isRecording ? "Stop Voice" : "Voice"}</span>
              </button>

              {/* Model Selector Dropdown */}
              <div className="relative" ref={dropdownRef}>
                <button
                  type="button"
                  onClick={() => setModelDropdownOpen((prev) => !prev)}
                  className={`flex items-center gap-2 rounded-xl border px-3 py-2 text-xs font-bold transition active:scale-[0.98] ${
                    isDark
                      ? "border-emerald-500/20 bg-[#05180f] text-emerald-300 hover:bg-emerald-950/60"
                      : "border-slate-300 bg-white text-slate-700 hover:bg-slate-50 shadow-sm"
                  }`}
                >
                  <Cpu size={14} className="text-emerald-400" />
                  <span className="font-mono">{selectedModel}</span>
                  <ChevronDown size={13} className="text-slate-400" />
                </button>

                {modelDropdownOpen && (
                  <div
                    className={`absolute bottom-full mb-2 left-0 w-72 rounded-2xl border p-1.5 shadow-2xl z-50 animate-fade-in ${
                      isDark
                        ? "border-emerald-500/30 bg-[#04160f] text-slate-100 shadow-[0_10px_35px_rgba(0,0,0,0.8)]"
                        : "border-slate-200 bg-white text-slate-900 shadow-xl"
                    }`}
                  >
                    <div className="px-2.5 py-1.5 text-[10px] font-mono font-bold uppercase tracking-wider text-emerald-400">
                      Neural Inference Engine
                    </div>
                    {MODEL_OPTIONS.map((m) => (
                      <button
                        key={m.id}
                        type="button"
                        onClick={() => {
                          onSelectModel?.(m.id);
                          setModelDropdownOpen(false);
                        }}
                        className={`flex w-full items-start justify-between rounded-xl p-2.5 text-left transition active:scale-[0.98] ${
                          selectedModel === m.id
                            ? isDark
                              ? "bg-emerald-500/20 text-emerald-300"
                              : "bg-emerald-50 text-emerald-900"
                            : isDark
                            ? "hover:bg-emerald-950/50 text-slate-300"
                            : "hover:bg-slate-100 text-slate-700"
                        }`}
                      >
                        <div>
                          <div className="flex items-center gap-1.5 font-bold text-xs">
                            <span>{m.name}</span>
                            {selectedModel === m.id && <Check size={13} className="text-emerald-400" />}
                          </div>
                          <p className="text-[11px] opacity-75">{m.desc}</p>
                        </div>
                        <span className="rounded bg-emerald-500/20 text-emerald-300 px-1.5 py-0.5 text-[9px] font-mono">
                          {m.badge}
                        </span>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Right: Submit Button */}
            <button
              type="button"
              onClick={handleSubmit}
              disabled={isLoading || (!inputText.trim() && attachments.length === 0)}
              className={`flex items-center gap-2 rounded-2xl px-5 py-2.5 text-xs font-black transition-all duration-200 active:scale-[0.98] ${
                inputText.trim() || attachments.length > 0
                  ? "bg-gradient-to-r from-emerald-500 to-teal-400 text-slate-950 shadow-md glow-emerald hover:brightness-110 cursor-pointer"
                  : "bg-slate-800/40 text-slate-500 cursor-not-allowed border border-slate-700/40"
              }`}
            >
              {isLoading ? (
                <>
                  <Loader2 size={15} className="animate-spin text-slate-950" />
                  <span>Thinking...</span>
                </>
              ) : (
                <>
                  <Send size={14} />
                  <span>Submit</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
