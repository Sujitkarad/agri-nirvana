import React, { useCallback, useEffect, useMemo, useState } from "react";
import { AlertCircle, ArrowDownRight, ArrowUpRight, RefreshCw, TrendingUp } from "lucide-react";

const COMMODITIES = ["Wheat", "Onion", "Soybean", "Cotton", "Tomato"];
const API_BASE = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8000").replace(/\/$/, "");

function formatPrice(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "—";
  return `₹${Number(value).toLocaleString("en-IN")}`;
}

function Trend({ trend }) {
  if (!trend || trend.change === null) return <span className="text-slate-400">—</span>;
  const up = trend.direction === "up";
  const Icon = up ? ArrowUpRight : ArrowDownRight;
  return (
    <span className={`inline-flex items-center gap-1 font-black ${up ? "text-emerald-500" : "text-rose-500"}`}>
      <Icon size={14} />
      {up ? "+" : "−"}₹{Math.abs(Number(trend.change)).toLocaleString("en-IN")}/q
    </span>
  );
}

export default function LiveMandiPrices({ isDark = true }) {
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");
  const [updatedAt, setUpdatedAt] = useState(null);

  const loadPrices = useCallback(async (manual = false) => {
    if (manual) setRefreshing(true);
    else setLoading(true);
    setError("");
    try {
      const results = await Promise.all(
        COMMODITIES.map(async (commodity) => {
          const response = await fetch(`${API_BASE}/api/v1/market/mandi-prices?commodity=${encodeURIComponent(commodity)}&limit=12`);
          const payload = await response.json();
          if (!response.ok) throw new Error(payload.detail || `Unable to load ${commodity}`);
          return payload.records || [];
        })
      );
      setRows(results.flat());
      setUpdatedAt(new Date());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Mandi feed unavailable");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    loadPrices();
    const timer = window.setInterval(() => loadPrices(), 10 * 60 * 1000);
    return () => window.clearInterval(timer);
  }, [loadPrices]);

  const grouped = useMemo(() => {
    return COMMODITIES.map((commodity) => ({
      commodity,
      records: rows
        .filter((row) => row.commodity?.toLowerCase() === commodity.toLowerCase())
        .sort((a, b) => String(b.arrival_date).localeCompare(String(a.arrival_date)))
        .slice(0, 5),
    }));
  }, [rows]);

  return (
    <section className={`border-b ${isDark ? "border-emerald-500/20 bg-[#020a06]" : "border-slate-200 bg-white"}`}>
      <div className="mx-auto max-w-7xl px-4 py-5 sm:px-6">
        <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
          <div>
            <div className="flex items-center gap-2">
              <TrendingUp size={18} className="text-emerald-500" />
              <h2 className={`text-lg font-black ${isDark ? "text-white" : "text-slate-900"}`}>Live Mandi Prices</h2>
              <span className="rounded-full bg-emerald-500/15 px-2 py-0.5 text-[10px] font-black text-emerald-500">DATA.GOV.IN</span>
            </div>
            <p className={`mt-1 text-xs ${isDark ? "text-slate-400" : "text-slate-500"}`}>
              AGMARKNET daily wholesale observations • modal price • ₹/quintal • change vs previous reported day
            </p>
          </div>
          <button
            type="button"
            onClick={() => loadPrices(true)}
            disabled={loading || refreshing}
            className={`inline-flex items-center gap-2 rounded-xl border px-3 py-2 text-xs font-bold transition ${isDark ? "border-emerald-500/30 bg-emerald-500/10 text-emerald-300 hover:bg-emerald-500/20" : "border-emerald-200 bg-emerald-50 text-emerald-700 hover:bg-emerald-100"}`}
          >
            <RefreshCw size={14} className={refreshing ? "animate-spin" : ""} /> Refresh
          </button>
        </div>

        {error && (
          <div className="mb-4 flex items-center gap-2 rounded-xl border border-amber-500/30 bg-amber-500/10 px-3 py-2 text-xs text-amber-500">
            <AlertCircle size={15} />
            <span>{error}. Add DATA_GOV_IN_API_KEY to the backend environment.</span>
          </div>
        )}

        {loading && !rows.length ? (
          <div className={`rounded-2xl border p-8 text-center text-sm ${isDark ? "border-emerald-500/15 text-slate-400" : "border-slate-200 text-slate-500"}`}>
            Loading government mandi data…
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-3 lg:grid-cols-2 xl:grid-cols-3">
            {grouped.map(({ commodity, records }) => (
              <div key={commodity} className={`rounded-2xl border overflow-hidden ${isDark ? "border-emerald-500/15 bg-emerald-950/20" : "border-slate-200 bg-white shadow-sm"}`}>
                <div className={`flex items-center justify-between px-4 py-3 border-b ${isDark ? "border-emerald-500/10" : "border-slate-100"}`}>
                  <span className={`font-black ${isDark ? "text-white" : "text-slate-900"}`}>{commodity}</span>
                  <span className="text-[10px] font-bold text-slate-400">{records.length} mandis</span>
                </div>
                <div className="divide-y divide-slate-500/10">
                  {records.length === 0 ? (
                    <div className="px-4 py-4 text-xs text-slate-500">No current record returned.</div>
                  ) : records.map((row, index) => (
                    <div key={`${row.market}-${row.variety}-${row.grade}-${row.arrival_date}-${index}`} className="px-4 py-3">
                      <div className="flex items-start justify-between gap-3">
                        <div className="min-w-0">
                          <div className={`truncate text-xs font-black ${isDark ? "text-slate-100" : "text-slate-800"}`}>{row.market}</div>
                          <div className="mt-0.5 truncate text-[10px] text-slate-500">{row.district}{row.state ? `, ${row.state}` : ""} • {row.arrival_date}</div>
                        </div>
                        <div className="text-right shrink-0">
                          <div className={`text-sm font-black ${isDark ? "text-emerald-300" : "text-emerald-700"}`}>{formatPrice(row.modal_price)}/q</div>
                          <div className="mt-0.5 text-[10px]"><Trend trend={row.trend} /></div>
                        </div>
                      </div>
                      <div className="mt-1.5 flex gap-3 text-[9px] text-slate-500">
                        <span>Min {formatPrice(row.min_price)}</span>
                        <span>Max {formatPrice(row.max_price)}</span>
                        {row.variety && <span className="truncate">{row.variety}</span>}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}

        <div className="mt-3 flex flex-wrap items-center justify-between gap-2 text-[10px] text-slate-500">
          <span>Source: Government of India Open Government Data / AGMARKNET. This is daily reported wholesale data, not an executable live quote.</span>
          {updatedAt && <span>Fetched {updatedAt.toLocaleTimeString("en-IN")}</span>}
        </div>
      </div>
    </section>
  );
}
