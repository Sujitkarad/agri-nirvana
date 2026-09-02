"""Production-safe crop diagnosis engine.

Rules for the production path:
- only the versioned local EfficientNetV2-S checkpoint is accepted;
- no silent Hugging Face/model substitution;
- crop evidence is checked before disease confidence is trusted;
- global calibrated probabilities remain global after crop filtering;
- low confidence, ambiguity, high entropy, and crop mismatch abstain;
- treatment recommendations are returned only for a successful diagnosis.
"""

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
        self.threshold = max(0.50, min(float(settings.AI_CONFIDENCE_THRESHOLD), 0.95))
        self.min_margin = float(settings.AI_MIN_TOP2_MARGIN)
        self.max_entropy = float(settings.AI_MAX_NORMALIZED_ENTROPY)
        self.min_crop_mass = float(settings.AI_MIN_CROP_PROBABILITY_MASS)
        self.require_local = bool(settings.AI_REQUIRE_LOCAL_CHECKPOINT)
        self._plant_validator = None
        self._disease_classifier = None
        self._models_loaded = False
        self._model_source = "unavailable"
        self._is_calibrated = False
        if self.provider_type == "real":
            self._load_models()

    def _load_models(self) -> None:
        """Load only the production checkpoint; never substitute another model."""
        try:
            from backend.ml.models.plant_validator import PlantValidator
            self._plant_validator = PlantValidator()
        except Exception as exc:
            print(f"[ProductionInferenceEngine] plant validator load failed: {exc}")
            self._plant_validator = None

        local_path = Path(settings.LOCAL_TRAINED_MODEL_PATH)
        if not local_path.is_file():
            print(f"[ProductionInferenceEngine] production checkpoint missing: {local_path}")
            return

        try:
            from backend.ml.models.efficientnet_classifier import EfficientNetDiseaseClassifier
            classifier = EfficientNetDiseaseClassifier(str(local_path))
            if classifier.model_id != "agri-nirvana-efficientnet-v2-s":
                raise ValueError("Production checkpoint must be EfficientNetV2-S")
            self._disease_classifier = classifier
            self._models_loaded = bool(classifier.is_loaded)
            self._model_source = "local_trained"
            self._is_calibrated = bool(getattr(classifier, "calibration", {}))
            print(f"[ProductionInferenceEngine] Loaded production model: {local_path}")
        except Exception as exc:
            print(f"[ProductionInferenceEngine] production model load failed: {exc}")
            self._disease_classifier = None
            self._models_loaded = False

    @property
    def model_source(self) -> str:
        return self._model_source

    @property
    def model_name(self) -> str:
        if self._models_loaded and self._disease_classifier:
            return f"{self._disease_classifier.model_id} + plant validation gate"
        return "Unavailable"

    @property
    def model_version(self) -> str:
        return "v5-efficientnet-v2-s" if self._models_loaded else "unavailable"

    def supported_crops(self) -> List[str]:
        if self._disease_classifier and self._disease_classifier.id2label:
            from backend.ml.models.disease_classifier import _parse_class_label
            detected = set()
            for label in self._disease_classifier.id2label.values():
                crop, _ = _parse_class_label(str(label))
                if crop in MODEL_SUPPORTED_CROPS:
                    detected.add(crop)
            if detected:
                return sorted(detected)
        return sorted(MODEL_SUPPORTED_CROPS)

    def _base(self, crop_type: str) -> Dict[str, Any]:
        return {
            "cropType": crop_type,
            "modelName": self.model_name,
            "modelVersion": self.model_version,
            "modelSource": self.model_source,
            "isMock": False,
        }

    def _unsupported_crop(self, crop_type: str) -> Dict[str, Any]:
        result = self._base(crop_type)
        result.update({
            "status": "unsupported_crop",
            "is_valid_crop_image": False,
            "validation": {
                "is_plant": True,
                "is_crop": True,
                "crop_supported": False,
                "rejection_reason": f"The current model is not trained for '{crop_type}'.",
                "remedy": f"Supported crops: {', '.join(self.supported_crops())}.",
            },
            "crop": {"name": crop_type, "confidence_pct": 0},
            "condition": "Unsupported Crop",
            "confidence": 0.0,
            "confidence_pct": 0,
            "severity": "Unknown",
            "uncertainty": {"abstain": True, "reason": "Crop is outside model training classes."},
            "supported_crops": self.supported_crops(),
        })
        return result

    def _unavailable(self, crop_type: str) -> Dict[str, Any]:
        result = self._base(crop_type)
        result.update({
            "status": "model_unavailable",
            "is_valid_crop_image": False,
            "condition": "Model Unavailable",
            "confidence": 0.0,
            "confidence_pct": 0,
            "severity": "Unknown",
            "uncertainty": {"abstain": True, "reason": "The production checkpoint is not loaded."},
            "recommendations": {
                "immediate": "Start the backend with the versioned production ML checkpoint.",
                "monitoring": "No diagnosis is available.",
                "prevention": "Do not apply disease-specific treatment from this result.",
                "expert_help": "Consult a local agriculture expert if symptoms are severe.",
            },
            "isMock": True,
        })
        return result

    def _invalid_image(self, crop_type: str, reason: str) -> Dict[str, Any]:
        result = self._base(crop_type)
        result.update({
            "status": "invalid_image",
            "is_valid_crop_image": False,
            "condition": "Invalid Image",
            "confidence": 0.0,
            "confidence_pct": 0,
            "severity": "Unknown",
            "uncertainty": {"abstain": True, "reason": reason},
            "recommendations": {
                "immediate": "Retake a clear close-up photo of the affected leaf in natural light.",
                "monitoring": "No diagnosis was generated.",
                "prevention": "Do not apply disease-specific treatment from this result.",
                "expert_help": "Consult a KVK/agriculture extension officer if symptoms are severe.",
            },
        })
        return result

    def _abstain(self, crop_type: str, classification: Dict[str, Any], reason: str) -> Dict[str, Any]:
        confidence = max(0.0, min(float(classification.get("confidence", 0.0)), 1.0))
        predictions = classification.get("top_predictions", [])
        result = self._base(crop_type)
        result.update({
            "status": "uncertain",
            "is_valid_crop_image": True,
            "validation": {"is_plant": True, "is_crop": True, "crop_supported": True, "rejection_reason": None},
            "crop": {"name": crop_type, "confidence_pct": round(confidence * 100)},
            "condition": "Uncertain Result",
            "confidence": round(confidence, 4),
            "confidence_pct": round(confidence * 100),
            "severity": "Unknown",
            "severityPercentage": 0,
            "symptoms": [],
            "symptoms_observed": [],
            "differential_diagnoses": [
                {
                    "crop": p.get("crop", crop_type),
                    "condition": p.get("condition", ""),
                    "confidence_pct": round(float(p.get("confidence", 0)) * 100),
                    "key_distinguishing_feature": "Visually similar symptoms require a clearer image or field confirmation.",
                }
                for p in predictions[1:3]
            ],
            "uncertainty": {"abstain": True, "reason": reason},
            "recommendations": {
                "immediate": "Retake a sharp close-up image of one affected leaf in natural light.",
                "monitoring": "Do not apply disease-specific chemical treatment from this result.",
                "prevention": "Continue normal field scouting until a reliable diagnosis is available.",
                "expert_help": "Consult a KVK/agriculture extension officer if symptoms are spreading.",
            },
        })
        return result

    def analyze(self, pil_image: Image.Image, crop_type: str) -> Dict[str, Any]:
        from backend.ml.models.disease_classifier import normalize_crop_name

        crop_type = normalize_crop_name((crop_type or "").strip())
        if not crop_type or crop_type == "Unknown":
            return self._unsupported_crop("Unknown")
        if crop_type not in self.supported_crops():
            return self._unsupported_crop(crop_type)
        if self.provider_type != "real" or not self._models_loaded or self._disease_classifier is None:
            return self._unavailable(crop_type)
        if pil_image is None:
            return self._abstain(crop_type, {}, "No image was provided.")

        if self._plant_validator is None:
            return self._invalid_image(crop_type, "Plant validation model is unavailable; diagnosis is disabled for safety.")

        validation = self._plant_validator.validate(pil_image)
        if validation.get("image_quality", {}).get("status") == "fail":
            return self._invalid_image(crop_type, validation.get("rejection_reason", "Image quality gate failed."))
        if not validation.get("is_plant", False):
            return self._invalid_image(crop_type, validation.get("rejection_reason", "Plant validation failed."))

        classification = self._disease_classifier.classify(pil_image, top_k=5, crop_filter=crop_type)
        diagnostics = classification.get("confidence_diagnostics", {})
        confidence = max(0.0, min(float(classification.get("confidence", 0.0)), 1.0))
        crop_mass = float(diagnostics.get("crop_probability_mass", 0.0))
        crop_match = bool(diagnostics.get("crop_match", False))
        global_crop = str(diagnostics.get("global_top_crop", ""))

        if not crop_match or crop_mass < self.min_crop_mass:
            return self._abstain(
                crop_type,
                classification,
                f"Crop mismatch/weak crop evidence: requested={crop_type}, model_top_crop={global_crop}, crop_probability_mass={crop_mass:.2f}.",
            )
        if confidence < self.threshold:
            return self._abstain(
                crop_type, classification,
                f"Calibrated confidence ({confidence:.2f}) is below the reliability threshold ({self.threshold:.2f}).",
            )

        margin = float(diagnostics.get("top2_margin", 1.0))
        if margin < self.min_margin:
            return self._abstain(
                crop_type, classification,
                f"Top-2 diagnostic margin ({margin:.2f}) is below the required margin ({self.min_margin:.2f}).",
            )

        entropy = float(diagnostics.get("normalized_entropy", 1.0))
        if entropy > self.max_entropy:
            return self._abstain(
                crop_type, classification,
                f"Prediction entropy ({entropy:.2f}) is above the maximum ({self.max_entropy:.2f}).",
            )

        from backend.ml.models.severity_estimator import estimate_severity
        from backend.ml.config.disease_knowledge import get_disease_info
        from backend.ml.inference.dynamic_advisor import generate_dynamic_advisory

        raw_label = classification.get("raw_label", "")
        disease_info = get_disease_info(raw_label)
        healthy = bool(classification.get("is_healthy")) or "healthy" in raw_label.lower()
        severity_result = estimate_severity(pil_image, model_confidence=confidence, is_healthy=healthy)
        severity_map = {"healthy": "Healthy", "early": "Low", "moderate": "Moderate", "severe": "Severe"}
        severity = severity_map.get(severity_result.get("severity"), "Unknown")

        # A non-healthy result must not silently receive a fabricated severity.
        if not healthy and not severity_result.get("reliable", False):
            return self._abstain(crop_type, classification, "Disease identified, but severity estimation is not reliable enough to report.")

        differential = [
            {
                "crop": p.get("crop", crop_type),
                "condition": p.get("condition", ""),
                "name": f"{p.get('crop', '')} — {p.get('condition', '')}",
                "confidence_pct": round(float(p.get("confidence", 0)) * 100),
                "key_distinguishing_feature": "Compare lesion margin, color and distribution before treatment.",
            }
            for p in classification.get("top_predictions", [])[1:3]
        ]

        advisory = generate_dynamic_advisory(
            crop=disease_info.get("crop", crop_type),
            disease=disease_info.get("display_name", classification.get("condition", "Unknown")),
            pathogen=disease_info.get("pathogen", ""),
            severity_tier=severity,
            necrotic_area_pct=severity_result.get("severity_percentage", 0.0),
            confidence_pct=round(confidence * 100),
            differential_diagnoses=differential,
            base_info=disease_info,
        )

        structured_chem = disease_info.get("structured_chemical", {})
        regional_terms = disease_info.get("regional_terms", {})
        verification_note = disease_info.get(
            "verification_note",
            "Confirm the exact product, label dose and current registration status with a local KVK/agriculture extension officer before application.",
        )
        ipm = advisory.get("ipm", {})
        chemical = ipm.get("tier_2_chemical", [])
        biological = ipm.get("tier_1_biological", [])
        cultural = ipm.get("tier_3_cultural", [])
        chem_item = chemical[0] if chemical else {}
        bio_item = biological[0] if biological else {}

        result = self._base(crop_type)
        result.update({
            "status": "success",
            "image_quality": validation.get("image_quality", {"status": "pass"}),
            "validation": {"is_plant": True, "is_crop": True, "crop_supported": True, "rejection_reason": None},
            "crop": {"name": disease_info.get("crop", crop_type), "confidence_pct": round(confidence * 100)},
            "plant_part": "leaf",
            "diagnosis": {
                "category": disease_info.get("pathogen_category", "Unknown").lower(),
                "name": disease_info.get("display_name", classification.get("condition", "Analyzed Disease")),
                "causal_agent": disease_info.get("pathogen", ""),
                "confidence_pct": round(confidence * 100),
            },
            "condition": disease_info.get("display_name", classification.get("condition", "Analyzed Disease")),
            "confidence": round(confidence, 4),
            "confidence_pct": round(confidence * 100),
            "severity": severity,
            "severityPercentage": round(float(severity_result.get("severity_percentage", 0.0))),
            "evidence_features": advisory.get("symptoms_observed", []),
            "symptoms": advisory.get("symptoms_observed", []),
            "symptoms_observed": advisory.get("symptoms_observed", []),
            "differential_diagnoses": differential,
            "uncertainty": {"abstain": False, "reason": None},
            "ipm": ipm,
            "farmer_summary": advisory.get("farmer_summary", ""),
            "treatment_organic": [
                f"{b.get('agent', 'Biological option')} — {b.get('dosage', 'Follow the registered label.')}"
                for b in biological
            ],
            "treatment_chemical": [
                f"{c.get('active_ingredient', '')} — {c.get('dose_ml_per_15L', c.get('dosage', 'Follow label'))}"
                for c in chemical
            ],
            "prevention_tips": cultural,
            "structured_chemical": structured_chem,
            "regional_terms": regional_terms,
            "verification_note": verification_note,
            "treatmentPlan": {
                "organic": {
                    "name": bio_item.get("agent", "Biological control option"),
                    "dosage": bio_item.get("dosage", "Follow the registered product label."),
                    "applicationSchedule": bio_item.get("application_timing", "Follow the registered product label."),
                },
                "chemical": {
                    "name": chem_item.get("active_ingredient", "No verified chemical option returned"),
                    "dosage": chem_item.get("dosage", chem_item.get("dose_ml_per_15L", "Follow the registered product label.")),
                    "dose_15L_tank": chem_item.get("dose_ml_per_15L"),
                    "frac_code": chem_item.get("frac_code", structured_chem.get("frac_code")),
                    "rotation_partner": structured_chem.get("rotation_partner"),
                    "safetyIntervalDays": structured_chem.get("phi_days"),
                },
                "preventive": {
                    "cultural": cultural[0] if cultural else "Maintain field sanitation and scout regularly.",
                    "irrigation": "Avoid prolonged foliar wetness where agronomically appropriate.",
                },
            },
            "droneMissionReady": False,
            "is_low_confidence": False,
            "provenance": {
                "source": "local_efficientnet_v2_s",
                "confidence_is_calibrated": self._is_calibrated,
                "treatment_allowed": not healthy,
                "crop_probability_mass": round(crop_mass, 4),
                "global_top_crop": global_crop,
            },
        })
        return result


inference_engine = ProductionInferenceEngine()
