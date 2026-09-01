"""Exhaustive test suite for Crop Diagnostics hardening, validation gates,
Gemini backend integration, calibration, and authenticated history.
"""

import io
import json
import unittest
from unittest.mock import patch, AsyncMock
from PIL import Image, ImageDraw
from fastapi.testclient import TestClient

from backend.main import app
from backend.routes.auth import create_access_token
from backend.ml.calibration.temperature_scaling import calibrator
from backend.ml.training.train_pipeline import MLTrainingPipeline

client = TestClient(app)


def _create_test_image(size=(256, 256), color=(40, 160, 40), draw_pattern=True) -> bytes:
    img = Image.new("RGB", size, color=color)
    if draw_pattern:
        draw = ImageDraw.Draw(img)
        # Add high-contrast lines for sharpness/focus
        for i in range(10, size[0], 20):
            draw.line([(i, 0), (i, size[1])], fill=(10, 80, 10), width=3)
            draw.line([(0, i), (size[0], i)], fill=(20, 120, 20), width=2)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=95)
    return buf.getvalue()


class TestDiagnosisHardening(unittest.TestCase):
    def setUp(self):
        self.farmer1_token = create_access_token("farmer_alpha")
        self.farmer2_token = create_access_token("farmer_beta")

    # 1. Tiny Image (<150x150 px) Gate
    def test_tiny_image_rejection(self):
        tiny_bytes = _create_test_image(size=(80, 80))
        files = {"image": ("tiny_leaf.jpg", tiny_bytes, "image/jpeg")}
        res = client.post("/api/v1/diagnosis/analyze", files=files, data={"cropType": "Tomato"})
        self.assertEqual(res.status_code, 400)
        self.assertIn("too low (<150x150 px)", res.json()["detail"])

    # 2. Dark Image (<35 mean) Gate
    def test_dark_image_rejection(self):
        dark_bytes = _create_test_image(size=(200, 200), color=(10, 10, 10), draw_pattern=False)
        files = {"image": ("dark_leaf.jpg", dark_bytes, "image/jpeg")}
        res = client.post("/api/v1/diagnosis/analyze", files=files, data={"cropType": "Tomato"})
        self.assertEqual(res.status_code, 400)
        self.assertIn("too dark", res.json()["detail"].lower())

    # 3. Blurry Image (Laplacian variance < 70) Gate
    def test_blurry_image_rejection(self):
        # Solid uniform color has zero edge variance (completely blurry)
        blurred_bytes = _create_test_image(size=(200, 200), color=(80, 140, 80), draw_pattern=False)
        files = {"image": ("blurred_leaf.jpg", blurred_bytes, "image/jpeg")}
        res = client.post("/api/v1/diagnosis/analyze", files=files, data={"cropType": "Tomato"})
        self.assertEqual(res.status_code, 400)
        self.assertIn("blurry", res.json()["detail"].lower())

    # 4. Unsupported Crop Gate
    def test_unsupported_crop(self):
        leaf_bytes = _create_test_image(size=(200, 200))
        files = {"image": ("leaf.jpg", leaf_bytes, "image/jpeg")}
        res = client.post("/api/v1/diagnosis/analyze", files=files, data={"cropType": "DragonFruitUnseenCrop"})
        self.assertEqual(res.status_code, 200)
        diag = res.json()["diagnosis"]
        self.assertEqual(diag["status"], "unsupported_crop")
        self.assertFalse(diag["provenance"]["treatment_allowed"])

    # 5. Symptom Unified JSON Request
    def test_symptom_json_request(self):
        payload = {
            "cropType": "Tomato",
            "symptomText": "Dark brown circular target-like spots on lower leaves with yellow halo"
        }
        res = client.post(
            "/api/v1/diagnosis/symptoms",
            json=payload,
            headers={"Authorization": f"Bearer {self.farmer1_token}"}
        )
        self.assertEqual(res.status_code, 200)
        diag = res.json()["diagnosis"]
        self.assertIn("Early Blight", diag["condition"])
        # Symptoms alone must NEVER unlock chemical treatment
        self.assertFalse(diag["provenance"]["treatment_allowed"])

    # 6. Gemini Backend Endpoint With Mocked AI
    @patch("httpx.AsyncClient.post")
    def test_gemini_backend_success(self, mock_post):
        mock_gemini_resp = {
            "candidates": [{
                "content": {
                    "parts": [{
                        "text": json.dumps({
                            "disease_name": "Tomato Early Blight",
                            "pathogen": "Alternaria solani",
                            "pathogen_category": "Fungal",
                            "confidence": 0.92,
                            "severity": "Moderate",
                            "affected_surface": "Lower leaf lamina",
                            "symptoms": ["Concentric dark rings", "Chlorotic halo"],
                            "likely_cause": "High humidity following rain",
                            "immediate_actions": ["Prune lower foliage", "Apply certified fungicide"],
                            "organic_treatment": "Trichoderma harzianum 5g/L",
                            "chemical_treatment": "Mancozeb 75 WP at 2.5 g/L",
                            "differential_diagnoses": [{"name": "Septoria Leaf Spot", "confidence_pct": 12, "key_distinguishing_feature": "Tiny black pycnidia"}]
                        })
                    }]
                }
            }]
        }
        mock_post.return_value = AsyncMock(status_code=200, json=lambda: mock_gemini_resp)

        leaf_bytes = _create_test_image(size=(200, 200))
        files = {"image": ("leaf.jpg", leaf_bytes, "image/jpeg")}
        res = client.post(
            "/api/v1/diagnosis/gemini",
            files=files,
            data={"cropType": "Tomato"},
            headers={"Authorization": f"Bearer {self.farmer1_token}"}
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["success"])
        diag = data["diagnosis"]
        self.assertEqual(diag["condition"], "Tomato Early Blight")
        self.assertEqual(diag["confidence_pct"], 92)
        self.assertTrue(diag["provenance"]["treatment_allowed"])

    # 7. Gemini Malformed JSON Fallback (Returns uncertain, no 500 crash)
    @patch("httpx.AsyncClient.post")
    def test_gemini_malformed_json_fallback(self, mock_post):
        mock_post.return_value = AsyncMock(
            status_code=200,
            json=lambda: {"candidates": [{"content": {"parts": [{"text": "I am not able to return JSON: error"}]}}]}
        )

        leaf_bytes = _create_test_image(size=(200, 200))
        files = {"image": ("leaf.jpg", leaf_bytes, "image/jpeg")}
        res = client.post(
            "/api/v1/diagnosis/gemini",
            files=files,
            data={"cropType": "Tomato"},
            headers={"Authorization": f"Bearer {self.farmer1_token}"}
        )
        self.assertEqual(res.status_code, 200)
        diag = res.json()["diagnosis"]
        self.assertEqual(diag["status"], "uncertain")
        self.assertFalse(diag["provenance"]["treatment_allowed"])

    # 8. Gemini Zero or Low Confidence Result (Abstains from treatment)
    @patch("httpx.AsyncClient.post")
    def test_gemini_low_confidence_abstention(self, mock_post):
        mock_gemini_resp = {
            "candidates": [{
                "content": {
                    "parts": [{
                        "text": json.dumps({
                            "disease_name": "Possible Blight",
                            "pathogen": "Unknown",
                            "pathogen_category": "Fungal",
                            "confidence": 0.35,  # Low confidence (< 0.50)
                            "severity": "Low",
                            "affected_surface": "Tip",
                            "symptoms": ["Mild yellowing"],
                            "likely_cause": "Unknown",
                            "immediate_actions": ["Monitor"],
                            "organic_treatment": None,
                            "chemical_treatment": None,
                            "differential_diagnoses": []
                        })
                    }]
                }
            }]
        }
        mock_post.return_value = AsyncMock(status_code=200, json=lambda: mock_gemini_resp)

        leaf_bytes = _create_test_image(size=(200, 200))
        files = {"image": ("leaf.jpg", leaf_bytes, "image/jpeg")}
        res = client.post(
            "/api/v1/diagnosis/gemini",
            files=files,
            data={"cropType": "Tomato"},
            headers={"Authorization": f"Bearer {self.farmer1_token}"}
        )
        self.assertEqual(res.status_code, 200)
        diag = res.json()["diagnosis"]
        self.assertEqual(diag["status"], "uncertain")
        self.assertTrue(diag["is_low_confidence"])
        self.assertFalse(diag["provenance"]["treatment_allowed"])

    # 9. Authenticated History Isolation
    def test_authenticated_history_isolation(self):
        # Farmer 1 saves a symptom diagnosis
        res1 = client.post(
            "/api/v1/diagnosis/symptoms",
            json={"cropType": "Tomato", "symptomText": "Concentric rings and yellow leaf margin"},
            headers={"Authorization": f"Bearer {self.farmer1_token}"}
        )
        self.assertEqual(res1.status_code, 200)
        diag_id = res1.json()["diagnosis"]["id"]

        # Farmer 2 checks history: Farmer 1's diagnosis must NOT be returned
        hist2_res = client.get(
            "/api/v1/diagnosis/history",
            headers={"Authorization": f"Bearer {self.farmer2_token}"}
        )
        self.assertEqual(hist2_res.status_code, 200)
        hist2_ids = [item["id"] for item in hist2_res.json()["history"]]
        self.assertNotIn(diag_id, hist2_ids)

        # Farmer 2 attempts to delete Farmer 1's diagnosis: Must return 404 Access Denied
        del_attempt = client.delete(
            f"/api/v1/diagnosis/{diag_id}",
            headers={"Authorization": f"Bearer {self.farmer2_token}"}
        )
        self.assertEqual(del_attempt.status_code, 404)

        # Farmer 1 deletes own diagnosis: Must succeed
        del_success = client.delete(
            f"/api/v1/diagnosis/{diag_id}",
            headers={"Authorization": f"Bearer {self.farmer1_token}"}
        )
        self.assertEqual(del_success.status_code, 200)

    # 10. Training Pipeline Evaluation Metrics Calculation (No Placeholders)
    def test_real_training_metrics_calculation(self):
        pipeline = MLTrainingPipeline(num_classes=3)
        y_true = [0, 0, 1, 1, 2, 2]
        y_pred = [0, 1, 1, 1, 2, 0]
        metrics = pipeline.evaluate_metrics(y_true, y_pred)

        self.assertIn("accuracy_top1", metrics)
        self.assertIn("macro_f1", metrics)
        self.assertIn("per_class_metrics", metrics)
        self.assertIn("confusion_matrix", metrics)
        # Verify it calculated actual accuracy (4 correct out of 6 = 0.6667)
        self.assertAlmostEqual(metrics["accuracy_top1"], 0.6667, places=3)


if __name__ == "__main__":
    unittest.main()
