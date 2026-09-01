"""Inference adapter for Agri Nirvana's trained EfficientNet disease model.

Supports the current EfficientNetV2-S checkpoint as well as legacy EfficientNet-B0
checkpoints so deployment can be upgraded without changing API callers.
"""
from __future__ import annotations

from typing import Dict, Optional

import torch
import torch.nn.functional as F
from PIL import Image
from torchvision import models, transforms

from backend.ml.models.disease_classifier import _parse_class_label


class EfficientNetDiseaseClassifier:
    def __init__(self, checkpoint_path: str):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        checkpoint = torch.load(checkpoint_path, map_location=self.device, weights_only=False)
        self.class_to_idx = checkpoint["class_to_idx"]
        self.id2label = {int(k): v for k, v in checkpoint["idx_to_class"].items()}
        self.image_size = int(checkpoint.get("image_size", 224))
        self.temperature = float(checkpoint.get("calibration", {}).get("temperature", 1.0))
        if self.temperature <= 0:
            self.temperature = 1.0

        self.transform = transforms.Compose([
            transforms.Resize(int(self.image_size * 1.14)),
            transforms.CenterCrop(self.image_size),
            transforms.ToTensor(),
            transforms.Normalize(
                tuple(checkpoint.get("mean", (0.485, 0.456, 0.406))),
                tuple(checkpoint.get("std", (0.229, 0.224, 0.225))),
            ),
        ])

        architecture = checkpoint.get("architecture", "efficientnet_b0").lower()
        if architecture == "efficientnet_v2_s":
            self.model = models.efficientnet_v2_s(weights=None)
            self.model_id = "agri-nirvana-efficientnet-v2-s"
        else:
            self.model = models.efficientnet_b0(weights=None)
            self.model_id = "agri-nirvana-efficientnet-b0"

        self.model.classifier[1] = torch.nn.Linear(
            self.model.classifier[1].in_features, len(self.class_to_idx)
        )
        self.model.load_state_dict(checkpoint["model_state_dict"])
        self.model.to(self.device).eval()
        self.is_loaded = True

    @torch.no_grad()
    def classify(
        self,
        pil_image: Image.Image,
        top_k: int = 5,
        crop_filter: Optional[str] = None,
    ) -> Dict:
        image = pil_image.convert("RGB")
        tensor = self.transform(image).unsqueeze(0).to(self.device)
        logits = self.model(tensor)[0] / self.temperature
        probs = F.softmax(logits, dim=0)

        candidates = []
        for idx, probability in enumerate(probs.tolist()):
            raw = self.id2label[idx]
            crop, condition = _parse_class_label(raw)
            if crop_filter and crop_filter.lower() not in ("all", "general", "auto"):
                if crop_filter.lower() != crop.lower() and crop_filter.lower() not in crop.lower():
                    continue
            candidates.append((probability, idx, raw, crop, condition))

        if not candidates:
            candidates = [
                (p, i, self.id2label[i], *_parse_class_label(self.id2label[i]))
                for i, p in enumerate(probs.tolist())
            ]
        candidates.sort(reverse=True, key=lambda x: x[0])
        top = candidates[:top_k]
        predictions = [
            {
                "raw_label": raw,
                "crop": crop,
                "condition": condition,
                "confidence": round(float(prob), 4),
            }
            for prob, _, raw, crop, condition in top
        ]
        best = predictions[0]
        return {
            "raw_label": best["raw_label"],
            "crop": best["crop"],
            "condition": best["condition"],
            "confidence": best["confidence"],
            "is_healthy": "healthy" in best["raw_label"].lower(),
            "top_predictions": predictions,
            "model_id": self.model_id,
            "confidence_diagnostics": {
                "top1_probability": best["confidence"],
                "top2_margin": round(
                    best["confidence"] - predictions[1]["confidence"], 4
                ) if len(predictions) > 1 else best["confidence"],
                "temperature": self.temperature,
                "calibration_status": "temperature_scaled",
            },
        }
