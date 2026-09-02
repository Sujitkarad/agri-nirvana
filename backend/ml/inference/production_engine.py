"""Single-model, fail-safe production crop diagnosis."""
from pathlib import Path
from typing import Any, Dict, List
from PIL import Image
from backend.config import settings

MODEL_SUPPORTED_CROPS = {"Apple", "Blueberry", "Cherry", "Corn", "Grape", "Orange", "Peach", "Pepper", "Potato", "Raspberry", "Soybean", "Squash", "Strawberry", "Tomato"}


class ProductionInferenceEngine:
    def __init__(self) -> None:
        self.provider_type = settings.AI_MODEL_PROVIDER.lower().strip()
        self.threshold = max(0.35, min(float(settings.AI_CONFIDENCE_THRESHOLD), 0.95))
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
            from backend.ml.models.efficientnet_classifier import EfficientNetDiseaseClassifier
            self._plant_validator = PlantValidator()
            path = Path(settings.LOCAL_TRAINED_MODEL_PATH)
            if not path.is_file():
                raise FileNotFoundError(str(path))
            model = EfficientNetDiseaseClassifier(str(path))
            if model.model_id != "agri-nirvana-efficientnet-v2-l":
                raise ValueError(f"Production checkpoint must be EfficientNetV2-L, got {model.model_id}")
            self._disease_classifier = model
            self._models_loaded = True
            self._model_source = "local_trained"
            self._is_calibrated = bool(model.calibration)
        except Exception as exc:
            self._models_loaded = False
            print(f"[ProductionInferenceEngine] disabled: {exc}")

    @property
    def model_source(self) -> str:
        return self._model_source

    @property
    def model_name(self) -> str:
        return self._disease_classifier.model_id if self._models_loaded else "Unavailable"

    @property
    def model_version(self) -> str:
        return "v6-efficientnet-v2-l" if self._models_loaded else "unavailable"

    def supported_crops(self) -> List[str]:
        if self._disease_classifier:
            from backend.ml.models.disease_classifier import _parse_class_label
            crops = {_parse_class_label(str(v))[0] for v in self._disease_classifier.id2label.values()} & MODEL_SUPPORTED_CROPS
            if crops:
                return sorted(crops)
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
            "symptoms": [],
            "symptoms_observed": [],
            "differential_diagnoses": [],
            "uncertainty": {"abstain": status != "success", "reason": reason or None},
            "recommendations": {
                "immediate": "Retake a clear close-up image in natural light.",
                "monitoring": "Do not apply disease-specific treatment from an uncertain result.",
                "prevention": "Continue normal field scouting.",
                "expert_help": "Consult a KVK/agriculture extension officer if symptoms spread.",
            },
            "modelName": self.model_name,
            "modelVersion": self.model_version,
            "modelSource": self.model_source,
            "isMock": False,
        }

    def analyze(self, pil_image: Image.Image, crop_type: str) -> Dict[str, Any]:
        from backend.ml.models.disease_classifier import normalize_crop_name
        crop = normalize_crop_name((crop_type or "").strip())
        if crop == "Unknown" or crop not in self.supported_crops():
            return self._safe(crop or "Unknown", "unsupported_crop", "Crop is outside the production model classes.")
        if self.provider_type != "real" or not self._models_loaded:
            return self._safe(crop, "model_unavailable", "Production EfficientNetV2-L checkpoint is not loaded.")
        if pil_image is None:
            return self._safe(crop, "uncertain", "No image was provided.")
        if self._plant_validator is None:
            return self._safe(crop, "model_unavailable", "Plant validation model is unavailable.")

        validation = self._plant_validator.validate(pil_image)
        if validation.get("image_quality", {}).get("status") == "fail":
            return self._safe(crop, "invalid_image", validation.get("rejection_reason", "Image quality gate failed."))
        if not validation.get("is_plant", False):
            return self._safe(crop, "invalid_image", validation.get("rejection_reason", "Plant validation failed."))

        classification = self._disease_classifier.classify(pil_image, top_k=5, crop_filter=crop)
        diag = classification.get("confidence_diagnostics", {})
        confidence = float(classification.get("confidence", 0.0))
        mass = float(diag.get("crop_probability_mass", 0.0))
        margin = float(diag.get("top2_margin", 0.0))
        entropy = float(diag.get("normalized_entropy", 1.0))
        if not bool(diag.get("crop_match", False)) or mass < self.min_crop_mass:
            return self._safe(crop, "uncertain", f"Crop evidence is insufficient (mass={mass:.2f}).", confidence)
        if confidence < self.threshold:
            return self._safe(crop, "uncertain", f"Confidence {confidence:.2f} is below {self.threshold:.2f}.", confidence)
        if margin < self.min_margin:
            return self._safe(crop, "uncertain", "Top-2 diagnosis margin is too narrow.", confidence)
        if entropy > self.max_entropy:
            return self._safe(crop, "uncertain", "Prediction entropy is too high.", confidence)

        top_preds = classification.get("top_predictions", [])
        if len(top_preds) > 1:
            margin = confidence - float(top_preds[1].get("confidence", 0.0))
            min_margin = float(getattr(settings, "AI_MIN_TOP2_MARGIN", 0.02))
            if margin < min_margin:
                return self._abstain(
                    crop_type,
                    classification,
                    f"Ambiguous prediction: margin between top-2 candidate conditions ({margin:.2f}) is too narrow (< {min_margin:.2f}). Retake clearer photo.",
                )

        conf_diag = classification.get("confidence_diagnostics", {})
        norm_entropy = float(conf_diag.get("normalized_entropy", 0.0))
        if norm_entropy > 0.90:
            return self._abstain(
                crop_type,
                classification,
                f"Prediction entropy ({norm_entropy:.2f}) exceeds 0.90, indicating visual ambiguity across classes.",
            )

        from backend.ml.models.severity_estimator import estimate_severity
        from backend.ml.config.disease_knowledge import get_disease_info
        from backend.ml.models.severity_estimator import estimate_severity
        from backend.ml.inference.dynamic_advisor import generate_dynamic_advisory
        info = get_disease_info(classification.get("raw_label", ""))
        healthy = bool(classification.get("is_healthy"))
        severity = estimate_severity(pil_image, model_confidence=confidence, is_healthy=healthy)
        if not healthy and not severity.get("reliable", False):
            return self._safe(crop, "uncertain", "Severity evidence is not reliable enough for a production diagnosis.", confidence)

        sev_name = {"healthy": "Healthy", "early": "Low", "moderate": "Moderate", "severe": "Severe"}.get(severity.get("severity"), "Unknown")
        alternatives = [
            {"name": f"{p.get('crop', crop)} — {p.get('condition', '')}", "confidence_pct": round(float(p.get("confidence", 0)) * 100)}
            for p in classification.get("top_predictions", [])[1:3]
        ]
        advisory = generate_dynamic_advisory(
            crop=info.get("crop", crop),
            disease=info.get("display_name", classification.get("condition", "Unknown")),
            pathogen=info.get("pathogen", ""),
            severity_tier=sev_name,
            necrotic_area_pct=severity.get("severity_percentage", 0),
            confidence_pct=round(confidence * 100),
            differential_diagnoses=alternatives,
            base_info=info,
        )
        ipm = advisory.get("ipm", {}) or {}
        biological = ipm.get("tier_1_biological", []) or []
        chemical = ipm.get("tier_2_chemical", []) or []
        cultural = ipm.get("tier_3_cultural", []) or []
        bio = biological[0] if biological else {}
        chem = chemical[0] if chemical else {}
        treatment_plan = {
            "organic": {"name": bio.get("agent"), "dosage": bio.get("dosage"), "applicationSchedule": bio.get("application_timing")},
            "chemical": {"name": chem.get("active_ingredient"), "dosage": chem.get("dosage"), "dose_15L_tank": chem.get("dose_ml_per_15L"), "frac_code": chem.get("frac_code"), "rotation_partner": info.get("structured_chemical", {}).get("rotation_partner"), "safetyIntervalDays": info.get("structured_chemical", {}).get("phi_days")},
            "preventive": {"cultural": cultural[0] if cultural else None, "irrigation": "Avoid prolonged foliar wetness where agronomically appropriate."},
        }
        return {
            "status": "success",
            "image_quality": validation.get("image_quality", {}),
            "validation": {"is_plant": True, "is_crop": True, "crop_supported": True, "rejection_reason": None},
            "crop": {"name": info.get("crop", crop), "confidence_pct": round(confidence * 100)},
            "cropType": info.get("crop", crop),
            "plant_part": "leaf",
            "condition": info.get("display_name", classification.get("condition", "Analyzed Disease")),
            "diagnosis": {"name": info.get("display_name", classification.get("condition", "Analyzed Disease")), "category": info.get("pathogen_category", "Unknown").lower(), "causal_agent": info.get("pathogen", ""), "confidence_pct": round(confidence * 100)},
            "confidence": round(confidence, 4),
            "confidence_pct": round(confidence * 100),
            "severity": sev_name,
            "severityPercentage": round(float(severity.get("severity_percentage", 0))),
            "symptoms": advisory.get("symptoms_observed", []),
            "symptoms_observed": advisory.get("symptoms_observed", []),
            "evidence_features": advisory.get("symptoms_observed", []),
            "differential_diagnoses": alternatives,
            "ipm": ipm,
            "farmer_summary": advisory.get("farmer_summary", ""),
            "likely_cause": advisory.get("likely_cause", ""),
            "immediate_precautions": advisory.get("immediate_precautions", []),
            "structured_chemical": info.get("structured_chemical", {}),
            "regional_terms": info.get("regional_terms", {}),
            "verification_note": info.get("verification_note", "Confirm the exact product, label dose and current registration status with a local KVK/agriculture extension officer before application."),
            "provenance": {"source": "local_efficientnet_v2_l", "confidence_is_calibrated": self._is_calibrated, "treatment_allowed": not healthy, "crop_probability_mass": round(mass, 4)},
            "treatmentPlan": treatment_plan,
            "modelName": self.model_name,
            "modelVersion": self.model_version,
            "modelSource": self.model_source,
            "isMock": False,
        }


inference_engine = ProductionInferenceEngine()
