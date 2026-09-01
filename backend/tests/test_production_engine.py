import unittest

from PIL import Image

from backend.ml.inference.production_engine import ProductionInferenceEngine
from backend.ml.models.plant_validator import PlantValidator
from backend.ml.models.severity_estimator import estimate_severity


class TestProductionEngine(unittest.TestCase):
    def _engine(self, provider="mock"):
        engine = ProductionInferenceEngine.__new__(ProductionInferenceEngine)
        engine.provider_type = provider
        engine.threshold = 0.70
        engine._models_loaded = False
        engine._plant_validator = None
        engine._disease_classifier = None
        engine._model_source = "unavailable"
        engine._is_calibrated = False
        return engine

    def test_engine_abstains_for_unsupported_crop(self):
        result = self._engine("real")._unsupported_crop("Cotton")
        self.assertEqual(result["status"], "unsupported_crop")
        self.assertTrue(result["uncertainty"]["abstain"])
        self.assertEqual(result["confidence"], 0.0)

    def test_engine_never_labels_mock_as_real_diagnosis(self):
        result = self._engine().analyze(None, "Tomato")
        self.assertEqual(result["status"], "model_unavailable")
        self.assertTrue(result["isMock"])
        self.assertEqual(result["confidence"], 0.0)


class TestPlantValidatorQualityGate(unittest.TestCase):
    def test_rejects_missing_image_without_loading_model(self):
        validator = PlantValidator.__new__(PlantValidator)
        result = validator.validate(None)
        self.assertFalse(result["is_plant"])
        self.assertEqual(result["image_quality"]["status"], "fail")
        self.assertIn("No image", result["rejection_reason"])

    def test_rejects_image_below_model_input_size(self):
        validator = PlantValidator.__new__(PlantValidator)
        tiny = Image.new("RGB", (64, 64), "white")
        result = validator.validate(tiny)
        self.assertFalse(result["is_plant"])
        self.assertEqual(result["image_quality"]["status"], "fail")
        self.assertIn("too small", result["image_quality"]["reason"])

    def test_quality_check_reports_measurements_for_valid_dimensions(self):
        image = Image.new("RGB", (256, 256), "white")
        quality = PlantValidator._quality_check(image)
        self.assertEqual(quality["width"], 256)
        self.assertEqual(quality["height"], 256)
        self.assertIsNotNone(quality["brightness"])
        self.assertIsNotNone(quality["sharpness"])


class TestSeverityEstimator(unittest.TestCase):
    def test_no_image_never_fabricates_severity(self):
        result = estimate_severity(None, model_confidence=0.99, is_healthy=False)
        self.assertEqual(result["severity"], "unknown")
        self.assertEqual(result["severity_percentage"], 0.0)
        self.assertFalse(result["reliable"])

    def test_unreliable_segmentation_never_uses_model_confidence_as_damage(self):
        image = Image.new("RGB", (256, 256), "white")
        result = estimate_severity(image, model_confidence=0.99, is_healthy=False)
        self.assertEqual(result["severity"], "unknown")
        self.assertEqual(result["severity_percentage"], 0.0)
        self.assertFalse(result["reliable"])

    def test_healthy_classification_is_explicit(self):
        result = estimate_severity(Image.new("RGB", (256, 256), "green"), model_confidence=0.5, is_healthy=True)
        self.assertEqual(result["severity"], "healthy")
        self.assertEqual(result["severity_percentage"], 0.0)
        self.assertTrue(result["reliable"])


if __name__ == "__main__":
    unittest.main()
