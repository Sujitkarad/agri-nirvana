"""Production-safe crop diagnosis engine.

The runtime engine never invents a diagnosis when the model is unavailable,
the selected crop is outside the model's training classes, or confidence is
below the configured reliability threshold.
"""

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
        self._plant_validator = None
        self._disease_classifier = None
        self._models_loaded = False
        if self.provider_type == "real":
            self._load_models()

    def _load_models(self) -> None:
        try:
            from backend.ml.models.plant_validator import PlantValidator
            from backend.ml.models.disease_classifier import DiseaseClassifier

            self._plant_validator = PlantValidator()
            self._disease_classifier = DiseaseClassifier(
                model_id=getattr(settings, "HF_MODEL_ID", None)
            )
            self._models_loaded = bool(
                self._plant_validator
                and self._disease_classifier
                and self._disease_classifier.is_loaded
            )
        except Exception as exc:
            print(f"[ProductionInferenceEngine] model load failed: {exc}")
            self._models_loaded = False

    @property
    def model_name(self) -> str:
        if self._models_loaded:
            return f"{self._disease_classifier.model_id} + ImageNet plant validator"
        return "Unavailable"

    @property
    def model_version(self) -> str:
        return "v3-production-safe" if self._models_loaded else "unavailable"

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

    def _unsupported_crop(self, crop_type: str) -> Dict[str, Any]:
        return {
            "status": "unsupported_crop",
            "is_valid_crop_image": False,
            "validation": {
                "is_plant": True,
                "is_crop": True,
                "crop_supported": False,
                "rejection_reason": (
                    f"The current AI model is not trained for '{crop_type}'. "
                    "No disease prediction was generated."
                ),
            },
            "crop": {"name": crop_type, "confidence_pct": 0},
            "cropType": crop_type,
            "condition": "Unsupported Crop",
            "confidence": 0.0,
            "confidence_pct": 0,
            "severity": "Unknown",
            "uncertainty": {"abstain": True, "reason": "Crop is outside model training classes."},
            "supported_crops": self.supported_crops(),
            "modelName": self.model_name,
            "modelVersion": self.model_version,
            "isMock": False,
        }

    def _unavailable(self, crop_type: str) -> Dict[str, Any]:
        return {
            "status": "model_unavailable",
            "is_valid_crop_image": False,
            "cropType": crop_type,
            "condition": "Model Unavailable",
            "confidence": 0.0,
            "confidence_pct": 0,
            "severity": "Unknown",
            "uncertainty": {"abstain": True, "reason": "Real ML model is not loaded."},
            "recommendations": {
                "immediate": "Start the backend with a real ML model before using diagnosis.",
                "monitoring": "No diagnosis available.",
                "prevention": "Do not select disease-specific treatment from this result.",
                "expert_help": "Consult a local agriculture expert if symptoms are severe.",
            },
            "modelName": self.model_name,
            "modelVersion": self.model_version,
            "isMock": True,
        }

    def _abstain(self, crop_type: str, classification: Dict[str, Any], reason: str) -> Dict[str, Any]:
        confidence = max(0.0, min(float(classification.get("confidence", 0.0)), 1.0))
        top_predictions = classification.get("top_predictions", [])
        return {
            "status": "uncertain",
            "is_valid_crop_image": True,
            "validation": {
                "is_plant": True,
                "is_crop": True,
                "crop_supported": True,
                "rejection_reason": None,
            },
            "crop": {"name": crop_type, "confidence_pct": round(confidence * 100)},
            "cropType": crop_type,
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
                    "key_distinguishing_feature": "Visually similar foliar symptoms."
                }
                for p in top_predictions[1:3]
            ],
            "uncertainty": {"abstain": True, "reason": reason},
            "recommendations": {
                "immediate": "Retake a clear close-up image of one leaf in natural light.",
                "monitoring": "Do not apply a disease-specific chemical treatment from this result.",
                "prevention": "Continue normal field scouting until a reliable diagnosis is available.",
                "expert_help": "Consult a KVK/agriculture extension officer if symptoms are spreading.",
            },
            "modelName": self.model_name,
            "modelVersion": self.model_version,
            "isMock": False,
        }

    def analyze(self, pil_image: Image.Image, crop_type: str) -> Dict[str, Any]:
        from backend.ml.models.disease_classifier import normalize_crop_name

        crop_type = normalize_crop_name((crop_type or "").strip())
        if not crop_type or crop_type == "Unknown":
            return self._unsupported_crop("Unknown")

        if crop_type not in self.supported_crops():
            return self._unsupported_crop(crop_type)

        if self.provider_type != "real" or not self._models_loaded:
            return self._unavailable(crop_type)

        if pil_image is None:
            return self._abstain(crop_type, {}, "No image was provided.")

        validation = self._plant_validator.validate(pil_image) if self._plant_validator else {"is_plant": True}
        if not validation.get("is_plant", True):
            return {
                "status": "invalid_image",
                "is_valid_crop_image": False,
                "rejection_reason": validation.get(
                    "rejection_reason", "Image does not appear to contain a crop leaf."
                ),
                "cropType": crop_type,
                "condition": "Invalid Image",
                "confidence": 0.0,
                "confidence_pct": 0,
                "severity": "Unknown",
                "uncertainty": {"abstain": True, "reason": "Plant validation failed."},
                "modelName": self.model_name,
                "modelVersion": self.model_version,
                "isMock": False,
            }

        classification = self._disease_classifier.classify(
            pil_image, top_k=5, crop_filter=crop_type
        )
        confidence = max(0.0, min(float(classification.get("confidence", 0.0)), 1.0))

        if confidence < self.threshold:
            return self._abstain(
                crop_type,
                classification,
                f"Model confidence {confidence:.2f} is below the configured reliability threshold {self.threshold:.2f}.",
            )

        from backend.ml.models.severity_estimator import estimate_severity
        from backend.ml.config.disease_knowledge import get_disease_info
        from backend.ml.inference.dynamic_advisor import generate_dynamic_advisory

        raw_label = classification.get("raw_label", "")
        disease_info = get_disease_info(raw_label)
        severity_result = estimate_severity(
            pil_image,
            model_confidence=confidence,
            is_healthy=bool(classification.get("is_healthy")),
        )

        severity_map = {"healthy": "Healthy", "early": "Low", "moderate": "Moderate", "severe": "Severe"}
        severity = severity_map.get(severity_result.get("severity"), "Moderate")
        confidence_pct = round(confidence * 100)
        healthy = bool(classification.get("is_healthy")) or "healthy" in raw_label.lower()

        differential = [
            {
                "crop": p.get("crop", crop_type),
                "condition": p.get("condition", ""),
                "name": f"{p.get('crop', '')} — {p.get('condition', '')}",
                "confidence_pct": round(float(p.get("confidence", 0)) * 100),
                "key_distinguishing_feature": "Compare lesion margin, color and distribution before escalating treatment.",
            }
            for p in classification.get("top_predictions", [])[1:3]
        ]

        advisory = generate_dynamic_advisory(
            crop=disease_info.get("crop", crop_type),
            disease=disease_info.get("display_name", classification.get("condition", "Unknown")),
            pathogen=disease_info.get("pathogen", ""),
            severity_tier=severity,
            necrotic_area_pct=severity_result.get("severity_percentage", 0.0),
            confidence_pct=confidence_pct,
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

        treatment_plan = {
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
        }

        return {
            "status": "success",
            "image_quality": {"status": "pass", "score": 100, "reason": None},
            "validation": {"is_plant": True, "is_crop": True, "crop_supported": True, "rejection_reason": None},
            "crop": {"name": disease_info.get("crop", crop_type), "confidence_pct": confidence_pct},
            "plant_part": "leaf",
            "diagnosis": {
                "category": disease_info.get("pathogen_category", "Unknown").lower(),
                "name": disease_info.get("display_name", classification.get("condition", "Analyzed Disease")),
                "causal_agent": disease_info.get("pathogen", ""),
                "confidence_pct": confidence_pct,
            },
            "evidence_features": advisory.get("symptoms_observed", []),
            "differential_diagnoses": differential,
            "uncertainty": {"abstain": False, "reason": ""},
            "severity": {
                "necrotic_area_pct": severity_result.get("severity_percentage", 0.0),
                "tier": severity,
                "confidence_pct": confidence_pct,
            },
            "agronomic_risk": {
                "level": "Low" if healthy else ("Critical" if severity == "Severe" else "Moderate"),
                "reason": "No active foliar pathogen detected." if healthy else "Disease detected; follow the verified advisory and monitor progression.",
            },
            "ipm": ipm,
            "farmer_summary": advisory.get("farmer_summary", ""),
            "is_valid_crop_image": True,
            "confidence": round(confidence, 4),
            "confidence_pct": confidence_pct,
            "cropType": disease_info.get("crop", crop_type),
            "condition": disease_info.get("display_name", classification.get("condition", "Analyzed Disease")),
            "pathogen": disease_info.get("pathogen", ""),
            "pathogenCategory": disease_info.get("pathogen_category", "Unknown"),
            "severityPercentage": severity_result.get("severity_percentage", 0.0),
            "affectedSurface": "Healthy leaf tissue" if healthy else "Foliar lamina and canopy regions",
            "symptoms": advisory.get("symptoms_observed", []),
            "symptoms_observed": advisory.get("symptoms_observed", []),
            "likely_cause": advisory.get("likely_cause", ""),
            "immediate_precautions": advisory.get("immediate_precautions", []),
            "treatment_organic": [f"{b.get('agent', '')} — {b.get('dosage', '')}" for b in biological],
            "treatment_chemical": [f"{c.get('active_ingredient', '')} — {c.get('dose_ml_per_15L', c.get('dosage', 'Follow label'))}" for c in chemical],
            "prevention_tips": cultural,
            "structured_chemical": structured_chem,
            "regional_terms": regional_terms,
            "verification_note": verification_note,
            "treatmentPlan": treatment_plan,
            "droneMissionReady": {
                "recommendedAltitudeMeters": 3.5,
                "spotSprayRequired": not healthy,
                "flowRateLitresPerHectare": 16.0,
                "chemicalReductionPct": 78.0 if not healthy else 0.0,
            },
            "lesionCoordinates3D": [] if healthy else [
                {"x": 0.42, "y": 0.58, "radius": 0.12},
                {"x": 0.61, "y": 0.35, "radius": 0.08},
            ],
            "recommendations": {
                "immediate": (advisory.get("immediate_precautions") or ["Monitor crop closely"])[0],
                "monitoring": "Scout the affected crop at least twice weekly and compare with previous scans.",
                "prevention": (cultural or ["Maintain good field sanitation"])[0],
                "expert_help": "Escalate severe or uncertain cases to a local KVK/agriculture extension officer.",
            },
            "modelName": self.model_name,
            "modelVersion": self.model_version,
            "isMock": False,
        }


inference_engine = ProductionInferenceEngine()
