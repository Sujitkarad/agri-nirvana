import unittest
from backend.ml.inference.production_engine import ProductionInferenceEngine


class TestProductionEngine(unittest.TestCase):
    def test_engine_abstains_for_unsupported_crop(self):
        engine = ProductionInferenceEngine.__new__(ProductionInferenceEngine)
        engine.provider_type = "real"
        engine.threshold = 0.70
        engine._models_loaded = False
        engine._plant_validator = None
        engine._disease_classifier = None

        result = engine._unsupported_crop("Cotton")

        self.assertEqual(result["status"], "unsupported_crop")
        self.assertTrue(result["uncertainty"]["abstain"])
        self.assertEqual(result["confidence"], 0.0)

    def test_engine_never_labels_mock_as_real_diagnosis(self):
        engine = ProductionInferenceEngine.__new__(ProductionInferenceEngine)
        engine.provider_type = "mock"
        engine.threshold = 0.70
        engine._models_loaded = False
        engine._plant_validator = None
        engine._disease_classifier = None

        result = engine.analyze(None, "Tomato")

        self.assertEqual(result["status"], "model_unavailable")
        self.assertTrue(result["isMock"])
        self.assertEqual(result["confidence"], 0.0)


if __name__ == "__main__":
    unittest.main()

