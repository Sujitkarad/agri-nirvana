"""Safety-focused tests for the production diagnosis contract."""

from backend.ml.inference.production_engine import ProductionInferenceEngine


def test_engine_abstains_for_unsupported_crop():
    engine = ProductionInferenceEngine.__new__(ProductionInferenceEngine)
    engine.provider_type = "real"
    engine.threshold = 0.70
    engine._models_loaded = False
    engine._plant_validator = None
    engine._disease_classifier = None

    result = engine._unsupported_crop("Cotton")

    assert result["status"] == "unsupported_crop"
    assert result["uncertainty"]["abstain"] is True
    assert result["confidence"] == 0.0


def test_engine_never_labels_mock_as_real_diagnosis():
    engine = ProductionInferenceEngine.__new__(ProductionInferenceEngine)
    engine.provider_type = "mock"
    engine.threshold = 0.70
    engine._models_loaded = False
    engine._plant_validator = None
    engine._disease_classifier = None

    result = engine.analyze(None, "Tomato")

    assert result["status"] == "model_unavailable"
    assert result["isMock"] is True
    assert result["confidence"] == 0.0
