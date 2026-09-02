"""Exhaustive test suite for Crop Diagnostics hardening, validation gates,
Gemini backend integration, calibration, and authenticated history.
"""

import io
import json
import unittest
from unittest.mock import patch, AsyncMock
from PIL import Image, ImageDraw
from fastapi.testclient import TestClient

from backend.config import settings
from backend.main import app
from backend.routes.auth import create_access_token
from backend.ml.calibration.temperature_scaling import calibrator
from backend.ml.training.train_pipeline import MLTrainingPipeline

client = TestClient(app)


def _create_test_image(size=(256, 256), color=(40, 160, 40), draw_pattern=True) -> bytes:
    img = Image.new("RGB", size=size, color=color)
    if draw_pattern:
        draw = ImageDraw.Draw(img)
        for i in range(10, size[0], 20):
            draw.line([(i, 0), (i, size[1])], fill=(10, 80, 10), width=3)
            draw.line([(0, i), (size[0], i)], fill=(20, 120, 20), width=2)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=95)
    return buf.getvalue()


class TestDiagnosisHardening(unittest.TestCase):
    def setUp(self):
        # Test-only secret; production must supply JWT_SECRET via its environment.
        settings.JWT_SECRET = "test-only-secret-do-not-use-in-production-32chars"
        self.farmer1_token = create_access_token("farmer_alpha")
        self.farmer2_token = create_access_token("farmer_beta")

    def test_tiny_image_rejection(self):
        tiny_bytes = _create_test_image(size=(80, 80))
        files = {"image": ("tiny_leaf.jpg", tiny_bytes, "image/jpeg")}
        res = client.post("/api/v1/diagnosis/analyze", files=files, data={"cropType": "Tomato"})
        self.assertEqual(res.status_code, 400)
        self.assertIn("too low (<150x150 px)", res.json()["detail"])

    def test_dark_image_rejection(self):
        dark_bytes = _create_test_image(size=(200, 200), color=(10, 10, 10), draw_pattern=False)
        files = {"image": ("dark_leaf.jpg", dark_bytes, "image/jpeg")}
        res = client.post("/api/v1/diagnosis/analyze", files=files, data={"cropType": "Tomato"})
        self.assertEqual(res.status_code, 400)
        self.assertIn("too dark", res.json()["detail"].lower())

    def test_blurry_image_rejection(self):
        blurred_bytes = _create_test_image(size=(200, 200), color=(80, 140, 80), draw_pattern=False)
        files = {"image": ("blurred_leaf.jpg", blurred_bytes, "image/jpeg")}
        res = client.post("/api/v1/diagnosis/analyze", files=files, data={"cropType": "Tomato"})
        self.assertEqual(res.status_code, 400)
        self.assertIn("blurry", res.json()["detail"].lower())

    def test_unsupported_crop(self):
        leaf_bytes = _create_test_image(size=(200, 200))
        files = {"image": ("leaf.jpg", leaf_bytes, "image/jpeg")}
        res = client.post("/api/v1/diagnosis/analyze", files=files, data={"cropType": "DragonFruitUnseenCrop"})
        self.assertEqual(res.status_code, 200)
        diag = res.json()["diagnosis"]
        self.assertEqual(diag["status"], "unsupported_crop")
        self.assertFalse(diag["provenance"]["treatment_allowed"])

    def test_symptom_json_request(self):
        payload = {"cropType": "Tomato", "symptomText": "Dark brown circular target-like spots on lower leaves with yellow halo"}
        res = client.post("/api/v1/diagnosis/symptoms", json=payload, headers={"Authorization": f"Bearer {self.farmer1_token}"})
        self.assertEqual(res.status_code, 200)
        diag = res.json()["diagnosis"]
        self.assertIn("Early Blight", diag["condition"])
        self.assertFalse(diag["provenance"]["treatment_allowed"])

    @patch("httpx.AsyncClient.post")
    def test_gemini_backend_success(self, mock_post):
        mock_gemini_resp = {"candidates": [{"content": {"parts": [{"text": json.dumps({"disease_name": "Tomato Early Blight", "pathogen": "Alternaria solani", "pathogen_category": "Fungal", "confidence": 0.92, "severity": "Moderate", "affected_surface": "Lower leaf lamina", "symptoms": ["Concentric dark rings", "Chlorotic halo"], "likely_cause": "High humidity following rain", "immediate_actions": ["Prune lower foliage", "Apply certified fungicide"], "organic_treatment": "Trichoderma harzianum 5g/L", "chemical_treatment": "Mancozeb 75 WP at 2.5 g/L", "differential_diagnoses": [{"name": "Septoria Leaf Spot", "confidence_pct": 12, "key_distinguishing_feature": "Tiny black pycnidia"}]})}]}}]}
        mock_post.return_value = AsyncMock(status_code=200, json=lambda: mock_gemini_resp)
        files = {"image": ("leaf.jpg", _create_test_image(size=(200, 200)), "image/jpeg")}
        res = client.post("/api/v1/diagnosis/gemini", files=files, data={"cropType": "Tomato"}, headers={"Authorization": f"Bearer {self.farmer1_token}"})
        self.assertEqual(res.status_code, 200)
        diag = res.json()["diagnosis"]
        self.assertEqual(diag["condition"], "Tomato Early Blight")
        self.assertEqual(diag["confidence_pct"], 92)
        self.assertTrue(diag["provenance"]["treatment_allowed"])

    @patch("httpx.AsyncClient.post")
    def test_gemini_malformed_json_fallback(self, mock_post):
        mock_post.return_value = AsyncMock(status_code=200, json=lambda: {"candidates": [{"content": {"parts": [{"text": "I am not able to return JSON: error"}]}}]})
        files = {"image": ("leaf.jpg", _create_test_image(size=(200, 200)), "image/jpeg")}
        res = client.post("/api/v1/diagnosis/gemini", files=files, data={"cropType": "Tomato"}, headers={"Authorization": f"Bearer {self.farmer1_token}"})
        self.assertEqual(res.status_code, 200)
        diag = res.json()["diagnosis"]
        self.assertEqual(diag["status"], "uncertain")
        self.assertFalse(diag["provenance"]["treatment_allowed"])

    @patch("httpx.AsyncClient.post")
    def test_gemini_low_confidence_abstention(self, mock_post):
        mock_gemini_resp = {"candidates": [{"content": {"parts": [{"text": json.dumps({"disease_name": "Possible Blight", "pathogen": "Unknown", "pathogen_category": "Fungal", "confidence": 0.35, "severity": "Low", "affected_surface": "Tip", "symptoms": ["Mild yellowing"], "likely_cause": "Unknown", "immediate_actions": ["Monitor"], "organic_treatment": None, "chemical_treatment": None, "differential_diagnoses": []})}]}}]}
        mock_post.return_value = AsyncMock(status_code=200, json=lambda: mock_gemini_resp)
        files = {"image": ("leaf.jpg", _create_test_image(size=(200, 200)), "image/jpeg")}
        res = client.post("/api/v1/diagnosis/gemini", files=files, data={"cropType": "Tomato"}, headers={"Authorization": f"Bearer {self.farmer1_token}"})
        self.assertEqual(res.status_code, 200)
        diag = res.json()["diagnosis"]
        self.assertEqual(diag["status"], "uncertain")
        self.assertTrue(diag["is_low_confidence"])
        self.assertFalse(diag["provenance"]["treatment_allowed"])

    def test_authenticated_history_isolation(self):
        res1 = client.post("/api/v1/diagnosis/symptoms", json={"cropType": "Tomato", "symptomText": "Concentric rings and yellow leaf margin"}, headers={"Authorization": f"Bearer {self.farmer1_token}"})
        self.assertEqual(res1.status_code, 200)
        diag_id = res1.json()["diagnosis"]["id"]
        hist2_res = client.get("/api/v1/diagnosis/history", headers={"Authorization": f"Bearer {self.farmer2_token}"})
        self.assertEqual(hist2_res.status_code, 200)
        self.assertNotIn(diag_id, [item["id"] for item in hist2_res.json()["history"]])
        del_attempt = client.delete(f"/api/v1/diagnosis/{diag_id}", headers={"Authorization": f"Bearer {self.farmer2_token}"})
        self.assertEqual(del_attempt.status_code, 404)
        del_success = client.delete(f"/api/v1/diagnosis/{diag_id}", headers={"Authorization": f"Bearer {self.farmer1_token}"})
        self.assertEqual(del_success.status_code, 200)

    def test_real_training_metrics_calculation(self):
        pipeline = MLTrainingPipeline(num_classes=3)
        metrics = pipeline.evaluate_metrics([0, 0, 1, 1, 2, 2], [0, 1, 1, 1, 2, 0])
        self.assertIn("accuracy_top1", metrics)
        self.assertIn("macro_f1", metrics)
        self.assertIn("per_class_metrics", metrics)
        self.assertIn("confusion_matrix", metrics)
        self.assertAlmostEqual(metrics["accuracy_top1"], 0.6667, places=3)


if __name__ == "__main__":
    unittest.main()
