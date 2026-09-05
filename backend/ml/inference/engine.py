from PIL import Image
from typing import Dict, Any
import os
import logging
from backend.config import settings
from backend.ml.models.base import CropDiseaseModel
from backend.ml.models.mock_model import MockCropDiseaseModel
from backend.ml.models.efficientnet_model import EfficientNetCropDiseaseModel

logger = logging.getLogger(__name__)

class InferenceEngine:
    def __init__(self):
        self.provider_type = settings.AI_MODEL_PROVIDER.lower()
        self.threshold = settings.AI_CONFIDENCE_THRESHOLD
        self.model: CropDiseaseModel = self._load_provider()

    def _load_provider(self) -> CropDiseaseModel:
        # If explicit provider is set to efficientnet, use it.
        if self.provider_type == "efficientnet":
            logger.info(f"[InferenceEngine] Initializing EfficientNet-B3 provider with threshold {self.threshold}...")
            return EfficientNetCropDiseaseModel(checkpoint_path=settings.AI_MODEL_PATH)

        # Auto-detect: if a checkpoint file exists at AI_MODEL_PATH, prefer EfficientNet provider
        try:
            ck_path = settings.AI_MODEL_PATH
            if ck_path and os.path.exists(ck_path):
                # If a meta checkpoint exists alongside the state dict, prefer loading meta so class labels are available
                meta_path = ck_path + ".ckpt.pth"
                if os.path.exists(meta_path):
                    logger.info(f"[InferenceEngine] Meta checkpoint found at {meta_path}; initializing EfficientNet provider with meta (auto-detect).")
                    self.provider_type = 'efficientnet'
                    return EfficientNetCropDiseaseModel(checkpoint_path=meta_path)

                # No meta; fallback to raw checkpoint file if present
                logger.info(f"[InferenceEngine] Checkpoint detected at {ck_path}; initializing EfficientNet provider (auto-detect).")
                self.provider_type = 'efficientnet'
                return EfficientNetCropDiseaseModel(checkpoint_path=ck_path)
        except Exception:
            pass

        # Fallback to mock
        logger.info(f"[InferenceEngine] Initializing Development Mock provider with threshold {self.threshold}...")
        self.provider_type = 'mock'
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
