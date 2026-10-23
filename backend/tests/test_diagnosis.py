"""Unit and API regression tests for Crop Diagnostics endpoints."""

import io
import unittest
from PIL import Image
from fastapi.testclient import TestClient
from backend.main import app
from backend.config import settings
from backend.routes.auth import create_access_token

client = TestClient(app)


class TestDiagnosisAPI(unittest.TestCase):
    def test_get_supported_crops(self):
        response = client.get("/api/v1/crops")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertIsInstance(data["crops"], list)
        self.assertGreater(len(data["crops"]), 0)

    def test_get_model_status(self):
        response = client.get("/api/v1/model/status")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertIn("model_name", data)
        self.assertIn("confidence_threshold", data)
        self.assertIn("supported_crops", data)

    def test_analyze_crop_symptoms_success(self):
        payload = {
            "cropType": "Tomato",
            "symptomsText": "Dark brown concentric target rings and yellow halo on lower leaves"
        }
        response = client.post("/api/v1/diagnosis/symptoms", data=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertIn("Early Blight", data["diagnosis"]["condition"])
        self.assertFalse(data["diagnosis"]["provenance"]["treatment_allowed"])

    def test_analyze_crop_symptoms_insufficient_evidence(self):
        payload = {
            "cropType": "Tomato",
            "symptomsText": "Plants look slightly different this morning with no specific discoloration"
        }
        response = client.post("/api/v1/diagnosis/symptoms", data=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["diagnosis"]["condition"], "Insufficient Evidence")

    def test_analyze_crop_symptoms_too_short(self):
        payload = {
            "cropType": "Tomato",
            "symptomsText": "spot"
        }
        response = client.post("/api/v1/diagnosis/symptoms", data=payload)
        self.assertEqual(response.status_code, 400)

    def test_diagnosis_history_and_deletion(self):
        # Private record access must be tied to a verified token subject.
        previous_secret = settings.JWT_SECRET
        settings.JWT_SECRET = "test-only-secret-that-is-long-enough-123"
        try:
            token = create_access_token("test_farmer")
            headers = {"Authorization": f"Bearer {token}"}
            symptom_payload = {
                "cropType": "Potato",
                "symptomsText": "Water soaked dark lesions with white fungal mold under leaves",
                "userId": "test_farmer",
            }
            symptom_res = client.post(
                "/api/v1/diagnosis/symptoms", data=symptom_payload, headers=headers
            )
            self.assertEqual(symptom_res.status_code, 200)
            diag_id = symptom_res.json()["diagnosis"]["id"]

            hist_res = client.get("/api/v1/diagnosis/history", headers=headers)
            self.assertEqual(hist_res.status_code, 200)
            history = hist_res.json()["history"]
            self.assertTrue(any(item["id"] == diag_id for item in history))

            item_res = client.get(f"/api/v1/diagnosis/{diag_id}", headers=headers)
            self.assertEqual(item_res.status_code, 200)
            self.assertEqual(item_res.json()["diagnosis"]["id"], diag_id)

            # A different authenticated farmer cannot read or delete the record.
            other_token = create_access_token("other_farmer")
            other_headers = {"Authorization": f"Bearer {other_token}"}
            other_read = client.get(f"/api/v1/diagnosis/{diag_id}", headers=other_headers)
            self.assertEqual(other_read.status_code, 404)
            other_delete = client.delete(f"/api/v1/diagnosis/{diag_id}", headers=other_headers)
            self.assertEqual(other_delete.status_code, 404)

            del_res = client.delete(f"/api/v1/diagnosis/{diag_id}", headers=headers)
            self.assertEqual(del_res.status_code, 200)
            del_check = client.get(f"/api/v1/diagnosis/{diag_id}", headers=headers)
            self.assertEqual(del_check.status_code, 404)
        finally:
            settings.JWT_SECRET = previous_secret

    def test_private_history_requires_authentication(self):
        response = client.get("/api/v1/diagnosis/history?userId=another_farmer")
        self.assertEqual(response.status_code, 401)

    def test_unverified_session_creation_is_disabled(self):
        response = client.post(
            "/api/v1/auth/session",
            json={"farmerId": "victim_farmer", "phone": "9999999999", "name": "Impersonator"},
        )
        self.assertEqual(response.status_code, 503)

    def test_analyze_image_valid_upload(self):
        img = Image.new("RGB", (256, 256), color=(40, 140, 40))
        from PIL import ImageDraw
        draw = ImageDraw.Draw(img)
        for i in range(10, 256, 20):
            draw.line([(i, 0), (i, 256)], fill=(10, 60, 10), width=2)
            draw.line([(0, i), (256, i)], fill=(20, 100, 20), width=2)
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        buf.seek(0)

        files = {"image": ("test_leaf.jpg", buf, "image/jpeg")}
        data = {"cropType": "Tomato", "userId": "test_farmer"}
        response = client.post("/api/v1/diagnosis/analyze", files=files, data=data)
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertTrue(result["success"])
        self.assertIn("diagnosis", result)

    def test_analyze_image_unsupported_format(self):
        files = {"image": ("malicious.exe", b"binary content", "application/octet-stream")}
        data = {"cropType": "Tomato"}
        response = client.post("/api/v1/diagnosis/analyze", files=files, data=data)
        self.assertEqual(response.status_code, 400)

    def test_agronomist_visit_request_success(self):
        payload = {
            "farmerPhone": "+919876543210",
            "preferredSlot": "Tomorrow Morning (9:00 AM)",
            "cropType": "Tomato",
            "condition": "Early Blight",
            "userId": "test_farmer"
        }
        response = client.post("/api/v1/diagnosis/agronomist-requests", json=payload)
        self.assertEqual(response.status_code, 200)
        res = response.json()
        self.assertTrue(res["success"])
        self.assertIn("referenceId", res)
        self.assertTrue(res["referenceId"].startswith("AGRO_"))
        self.assertEqual(res["cropType"], "Tomato")

    def test_agronomist_visit_request_invalid_phone(self):
        payload = {
            "farmerPhone": "12",
            "cropType": "Tomato"
        }
        response = client.post("/api/v1/diagnosis/agronomist-requests", json=payload)
        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
