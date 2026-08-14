from abc import ABC, abstractmethod
from typing import Dict, Any
from PIL import Image

class CropDiseaseModel(ABC):
    @property
    @abstractmethod
    def model_name(self) -> str:
        pass

    @property
    @abstractmethod
    def model_version(self) -> str:
        pass

    @abstractmethod
    def predict(self, pil_image: Image.Image, crop_type: str) -> Dict[str, Any]:
        """
        Executes prediction on PIL image for given crop type.
        Returns structured dict matching schema:
        {
            "crop": str,
            "condition": str,
            "confidence": float (0.0 to 1.0),
            "severity": str ("Healthy", "Low", "Moderate", "Severe", "Unknown"),
            "symptoms": list[str],
            "recommendations": dict,
            "model_name": str,
            "model_version": str,
            "is_mock": bool
        }
        """
        pass
