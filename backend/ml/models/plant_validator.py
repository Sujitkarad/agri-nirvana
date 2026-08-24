"""
Stage A — Plant/Leaf Image Validation Gate.

Uses a pretrained MobileNetV2 (ImageNet-1K) to verify that the uploaded
image actually contains a plant, leaf, fruit, or vegetation before
sending it to the disease classifier (Stage B).

No training required — pure inference on torchvision pretrained weights.
"""

import torch
import torch.nn.functional as F
from torchvision import models, transforms
from torchvision.models import MobileNet_V2_Weights
from PIL import Image
from typing import Tuple, List, Dict

from backend.ml.config.imagenet_plant_classes import build_plant_class_indices


class PlantValidator:
    """
    Validates whether an uploaded image contains plant/leaf content
    using MobileNetV2 pretrained on ImageNet-1K.
    """

    def __init__(self):
        print("[PlantValidator] Loading MobileNetV2 (ImageNet-1K) for plant validation...")

        self.weights = MobileNet_V2_Weights.IMAGENET1K_V1
        self.model = models.mobilenet_v2(weights=self.weights)
        self.model.eval()

        # Use the weights' built-in transforms for correct preprocessing
        self.transform = self.weights.transforms()

        # Get the category names from the weights metadata
        self.categories = self.weights.meta["categories"]

        # Build the set of plant-related class indices
        self.plant_indices = build_plant_class_indices(self.categories)
        print(f"[PlantValidator] Mapped {len(self.plant_indices)} plant-related ImageNet classes")

        # Device setup
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        print(f"[PlantValidator] Ready on {self.device}")

    @torch.no_grad()
    def validate(
        self,
        pil_image: Image.Image,
        top_k: int = 10,
        plant_threshold: float = 0.05
    ) -> Dict:
        """
        Check if the image contains plant/vegetation content.

        Args:
            pil_image: PIL Image (RGB)
            top_k: Number of top predictions to consider
            plant_threshold: Minimum cumulative probability across plant classes
                to accept as a valid plant image

        Returns:
            Dict with keys:
                - is_plant: bool
                - top_plant_class: str (best matching plant class name, or None)
                - top_plant_confidence: float
                - plant_cumulative_score: float (sum of all plant class probs in top-k)
                - top_predictions: list of (class_name, probability) for top-k
                - rejection_reason: str or None
        """
        # Preprocess
        tensor = self.transform(pil_image).unsqueeze(0).to(self.device)

        # Inference
        outputs = self.model(tensor)
        probabilities = F.softmax(outputs[0], dim=0)

        # Get top-k predictions
        top_probs, top_indices = torch.topk(probabilities, top_k)
        top_predictions = [
            (self.categories[idx.item()], prob.item())
            for prob, idx in zip(top_probs, top_indices)
        ]

        # Check for plant classes in top predictions
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

        # Also check overall: sum of ALL plant class probabilities (not just top-k)
        all_plant_prob = sum(
            probabilities[i].item() for i in self.plant_indices
        )

        # Foliage color spectrum analysis (green/chlorotic leaf tissue detection)
        try:
            import numpy as np
            img_rgb = np.array(pil_image.convert("RGB"))
            r, g, b = img_rgb[:, :, 0].astype(float), img_rgb[:, :, 1].astype(float), img_rgb[:, :, 2].astype(float)
            # Foliage: green-dominant or chlorotic yellow/brown necrosis
            foliage_mask = ((g > r * 0.80) & (g > b * 0.80)) | ((r > 80) & (g > 80) & (b < 140))
            foliage_ratio = float(np.sum(foliage_mask)) / float(img_rgb.shape[0] * img_rgb.shape[1])
        except Exception:
            foliage_ratio = 0.0

        is_plant = (
            plant_cumulative >= plant_threshold
            or all_plant_prob >= 0.05
            or best_plant_conf >= 0.02
            or foliage_ratio >= 0.18
        )

        rejection_reason = None
        if not is_plant:
            top_class = top_predictions[0][0] if top_predictions else "unknown"
            rejection_reason = (
                f"This doesn't look like a crop or leaf image. "
                f"The image appears to contain '{top_class}' "
                f"(confidence: {top_predictions[0][1]*100:.0f}%). "
                f"Please upload a clear photo of the affected plant part."
            )

        return {
            "is_plant": is_plant,
            "top_plant_class": best_plant_class,
            "top_plant_confidence": round(best_plant_conf, 4),
            "plant_cumulative_score": round(plant_cumulative, 4),
            "all_plant_probability": round(all_plant_prob, 4),
            "top_predictions": top_predictions,
            "rejection_reason": rejection_reason
        }
