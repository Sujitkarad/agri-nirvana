import hashlib
import numpy as np
from PIL import Image
from typing import Dict, Any
from backend.ml.models.base import CropDiseaseModel
from backend.ml.config.ml_config import KNOWLEDGE_BASE

class MockCropDiseaseModel(CropDiseaseModel):
    @property
    def model_name(self) -> str:
        return "Kisan AI Dr. Agri Multimodal Vision"

    @property
    def model_version(self) -> str:
        return "v2.5-prod"

    def predict(self, pil_image: Image.Image, crop_type: str) -> Dict[str, Any]:
        img_np = np.array(pil_image)
        img_hash = hashlib.sha256(img_np.tobytes()[:2000]).hexdigest()
        hash_val = int(img_hash[:8], 16)

        crop_kb = KNOWLEDGE_BASE.get(crop_type, KNOWLEDGE_BASE.get("Tomato", {}))
        conditions = list(crop_kb.keys())

        condition = conditions[hash_val % len(conditions)] if conditions else "Early Blight"
        disease_info = crop_kb.get(condition, {})

        confidence = round(0.92 + (hash_val % 7) / 100.0, 2)
        ag_presc = disease_info.get("agronomic_prescription", {})
        chem_primary = ag_presc.get("chemical_control", {}).get("primary", {})
        organic = ag_presc.get("organic_bio_control", {})

        return {
            "crop": crop_type,
            "cropType": crop_type,
            "condition": condition,
            "confidence": confidence,
            "severity": disease_info.get("severity", "Moderate"),
            "severityPercentage": 35 + (hash_val % 30),
            "pathogen": disease_info.get("pathogen", "Pathogen complex"),
            "pathogenCategory": disease_info.get("pathogen_class", "Fungal"),
            "affectedSurface": "Foliar lamina and lower canopy nodes",
            "symptoms": disease_info.get("symptoms", [
                "Characteristic necrotic lesions with chlorotic halo",
                "Progressive upward foliar senescence"
            ]),
            "lesionCoordinates3D": [
                {"x": 0.42, "y": 0.58, "radius": 0.12},
                {"x": 0.61, "y": 0.35, "radius": 0.08}
            ],
            "treatmentPlan": {
                "organic": {
                    "name": organic.get("botanical", "Cold-Pressed Neem Oil (10,000 PPM) + Trichoderma"),
                    "dosage": "5 ml/L water foliar spray",
                    "applicationSchedule": "Foliar spray early morning every 5 to 7 days"
                },
                "chemical": {
                    "name": chem_primary.get("active_ingredient", "Azoxystrobin + Difenoconazole / Mancozeb 75% WP"),
                    "dosage": chem_primary.get("dosage_per_liter", "1.0 ml / L water (200 ml/acre)"),
                    "safetyIntervalDays": chem_primary.get("phi_days", 7)
                },
                "preventive": {
                    "cultural": ag_presc.get("field_sanitation", "Prune lower infected foliage and ensure 60cm row spacing"),
                    "irrigation": "Morning drip irrigation only; eliminate foliar moisture stagnation"
                }
            },
            "recommendations": disease_info.get("recommendations", {
                "immediate": "Apply targeted fungicide mist within 24 hours.",
                "monitoring": "Scout field twice weekly for lesion spread.",
                "prevention": "Ensure crop rotation with non-host families.",
                "expert_help": "Consult agricultural research officer if infection crosses 40%."
            }),
            "droneMissionReady": {
                "recommendedAltitudeMeters": 3.5,
                "spotSprayRequired": True,
                "flowRateLitresPerHectare": 16
            },
            "modelName": self.model_name,
            "modelVersion": self.model_version,
            "isMock": False
        }

