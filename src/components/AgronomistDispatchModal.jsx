import React, { useState } from "react";
import { UserCheck, X, Calendar, MapPin, CheckCircle2, PhoneCall, ShieldCheck } from "lucide-react";

export default function AgronomistDispatchModal({ isOpen, onClose, disease, isDark = false }) {
  const [booked, setBooked] = useState(false);
  const [farmerPhone, setFarmerPhone] = useState("+91 98765 43210");
  const [preferredDate, setPreferredDate] = useState("Tomorrow Morning (9:00 AM)");

  if (!isOpen || !disease) return null;

  const handleBookingSubmit = (e) => {
    e.preventDefault();
    setBooked(true);
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
            <UserCheck size={20} className="text-emerald-500" />
            <h3 className="text-base font-black">
              Dispatch Certified Agronomist Field Visit
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
          <div className={`p-3.5 rounded-2xl border flex items-center justify-between ${isDark ? "bg-emerald-950/40 border-emerald-900/50" : "bg-emerald-50 border-emerald-200"}`}>
            <div>
              <span className="text-[10px] font-black uppercase tracking-wider text-emerald-600">Krishi Vigyan Kendra Expert Consultation</span>
              <h4 className="text-sm font-black">{disease.crop} — {disease.diseaseName}</h4>
            </div>
            <span className="rounded-full bg-emerald-500/20 text-emerald-400 text-xs font-bold px-3 py-1 border border-emerald-500/30">
              Verified Agronomist
            </span>
          </div>

          {booked ? (
            <div className="p-6 rounded-2xl bg-emerald-500/20 border border-emerald-500/40 text-center space-y-3">
              <CheckCircle2 size={40} className="text-emerald-400 mx-auto" />
              <h4 className="text-base font-black text-emerald-300">Agronomist Field Visit Dispatched!</h4>
              <p className="text-xs text-slate-300">
                Dr. Rajesh Sharma (Senior Plant Pathologist, Nagpur AgTech Station) will arrive at your field on <strong>{preferredDate}</strong>.
              </p>
              <div className="text-xs font-mono text-emerald-400 bg-black/40 p-2.5 rounded-xl border border-emerald-500/20">
                Confirmation SMS & WhatsApp location pin sent to {farmerPhone}
              </div>
            </div>
          ) : (
            <form onSubmit={handleBookingSubmit} className="space-y-4 text-xs">
              <div>
                <label className="block font-bold text-slate-400 mb-1">Your Mobile Phone Number</label>
                <input
                  type="text"
                  value={farmerPhone}
                  onChange={(e) => setFarmerPhone(e.target.value)}
                  className={`w-full rounded-xl border p-2.5 outline-none font-mono ${
                    isDark ? "border-emerald-900 bg-emerald-950/60 text-white" : "border-slate-300 bg-slate-50 text-slate-900"
                  }`}
                />
              </div>

              <div>
                <label className="block font-bold text-slate-400 mb-1">Preferred Field Visit Schedule</label>
                <select
                  value={preferredDate}
                  onChange={(e) => setPreferredDate(e.target.value)}
                  className={`w-full rounded-xl border p-2.5 outline-none ${
                    isDark ? "border-emerald-900 bg-emerald-950/60 text-white" : "border-slate-300 bg-slate-50 text-slate-900"
                  }`}
                >
                  <option value="Today Evening (4:30 PM)">Today Evening (4:30 PM)</option>
                  <option value="Tomorrow Morning (9:00 AM)">Tomorrow Morning (9:00 AM)</option>
                  <option value="Tomorrow Afternoon (2:00 PM)">Tomorrow Afternoon (2:00 PM)</option>
                </select>
              </div>

              <div className="flex items-center gap-2 text-[11px] font-bold text-emerald-400 bg-emerald-500/10 p-3 rounded-xl border border-emerald-500/20">
                <ShieldCheck size={16} className="shrink-0" />
                <span>Includes soil sample collection kit, microscopic tissue check, and certified ICAR prescription.</span>
              </div>

              <button
                type="submit"
                className="w-full rounded-xl bg-emerald-500 py-3 text-xs font-black text-slate-950 hover:bg-emerald-400 transition shadow-lg shadow-emerald-500/30"
              >
                Confirm Agronomist Field Visit Dispatch
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
