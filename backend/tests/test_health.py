import unittest

from fastapi.testclient import TestClient

from backend.main import app


class TestHealthAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_root_reports_service_metadata(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["status"], "online")
        self.assertIn("service", payload)
        self.assertIn("version", payload)

    def test_health_reports_ok(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_production_frontend_origin_is_allowed(self):
        response = self.client.options(
            "/health",
            headers={
                "Origin": "https://agri-nirvana.vercel.app",
                "Access-Control-Request-Method": "GET",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.headers.get("access-control-allow-origin"),
            "https://agri-nirvana.vercel.app",
        )


if __name__ == "__main__":
    unittest.main()
