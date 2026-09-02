"""Agri Nirvana - Weather & Agricultural Intelligence API Route.

Exposes REST endpoints to query real-time Open-Meteo forecasts combined with
deterministic agricultural rules for crop management, spray windows, and irrigation checks.
"""

from typing import Any, Dict, Optional
import logging
from fastapi import APIRouter, HTTPException, Query, status

from backend.services.ag_weather_rules import evaluate_agricultural_weather
from backend.services.weather_service import weather_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/weather", tags=["Farm Weather Intelligence"])


@router.get("/status")
async def get_weather_status() -> Dict[str, Any]:
    """Check health and cache status of the weather service."""
    return {
        "status": "healthy",
        "provider": "Open-Meteo",
        "cached_locations_count": len(weather_service._cache),
        "cache_ttl_seconds": weather_service.cache_ttl,
    }


@router.get("/forecast")
async def get_weather_forecast(
    lat: float = Query(
        19.8864,
        ge=-90.0,
        le=90.0,
        description="Latitude in WGS 84 (default: Kopargaon, Maharashtra)",
    ),
    lon: float = Query(
        74.4784,
        ge=-180.0,
        le=180.0,
        description="Longitude in WGS 84 (default: Kopargaon, Maharashtra)",
    ),
    location_name: Optional[str] = Query(
        "Kopargaon, Maharashtra",
        description="Display name for the selected locality or farm",
    ),
) -> Dict[str, Any]:
    """Retrieve full agricultural weather forecast including current conditions,

    hourly predictions, 7-day outlook, and agronomic management signals.
    """
    try:
        raw_weather = await weather_service.fetch_forecast(
            latitude=lat,
            longitude=lon,
            location_name=location_name,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )
    except RuntimeError as e:
        logger.error("Weather service runtime failure: %s", e)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Weather service temporarily unavailable: {str(e)}",
        )
    except Exception as e:
        logger.exception("Unexpected error fetching weather: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve weather forecast.",
        )

    # Attach agricultural intelligence interpretation
    agriculture_signals = evaluate_agricultural_weather(raw_weather)
    raw_weather["agriculture"] = agriculture_signals
    return raw_weather
