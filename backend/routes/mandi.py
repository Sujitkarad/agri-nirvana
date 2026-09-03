"""Agri Nirvana - Mandi Prices & Agmarknet Market Intelligence API Route.

Exposes REST endpoints to query real-time Data.gov.in Agmarknet commodity prices
(Wheat, Onion, Soybean, Cotton, Tomato) with daily price trends (+ / - ₹/quintal).
"""

from typing import Any, Dict, List, Optional
import logging
from fastapi import APIRouter, Query, status

from backend.services.agmarknet_service import agmarknet_service, FLAGSHIP_COMMODITIES

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/mandi", tags=["Mandi Market Intelligence & Agmarknet"])


@router.get("/status")
async def get_mandi_status() -> Dict[str, Any]:
    """Check cache status and connection configuration of the Agmarknet Mandi service."""
    return {
        "status": "healthy",
        "provider": "Data.gov.in Agmarknet / e-NAM",
        "commodities_tracked": FLAGSHIP_COMMODITIES,
        "cached_queries_count": len(agmarknet_service._cache),
        "cache_ttl_seconds": agmarknet_service.cache_ttl,
    }


@router.get("/prices")
async def get_mandi_prices(
    commodity: Optional[str] = Query(
        None,
        description="Filter by commodity (e.g., Wheat, Onion, Soybean, Cotton, Tomato)",
    ),
    state: Optional[str] = Query(
        None,
        description="Filter by Indian State (e.g., Maharashtra, Madhya Pradesh, Gujarat)",
    ),
) -> Dict[str, Any]:
    """Retrieve verified Agmarknet mandi commodity prices with daily trends (+ / - ₹/quintal)."""
    prices = await agmarknet_service.fetch_prices(commodity=commodity, state=state)
    return {
        "success": True,
        "count": len(prices),
        "commodity_filter": commodity,
        "state_filter": state,
        "prices": prices,
    }


@router.get("/summary")
async def get_mandi_summary() -> Dict[str, Any]:
    """Retrieve market telemetry summary including top daily price gainer and loser."""
    summary = await agmarknet_service.get_summary_stats()
    return {
        "success": True,
        "summary": summary,
    }
