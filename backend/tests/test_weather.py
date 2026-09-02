"""Unit and integration tests for Agri Nirvana Weather & Agricultural Intelligence."""

import unittest
from unittest.mock import AsyncMock, patch
import httpx
from fastapi.testclient import TestClient

from backend.main import app
from backend.services.ag_weather_rules import evaluate_agricultural_weather
from backend.services.weather_service import WeatherService, weather_service


class TestWeatherServiceAndRules(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        # Clear cache before each test
        weather_service._cache.clear()

    def test_agricultural_rules_good_window(self):
        sample_data = {
            "current": {
                "temperature_c": 26.0,
                "relative_humidity_pct": 55.0,
                "wind_speed_kmh": 8.0,
                "wind_gusts_kmh": 12.0,
                "precipitation_mm": 0.0,
            },
            "daily": [{
                "precipitation_probability_max_pct": 10,
                "rain_sum_mm": 0.0,
                "et0_fao_evapotranspiration_mm": 4.2,
            }],
        }
        signals = evaluate_agricultural_weather(sample_data)
        self.assertEqual(signals["field_activity_window"]["status"], "Good")
        self.assertEqual(signals["field_activity_window"]["level"], "emerald")
        self.assertEqual(signals["rain_outlook"]["level"], "dry")
        self.assertEqual(signals["disease_favorable_weather"]["level"], "low")

    def test_agricultural_rules_poor_window_high_wind(self):
        sample_data = {
            "current": {
                "temperature_c": 28.0,
                "relative_humidity_pct": 60.0,
                "wind_speed_kmh": 22.0,
                "wind_gusts_kmh": 32.0,
                "precipitation_mm": 0.0,
            },
            "daily": [{
                "precipitation_probability_max_pct": 15,
                "rain_sum_mm": 0.0,
                "et0_fao_evapotranspiration_mm": 5.0,
            }],
        }
        signals = evaluate_agricultural_weather(sample_data)
        self.assertEqual(signals["field_activity_window"]["status"], "Poor")
        self.assertEqual(signals["field_activity_window"]["level"], "red")
        self.assertIn("drift", signals["field_activity_window"]["rationale"].lower())

    def test_agricultural_rules_poor_window_heavy_rain(self):
        sample_data = {
            "current": {
                "temperature_c": 23.0,
                "relative_humidity_pct": 88.0,
                "wind_speed_kmh": 10.0,
                "wind_gusts_kmh": 14.0,
                "precipitation_mm": 4.5,
            },
            "daily": [{
                "precipitation_probability_max_pct": 85,
                "rain_sum_mm": 18.0,
                "et0_fao_evapotranspiration_mm": 2.1,
            }],
        }
        signals = evaluate_agricultural_weather(sample_data)
        self.assertEqual(signals["field_activity_window"]["status"], "Poor")
        self.assertEqual(signals["irrigation_check"]["badge"], "Hold")
        self.assertEqual(signals["disease_favorable_weather"]["level"], "elevated")
        self.assertIn("not a disease diagnosis", signals["disease_favorable_weather"]["disclaimer"].lower())

    def test_weather_endpoint_invalid_lat(self):
        response = self.client.get("/api/v1/weather/forecast?lat=120.0&lon=74.47")
        self.assertEqual(response.status_code, 422)

    def test_weather_endpoint_invalid_lon(self):
        response = self.client.get("/api/v1/weather/forecast?lat=19.88&lon=250.0")
        self.assertEqual(response.status_code, 422)

    def test_weather_status_endpoint(self):
        response = self.client.get("/api/v1/weather/status")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["provider"], "Open-Meteo")

    @patch("backend.services.weather_service.WeatherService.fetch_forecast")
    def test_weather_forecast_endpoint_success(self, mock_fetch):
        mock_fetch.return_value = {
            "success": True,
            "location": {
                "name": "Kopargaon, Maharashtra",
                "latitude": 19.8864,
                "longitude": 74.4784,
                "elevation_m": 490.0,
                "timezone": "Asia/Kolkata",
                "timezone_abbreviation": "IST",
            },
            "current": {
                "time": "2026-09-02T12:00",
                "temperature_c": 29.4,
                "apparent_temperature_c": 32.1,
                "relative_humidity_pct": 68.0,
                "precipitation_mm": 0.0,
                "rain_mm": 0.0,
                "weather_code": 1,
                "wind_speed_kmh": 9.2,
                "wind_direction_deg": 280.0,
                "wind_gusts_kmh": 14.5,
            },
            "hourly": [
                {
                    "time": "2026-09-02T12:00",
                    "temperature_c": 29.4,
                    "relative_humidity_pct": 68.0,
                    "precipitation_probability_pct": 10,
                    "precipitation_mm": 0.0,
                    "weather_code": 1,
                    "wind_speed_kmh": 9.2,
                }
            ],
            "daily": [
                {
                    "date": "2026-09-02",
                    "temp_max_c": 31.0,
                    "temp_min_c": 22.0,
                    "precipitation_probability_max_pct": 15,
                    "rain_sum_mm": 0.0,
                    "weather_code": 1,
                    "et0_fao_evapotranspiration_mm": 4.5,
                }
            ],
            "source": {
                "provider": "Open-Meteo",
                "model": "ECMWF / GFS Hybrid Multi-Model",
                "updated_at": "2026-09-02T12:00:00Z",
            },
            "cached": False,
        }

        response = self.client.get("/api/v1/weather/forecast?lat=19.8864&lon=74.4784&location_name=Kopargaon")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertIn("agriculture", data)
        self.assertEqual(data["location"]["name"], "Kopargaon, Maharashtra")
        self.assertEqual(data["current"]["temperature_c"], 29.4)
        self.assertEqual(data["agriculture"]["field_activity_window"]["status"], "Good")

    def test_caching_mechanism(self):
        svc = WeatherService(cache_ttl_seconds=60)
        key = svc._get_cache_key(19.8864, 74.4784)
        svc._set_cache(key, {"test": 123})
        cached = svc._get_from_cache(key)
        self.assertIsNotNone(cached)
        self.assertEqual(cached["test"], 123)


if __name__ == "__main__":
    unittest.main()
