import React, { useState } from "react";
import { Cpu, X, Download, CheckCircle2, ShieldCheck, Zap, Layers } from "lucide-react";
import { generateDroneMavLinkMission } from "../data/agriData";

export default function DroneMissionGeneratorModal({ isOpen, onClose, disease, isDark = false }) {
  const [fileFormat, setFileFormat] = useState("mavlink"); // 'mavlink' | 'kml' | 'gcode'
  const [acres, setAcres] = useState(2.5);

  if (!isOpen || !disease) return null;

  const mission = generateDroneMavLinkMission(disease.crop, acres, disease.diseaseName);

  const downloadFile = (content, filename, type) => {
    const blob = new Blob([content], { type });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleExport = () => {
    if (fileFormat === "mavlink") {
      downloadFile(mission.mavlinkString, `drone_spot_spray_${disease.crop.toLowerCase()}.waypoint`, "text/plain");
    } else if (fileFormat === "kml") {
      downloadFile(mission.kmlString, `drone_spot_spray_${disease.crop.toLowerCase()}.kml`, "application/vnd.google-earth.kml+xml");
    } else if (fileFormat === "gcode") {
      downloadFile(mission.gcodeString, `drone_spot_spray_${disease.crop.toLowerCase()}.gcode`, "text/plain");
    }
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
            <Cpu size={20} className="text-emerald-500" />
            <h3 className="text-base font-black">
              Autonomous Drone Spot-Spraying Mission Generator
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
          <div className={`p-4 rounded-2xl border flex items-center justify-between ${isDark ? "bg-emerald-950/40 border-emerald-900/50" : "bg-emerald-50 border-emerald-200"}`}>
            <div>
              <span className="text-[10px] font-black uppercase tracking-wider text-emerald-600">Spot-Spraying Flight Target</span>
              <h4 className="text-sm font-black">{disease.crop} — {disease.diseaseName}</h4>
            </div>
            <span className="rounded-full bg-emerald-500/20 text-emerald-400 text-xs font-bold px-3 py-1 border border-emerald-500/30">
              68% Chemical Reduction
            </span>
          </div>

          {/* SAVINGS MATRIX */}
          <div className="grid grid-cols-2 gap-3 text-center">
            <div className={`p-3 rounded-xl border ${isDark ? "bg-emerald-950/30 border-emerald-900/40" : "bg-slate-50 border-slate-200"}`}>
              <span className="text-[10px] font-bold text-slate-500 block">Spot-Spray Volume</span>
              <span className="text-lg font-black text-emerald-500 font-mono">{mission.spotSprayLiters} L</span>
              <span className="text-[10px] text-slate-400 block line-through">Full Spray: {mission.fullSprayLiters} L</span>
            </div>
            <div className={`p-3 rounded-xl border ${isDark ? "bg-emerald-950/30 border-emerald-900/40" : "bg-slate-50 border-slate-200"}`}>
              <span className="text-[10px] font-bold text-slate-500 block">Cost Savings</span>
              <span className="text-lg font-black text-emerald-400 font-mono">₹{mission.savingsINR}</span>
              <span className="text-[10px] text-emerald-500 font-bold block">68% Less Chemical</span>
            </div>
          </div>

          {/* FILE FORMAT SELECTOR */}
          <div>
            <label className="text-xs font-bold uppercase tracking-wider text-slate-500 block mb-2">
              Select Drone Flight Control System Format:
            </label>
            <div className="grid grid-cols-3 gap-2">
              {[
                { id: "mavlink", label: "MavLink .WAYPOINT", sub: "ArduPilot / QGC" },
                { id: "kml", label: "KML Polygon", sub: "DJI Agras / Terra" },
                { id: "gcode", label: "G-Code Spray", sub: "Custom Spray UAV" },
              ].map(({ id, label, sub }) => (
                <button
                  key={id}
                  onClick={() => setFileFormat(id)}
                  className={`p-2.5 rounded-xl border text-left transition ${
                    fileFormat === id
                      ? "border-emerald-500 bg-emerald-500/20 text-emerald-300"
                      : isDark
                      ? "border-emerald-900/50 bg-emerald-950/30 text-slate-400"
                      : "border-slate-200 bg-slate-50 text-slate-700"
                  }`}
                >
                  <div className="text-xs font-bold">{label}</div>
                  <div className="text-[10px] opacity-75">{sub}</div>
                </button>
              ))}
            </div>
          </div>

          <div className="flex items-center gap-2 text-[11px] font-bold text-emerald-600 dark:text-emerald-400 bg-emerald-500/10 p-3 rounded-xl border border-emerald-500/20">
            <ShieldCheck size={16} className="shrink-0" />
            <span>Flight plan optimized for 5m altitude with nozzle flow control locked to sub-zone coordinates.</span>
          </div>
        </div>

        {/* FOOTER */}
        <div className={`p-4 px-6 border-t flex items-center justify-between ${isDark ? "border-emerald-900/50 bg-[#04160f]" : "border-slate-200 bg-slate-50"}`}>
          <button onClick={onClose} className="text-xs font-bold text-slate-400 hover:text-white">Cancel</button>
          <button
            onClick={handleExport}
            className="flex items-center gap-2 rounded-xl bg-emerald-500 px-6 py-2.5 text-xs font-black text-slate-950 hover:bg-emerald-400 transition shadow-lg shadow-emerald-500/30"
          >
            <Download size={15} /> Export {fileFormat.toUpperCase()} Mission
          </button>
        </div>
      </div>
    </div>
  );
}
