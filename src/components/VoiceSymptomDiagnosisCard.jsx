import React, { useState } from "react";
import { Mic, MicOff, Search, Sparkles, Volume2, MessageSquare } from "lucide-react";
import { diagnoseBySymptomDescription } from "../data/agriData";

export default function VoiceSymptomDiagnosisCard({ onDiagnoseSymptom, isDark = false }) {
  const [symptomText, setSymptomText] = useState("");
  const [isListening, setIsListening] = useState(false);

  const handleVoiceListen = () => {
    if (!("webkitSpeechRecognition" in window) && !("SpeechRecognition" in window)) {
      alert("Voice recognition is not supported on this browser. You can type your symptoms!");
      return;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = "en-US";

    recognition.onstart = () => setIsListening(true);
    recognition.onend = () => setIsListening(false);
    recognition.onerror = () => setIsListening(false);

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      setSymptomText(transcript);
      const resultDisease = diagnoseBySymptomDescription(transcript);
      onDiagnoseSymptom(resultDisease, transcript);
    };

    recognition.start();
  };

  const handleTextSubmit = (e) => {
    e.preventDefault();
    if (!symptomText.trim()) return;
    const resultDisease = diagnoseBySymptomDescription(symptomText);
    onDiagnoseSymptom(resultDisease, symptomText);
  };

  return (
    <div className={`rounded-2xl p-4 border transition-all ${isDark ? "border-emerald-800/40 bg-[#04160f]" : "border-slate-200 bg-white shadow-sm"}`}>
      <div className="flex items-center justify-between mb-3 border-b pb-2 border-slate-200/50">
        <div className="flex items-center gap-2">
          <MessageSquare size={16} className="text-emerald-500" />
          <h4 className={`text-xs font-black uppercase tracking-wider ${isDark ? "text-emerald-300" : "text-slate-800"}`}>
            Voice & Multimodal Symptom Diagnostic Assistant
          </h4>
        </div>
        <span className="text-[10px] font-mono font-bold text-cyan-400 bg-cyan-500/10 px-2 py-0.5 rounded border border-cyan-500/20">
          NLP Agronomy Engine
        </span>
      </div>

      <form onSubmit={handleTextSubmit} className="flex gap-2">
        <input
          type="text"
          value={symptomText}
          onChange={(e) => setSymptomText(e.target.value)}
          placeholder="Describe symptoms (e.g. 'water-soaked dark spots' or 'white powdery mold')..."
          className={`flex-1 rounded-xl border p-2.5 text-xs outline-none transition ${
            isDark
              ? "border-emerald-900 bg-emerald-950/60 text-white placeholder-slate-500 focus:border-emerald-500"
              : "border-slate-300 bg-slate-50 text-slate-900 placeholder-slate-400 focus:border-emerald-500"
          }`}
        />

        <button
          type="button"
          onClick={handleVoiceListen}
          className={`p-2.5 rounded-xl border transition flex items-center gap-1 text-xs font-bold ${
            isListening
              ? "bg-red-500 text-white border-red-400 animate-pulse"
              : isDark
              ? "bg-emerald-900/60 text-emerald-300 border-emerald-800 hover:bg-emerald-800"
              : "bg-slate-100 text-slate-700 border-slate-300 hover:bg-slate-200"
          }`}
        >
          {isListening ? <MicOff size={16} /> : <Mic size={16} />}
        </button>

        <button
          type="submit"
          className="flex items-center gap-1.5 rounded-xl bg-emerald-600 px-4 py-2.5 text-xs font-black text-white hover:bg-emerald-700 shadow-md"
        >
          <Sparkles size={14} /> Diagnose
        </button>
      </form>
    </div>
  );
}
