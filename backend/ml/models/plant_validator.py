"""Stage A — conservative plant/leaf image validation gate.

This gate rejects clearly unusable uploads and records measurable quality
signals. It is intentionally conservative: ImageNet is used as a coarse
vegetation signal, while the disease model remains responsible for diagnosis.
"""

from typing import Dict

import torch
import torch.nn.functional as F
from PIL import Image
from torchvision import models
from torchvision.models import MobileNet_V2_Weights

from backend.ml.config.imagenet_plant_classes import build_plant_class_indices


class PlantValidator:
    MIN_WIDTH = 256
    MIN_HEIGHT = 256
    MIN_PLANT_CUMULATIVE = 0.10
    MIN_ALL_PLANT_PROBABILITY = 0.15
    MIN_BEST_PLANT_CONFIDENCE = 0.05
    MIN_FOLIAGE_RATIO = 0.30

    def __init__(self):
        print("[PlantValidator] Loading MobileNetV2 (ImageNet-1K) for plant validation...")
        self.weights = MobileNet_V2_Weights.IMAGENET1K_V1
        self.model = models.mobilenet_v2(weights=self.weights)
        self.model.eval()
        self.transform = self.weights.transforms()
        self.categories = self.weights.meta["categories"]
        self.plant_indices = build_plant_class_indices(self.categories)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        print(f"[PlantValidator] Mapped {len(self.plant_indices)} plant-related ImageNet classes")
        print(f"[PlantValidator] Ready on {self.device}")

    @staticmethod
    def _quality_check(pil_image: Image.Image) -> Dict:
        width, height = pil_image.size
        quality = {
            "status": "pass",
            "width": width,
            "height": height,
            "megapixels": round((width * height) / 1_000_000, 3),
            "brightness": None,
            "sharpness": None,
            "reason": None,
        }
        if width < PlantValidator.MIN_WIDTH or height < PlantValidator.MIN_HEIGHT:
            quality["status"] = "fail"
            quality["reason"] = (
                f"Image is too small for reliable diagnosis ({width}x{height}). "
                f"Use at least {PlantValidator.MIN_WIDTH}x{PlantValidator.MIN_HEIGHT}px."
            )
            return quality
        try:
            import numpy as np
            gray = np.asarray(pil_image.convert("L"), dtype=np.float32)
            quality["brightness"] = round(float(gray.mean()) / 255.0, 3)
            center = gray[1:-1, 1:-1]
            lap = (
                gray[:-2, 1:-1] + gray[2:, 1:-1] + gray[1:-1, :-2]
                + gray[1:-1, 2:] - 4.0 * center
            )
            quality["sharpness"] = round(float(lap.var()), 2)
            if quality["brightness"] < 0.04 or quality["brightness"] > 0.98:
                quality["status"] = "warning"
                quality["reason"] = "Lighting is extreme; diagnosis confidence may be reduced."
            elif quality["sharpness"] < 8.0:
                quality["status"] = "warning"
                quality["reason"] = "Image may be blurry; retake a close-up in steady natural light."
        except Exception:
            quality["status"] = "pass"
        return quality

    @torch.no_grad()
    def validate(self, pil_image: Image.Image, top_k: int = 10) -> Dict:
        if pil_image is None:
            return {
                "is_plant": False,
                "top_plant_class": None,
                "top_plant_confidence": 0.0,
                "plant_cumulative_score": 0.0,
                "all_plant_probability": 0.0,
                "top_predictions": [],
                "image_quality": {"status": "fail", "reason": "No image was provided."},
                "rejection_reason": "No image was provided.",
            }

        quality = self._quality_check(pil_image)
        if quality["status"] == "fail":
            return {
                "is_plant": False,
                "top_plant_class": None,
                "top_plant_confidence": 0.0,
                "plant_cumulative_score": 0.0,
                "all_plant_probability": 0.0,
                "top_predictions": [],
                "image_quality": quality,
                "rejection_reason": quality["reason"],
            }

        tensor = self.transform(pil_image.convert("RGB")).unsqueeze(0).to(self.device)
        probabilities = F.softmax(self.model(tensor)[0], dim=0)
        k = min(top_k, len(probabilities))
        top_probs, top_indices = torch.topk(probabilities, k)
        top_predictions = [(self.categories[idx.item()], prob.item()) for prob, idx in zip(top_probs, top_indices)]

        best_plant_class = None
        best_plant_conf = 0.0
        plant_cumulative = 0.0
        for idx_tensor, prob_tensor in zip(top_indices, top_probs):
            idx = idx_tensor.item()
            prob = prob_tensor.item()
            if idx in self.plant_indices:
                plant_cumulative += prob
                if prob > best_plant_conf:
                    best_plant_conf = prob
                    best_plant_class = self.categories[idx]

        all_plant_prob = sum(probabilities[i].item() for i in self.plant_indices)

        try:
            import numpy as np
            img_rgb = np.asarray(pil_image.convert("RGB"), dtype=np.float32)
            r, g, b = img_rgb[:, :, 0], img_rgb[:, :, 1], img_rgb[:, :, 2]
            foliage_mask = ((g > r * 0.80) & (g > b * 0.80)) | ((r > 80) & (g > 80) & (b < 140))
            foliage_ratio = float(foliage_mask.mean())
        except Exception:
            foliage_ratio = 0.0

        is_plant = (
            plant_cumulative >= self.MIN_PLANT_CUMULATIVE
            or all_plant_prob >= self.MIN_ALL_PLANT_PROBABILITY
            or best_plant_conf >= self.MIN_BEST_PLANT_CONFIDENCE
            or foliage_ratio >= self.MIN_FOLIAGE_RATIO
        )

        rejection_reason = None
        if not is_plant:
            top_class = top_predictions[0][0] if top_predictions else "unknown"
            rejection_reason = (
                "This does not contain enough evidence of a crop/leaf image. "
                f"The strongest ImageNet class was '{top_class}'. Upload a clear close-up of the affected plant part."
            )

        return {
            "is_plant": is_plant,
            "top_plant_class": best_plant_class,
            "top_plant_confidence": round(best_plant_conf, 4),
            "plant_cumulative_score": round(plant_cumulative, 4),
            "all_plant_probability": round(all_plant_prob, 4),
            "foliage_ratio": round(foliage_ratio, 4),
            "top_predictions": top_predictions,
            "image_quality": quality,
            "rejection_reason": rejection_reason,
        }
