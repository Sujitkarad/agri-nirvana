import React, { useState, useEffect, useMemo } from "react";
import {
  TrendingUp,
  TrendingDown,
  Minus,
  RefreshCw,
  Search,
  MapPin,
  Clock,
  Award,
  PlusCircle,
  Building2,
  CheckCircle2,
  ArrowUpRight,
  ArrowDownRight,
  SlidersHorizontal,
} from "lucide-react";
import { fetchMandiPrices, fetchMandiSummary } from "../../services/mandiService";

const COMMODITY_TABS = [
  { id: "all", label: "All Commodities", icon: "🌾" },
  { id: "Wheat", label: "Wheat (गहू)", icon: "🌾" },
  { id: "Onion", label: "Onion (कांदा)", icon: "🧅" },
  { id: "Soybean", label: "Soybean (सोयाबीन)", icon: "🌱" },
  { id: "Cotton", label: "Cotton (कापूस)", icon: "☁️" },
  { id: "Tomato", label: "Tomato (टोमॅटो)", icon: "🍅" },
];

export default function LiveMandiMarketView({
  isDark = true,
  t = {},
  produceFormCrop,
  setProduceFormCrop,
  produceQuantity,
  setProduceQuantity,
  produceExpectedPrice,
  setProduceExpectedPrice,
  produceFormQty,
  setProduceFormQty,
  produceFormPrice,
  setProduceFormPrice,
  produceMandi,
  setProduceMandi,
  handleProduceSubmit,
  produceSuccess,
}) {
  const [selectedCommodity, setSelectedCommodity] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [prices, setPrices] = useState([]);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState("");
  const [dataSource, setDataSource] = useState("agmarknet_verified");
  const [localMandiTarget, setLocalMandiTarget] = useState("Kopargaon APMC Main Yard");

  const qtyValue = produceQuantity !== undefined ? produceQuantity : (produceFormQty !== undefined ? produceFormQty : 25);
  const handleQtyChange = (val) => {
    if (setProduceQuantity) setProduceQuantity(val);
    if (setProduceFormQty) setProduceFormQty(Number(val));
  };

  const priceValue = produceExpectedPrice !== undefined ? produceExpectedPrice : (produceFormPrice !== undefined ? produceFormPrice : 3200);
  const handlePriceChange = (val) => {
    if (setProduceExpectedPrice) setProduceExpectedPrice(val);
    if (setProduceFormPrice) setProduceFormPrice(Number(val));
  };

  const mandiTargetValue = produceMandi !== undefined ? produceMandi : localMandiTarget;
  const handleMandiChange = (val) => {
    if (setProduceMandi) setProduceMandi(val);
    setLocalMandiTarget(val);
  };

  const loadData = async (comm = selectedCommodity) => {
    setLoading(true);
    try {
      const [priceRes, summaryRes] = await Promise.all([
        fetchMandiPrices(comm === "all" ? null : comm),
        fetchMandiSummary(),
      ]);
      if (priceRes.success) {
        setPrices(priceRes.prices);
        setDataSource(priceRes.source);
      }
      if (summaryRes) {
        setSummary(summaryRes);
      }
      setLastUpdated(new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }));
    } catch (err) {
      console.error("Error loading mandi feed:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData(selectedCommodity);
  }, [selectedCommodity]);

  const filteredPrices = useMemo(() => {
    return prices.filter((p) => {
      const matchesSearch =
        searchQuery === "" ||
        p.mandiName.toLowerCase().includes(searchQuery.toLowerCase()) ||
        p.crop.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (p.district && p.district.toLowerCase().includes(searchQuery.toLowerCase())) ||
        (p.state && p.state.toLowerCase().includes(searchQuery.toLowerCase()));
      return matchesSearch;
    });
  }, [prices, searchQuery]);

  const bestMandiItem = useMemo(() => {
    return prices.find((m) => m.isBestPrice) || prices[0] || null;
  }, [prices]);

  return (
    <div className="space-y-6">
      {/* MAIN CONTAINER */}
      <div
        className={`rounded-3xl p-6 border transition-all ${
          isDark
            ? "border-emerald-800/40 bg-[#072017]"
            : "border-slate-200 bg-white shadow-xl"
        }`}
      >
        {/* HEADER */}
        <div className="flex flex-wrap items-center justify-between gap-4 mb-6">
          <div>
            <div className="flex items-center gap-2.5">
              <div className="h-9 w-9 rounded-xl bg-emerald-500/20 text-emerald-400 flex items-center justify-center">
                <TrendingUp size={22} />
              </div>
              <div>
                <h2
                  className={`text-xl font-black flex items-center gap-2 ${
                    isDark ? "text-white" : "text-slate-900"
                  }`}
                >
                  {t.mandiTitle || "Data.gov.in Agmarknet & e-NAM Live Mandi Telemetry"}
                </h2>
                <div className="flex flex-wrap items-center gap-2 mt-0.5">
                  <span className="inline-flex items-center gap-1 text-[11px] font-mono text-emerald-400">
                    <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
                    Open Government Data (Agmarknet Portal)
                  </span>
                  <span className="text-slate-500">•</span>
                  <span className={`text-[11px] font-mono ${isDark ? "text-slate-400" : "text-slate-600"}`}>
                    Updated {lastUpdated || "Just now"}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {/* Refresh Button */}
            <button
              onClick={() => loadData(selectedCommodity)}
              disabled={loading}
              className={`flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-bold transition border ${
                isDark
                  ? "border-emerald-900/60 bg-[#04160f] text-emerald-300 hover:border-emerald-500"
                  : "border-slate-300 bg-slate-100 text-slate-700 hover:bg-slate-200"
              }`}
              title="Refresh live mandi rates"
            >
              <RefreshCw size={14} className={loading ? "animate-spin text-emerald-400" : ""} />
              <span>Refresh</span>
            </button>

            {/* Best Regional Price Spotlight */}
            {bestMandiItem && (
              <div
                className={`rounded-2xl border p-3 text-xs flex items-center gap-3 ${
                  isDark
                    ? "border-emerald-500/40 bg-emerald-500/10 text-emerald-400"
                    : "border-emerald-300 bg-emerald-50 text-emerald-900 shadow-xs"
                }`}
              >
                <Award size={22} className="shrink-0 text-emerald-500" />
                <div>
                  <p className={`font-black ${isDark ? "text-white" : "text-slate-900"}`}>
                    {t.bestPriceToday || "Top Benchmark"}: {bestMandiItem.mandiName}
                  </p>
                  <p className="text-[11px] font-mono">
                    {bestMandiItem.commodity} @ ₹{bestMandiItem.modalPriceINR} {bestMandiItem.unit} (
                    <span className="text-emerald-400 font-bold">{bestMandiItem.trend}</span>)
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* MARKET SUMMARY STATS BAR */}
        {summary && (
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-6">
            <div
              className={`rounded-2xl border p-3.5 ${
                isDark ? "border-emerald-900/60 bg-[#04160f]" : "border-slate-200 bg-slate-50"
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="text-[11px] uppercase font-bold tracking-wider text-slate-400">
                  Top Daily Price Surge
                </span>
                <span className="h-6 w-6 rounded-lg bg-emerald-500/20 text-emerald-400 flex items-center justify-center">
                  <ArrowUpRight size={14} />
                </span>
              </div>
              {summary.top_gainer ? (
                <div className="mt-1">
                  <p className={`text-sm font-bold truncate ${isDark ? "text-white" : "text-slate-900"}`}>
                    {summary.top_gainer.crop}
                  </p>
                  <div className="flex items-center gap-2 mt-0.5">
                    <span className="text-xs font-mono font-black text-emerald-400">
                      + ₹{summary.top_gainer.diffINR}/Qtl
                    </span>
                    <span className="text-[10px] text-slate-400">({summary.top_gainer.mandiName})</span>
                  </div>
                </div>
              ) : (
                <p className="text-xs text-slate-400 mt-1">Rates stable</p>
              )}
            </div>

            <div
              className={`rounded-2xl border p-3.5 ${
                isDark ? "border-emerald-900/60 bg-[#04160f]" : "border-slate-200 bg-slate-50"
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="text-[11px] uppercase font-bold tracking-wider text-slate-400">
                  Active APMC Yards
                </span>
                <span className="h-6 w-6 rounded-lg bg-cyan-500/20 text-cyan-400 flex items-center justify-center">
                  <Building2 size={14} />
                </span>
              </div>
              <div className="mt-1">
                <p className={`text-xl font-mono font-black ${isDark ? "text-white" : "text-slate-900"}`}>
                  {summary.total_mandis} Trading Yards
                </p>
                <p className="text-[10px] text-slate-400 mt-0.5">Maharashtra, MP, Gujarat, Punjab, Karnataka</p>
              </div>
            </div>

            <div
              className={`rounded-2xl border p-3.5 ${
                isDark ? "border-emerald-900/60 bg-[#04160f]" : "border-slate-200 bg-slate-50"
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="text-[11px] uppercase font-bold tracking-wider text-slate-400">
                  Data.gov.in Feed Status
                </span>
                <span className="h-6 w-6 rounded-lg bg-emerald-500/20 text-emerald-400 flex items-center justify-center">
                  <CheckCircle2 size={14} />
                </span>
              </div>
              <div className="mt-1">
                <p className="text-xs font-bold text-emerald-400 flex items-center gap-1">
                  <span className="h-2 w-2 rounded-full bg-emerald-400 animate-ping" />
                  AGMARKNET / e-NAM Linked
                </p>
                <p className="text-[10px] text-slate-400 mt-0.5">Daily Modal & Trend Differential Active</p>
              </div>
            </div>
          </div>
        )}

        {/* COMMODITY FILTER TABS & SEARCH BAR */}
        <div className="flex flex-col md:flex-row items-stretch md:items-center justify-between gap-3 mb-6">
          {/* Commodity Tabs */}
          <div className="flex overflow-x-auto gap-2 pb-1 no-scrollbar">
            {COMMODITY_TABS.map((tab) => {
              const isActive = selectedCommodity === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setSelectedCommodity(tab.id)}
                  className={`px-3.5 py-2 rounded-xl text-xs font-bold whitespace-nowrap transition flex items-center gap-1.5 border ${
                    isActive
                      ? isDark
                        ? "border-emerald-500 bg-emerald-500/20 text-emerald-300 shadow-sm"
                        : "border-emerald-600 bg-emerald-600 text-white shadow-sm"
                      : isDark
                      ? "border-emerald-900/60 bg-[#04160f] text-slate-400 hover:text-white hover:border-emerald-700"
                      : "border-slate-200 bg-white text-slate-600 hover:border-slate-300"
                  }`}
                >
                  <span>{tab.icon}</span>
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </div>

          {/* Search Input */}
          <div className="relative shrink-0 md:w-72">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={14} />
            <input
              type="text"
              placeholder="Search mandi yard, district..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className={`w-full pl-9 pr-3 py-2 rounded-xl text-xs outline-none border transition ${
                isDark
                  ? "border-emerald-900/60 bg-[#04160f] text-white placeholder-slate-500 focus:border-emerald-500"
                  : "border-slate-300 bg-white text-slate-800 placeholder-slate-400 focus:border-emerald-600"
              }`}
            />
          </div>
        </div>

        {/* MANDI CARDS GRID */}
        {loading ? (
          <div className="py-16 text-center">
            <RefreshCw className="animate-spin text-emerald-500 mx-auto mb-3" size={28} />
            <p className="text-sm font-mono text-emerald-400">Querying Agmarknet Data.gov.in price telemetry...</p>
          </div>
        ) : filteredPrices.length === 0 ? (
          <div className="py-12 text-center text-slate-400 text-xs">
            No mandi records match your filter. Try clearing the search or selecting "All Commodities".
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-4">
            {filteredPrices.map((mandi) => {
              const isUp = mandi.trendDirection === "up";
              const isDown = mandi.trendDirection === "down";

              return (
                <div
                  key={mandi.id}
                  className={`rounded-2xl border p-4.5 flex flex-col justify-between transition-all duration-300 hover:shadow-lg ${
                    isDark
                      ? "border-emerald-900/60 bg-[#04160f] hover:border-emerald-500/60"
                      : "border-slate-200 bg-white shadow-xs hover:border-emerald-500"
                  }`}
                >
                  {/* Top Row: Crop Name & Daily Trend Badge */}
                  <div>
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="text-[10px] font-bold text-emerald-400 uppercase tracking-wider bg-emerald-500/10 px-2 py-0.5 rounded-md border border-emerald-500/20">
                            {mandi.commodity}
                          </span>
                          {mandi.isBestPrice && (
                            <span className="text-[9px] font-black uppercase tracking-wider bg-amber-500/20 text-amber-300 border border-amber-500/30 px-1.5 py-0.5 rounded">
                              ⭐ Regional Peak
                            </span>
                          )}
                        </div>
                        <h3 className={`font-black text-base mt-1.5 ${isDark ? "text-white" : "text-slate-900"}`}>
                          {mandi.mandiName}
                        </h3>
                        <p className={`text-xs mt-0.5 font-medium ${isDark ? "text-slate-400" : "text-slate-600"}`}>
                          {mandi.crop}
                        </p>
                      </div>

                      {/* Daily Trend Pill with +/- ₹/Qtl */}
                      <div className="text-right shrink-0">
                        <div
                          className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-mono font-bold border ${
                            isUp
                              ? "bg-emerald-500/15 text-emerald-400 border-emerald-500/30"
                              : isDown
                              ? "bg-rose-500/15 text-rose-400 border-rose-500/30"
                              : "bg-slate-500/15 text-slate-400 border-slate-500/30"
                          }`}
                        >
                          {isUp ? (
                            <TrendingUp size={13} className="text-emerald-400" />
                          ) : isDown ? (
                            <TrendingDown size={13} className="text-rose-400" />
                          ) : (
                            <Minus size={13} className="text-slate-400" />
                          )}
                          <span>{mandi.trend}</span>
                        </div>
                        <span className="text-[10px] text-slate-500 font-mono block mt-1">24h Momentum</span>
                      </div>
                    </div>

                    {/* Yard Details */}
                    <div className="mt-3 flex flex-wrap items-center gap-3 text-xs text-slate-400">
                      <span className="flex items-center gap-1">
                        <MapPin size={12} className="text-emerald-400" />
                        {mandi.district}, {mandi.state}
                      </span>
                      {mandi.distanceKm > 0 && (
                        <span>• {mandi.distanceKm} km away</span>
                      )}
                      {mandi.bestSellingWindow && (
                        <span className="flex items-center gap-1 font-mono text-[11px] text-amber-400/90">
                          <Clock size={11} /> {mandi.bestSellingWindow}
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Bottom Row: Price Matrix and Range */}
                  <div
                    className={`mt-4 pt-3 border-t flex flex-wrap items-end justify-between gap-3 ${
                      isDark ? "border-emerald-900/40" : "border-slate-100"
                    }`}
                  >
                    <div>
                      <div className="flex items-baseline gap-1.5">
                        <span className="text-2xl font-mono font-black text-emerald-400">
                          ₹{mandi.modalPriceINR.toLocaleString()}
                        </span>
                        <span className="text-[11px] text-slate-400 font-mono">/ Quintal</span>
                        <span className="text-[11px] font-mono text-slate-500">
                          (₹{mandi.priceKg}/kg)
                        </span>
                      </div>
                      <p className="text-[10px] font-mono text-slate-400 mt-0.5">
                        Trading Range: <span className="font-bold text-slate-300">₹{mandi.minPriceINR.toLocaleString()}</span> – <span className="font-bold text-slate-300">₹{mandi.maxPriceINR.toLocaleString()}</span>
                      </p>
                    </div>

                    <div className="text-right">
                      {mandi.arrival && (
                        <div className="text-xs font-mono">
                          <span className="text-[10px] text-slate-400 block">Daily Arrivals</span>
                          <span className={`font-bold ${isDark ? "text-emerald-300" : "text-emerald-800"}`}>
                            {mandi.arrival}
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* PRODUCE LISTING FORM */}
        <div
          className={`mt-8 rounded-2xl border p-6 ${
            isDark ? "border-emerald-900/60 bg-[#04160f]" : "border-slate-200 bg-slate-50"
          }`}
        >
          <h3
            className={`text-base font-black mb-4 flex items-center gap-2 ${
              isDark ? "text-white" : "text-slate-900"
            }`}
          >
            <PlusCircle size={18} className="text-emerald-500" />
            {t.listProduce || "List Your Produce on e-NAM / Direct Buyer Channel"}
          </h3>
          <form onSubmit={handleProduceSubmit} className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
            <div>
              <label className="block font-bold mb-1">Crop Type</label>
              <select
                value={produceFormCrop}
                onChange={(e) => setProduceFormCrop(e.target.value)}
                className={`w-full rounded-xl border p-2.5 outline-none font-bold ${
                  isDark
                    ? "border-emerald-900 bg-[#04160f] text-white"
                    : "border-slate-300 bg-white text-slate-800"
                }`}
              >
                <option value="Wheat">Wheat (गहू / Lokwan, Sharbati)</option>
                <option value="Onion">Onion (लाल कांदा / Nashik Red)</option>
                <option value="Soybean">Soybean (पिवळा सोयाबीन / JS-335)</option>
                <option value="Cotton">Cotton (कापूस / Shankar-6)</option>
                <option value="Tomato">Tomato (टोमॅटो / Desi / Hybrid)</option>
                <option value="Sugarcane">Sugarcane (ऊस / Co 86032)</option>
                <option value="Maize">Maize (पिवळी मका)</option>
                <option value="Pomegranate">Pomegranate (भगवा डाळिंब)</option>
                <option value="Chickpea">Chickpea / Gram (हरभरा)</option>
              </select>
            </div>
            <div>
              <label className="block font-bold mb-1">Quantity (Quintals)</label>
              <input
                type="number"
                min="1"
                step="0.5"
                placeholder="e.g. 50"
                value={qtyValue}
                onChange={(e) => handleQtyChange(e.target.value)}
                className={`w-full rounded-xl border p-2.5 outline-none font-bold ${
                  isDark
                    ? "border-emerald-900 bg-[#04160f] text-white"
                    : "border-slate-300 bg-white text-slate-800"
                }`}
                required
              />
            </div>
            <div>
              <label className="block font-bold mb-1">Expected Price (₹ / Quintal)</label>
              <input
                type="number"
                min="100"
                placeholder="e.g. 2600"
                value={priceValue}
                onChange={(e) => handlePriceChange(e.target.value)}
                className={`w-full rounded-xl border p-2.5 outline-none font-bold ${
                  isDark
                    ? "border-emerald-900 bg-[#04160f] text-white"
                    : "border-slate-300 bg-white text-slate-800"
                }`}
                required
              />
            </div>
            <div className="sm:col-span-2">
              <label className="block font-bold mb-1">Target APMC Trading Yard</label>
              <input
                type="text"
                placeholder="e.g. Kopargaon APMC Main Yard / Lasalgaon APMC"
                value={mandiTargetValue}
                onChange={(e) => handleMandiChange(e.target.value)}
                className={`w-full rounded-xl border p-2.5 outline-none font-bold ${
                  isDark
                    ? "border-emerald-900 bg-[#04160f] text-white"
                    : "border-slate-300 bg-white text-slate-800"
                }`}
                required
              />
            </div>
            <div className="sm:col-span-1 flex items-end">
              <button
                type="submit"
                className="w-full rounded-xl bg-emerald-500 px-4 py-2.5 font-black text-slate-950 hover:bg-emerald-400 transition shadow-md glow-emerald cursor-pointer"
              >
                {t.submitListing || "Submit Listing"}
              </button>
            </div>
          </form>

          {produceSuccess && (
            <div className="mt-4 rounded-xl border border-emerald-500/40 bg-emerald-500/15 p-3 text-xs text-emerald-400 font-bold animate-fade-in flex items-center gap-2">
              <CheckCircle2 size={16} />
              <span>{produceSuccess}</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
