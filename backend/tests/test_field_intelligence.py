"""Tests for the Precision Field Intelligence Engine router."""

import unittest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


class TestFieldIntelligence(unittest.TestCase):
    def test_field_intelligence_simulated_analysis(self):
        payload = {
            "crop_type": "Cotton",
            "cultivar": "RCH-659 BG II",
            "total_area_ha": 10.50,
            "center_latitude": 20.7453,
            "center_longitude": 78.5621,
            "target_pathogen": "Bacterial Blight / Root Rot",
            "planting_date": "2026-06-15",
            "growth_stage": "Square & Peak Flowering (BBCH 65)",
            "wind_speed_kmh": 8.4,
            "wind_gust_kmh": 12.2,
            "precipitation_prob_pct": 10.0,
            "temperature_c": 31.2,
            "relative_humidity_pct": 82.0,
            "is_simulated": True
        }

        response = client.post("/api/v1/field-intelligence/analyze", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertTrue(data["success"])
        self.assertIn("🟠 SIMULATED", data["provenance"])
        self.assertEqual(data["telemetry_summary"]["crop_type"], "Cotton")
        self.assertEqual(data["telemetry_summary"]["total_area_ha"], 10.50)
        self.assertGreater(data["telemetry_summary"]["total_area_acres"], 25.0)

        # Multispectral & Zoning checks
        self.assertEqual(data["telemetry_summary"]["mean_ndvi"], 0.638)
        self.assertEqual(data["telemetry_summary"]["mean_ndre"], 0.412)
        total_zone_pct = (
            data["telemetry_summary"]["zone_alpha_pct"] +
            data["telemetry_summary"]["zone_beta_pct"] +
            data["telemetry_summary"]["zone_gamma_pct"]
        )
        self.assertEqual(total_zone_pct, 100.0)

        # Drone Flight and GSD calculations
        self.assertLessEqual(data["drone_flight_plan"]["calculated_gsd_cm_px"], 1.5)
        self.assertEqual(len(data["drone_flight_plan"]["waypoints"]), 12)
        self.assertIn("SAFE", data["drone_flight_plan"]["safety_assessment"]["status"])

        # VRA & Resource Savings
        res = data["vra_prescription"]["resource_comparison"]
        self.assertGreater(res["chemical_saved_kg"], 0)
        self.assertGreater(res["chemical_reduction_pct"], 50.0)
        self.assertGreater(res["water_saved_l"], 1000.0)

        # Economic ROI Ledger
        econ = data["economic_ledger_inr"]
        self.assertGreater(econ["gross_savings_inr"], 0)
        self.assertGreater(econ["roi_pct"], 100.0)

    def test_field_intelligence_excessive_wind_safety_check(self):
        payload = {
            "crop_type": "Wheat",
            "total_area_ha": 5.0,
            "center_latitude": 28.6139,
            "center_longitude": 77.2090,
            "wind_speed_kmh": 42.0,  # Dangerous wind
            "wind_gust_kmh": 50.0,
            "precipitation_prob_pct": 5.0,
            "temperature_c": 26.0,
            "relative_humidity_pct": 55.0,
            "is_simulated": True
        }

        response = client.post("/api/v1/field-intelligence/analyze", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()

        safety = data["drone_flight_plan"]["safety_assessment"]
        self.assertEqual(safety["status"], "DO_NOT_FLY")
        self.assertEqual(safety["status_icon"], "🔴")


if __name__ == "__main__":
    unittest.main()
