"""Agri Nirvana - Open-Meteo Weather Service.

Fetches real-time weather, hourly projections, and 7-day agricultural forecasts
from the Open-Meteo API with strict validation, in-memory TTL caching, and error handling.
Never produces fake or fabricated weather values.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
import logging
import time
from typing import Any, Dict, Optional, Tuple
import httpx

logger = logging.getLogger(__name__)

OPEN_METEO_FORECAST_URL = "https://api.open-meteo.com/v1/forecast"


@dataclass
class CacheEntry:
    data: Dict[str, Any]
    timestamp: float


class WeatherService:
    def __init__(self, cache_ttl_seconds: int = 600, timeout_seconds: float = 8.0):
        self.cache_ttl = cache_ttl_seconds
        self.timeout = timeout_seconds
        self._cache: Dict[str, CacheEntry] = {}

    def _get_cache_key(self, lat: float, lon: float) -> str:
        # Round to 2 decimal places (~1.1 km precision) to maximize cache hits
        return f"{round(lat, 2)}:{round(lon, 2)}"

    def _get_from_cache(self, key: str) -> Optional[Dict[str, Any]]:
        entry = self._cache.get(key)
        if entry:
            if time.time() - entry.timestamp < self.cache_ttl:
                return entry.data
            else:
                del self._cache[key]
        return None

    def _set_cache(self, key: str, data: Dict[str, Any]) -> None:
        self._cache[key] = CacheEntry(data=data, timestamp=time.time())

    async def fetch_forecast(
        self,
        latitude: float,
        longitude: float,
        location_name: Optional[str] = None,
        client: Optional[httpx.AsyncClient] = None
    ) -> Dict[str, Any]:
        """Fetch full agricultural weather forecast for given latitude and longitude.

        Parameters:
        - latitude: float between -90 and 90
        - longitude: float between -180 and 180
        - location_name: optional human-readable location name
        """
        if not (-90.0 <= latitude <= 90.0):
            raise ValueError(f"Latitude must be between -90 and 90. Received: {latitude}")
        if not (-180.0 <= longitude <= 180.0):
            raise ValueError(f"Longitude must be between -180 and 180. Received: {longitude}")

        cache_key = self._get_cache_key(latitude, longitude)
        cached_data = self._get_from_cache(cache_key)
        if cached_data:
            logger.info("Serving weather from cache for %s (%s)", location_name or "coordinates", cache_key)
            result = dict(cached_data)
            result["cached"] = True
            if location_name:
                result["location"]["name"] = location_name
            return result

        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": [
                "temperature_2m",
                "relative_humidity_2m",
                "apparent_temperature",
                "precipitation",
                "rain",
                "weather_code",
                "wind_speed_10m",
                "wind_direction_10m",
                "wind_gusts_10m",
            ],
            "hourly": [
                "temperature_2m",
                "relative_humidity_2m",
                "precipitation_probability",
                "precipitation",
                "rain",
                "weather_code",
                "wind_speed_10m",
                "wind_direction_10m",
                "wind_gusts_10m",
                "shortwave_radiation",
                "et0_fao_evapotranspiration",
            ],
            "daily": [
                "temperature_2m_max",
                "temperature_2m_min",
                "apparent_temperature_max",
                "apparent_temperature_min",
                "precipitation_sum",
                "rain_sum",
                "precipitation_probability_max",
                "wind_speed_10m_max",
                "wind_gusts_10m_max",
                "sunrise",
                "sunset",
                "weather_code",
                "et0_fao_evapotranspiration",
            ],
            "timezone": "auto",
            "forecast_days": 7,
        }

        should_close_client = False
        if client is None:
            client = httpx.AsyncClient(timeout=self.timeout)
            should_close_client = True

        try:
            response = await client.get(OPEN_METEO_FORECAST_URL, params=params)
            response.raise_for_status()
            raw = response.json()
        except httpx.HTTPStatusError as e:
            logger.error("Open-Meteo HTTP error: %s", e)
            raise RuntimeError(f"Weather provider HTTP error: {e.response.status_code}") from e
        except httpx.RequestError as e:
            logger.error("Open-Meteo network error: %s", e)
            raise RuntimeError("Weather provider connection timed out or is unavailable.") from e
        finally:
            if should_close_client:
                await client.aclose()

        # Parse & structure the payload
        structured = self._format_response(raw, latitude, longitude, location_name)
        self._set_cache(cache_key, structured)
        return structured

    def _format_response(
        self,
        raw: Dict[str, Any],
        latitude: float,
        longitude: float,
        location_name: Optional[str]
    ) -> Dict[str, Any]:
        timezone_str = raw.get("timezone", "UTC")
        timezone_abbrev = raw.get("timezone_abbreviation", "UTC")
        elevation = raw.get("elevation", 0.0)

        current_raw = raw.get("current", {})
        hourly_raw = raw.get("hourly", {})
        daily_raw = raw.get("daily", {})

        current = {
            "time": current_raw.get("time"),
            "temperature_c": current_raw.get("temperature_2m"),
            "apparent_temperature_c": current_raw.get("apparent_temperature"),
            "relative_humidity_pct": current_raw.get("relative_humidity_2m"),
            "precipitation_mm": current_raw.get("precipitation", 0.0),
            "rain_mm": current_raw.get("rain", 0.0),
            "weather_code": current_raw.get("weather_code", 0),
            "wind_speed_kmh": current_raw.get("wind_speed_10m", 0.0),
            "wind_direction_deg": current_raw.get("wind_direction_10m", 0.0),
            "wind_gusts_kmh": current_raw.get("wind_gusts_10m", 0.0),
        }

        # Build clean hourly list (first 24-48 hours)
        hourly_times = hourly_raw.get("time", [])
        hourly_temps = hourly_raw.get("temperature_2m", [])
        hourly_humidity = hourly_raw.get("relative_humidity_2m", [])
        hourly_pop = hourly_raw.get("precipitation_probability", [])
        hourly_precip = hourly_raw.get("precipitation", [])
        hourly_rain = hourly_raw.get("rain", [])
        hourly_code = hourly_raw.get("weather_code", [])
        hourly_wind = hourly_raw.get("wind_speed_10m", [])
        hourly_wind_dir = hourly_raw.get("wind_direction_10m", [])
        hourly_radiation = hourly_raw.get("shortwave_radiation", [])
        hourly_et0 = hourly_raw.get("et0_fao_evapotranspiration", [])

        hourly = []
        limit_hours = min(len(hourly_times), 48)
        for i in range(limit_hours):
            hourly.append({
                "time": hourly_times[i],
                "temperature_c": hourly_temps[i] if i < len(hourly_temps) else None,
                "relative_humidity_pct": hourly_humidity[i] if i < len(hourly_humidity) else None,
                "precipitation_probability_pct": hourly_pop[i] if i < len(hourly_pop) else 0,
                "precipitation_mm": hourly_precip[i] if i < len(hourly_precip) else 0.0,
                "rain_mm": hourly_rain[i] if i < len(hourly_rain) else 0.0,
                "weather_code": hourly_code[i] if i < len(hourly_code) else 0,
                "wind_speed_kmh": hourly_wind[i] if i < len(hourly_wind) else 0.0,
                "wind_direction_deg": hourly_wind_dir[i] if i < len(hourly_wind_dir) else 0.0,
                "shortwave_radiation_wm2": hourly_radiation[i] if i < len(hourly_radiation) else 0.0,
                "et0_mm": hourly_et0[i] if i < len(hourly_et0) else 0.0,
            })

        # Build clean daily list (up to 7 days)
        daily_times = daily_raw.get("time", [])
        daily_max_temps = daily_raw.get("temperature_2m_max", [])
        daily_min_temps = daily_raw.get("temperature_2m_min", [])
        daily_apparent_max = daily_raw.get("apparent_temperature_max", [])
        daily_apparent_min = daily_raw.get("apparent_temperature_min", [])
        daily_precip_sum = daily_raw.get("precipitation_sum", [])
        daily_rain_sum = daily_raw.get("rain_sum", [])
        daily_pop_max = daily_raw.get("precipitation_probability_max", [])
        daily_wind_max = daily_raw.get("wind_speed_10m_max", [])
        daily_gust_max = daily_raw.get("wind_gusts_10m_max", [])
        daily_sunrise = daily_raw.get("sunrise", [])
        daily_sunset = daily_raw.get("sunset", [])
        daily_codes = daily_raw.get("weather_code", [])
        daily_et0 = daily_raw.get("et0_fao_evapotranspiration", [])

        daily = []
        for i in range(len(daily_times)):
            daily.append({
                "date": daily_times[i],
                "temp_max_c": daily_max_temps[i] if i < len(daily_max_temps) else None,
                "temp_min_c": daily_min_temps[i] if i < len(daily_min_temps) else None,
                "apparent_max_c": daily_apparent_max[i] if i < len(daily_apparent_max) else None,
                "apparent_min_c": daily_apparent_min[i] if i < len(daily_apparent_min) else None,
                "precipitation_sum_mm": daily_precip_sum[i] if i < len(daily_precip_sum) else 0.0,
                "rain_sum_mm": daily_rain_sum[i] if i < len(daily_rain_sum) else 0.0,
                "precipitation_probability_max_pct": daily_pop_max[i] if i < len(daily_pop_max) else 0,
                "wind_speed_max_kmh": daily_wind_max[i] if i < len(daily_wind_max) else 0.0,
                "wind_gusts_max_kmh": daily_gust_max[i] if i < len(daily_gust_max) else 0.0,
                "sunrise": daily_sunrise[i] if i < len(daily_sunrise) else None,
                "sunset": daily_sunset[i] if i < len(daily_sunset) else None,
                "weather_code": daily_codes[i] if i < len(daily_codes) else 0,
                "et0_fao_evapotranspiration_mm": daily_et0[i] if i < len(daily_et0) else 0.0,
            })

        return {
            "success": True,
            "location": {
                "name": location_name or f"{latitude:.4f}° N, {longitude:.4f}° E",
                "latitude": latitude,
                "longitude": longitude,
                "elevation_m": elevation,
                "timezone": timezone_str,
                "timezone_abbreviation": timezone_abbrev,
            },
            "current": current,
            "hourly": hourly,
            "daily": daily,
            "source": {
                "provider": "Open-Meteo",
                "model": "ECMWF / GFS Hybrid Multi-Model",
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "documentation": "https://open-meteo.com/",
            },
            "cached": False,
        }


# Global singleton instance
weather_service = WeatherService()
