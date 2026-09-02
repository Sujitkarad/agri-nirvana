"""Single-model, fail-safe production crop diagnosis."""
from pathlib import Path
from typing import Any, Dict, List

from PIL import Image

from backend.config import settings

MODEL_SUPPORTED_CROPS = {
    "Apple", "Blueberry", "Cherry", "Corn", "Grape", "Orange", "Peach",
    "Pepper", "Potato", "Raspberry", "Soybean", "Squash", "Strawberry", "Tomato",
}


class ProductionInferenceEngine:
    def __init__(self) -> None:
        self.provider_type = settings.AI_MODEL_PROVIDER.lower().strip()
        self.threshold = float(settings.AI_CONFIDENCE_THRESHOLD)
        self.min_margin = float(settings.AI_MIN_TOP2_MARGIN)
        self.max_entropy = float(settings.AI_MAX_NORMALIZED_ENTROPY)
        self.min_crop_mass = float(settings.AI_MIN_CROP_PROBABILITY_MASS)
        self._plant_validator = None
        self._disease_classifier = None
        self._models_loaded = False
        self._model_source = "unavailable"
        self._is_calibrated = False
        if self.provider_type == "real":
            self._load_models()

    def _load_models(self) -> None:
        try:
            from backend.ml.models.plant_validator import PlantValidator
            self._plant_validator = PlantValidator()
        except Exception as exc:
            print(f"[ProductionInferenceEngine] validator unavailable: {exc}")
            return
        path = Path(settings.LOCAL_TRAINED_MODEL_PATH)
        if not path.is_file():
            print(f"[ProductionInferenceEngine] production checkpoint missing: {path}")
            return
        try:
            from backend.ml.models.efficientnet_classifier import EfficientNetDiseaseClassifier
            model = EfficientNetDiseaseClassifier(str(path))
            if model.model_id != "agri-nirvana-efficientnet-v2-s":
                raise ValueError("Only EfficientNetV2-S is permitted in production")
            self._disease_classifier = model
            self._models_loaded = bool(model.is_loaded)
            self._model_source = "local_trained"
            self._is_calibrated = bool(model.calibration)
        except Exception as exc:
            print(f"[ProductionInferenceEngine] checkpoint load failed: {exc}")

    @property
    def model_source(self) -> str:
        return self._model_source

    @property
    def model_name(self) -> str:
        return self._disease_classifier.model_id if self._models_loaded else "Unavailable"

    @property
    def model_version(self) -> str:
        return "v5-efficientnet-v2-s" if self._models_loaded else "unavailable"

    def supported_crops(self) -> List[str]:
        if self._disease_classifier:
            from backend.ml.models.disease_classifier import _parse_class_label
            crops = {_parse_class_label(str(v))[0] for v in self._disease_classifier.id2label.values()}
            crops &= MODEL_SUPPORTED_CROPS
            if crops:
                return sorted(crops)
        return sorted(MODEL_SUPPORTED_CROPS)

    def _result(self, crop: str, status: str, condition: str = "Uncertain Result", confidence: float = 0.0, reason: str = "") -> Dict[str, Any]:
        return {
            "status": status,
            "is_valid_crop_image": status not in {"model_unavailable", "unsupported_crop", "invalid_image"},
            "crop": {"name": crop, "confidence_pct": round(confidence * 100)},
            "cropType": crop,
            "condition": condition,
            "confidence": round(confidence, 4),
            "confidence_pct": round(confidence * 100),
            "severity": "Unknown",
            "severityPercentage": 0,
            "symptoms": [],
            "symptoms_observed": [],
            "differential_diagnoses": [],
            "uncertainty": {"abstain": status != "success", "reason": reason or None},
            "recommendations": {
                "immediate": "Retake a sharp close-up image in natural light.",
                "monitoring": "Do not apply disease-specific treatment from an uncertain result.",
                "prevention": "Continue normal field scouting.",
                "expert_help": "Consult a KVK/agriculture extension officer if symptoms are severe or spreading.",
            },
            "modelName": self.model_name,
            "modelVersion": self.model_version,
            "modelSource": self.model_source,
            "isMock": status == "model_unavailable",
        }

    def analyze(self, pil_image: Image.Image, crop_type: str) -> Dict[str, Any]:
        from backend.ml.models.disease_classifier import normalize_crop_name
        crop = normalize_crop_name((crop_type or "").strip())
        if not crop or crop == "Unknown" or crop not in self.supported_crops():
            return self._result(crop or "Unknown", "unsupported_crop", "Unsupported Crop", reason="Crop is outside the production model classes.")
        if self.provider_type != "real" or not self._models_loaded:
            return self._result(crop, "model_unavailable", "Model Unavailable", reason="Production checkpoint is not loaded.")
        if pil_image is None:
            return self._result(crop, "uncertain", reason="No image was provided.")
        if self._plant_validator is None:
            return self._result(crop, "model_unavailable", "Model Unavailable", reason="Plant validation model is unavailable.")

        validation = self._plant_validator.validate(pil_image)
        if validation.get("image_quality", {}).get("status") == "fail":
            return self._result(crop, "invalid_image", "Invalid Image", reason=validation.get("rejection_reason", "Image quality gate failed."))
        if not validation.get("is_plant", False):
            return self._result(crop, "invalid_image", "Invalid Image", reason=validation.get("rejection_reason", "Plant validation failed."))

        classification = self._disease_classifier.classify(pil_image, top_k=5, crop_filter=crop)
        diag = classification.get("confidence_diagnostics", {})
        confidence = float(classification.get("confidence", 0.0))
        crop_mass = float(diag.get("crop_probability_mass", 0.0))
        global_crop = str(diag.get("global_top_crop", ""))
        if not bool(diag.get("crop_match", False)) or crop_mass < self.min_crop_mass:
            return self._result(crop, "uncertain", confidence=confidence, reason=f"Crop evidence is insufficient: requested={crop}, model_top_crop={global_crop}, probability_mass={crop_mass:.2f}.")
        if confidence < self.threshold:
            return self._result(crop, "uncertain", confidence=confidence, reason=f"Confidence {confidence:.2f} is below threshold {self.threshold:.2f}.")
        margin = float(diag.get("top2_margin", 0.0))
        if margin < self.min_margin:
            return self._result(crop, "uncertain", confidence=confidence, reason=f"Top-2 margin {margin:.2f} is below {self.min_margin:.2f}.")
        entropy = float(diag.get("normalized_entropy", 1.0))
        if entropy > self.max_entropy:
            return self._result(crop, "uncertain", confidence=confidence, reason=f"Prediction entropy {entropy:.2f} exceeds {self.max_entropy:.2f}.")

        from backend.ml.config.disease_knowledge import get_disease_info
        from backend.ml.models.severity_estimator import estimate_severity
        from backend.ml.inference.dynamic_advisor import generate_dynamic_advisory
        raw_label = classification.get("raw_label", "")
        info = get_disease_info(raw_label)
        healthy = bool(classification.get("is_healthy"))
        severity = estimate_severity(pil_image, model_confidence=confidence, is_healthy=healthy)
        if not healthy and not severity.get("reliable", False):
            return self._result(crop, "uncertain", confidence=confidence, reason="Disease confidence passed, but severity evidence is not reliable enough for a production result.")
        sev_map = {"healthy": "Healthy", "early": "Low", "moderate": "Moderate", "severe": "Severe"}
        sev = sev_map.get(severity.get("severity"), "Unknown")
        alternatives = classification.get("top_predictions", [])[1:3]
        differential = [{"name": f"{p.get('crop', crop)} — {p.get('condition', '')}", "confidence_pct": round(float(p.get('confidence', 0)) * 100)} for p in alternatives]
        advisory = generate_dynamic_advisory(
            crop=info.get("crop", crop), disease=info.get("display_name", classification.get("condition", "Unknown")),
            pathogen=info.get("pathogen", ""), severity_tier=sev,
            necrotic_area_pct=severity.get("severity_percentage", 0.0), confidence_pct=round(confidence * 100),
            differential_diagnoses=differential, base_info=info,
        )
        result = self._result(crop, "success", info.get("display_name", classification.get("condition", "Analyzed Disease")), confidence)
        result.update({
            "image_quality": validation.get("image_quality", {"status": "pass"}),
            "validation": {"is_plant": True, "is_crop": True, "crop_supported": True, "rejection_reason": None},
            "plant_part": "leaf",
            "diagnosis": {"name": info.get("display_name", classification.get("condition", "Analyzed Disease")), "category": info.get("pathogen_category", "Unknown").lower(), "causal_agent": info.get("pathogen", ""), "confidence_pct": round(confidence * 100)},
            "severity": sev,
            "severityPercentage": round(float(severity.get("severity_percentage", 0.0))),
            "symptoms": advisory.get("symptoms_observed", []),
            "symptoms_observed": advisory.get("symptoms_observed", []),
            "evidence_features": advisory.get("symptoms_observed", []),
            "differential_diagnoses": differential,
            "ipm": advisory.get("ipm", {}),
            "farmer_summary": advisory.get("farmer_summary", ""),
            "likely_cause": advisory.get("likely_cause", ""),
            "immediate_precautions": advisory.get("immediate_precautions", []),
            "structured_chemical": info.get("structured_chemical", {}),
            "regional_terms": info.get("regional_terms", {}),
            "verification_note": info.get("verification_note", "Confirm product label and registration with a local KVK/agriculture extension officer before application."),
            "provenance": {"source": "local_efficientnet_v2_s", "confidence_is_calibrated": self._is_calibrated, "treatment_allowed": not healthy, "crop_probability_mass": round(crop_mass, 4)},
        })
        return result


inference_engine = ProductionInferenceEngine()
