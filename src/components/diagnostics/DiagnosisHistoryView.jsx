import React, { useState, useEffect } from "react";
import { History, Filter, Trash2, Calendar, TrendingUp, Sparkles, AlertCircle, ArrowUpRight } from "lucide-react";
import { fetchDiagnosisHistoryApi, deleteDiagnosisItemApi } from "../../services/diagnosisApi";

export default function DiagnosisHistoryView({
  onSelectRecord = () => {},
  onStartNewDiagnosis = () => {},
  isDark = true
}) {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedCropFilter, setSelectedCropFilter] = useState("All");
  const [sortBy, setSortBy] = useState("newest"); // "newest" | "oldest"

  const loadHistory = async () => {
    setLoading(true);
    const res = await fetchDiagnosisHistoryApi(selectedCropFilter);
    if (res && res.history) {
      setHistory(res.history);
    }
    setLoading(false);
  };

  useEffect(() => {
    loadHistory();
  }, [selectedCropFilter]);

  const handleDelete = async (e, id) => {
    e.stopPropagation();
    if (window.confirm("Are you sure you want to delete this diagnosis record from your history?")) {
      await deleteDiagnosisItemApi(id);
      loadHistory();
    }
  };

  const sortedHistory = [...history].sort((a, b) => {
    const timeA = new Date(a.createdAt).getTime();
    const timeB = new Date(b.createdAt).getTime();
    return sortBy === "newest" ? timeB - timeA : timeA - timeB;
  });

  return (
    <div className="space-y-6 animate-fade-in">
      {/* HEADER & CONTROLS */}
      <div className={`rounded-3xl p-6 border flex flex-wrap items-center justify-between gap-4 ${
        isDark ? "border-emerald-800/40 bg-[#072017]" : "border-slate-200 bg-white shadow-xl"
      }`}>
        <div>
          <h2 className="text-xl font-black flex items-center gap-2">
            <History className="text-emerald-400" size={24} />
            My Crop Health History
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Track historical plant health diagnoses, severity timelines, and treatment progress over time.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          {/* CROP FILTER */}
          <div className="flex items-center gap-1.5 text-xs font-bold bg-emerald-950/60 p-1.5 rounded-xl border border-emerald-900/60">
            <Filter size={14} className="text-emerald-400 ml-1" />
            <select
              value={selectedCropFilter}
              onChange={(e) => setSelectedCropFilter(e.target.value)}
              className="bg-transparent text-emerald-300 font-bold outline-none cursor-pointer pr-2"
            >
              <option value="All" className="bg-slate-900 text-white">All Crops</option>
              <option value="Tomato" className="bg-slate-900 text-white">Tomato</option>
              <option value="Potato" className="bg-slate-900 text-white">Potato</option>
              <option value="Cotton" className="bg-slate-900 text-white">Cotton</option>
              <option value="Rice" className="bg-slate-900 text-white">Paddy / Rice</option>
              <option value="Wheat" className="bg-slate-900 text-white">Wheat</option>
            </select>
          </div>

          {/* SORT ORDER */}
          <div className="flex items-center gap-1 text-xs font-bold bg-emerald-950/60 p-1.5 rounded-xl border border-emerald-900/60">
            <button
              onClick={() => setSortBy("newest")}
              className={`px-2.5 py-1 rounded-lg transition ${sortBy === "newest" ? "bg-emerald-600 text-white" : "text-slate-400"}`}
            >
              Newest
            </button>
            <button
              onClick={() => setSortBy("oldest")}
              className={`px-2.5 py-1 rounded-lg transition ${sortBy === "oldest" ? "bg-emerald-600 text-white" : "text-slate-400"}`}
            >
              Oldest
            </button>
          </div>

          <button
            onClick={onStartNewDiagnosis}
            className="flex items-center gap-2 rounded-xl bg-emerald-600 px-4 py-2 text-xs font-black text-white hover:bg-emerald-700 transition shadow"
          >
            <Sparkles size={14} /> Diagnose New Leaf
          </button>
        </div>
      </div>

      {/* DISEASE SEVERITY PROGRESSION MONITORING CHART */}
      {sortedHistory.length > 1 && (
        <div className={`rounded-3xl p-6 border ${isDark ? "border-emerald-800/40 bg-[#072017]" : "border-slate-200 bg-white shadow-xl"}`}>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-black flex items-center gap-2 text-emerald-400">
              <TrendingUp size={18} /> Historical Severity Progression Chart
            </h3>
            <span className="text-[10px] font-mono text-slate-400">Time-Series Comparative Analysis</span>
          </div>

          <div className="h-32 flex items-end justify-between gap-2 pt-6 px-4 border-b border-emerald-900/40">
            {sortedHistory.slice(0, 8).reverse().map((item, idx) => {
              const sev = (item.severity || "Moderate").toLowerCase();
              let heightPct = 50;
              let barColor = "bg-amber-500";
              if (sev === "healthy") { heightPct = 20; barColor = "bg-emerald-500"; }
              if (sev === "low") { heightPct = 35; barColor = "bg-cyan-500"; }
              if (sev === "moderate") { heightPct = 65; barColor = "bg-amber-500"; }
              if (sev === "severe") { heightPct = 95; barColor = "bg-rose-500"; }

              return (
                <div key={item.id} className="flex-1 flex flex-col items-center gap-2 group">
                  <div className="w-full max-w-[36px] rounded-t-lg transition-all duration-500 relative flex items-end justify-center" style={{ height: `${heightPct}%` }}>
                    <div className={`w-full h-full rounded-t-lg ${barColor} opacity-80 group-hover:opacity-100 transition-opacity`} />
                    <span className="absolute -top-5 text-[9px] font-mono font-bold text-emerald-300 opacity-0 group-hover:opacity-100 transition-opacity">
                      {Math.round((item.confidence > 1 ? item.confidence : item.confidence * 100))}%
                    </span>
                  </div>
                  <span className="text-[9px] font-mono text-slate-400 truncate max-w-[48px]">
                    {new Date(item.createdAt).toLocaleDateString(undefined, { month: "numeric", day: "numeric" })}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* HISTORY CARDS GRID */}
      {loading ? (
        <div className="p-12 text-center text-xs text-slate-400 font-mono">Loading diagnosis history...</div>
      ) : sortedHistory.length === 0 ? (
        /* SECTION 22 EMPTY STATE */
        <div className={`rounded-3xl border p-12 text-center space-y-4 ${
          isDark ? "border-emerald-900/40 bg-[#04160f]" : "border-slate-200 bg-slate-50"
        }`}>
          <div className="mx-auto h-16 w-16 rounded-3xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 flex items-center justify-center">
            <History size={32} />
          </div>
          <h3 className="text-lg font-black">No crop diagnoses recorded yet</h3>
          <p className="text-xs text-slate-400 max-w-sm mx-auto">
            Upload your first crop leaf photo to start building your historical crop health timeline.
          </p>
          <button
            onClick={onStartNewDiagnosis}
            className="mt-2 inline-flex items-center gap-2 rounded-xl bg-emerald-600 px-6 py-2.5 text-xs font-black text-white hover:bg-emerald-700 transition shadow-lg shadow-emerald-600/30"
          >
            <Sparkles size={16} /> Diagnose My Crop
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {sortedHistory.map((item) => {
            const confPercent = Math.round(item.confidence > 1 ? item.confidence : item.confidence * 100);
            return (
              <div
                key={item.id}
                onClick={() => onSelectRecord(item)}
                className={`group cursor-pointer rounded-2xl border p-4 transition-all duration-300 relative hover:scale-[1.01] ${
                  isDark ? "border-emerald-900/60 bg-[#04160f] hover:border-emerald-500/60" : "border-slate-200 bg-white hover:border-emerald-400 shadow-sm"
                }`}
              >
                <div className="flex items-start gap-3">
                  <div className="relative h-16 w-16 rounded-xl overflow-hidden bg-slate-950 shrink-0 border border-emerald-900/60">
                    <img src={item.imageUrl} alt={item.crop} className="h-full w-full object-cover group-hover:scale-110 transition-transform duration-500" />
                  </div>

                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] font-black uppercase text-emerald-400">{item.crop}</span>
                      <span className="text-[10px] font-mono text-slate-400 flex items-center gap-1">
                        <Calendar size={10} /> {new Date(item.createdAt).toLocaleDateString()}
                      </span>
                    </div>

                    <h4 className="text-sm font-black text-white truncate mt-0.5">{item.condition}</h4>

                    <div className="flex items-center gap-2 mt-2">
                      <span className="px-2 py-0.5 rounded-md text-[10px] font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                        {confPercent}% Match
                      </span>
                      <span className="text-[10px] font-bold text-slate-400">
                        {item.severity} Severity
                      </span>
                    </div>
                  </div>

                  <button
                    onClick={(e) => handleDelete(e, item.id)}
                    className="opacity-0 group-hover:opacity-100 p-1.5 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-rose-950/40 transition"
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
