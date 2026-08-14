from PIL import Image
from typing import Dict, Any
from backend.config import settings
from backend.ml.models.base import CropDiseaseModel
from backend.ml.models.mock_model import MockCropDiseaseModel
from backend.ml.models.efficientnet_model import EfficientNetCropDiseaseModel

class InferenceEngine:
    def __init__(self):
        self.provider_type = settings.AI_MODEL_PROVIDER.lower()
        self.threshold = settings.AI_CONFIDENCE_THRESHOLD
        self.model: CropDiseaseModel = self._load_provider()

    def _load_provider(self) -> CropDiseaseModel:
        if self.provider_type == "efficientnet":
            print(f"[InferenceEngine] Initializing EfficientNet-B3 provider with threshold {self.threshold}...")
            return EfficientNetCropDiseaseModel(checkpoint_path=settings.AI_MODEL_PATH)
        else:
            print(f"[InferenceEngine] Initializing Development Mock provider with threshold {self.threshold}...")
            return MockCropDiseaseModel()

    def analyze(self, pil_image: Image.Image, crop_type: str) -> Dict[str, Any]:
        result = self.model.predict(pil_image, crop_type)
        
        # Check against low confidence threshold (e.g. 0.70)
        confidence = result.get("confidence", 0.0)
        if confidence < self.threshold:
            result["is_low_confidence"] = True
            result["condition_label"] = "Uncertain Result"
            result["low_confidence_notice"] = (
                f"The AI confidence ({int(confidence*100)}%) is below the reliable threshold ({int(self.threshold*100)}%). "
                "The image does not provide enough clear evidence for a definitive diagnosis. "
                "Please retake a sharper photo in bright, natural light."
            )
        else:
            result["is_low_confidence"] = False
            result["condition_label"] = result.get("condition", "Analyzed")

        return result

# Global singleton engine instance
inference_engine = InferenceEngine()
