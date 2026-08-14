import hashlib
import numpy as np
from PIL import Image
from typing import Dict, Any
from backend.ml.models.base import CropDiseaseModel
from backend.ml.config.ml_config import KNOWLEDGE_BASE

class MockCropDiseaseModel(CropDiseaseModel):
    @property
    def model_name(self) -> str:
        return "MockDevelopmentInferenceProvider"

    @property
    def model_version(self) -> str:
        return "mock-v1.0-dev"

    def predict(self, pil_image: Image.Image, crop_type: str) -> Dict[str, Any]:
        # Generate deterministic mock output based on image bytes hash & average color
        img_np = np.array(pil_image)
        img_hash = hashlib.sha256(img_np.tobytes()[:2000]).hexdigest()
        hash_val = int(img_hash[:8], 16)

        crop_kb = KNOWLEDGE_BASE.get(crop_type, KNOWLEDGE_BASE["Default"])
        conditions = list(crop_kb.keys())

        # Select condition deterministically
        condition = conditions[hash_val % len(conditions)]
        disease_info = crop_kb[condition]

        # Calculate realistic confidence score (e.g., 0.88 to 0.96 for clear, or lower if dark)
        mean_green = np.mean(img_np[:, :, 1])
        mean_red = np.mean(img_np[:, :, 0])
        
        # High green ratio gives healthy/high confidence
        if mean_green > mean_red * 1.1:
            confidence = round(0.89 + (hash_val % 9) / 100.0, 2)
        else:
            confidence = round(0.82 + (hash_val % 13) / 100.0, 2)

        return {
            "crop": crop_type,
            "condition": condition,
            "confidence": confidence,
            "severity": disease_info["severity"],
            "pathogen": disease_info.get("pathogen", "Pathogen complex"),
            "symptoms": disease_info["symptoms"],
            "recommendations": disease_info["recommendations"],
            "model_name": self.model_name,
            "model_version": self.model_version,
            "is_mock": True
        }
