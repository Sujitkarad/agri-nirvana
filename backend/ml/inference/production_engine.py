"""Single-model, fail-safe production crop diagnosis."""
from pathlib import Path
from typing import Any, Dict, List
from PIL import Image
from backend.config import settings

MODEL_SUPPORTED_CROPS = {"Apple","Blueberry","Cherry","Corn","Grape","Orange","Peach","Pepper","Potato","Raspberry","Soybean","Squash","Strawberry","Tomato"}

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
        if self.provider_type == "real": self._load_models()

    def _load_models(self) -> None:
        try:
            from backend.ml.models.plant_validator import PlantValidator
            self._plant_validator = PlantValidator()
            path = Path(settings.LOCAL_TRAINED_MODEL_PATH)
            if not path.is_file(): raise FileNotFoundError(str(path))
            from backend.ml.models.efficientnet_classifier import EfficientNetDiseaseClassifier
            model = EfficientNetDiseaseClassifier(str(path))
            if model.model_id != "agri-nirvana-efficientnet-v2-s": raise ValueError("Production model must be EfficientNetV2-S")
            self._disease_classifier = model
            self._models_loaded = True
            self._model_source = "local_trained"
            self._is_calibrated = bool(model.calibration)
        except Exception as exc:
            print(f"[ProductionInferenceEngine] disabled: {exc}")

    @property
    def model_source(self) -> str: return self._model_source
    @property
    def model_name(self) -> str: return self._disease_classifier.model_id if self._models_loaded else "Unavailable"
    @property
    def model_version(self) -> str: return "v5-efficientnet-v2-s" if self._models_loaded else "unavailable"

    def supported_crops(self) -> List[str]:
        if self._disease_classifier:
            from backend.ml.models.disease_classifier import _parse_class_label
            crops = {_parse_class_label(str(v))[0] for v in self._disease_classifier.id2label.values()} & MODEL_SUPPORTED_CROPS
            if crops: return sorted(crops)
        return sorted(MODEL_SUPPORTED_CROPS)

    def _safe(self, crop: str, status: str, reason: str, confidence: float = 0.0) -> Dict[str, Any]:
        return {
            "status": status,
            "is_valid_crop_image": status == "success",
            "crop": {"name": crop, "confidence_pct": round(confidence * 100)},
            "cropType": crop,
            "condition": "Uncertain Result" if status != "success" else "Analyzed Disease",
            "confidence": round(confidence, 4),
            "confidence_pct": round(confidence * 100),
            "severity": "Unknown",
            "severityPercentage": 0,
            "symptoms": [], "symptoms_observed": [], "differential_diagnoses": [],
            "uncertainty": {"abstain": status != "success", "reason": reason or None},
            "recommendations": {"immediate": "Retake a clear close-up image in natural light.", "monitoring": "Do not apply disease-specific treatment from an uncertain result.", "prevention": "Continue normal field scouting.", "expert_help": "Consult a KVK/agriculture extension officer if symptoms spread."},
            "modelName": self.model_name, "modelVersion": self.model_version,
            "modelSource": self.model_source, "isMock": status == "model_unavailable",
        }

    def analyze(self, pil_image: Image.Image, crop_type: str) -> Dict[str, Any]:
        from backend.ml.models.disease_classifier import normalize_crop_name
        crop = normalize_crop_name((crop_type or "").strip())
        if crop == "Unknown" or crop not in self.supported_crops(): return self._safe(crop or "Unknown", "unsupported_crop", "Crop is outside the production model classes.")
        if self.provider_type != "real" or not self._models_loaded: return self._safe(crop, "model_unavailable", "Production checkpoint is not loaded.")
        if pil_image is None: return self._safe(crop, "uncertain", "No image was provided.")
        if self._plant_validator is None: return self._safe(crop, "model_unavailable", "Plant validation model is unavailable.")
        validation = self._plant_validator.validate(pil_image)
        if validation.get("image_quality", {}).get("status") == "fail": return self._safe(crop, "invalid_image", validation.get("rejection_reason", "Image quality gate failed."))
        if not validation.get("is_plant", False): return self._safe(crop, "invalid_image", validation.get("rejection_reason", "Plant validation failed."))

        classification = self._disease_classifier.classify(pil_image, top_k=5, crop_filter=crop)
        diag = classification.get("confidence_diagnostics", {})
        confidence = float(classification.get("confidence", 0.0))
        mass = float(diag.get("crop_probability_mass", 0.0))
        if not bool(diag.get("crop_match", False)) or mass < self.min_crop_mass: return self._safe(crop, "uncertain", f"Crop evidence is insufficient (mass={mass:.2f}).", confidence)
        if confidence < self.threshold: return self._safe(crop, "uncertain", f"Confidence {confidence:.2f} is below {self.threshold:.2f}.", confidence)
        if float(diag.get("top2_margin", 0.0)) < self.min_margin: return self._safe(crop, "uncertain", "Top-2 diagnosis margin is too narrow.", confidence)
        if float(diag.get("normalized_entropy", 1.0)) > self.max_entropy: return self._safe(crop, "uncertain", "Prediction entropy is too high.", confidence)

        from backend.ml.config.disease_knowledge import get_disease_info
        from backend.ml.models.severity_estimator import estimate_severity
        from backend.ml.inference.dynamic_advisor import generate_dynamic_advisory
        info = get_disease_info(classification.get("raw_label", ""))
        healthy = bool(classification.get("is_healthy"))
        sev = estimate_severity(pil_image, model_confidence=confidence, is_healthy=healthy)
        if not healthy and not sev.get("reliable", False): return self._safe(crop, "uncertain", "Severity evidence is not reliable enough for a production diagnosis.", confidence)
        sev_name = {"healthy":"Healthy","early":"Low","moderate":"Moderate","severe":"Severe"}.get(sev.get("severity"), "Unknown")
        alternatives = [{"name": f"{p.get('crop',crop)} — {p.get('condition','')}", "confidence_pct": round(float(p.get('confidence',0))*100)} for p in classification.get("top_predictions", [])[1:3]]
        advisory = generate_dynamic_advisory(crop=info.get("crop", crop), disease=info.get("display_name", classification.get("condition", "Unknown")), pathogen=info.get("pathogen", ""), severity_tier=sev_name, necrotic_area_pct=sev.get("severity_percentage",0), confidence_pct=round(confidence*100), differential_diagnoses=alternatives, base_info=info)
        condition = info.get("display_name", classification.get("condition", "Analyzed Disease"))
        result = self._safe(crop, "success", "", confidence)
        result.update({"condition": condition, "diagnosis": {"name": condition, "category": info.get("pathogen_category", "Unknown").lower(), "causal_agent": info.get("pathogen", ""), "confidence_pct": round(confidence*100)}, "validation": {"is_plant": True, "is_crop": True, "crop_supported": True, "rejection_reason": None}, "image_quality": validation.get("image_quality", {}), "plant_part": "leaf", "severity": sev_name, "severityPercentage": round(float(sev.get("severity_percentage",0))), "symptoms": advisory.get("symptoms_observed", []), "symptoms_observed": advisory.get("symptoms_observed", []), "evidence_features": advisory.get("symptoms_observed", []), "differential_diagnoses": alternatives, "ipm": advisory.get("ipm", {}), "farmer_summary": advisory.get("farmer_summary", ""), "likely_cause": advisory.get("likely_cause", ""), "immediate_precautions": advisory.get("immediate_precautions", []), "structured_chemical": info.get("structured_chemical", {}), "regional_terms": info.get("regional_terms", {}), "verification_note": info.get("verification_note", "Confirm product label and registration with a local KVK/agriculture extension officer before application."), "provenance": {"source": "local_efficientnet_v2_s", "confidence_is_calibrated": self._is_calibrated, "treatment_allowed": not healthy, "crop_probability_mass": round(mass,4)}, "treatmentPlan": {"organic": {}, "chemical": {}, "preventive": {}}})
        return result

inference_engine = ProductionInferenceEngine()
