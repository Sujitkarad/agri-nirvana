import React, { useState } from "react";
import { Landmark, X, ShieldCheck, CheckCircle2, Lock, Sparkles, FileText } from "lucide-react";
import { generateKisanCryptographicCertificate } from "../data/agriData";

export default function ParametricClaimModal({ isOpen, onClose, disease, selectedField, isDark = false }) {
  const [claimState, setClaimState] = useState("idle"); // 'idle' | 'filing' | 'claimed'

  if (!isOpen || !disease) return null;

  const cert = generateKisanCryptographicCertificate(disease, selectedField);

  const handleFileClaim = () => {
    setClaimState("filing");
    setTimeout(() => {
      setClaimState("claimed");
    }, 1800);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-fade-in">
      <div
        className={`relative w-full max-w-lg overflow-hidden rounded-3xl border shadow-2xl transition-all ${
          isDark ? "border-emerald-800/60 bg-[#061e15] text-white" : "border-slate-200 bg-white text-slate-900"
        }`}
      >
        {/* HEADER */}
        <div className={`flex items-center justify-between p-4 px-6 border-b ${isDark ? "border-emerald-900/50" : "border-slate-200"}`}>
          <div className="flex items-center gap-2">
            <Landmark size={20} className="text-emerald-500" />
            <h3 className="text-base font-black">
              Parametric Insurance Cryptographic Auto-Claim
            </h3>
          </div>
          <button
            onClick={onClose}
            className={`rounded-full p-2 transition ${isDark ? "hover:bg-emerald-900/40 text-slate-400 hover:text-white" : "hover:bg-slate-100 text-slate-600"}`}
          >
            <X size={18} />
          </button>
        </div>

        {/* BODY */}
        <div className="p-6 space-y-4">
          {/* CERTIFICATE RECAP */}
          <div className={`p-4 rounded-2xl border space-y-2 ${isDark ? "bg-emerald-950/40 border-emerald-900/50" : "bg-emerald-50 border-emerald-200"}`}>
            <div className="flex items-center justify-between font-mono text-[10px] text-emerald-400 font-bold">
              <span>CERT ID: {cert.certId}</span>
              <span className="flex items-center gap-1"><Lock size={10} /> Cryptographic SHA-256 Hash</span>
            </div>
            <div className="text-xs font-mono text-slate-300 break-all bg-black/40 p-2 rounded-lg border border-emerald-500/20">
              {cert.hashHex}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3 text-xs">
            <div className={`p-3 rounded-xl border ${isDark ? "bg-emerald-950/30 border-emerald-900/40" : "bg-slate-50 border-slate-200"}`}>
              <span className="text-[10px] font-bold text-slate-500 block">Diagnosed Pathogen</span>
              <span className="font-bold text-emerald-400">{cert.crop} — {cert.diseaseName}</span>
            </div>
            <div className={`p-3 rounded-xl border ${isDark ? "bg-emerald-950/30 border-emerald-900/40" : "bg-slate-50 border-slate-200"}`}>
              <span className="text-[10px] font-bold text-slate-500 block">Insurance Payout</span>
              <span className="font-mono text-base font-black text-emerald-500">₹{cert.claimPayoutINR}</span>
            </div>
          </div>

          {claimState === "claimed" ? (
            <div className="p-4 rounded-2xl bg-emerald-500/20 border border-emerald-500/40 text-center space-y-2">
              <CheckCircle2 size={36} className="text-emerald-400 mx-auto" />
              <h4 className="text-sm font-black text-emerald-300">PMFBY Parametric Payout Approved!</h4>
              <p className="text-xs text-slate-300">
                ₹18,500 has been initiated for Direct Benefit Transfer (DBT) to your Aadhaar-linked Bank Account.
              </p>
            </div>
          ) : (
            <div className="flex items-center gap-2 text-[11px] font-bold text-emerald-600 dark:text-emerald-400 bg-emerald-500/10 p-3 rounded-xl border border-emerald-500/20">
              <ShieldCheck size={16} className="shrink-0" />
              <span>Parametric trigger criteria met (&gt;15% lesion damage verified by telemetry). Direct benefit transfer ready.</span>
            </div>
          )}
        </div>

        {/* FOOTER */}
        <div className={`p-4 px-6 border-t flex items-center justify-between ${isDark ? "border-emerald-900/50 bg-[#04160f]" : "border-slate-200 bg-slate-50"}`}>
          <button onClick={onClose} className="text-xs font-bold text-slate-400 hover:text-white">Close</button>
          {claimState !== "claimed" && (
            <button
              onClick={handleFileClaim}
              disabled={claimState === "filing"}
              className="flex items-center gap-2 rounded-xl bg-emerald-500 px-6 py-2.5 text-xs font-black text-slate-950 hover:bg-emerald-400 transition shadow-lg shadow-emerald-500/30 disabled:opacity-50"
            >
              {claimState === "filing" ? (
                <>
                  <div className="h-4 w-4 rounded-full border-2 border-slate-950 border-t-transparent animate-spin" />
                  Verifying Smart Contract...
                </>
              ) : (
                <>
                  <Landmark size={15} /> Submit Auto-Claim (₹18,500)
                </>
              )}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
