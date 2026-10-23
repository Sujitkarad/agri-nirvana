/**
 * Agri Nirvana - Data.gov.in Agmarknet Market Intelligence Frontend Service.
 * Fetches real-time mandi prices and daily momentum trends (+ / - ₹/quintal)
 * for flagship commodities: Wheat, Onion, Soybean, Cotton, Tomato.
 */

import { MANDI_PRICES_FEED } from "../data/agriData";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "";

/**
 * Fetch live Mandi prices filtered optionally by commodity or state.
 * @param {string} [commodity] - e.g. "Wheat", "Onion", "Soybean", "Cotton", "Tomato"
 * @param {string} [state] - e.g. "Maharashtra"
 * @returns {Promise<{success: boolean, prices: Array, source: string}>}
 */
export async function fetchMandiPrices(commodity = null, state = null) {
  try {
    const params = new URLSearchParams();
    if (commodity && commodity !== "all") params.append("commodity", commodity);
    if (state) params.append("state", state);

    const qs = params.toString() ? `?${params.toString()}` : "";
    const url = `${API_BASE}/api/v1/mandi/prices${qs}`;

    const res = await fetch(url, {
      headers: { "Content-Type": "application/json" },
    });

    if (!res.ok) {
      throw new Error(`HTTP ${res.status}: Failed to fetch mandi prices`);
    }

    const data = await res.json();
    return {
      success: true,
      prices: data.prices || [],
      source: data.prices?.[0]?.source || "agmarknet_api",
      count: data.count || 0,
    };
  } catch (err) {
    console.warn("[mandiService] Live market API unavailable; showing static reference data only:", err);
    // This feed is not live or independently verified. Never synthesize price movement.
    let fallback = MANDI_PRICES_FEED.map((item) => {
      const modal = item.modalPriceINR || null;
      return {
        ...item,
        diffINR: null,
        percentChange: null,
        prevModalPriceINR: null,
        trend: "Reference only — live feed unavailable",
        trendDirection: "unknown",
        priceKg: modal == null ? null : (modal / 100).toFixed(2),
        source: "static_reference_not_live",
        isLive: false,
        dataWarning: "Static reference value, not today's verified mandi price. Confirm with the APMC/Agmarknet before making a sale decision.",
      };
    });

    if (commodity && commodity !== "all") {
      fallback = fallback.filter((f) =>
        f.crop.toLowerCase().includes(commodity.toLowerCase()) ||
        (f.commodity && f.commodity.toLowerCase() === commodity.toLowerCase())
      );
    }

    return {
      success: true,
      prices: fallback,
      source: "static_reference_not_live",
      isLive: false,
      warning: "Live mandi data is unavailable. Values shown are static references, not current prices.",
      count: fallback.length,
    };
  }
}

/**
 * Fetch Mandi market summary statistics.
 */
export async function fetchMandiSummary() {
  try {
    const res = await fetch(`${API_BASE}/api/v1/mandi/summary`);
    if (!res.ok) throw new Error("Failed to fetch mandi summary");
    const data = await res.json();
    return data.summary || null;
  } catch (err) {
    console.warn("[mandiService] Summary API unavailable:", err);
    return null;
  }
}
