"""Production-safe crop diagnosis engine.

This engine deliberately refuses to fabricate a diagnosis when the active
model does not contain the requested crop or when confidence is too low.
It is the runtime engine used by the API; the legacy engine remains in the
repository for backwards compatibility but is no longer imported by routes.
"""

from typing import Any, Dict, List

from PIL import Image

from backend.config import settings


# PlantVillage crops actually represented by the current classifier.
# Do not add Maharashtra crops here until a model trained on those crops exists.
MODEL_SUPPORTED_CROPS = {
    "Apple",
    "Blueberry",
    "Cherry",
    "Corn",
    "Grape",
    "Orange",
    "Peach",
    "Pepper",
    "Potato",
    "Raspberry",
    "Soybean",
    "Squash",
    "Strawberry",
    "Tomato",
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
        return "v2-production-safe" if self._models_loaded else "unavailable"

    def supported_crops(self) -> List[str]:
        if self._disease_classifier and self._disease_classifier.id2label:
            crops = set()
            from backend.ml.models.disease_classifier import _parse_class_label
            for label in self._disease_classifier.id2label.values():
                crop, _ = _parse_class_label(str(label))
                crops.add(crop)
            if crops:
                return sorted(crops)
        return sorted(MODEL_SUPPORTED_CROPS)

    def _unsupported_crop(self, crop_type: str) -> Dict[str, Any]:
        supported = self.supported_crops()
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
            "supported_crops": supported,
            "modelName": self.model_name,
            "modelVersion": self.model_version,
            "isMock": False,
        }

    def _abstain(self, crop_type: str, classification: Dict[str, Any], reason: str) -> Dict[str, Any]:
        confidence = float(classification.get("confidence", 0.0))
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
                    "name": f"{p.get('crop', '')} — {p.get('condition', '')}",
                    "confidence_pct": round(float(p.get("confidence", 0)) * 100),
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
        crop_type = (crop_type or "").strip()
        if not crop_type:
            return self._unsupported_crop("Unknown")

        if self.provider_type != "real" or not self._models_loaded:
            return {
                "status": "model_unavailable",
                "is_valid_crop_image": False,
                "cropType": crop_type,
                "condition": "Model Unavailable",
                "confidence": 0.0,
                "uncertainty": {"abstain": True, "reason": "Real ML model is not loaded."},
                "recommendations": {
                    "immediate": "Start the backend with a real ML model before using diagnosis.",
                    "monitoring": "No diagnosis available.",
                    "prevention": "No disease-specific treatment should be selected.",
                    "expert_help": "Consult a local agriculture expert if symptoms are severe.",
                },
                "modelName": self.model_name,
                "modelVersion": self.model_version,
                "isMock": True,
            }

        supported_lower = {c.lower(): c for c in self.supported_crops()}
        if crop_type.lower() not in supported_lower:
            return self._unsupported_crop(crop_type)

        validation = self._plant_validator.validate(pil_image)
        if not validation.get("is_plant", False):
            return {
                "status": "invalid_image",
                "is_valid_crop_image": False,
                "rejection_reason": validation.get("rejection_reason", "Image is not a valid plant image."),
                "cropType": crop_type,
                "condition": "Invalid Image",
                "confidence": 0.0,
                "severity": "Unknown",
                "uncertainty": {"abstain": True, "reason": "Plant validation failed."},
                "modelName": self.model_name,
                "modelVersion": self.model_version,
                "isMock": False,
            }

        classification = self._disease_classifier.classify(
            pil_image, top_k=5, crop_filter=supported_lower[crop_type.lower()]
        )
        confidence = float(classification.get("confidence", 0.0))

        if confidence < self.threshold:
            return self._abstain(
                crop_type,
                classification,
                f"Model confidence {confidence:.2f} is below the reliability threshold {self.threshold:.2f}.",
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
        severity = severity_map.get(severity_result.get("severity"), "Unknown")
        confidence_pct = round(confidence * 100)

        differential = []
        for prediction in classification.get("top_predictions", [])[1:3]:
            differential.append({
                "name": f"{prediction.get('crop', '')} — {prediction.get('condition', '')}",
                "confidence_pct": round(float(prediction.get("confidence", 0)) * 100),
            })

        advisory = generate_dynamic_advisory(
            crop=disease_info.get("crop", crop_type),
            disease=disease_info.get("display_name", classification.get("condition", "Unknown")),
            pathogen=disease_info.get("pathogen", ""),
            severity_tier=severity,
            necrotic_area_pct=severity_result.get("severity_percentage", 0),
            confidence_pct=confidence_pct,
            differential_diagnoses=differential,
            base_info=disease_info,
        )

        healthy = bool(classification.get("is_healthy"))
        return {
            "status": "success",
            "image_quality": {"status": "pass", "score": 100, "reason": None},
            "validation": {"is_plant": True, "is_crop": True, "crop_supported": True, "rejection_reason": None},
            "crop": {"name": disease_info.get("crop", crop_type), "confidence_pct": confidence_pct},
            "plant_part": "leaf",
            "diagnosis": {
                "category": disease_info.get("pathogen_category", "Unknown").lower(),
                "name": disease_info.get("display_name", classification.get("condition", "Unknown")),
                "causal_agent": disease_info.get("pathogen", ""),
                "confidence_pct": confidence_pct,
            },
            "evidence_features": advisory.get("symptoms_observed", []),
            "differential_diagnoses": differential,
            "uncertainty": {"abstain": False, "reason": ""},
            "severity": {
                "necrotic_area_pct": severity_result.get("severity_percentage", 0),
                "tier": severity,
                "confidence_pct": confidence_pct,
            },
            "agronomic_risk": {
                "level": "Low" if healthy else ("Critical" if severity == "Severe" else "Moderate"),
                "reason": "No active foliar pathogen detected." if healthy else "Disease detected; follow the verified advisory and monitor progression.",
            },
            "ipm": advisory.get("ipm", {}),
            "farmer_summary": advisory.get("farmer_summary", ""),
            "is_valid_crop_image": True,
            "confidence": round(confidence, 4),
            "confidence_pct": confidence_pct,
            "cropType": disease_info.get("crop", crop_type),
            "condition": disease_info.get("display_name", classification.get("condition", "Unknown")),
            "pathogen": disease_info.get("pathogen", ""),
            "pathogenCategory": disease_info.get("pathogen_category", "Unknown"),
            "severityPercentage": severity_result.get("severity_percentage", 0),
            "symptoms": advisory.get("symptoms_observed", []),
            "symptoms_observed": advisory.get("symptoms_observed", []),
            "likely_cause": advisory.get("likely_cause", ""),
            "immediate_precautions": advisory.get("immediate_precautions", []),
            "treatment_organic": advisory.get("ipm", {}).get("tier_1_biological", []),
            "treatment_chemical": advisory.get("ipm", {}).get("tier_2_chemical", []),
            "prevention_tips": advisory.get("ipm", {}).get("tier_3_cultural", []),
            "recommendations": {
                "immediate": (advisory.get("immediate_precautions") or ["Monitor crop closely"])[0],
                "monitoring": "Scout the affected crop at least twice weekly and compare with the previous diagnosis.",
                "prevention": (advisory.get("ipm", {}).get("tier_3_cultural") or ["Maintain good field sanitation"])[0],
                "expert_help": "Escalate severe or uncertain cases to a local KVK/agriculture extension officer.",
            },
            "modelName": self.model_name,
            "modelVersion": self.model_version,
            "isMock": False,
        }


inference_engine = ProductionInferenceEngine()
