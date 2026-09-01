"""Unit and API regression tests for Crop Diagnostics endpoints."""

import io
import unittest
from PIL import Image
from fastapi.testclient import TestClient
from backend.main import app

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
        # Create a symptom record
        symptom_payload = {
            "cropType": "Potato",
            "symptomsText": "Water soaked dark lesions with white fungal mold under leaves"
        }
        symptom_res = client.post("/api/v1/diagnosis/symptoms", data=symptom_payload)
        self.assertEqual(symptom_res.status_code, 200)
        diag_id = symptom_res.json()["diagnosis"]["id"]

        # Retrieve history
        hist_res = client.get("/api/v1/diagnosis/history")
        self.assertEqual(hist_res.status_code, 200)
        history = hist_res.json()["history"]
        self.assertTrue(any(item["id"] == diag_id for item in history))

        # Get single item
        item_res = client.get(f"/api/v1/diagnosis/{diag_id}")
        self.assertEqual(item_res.status_code, 200)
        self.assertEqual(item_res.json()["diagnosis"]["id"], diag_id)

        # Delete item
        del_res = client.delete(f"/api/v1/diagnosis/{diag_id}")
        self.assertEqual(del_res.status_code, 200)

        # Confirm 404 after deletion
        del_check = client.get(f"/api/v1/diagnosis/{diag_id}")
        self.assertEqual(del_check.status_code, 404)

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


if __name__ == "__main__":
    unittest.main()
