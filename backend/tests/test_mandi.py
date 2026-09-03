"""Unit tests for Mandi Agmarknet price service and API routes."""

import unittest
from fastapi.testclient import TestClient
from backend.main import app
from backend.services.agmarknet_service import agmarknet_service, FLAGSHIP_COMMODITIES


class TestMandiAgmarknet(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_mandi_status_endpoint(self):
        """Test GET /api/v1/mandi/status returns healthy status."""
        response = self.client.get("/api/v1/mandi/status")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertIn("Data.gov.in", data["provider"])
        self.assertListEqual(data["commodities_tracked"], FLAGSHIP_COMMODITIES)

    def test_mandi_prices_all(self):
        """Test GET /api/v1/mandi/prices returns records with daily trends."""
        response = self.client.get("/api/v1/mandi/prices")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertGreater(data["count"], 0)

        # Check required fields and daily trends on each record
        for item in data["prices"]:
            self.assertIn("commodity", item)
            self.assertIn("mandiName", item)
            self.assertIn("modalPriceINR", item)
            self.assertIn("diffINR", item)
            self.assertIn("percentChange", item)
            self.assertIn("trend", item)
            self.assertIn("trendDirection", item)
            self.assertIn(item["trendDirection"], ["up", "down", "stable"])
            self.assertIn("₹", item["trend"])
            self.assertIn("Qtl", item["trend"])

    def test_mandi_prices_filtered_commodity(self):
        """Test filtering by each flagship commodity (Wheat, Onion, Soybean, Cotton, Tomato)."""
        for comm in FLAGSHIP_COMMODITIES:
            response = self.client.get(f"/api/v1/mandi/prices?commodity={comm}")
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertTrue(data["success"])
            self.assertGreater(data["count"], 0, f"Expected records for {comm}")
            for item in data["prices"]:
                self.assertEqual(item["commodity"].lower(), comm.lower())

    def test_mandi_summary_endpoint(self):
        """Test GET /api/v1/mandi/summary returns valid telemetry."""
        response = self.client.get("/api/v1/mandi/summary")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        summary = data["summary"]
        self.assertIn("total_mandis", summary)
        self.assertGreater(summary["total_mandis"], 0)
        self.assertIn("top_gainer", summary)


if __name__ == "__main__":
    unittest.main()
