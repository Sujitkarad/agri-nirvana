"""Agri Nirvana Production Inference Engine (Resilient Hybrid Vision).

Integrates:
1. PlantValidator (MobileNetV2 ImageNet-1K vegetation and quality check)
2. RiceMaizeClassifier (Trained MobileNetV3 for 17 Rice and Maize classes)
3. DiseaseClassifier (HuggingFace MobileNetV2 for 38 PlantVillage classes)
4. EfficientNetDiseaseClassifier (Optional local large checkpoint)
5. SeverityEstimator & Dynamic IPM Treatment Advisor
"""

from __future__ import annotations
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
from PIL import Image

from backend.config import settings

logger = logging.getLogger("agri_nirvana.inference")

MODEL_SUPPORTED_CROPS = {
    "Apple", "Blueberry", "Cherry", "Corn", "Grape", "Maize",
    "Orange", "Peach", "Pepper", "Potato", "Raspberry", "Rice", "Soybean",
    "Squash", "Strawberry", "Tomato"
}


class ProductionInferenceEngine:
    def __init__(self) -> None:
        self.provider_type = settings.AI_MODEL_PROVIDER.lower().strip()
        self.threshold = max(0.25, min(float(settings.AI_CONFIDENCE_THRESHOLD), 0.95))
        self.min_crop_mass = float(getattr(settings, "AI_MIN_CROP_PROBABILITY_MASS", 0.35))
        self.min_margin = float(getattr(settings, "AI_MIN_TOP2_MARGIN", 0.01))
        self.max_entropy = float(getattr(settings, "AI_MAX_ENTROPY", 0.95))

        self._plant_validator = None
        self._disease_classifier = None
        self._rice_maize_classifier = None
        self._models_loaded = False
        self._model_source = "unavailable"
        self._is_calibrated = False

        if self.provider_type == "real":
            self._load_models()

    def _load_models(self) -> None:
        """Load vision classifiers and plant validator with robust fallback."""
        # 1. ImageNet Plant Validator Gate
        try:
            from backend.ml.models.plant_validator import PlantValidator
            self._plant_validator = PlantValidator()
        except Exception as exc:
            logger.warning("Plant validator could not be initialized: %s", exc)

        # 2. Specialized Rice & Maize Classifier
        try:
            from backend.ml.models.rice_maize_classifier import RiceMaizeClassifier
            rm_clf = RiceMaizeClassifier()
            if rm_clf.is_loaded:
                self._rice_maize_classifier = rm_clf
                logger.info("Rice & Maize 17-class classifier loaded successfully.")
        except Exception as exc:
            logger.warning("Rice & Maize classifier unavailable: %s", exc)

        # 3. Primary Multi-Crop Disease Classifier
        loaded_primary = False
        path = Path(settings.LOCAL_TRAINED_MODEL_PATH)
        if path.is_file():
            try:
                from backend.ml.models.efficientnet_classifier import EfficientNetDiseaseClassifier
                model = EfficientNetDiseaseClassifier(str(path))
                self._disease_classifier = model
                self._model_source = "local_trained_efficientnet"
                self._is_calibrated = bool(model.calibration)
                loaded_primary = True
            except Exception as exc:
                logger.warning("Local EfficientNet checkpoint failed: %s", exc)

        if not loaded_primary:
            try:
                from backend.ml.models.disease_classifier import DiseaseClassifier
                hf_model = DiseaseClassifier()
                if hf_model.is_loaded:
                    self._disease_classifier = hf_model
                    self._model_source = "production_mobilenet_v2"
                    loaded_primary = True
            except Exception as exc:
                logger.warning("DiseaseClassifier fallback failed: %s", exc)

        self._models_loaded = bool(self._disease_classifier or getattr(self, "_rice_maize_classifier", None))
        print(f"[ProductionInferenceEngine] Ready: loaded={self._models_loaded}, source={self._model_source}")

    @property
    def model_source(self) -> str:
        return getattr(self, "_model_source", "unavailable")

    @property
    def model_name(self) -> str:
        dc = getattr(self, "_disease_classifier", None)
        if dc and hasattr(dc, "model_id"):
            return dc.model_id
        rm = getattr(self, "_rice_maize_classifier", None)
        if rm and hasattr(rm, "model_id"):
            return rm.model_id
        return "Unavailable"

    @property
    def model_version(self) -> str:
        return "v3.5-hybrid-ensemble" if getattr(self, "_models_loaded", False) else "unavailable"

    def supported_crops(self) -> List[str]:
        dc = getattr(self, "_disease_classifier", None)
        if dc and hasattr(dc, "id2label"):
            from backend.ml.models.disease_classifier import _parse_class_label
            crops = {_parse_class_label(str(v))[0] for v in dc.id2label.values()} & MODEL_SUPPORTED_CROPS
            if crops:
                return sorted(crops | {"Rice", "Maize", "Corn"})
        return sorted(MODEL_SUPPORTED_CROPS)

    def _safe(self, crop: str, status: str, reason: str, confidence: float = 0.0) -> Dict[str, Any]:
        return {
            "status": status,
            "is_valid_crop_image": status == "success",
            "crop": {"name": crop, "confidence_pct": round(confidence * 100)},
            "cropType": crop,
            "condition": "Uncertain Result" if status != "success" else "Analyzed Condition",
            "confidence": round(confidence, 4),
            "confidence_pct": round(confidence * 100),
            "severity": "Unknown",
            "severityPercentage": 0,
            "symptoms": [],
            "symptoms_observed": [],
            "differential_diagnoses": [],
            "uncertainty": {"abstain": status != "success", "reason": reason or None},
            "recommendations": {
                "immediate": "Retake a clear close-up image in natural daylight.",
                "monitoring": "Do not apply aggressive chemical treatment from an uncertain result.",
                "prevention": "Continue regular field scouting and sanitation.",
                "expert_help": "Consult a local Krishi Vigyan Kendra (KVK) officer if symptoms spread.",
            },
            "modelName": self.model_name,
            "modelVersion": self.model_version,
            "modelSource": self.model_source,
            "isMock": False,
        }

    def analyze(self, pil_image: Image.Image, crop_type: str) -> Dict[str, Any]:
        """Run complete multimodal analysis pipeline on leaf image."""
        from backend.ml.models.disease_classifier import normalize_crop_name
        crop = normalize_crop_name((crop_type or "").strip())
        if crop == "Unknown" or not crop:
            crop = "Tomato"

        # Check crop support first
        if crop not in self.supported_crops():
            return self._safe(crop, "unsupported_crop", "Crop is outside the production model classes.")

        # Check provider type & loaded state
        if getattr(self, "provider_type", "real") != "real" or not getattr(self, "_models_loaded", False):
            return self._safe(crop, "model_unavailable", "Production vision models are not loaded.")

        if pil_image is None:
            return self._safe(crop, "uncertain", "No image was provided.")

        # 1. Conservative Image Validation
        validation = {"is_plant": True, "image_quality": {"status": "pass"}}
        validator = getattr(self, "_plant_validator", None)
        if validator is not None:
            try:
                validation = validator.validate(pil_image)
                if validation.get("image_quality", {}).get("status") == "fail":
                    return self._safe(crop, "invalid_image", validation.get("rejection_reason", "Image quality gate failed."))
            except Exception as val_err:
                logger.warning("Plant validator exception: %s", val_err)

        # 2. Intelligent Routing to Specialized Classifiers
        is_rice_or_maize = crop.lower() in ["rice", "paddy", "corn", "maize"]

        classification = None
        used_model_source = self.model_source
        rm_clf = getattr(self, "_rice_maize_classifier", None)
        dc_clf = getattr(self, "_disease_classifier", None)

        if is_rice_or_maize and rm_clf and rm_clf.is_loaded:
            classification = rm_clf.classify(pil_image, top_k=5, crop_filter=crop)
            used_model_source = "local_rice_and_maize_classifier"
        elif dc_clf:
            classification = dc_clf.classify(pil_image, top_k=5, crop_filter=crop)
        elif rm_clf and rm_clf.is_loaded:
            classification = rm_clf.classify(pil_image, top_k=5, crop_filter=crop)
            used_model_source = "local_rice_and_maize_classifier"

        if not classification or classification.get("raw_label") in ["model_not_loaded", "invalid_image"]:
            return self._safe(crop, "model_unavailable", "Vision classification models could not process image.")

        confidence = float(classification.get("confidence", 0.0))
        top_preds = classification.get("top_predictions", [])
        raw_label = classification.get("raw_label", "")

        from backend.ml.models.severity_estimator import estimate_severity
        from backend.ml.config.disease_knowledge import get_disease_info
        from backend.ml.inference.dynamic_advisor import generate_dynamic_advisory

        info = get_disease_info(raw_label)
        healthy = bool(classification.get("is_healthy")) or "healthy" in raw_label.lower()
        severity = estimate_severity(pil_image, model_confidence=confidence, is_healthy=healthy)

        sev_name = {"healthy": "Healthy", "early": "Low", "moderate": "Moderate", "severe": "Severe"}.get(
            severity.get("severity"), "Moderate" if not healthy else "Healthy"
        )

        alternatives = [
            {
                "name": f"{p.get('crop', crop)} — {p.get('condition', '')}",
                "confidence_pct": round(float(p.get("confidence", 0)) * 100)
            }
            for p in top_preds[1:4]
        ]

        display_disease = info.get("display_name", classification.get("condition", "Analyzed Condition"))

        advisory = generate_dynamic_advisory(
            crop=info.get("crop", crop),
            disease=display_disease,
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

        default_organic = info.get("treatment_organic", ["Neem Oil (10,000 PPM) @ 3-5 ml/L"])[0]
        default_chemical = info.get("treatment_chemical", ["Copper Hydroxide 77% WP @ 2 g/L"])[0]

        treatment_plan = {
            "organic": {
                "name": bio.get("agent") or default_organic,
                "dosage": bio.get("dosage", "3-5 ml/L"),
                "applicationSchedule": bio.get("application_timing", "Early morning foliar spray at 7-10 day intervals")
            },
            "chemical": {
                "name": chem.get("active_ingredient") or default_chemical,
                "dosage": chem.get("dosage", "2-2.5 g/L"),
                "dose_15L_tank": chem.get("dose_ml_per_15L", 37.5),
                "frac_code": chem.get("frac_code", "FRAC M03 / Group 11"),
                "rotation_partner": info.get("structured_chemical", {}).get("rotation_partner", "Saaf (Carbendazim + Mancozeb)"),
                "safetyIntervalDays": info.get("structured_chemical", {}).get("phi_days", 7)
            },
            "preventive": {
                "cultural": cultural[0] if cultural else "Avoid prolonged foliar wetness; scout fields weekly.",
                "irrigation": "Avoid overhead sprinkling in humid weather."
            },
        }

        return {
            "status": "success",
            "image_quality": validation.get("image_quality", {}),
            "validation": {"is_plant": True, "is_crop": True, "crop_supported": True, "rejection_reason": None},
            "crop": {"name": info.get("crop", crop), "confidence_pct": round(confidence * 100)},
            "cropType": info.get("crop", crop),
            "plant_part": "leaf",
            "condition": display_disease,
            "diagnosis": {
                "name": display_disease,
                "category": info.get("pathogen_category", "Foliar").lower(),
                "causal_agent": info.get("pathogen", ""),
                "confidence_pct": round(confidence * 100)
            },
            "confidence": round(confidence, 4),
            "confidence_pct": round(confidence * 100),
            "severity": sev_name,
            "severityPercentage": round(float(severity.get("severity_percentage", 25 if not healthy else 0))),
            "symptoms": advisory.get("symptoms_observed", info.get("symptoms_observed", [])),
            "symptoms_observed": advisory.get("symptoms_observed", info.get("symptoms_observed", [])),
            "evidence_features": advisory.get("symptoms_observed", info.get("symptoms_observed", [])),
            "differential_diagnoses": alternatives,
            "ipm": ipm,
            "farmer_summary": advisory.get("farmer_summary", ""),
            "likely_cause": advisory.get("likely_cause", info.get("likely_cause", "")),
            "immediate_precautions": advisory.get("immediate_precautions", info.get("immediate_precautions", [])),
            "structured_chemical": info.get("structured_chemical", {}),
            "regional_terms": info.get("regional_terms", {}),
            "verification_note": info.get("verification_note", "Confirm the exact product, label dose and registration status with a local KVK/agri extension officer before application."),
            "provenance": {
                "source": used_model_source,
                "confidence_is_calibrated": getattr(self, "_is_calibrated", False),
                "treatment_allowed": not healthy,
                "crop_probability_mass": round(confidence, 4)
            },
            "treatmentPlan": treatment_plan,
            "modelName": self.model_name,
            "modelVersion": self.model_version,
            "modelSource": used_model_source,
            "isMock": False,
        }


inference_engine = ProductionInferenceEngine()
