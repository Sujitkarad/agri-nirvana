import unittest

from PIL import Image

from backend.config import settings
from backend.ml.inference.production_engine import ProductionInferenceEngine
from backend.ml.models.plant_validator import PlantValidator
from backend.ml.models.severity_estimator import estimate_severity


class TestProductionEngine(unittest.TestCase):
    def setUp(self):
        settings.JWT_SECRET = "test-only-secret-do-not-use-in-production-32chars"

    def _engine(self, provider="mock"):
        engine = ProductionInferenceEngine.__new__(ProductionInferenceEngine)
        engine.provider_type = provider
        engine.threshold = 0.70
        engine.min_margin = 0.10
        engine.max_entropy = 0.90
        engine.min_crop_mass = 0.45
        engine._models_loaded = False
        engine._plant_validator = None
        engine._disease_classifier = None
        engine._model_source = "unavailable"
        engine._is_calibrated = False
        return engine

    def test_constructor_initializes_uncertainty_gates_from_settings(self):
        original_provider = settings.AI_MODEL_PROVIDER
        try:
            settings.AI_MODEL_PROVIDER = "mock"
            engine = ProductionInferenceEngine()
            self.assertEqual(engine.min_margin, float(settings.AI_MIN_TOP2_MARGIN))
            self.assertEqual(engine.max_entropy, float(settings.AI_MAX_NORMALIZED_ENTROPY))
            self.assertEqual(engine.min_crop_mass, float(settings.AI_MIN_CROP_PROBABILITY_MASS))
        finally:
            settings.AI_MODEL_PROVIDER = original_provider

    def test_abstain_returns_safe_uncertain_result(self):
        engine = self._engine("real")
        result = engine._abstain("Tomato", {"crop": "Tomato", "confidence": 0.61}, "ambiguous prediction")
        self.assertEqual(result["status"], "uncertain")
        self.assertTrue(result["uncertainty"]["abstain"])
        self.assertEqual(result["confidence"], 0.61)
        self.assertEqual(result["uncertainty"]["reason"], "ambiguous prediction")
        self.assertFalse(result["isMock"])

    def test_engine_abstains_for_unsupported_crop(self):
        result = self._engine("real").analyze(None, "Cotton")
        self.assertEqual(result["status"], "unsupported_crop")
        self.assertTrue(result["uncertainty"]["abstain"])
        self.assertEqual(result["confidence"], 0.0)
        self.assertFalse(result["isMock"])

    def test_engine_never_fabricates_when_model_provider_is_not_real(self):
        result = self._engine().analyze(None, "Tomato")
        self.assertEqual(result["status"], "model_unavailable")
        self.assertTrue(result["uncertainty"]["abstain"])
        self.assertFalse(result["isMock"])
        self.assertEqual(result["confidence"], 0.0)

    def test_engine_abstains_when_local_model_is_unavailable(self):
        result = self._engine("real").analyze(Image.new("RGB", (256, 256), "green"), "Tomato")
        self.assertEqual(result["status"], "model_unavailable")
        self.assertTrue(result["uncertainty"]["abstain"])
        self.assertFalse(result["isMock"])


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
