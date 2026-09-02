"""Inference adapter for Agri Nirvana's trained EfficientNet disease model.

The production checkpoint is authoritative. The adapter supports the current
EfficientNetV2-S architecture and legacy B0 checkpoints for controlled offline
compatibility, while exposing global crop evidence so the caller can reject a
user-selected crop that conflicts with the image.
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

        required = ("class_to_idx", "idx_to_class", "model_state_dict", "architecture")
        missing = [key for key in required if key not in checkpoint]
        if missing:
            raise ValueError(f"Invalid production checkpoint; missing keys: {missing}")

        self.class_to_idx = checkpoint["class_to_idx"]
        self.id2label = {int(k): v for k, v in checkpoint["idx_to_class"].items()}
        self.image_size = int(checkpoint.get("image_size", 384))
        self.calibration = checkpoint.get("calibration", {}) or {}
        self.temperature = float(self.calibration.get("temperature", 1.0))
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

        architecture = str(checkpoint.get("architecture", "")).lower().strip()
        if architecture == "efficientnet_v2_s":
            self.model = models.efficientnet_v2_s(weights=None)
            self.model_id = "agri-nirvana-efficientnet-v2-s"
        elif architecture == "efficientnet_b0":
            # Legacy checkpoints can still be inspected offline, but the
            # production training pipeline emits EfficientNetV2-S only.
            self.model = models.efficientnet_b0(weights=None)
            self.model_id = "agri-nirvana-efficientnet-b0-legacy"
        else:
            raise ValueError(f"Unsupported checkpoint architecture: {architecture}")

        self.model.classifier[1] = torch.nn.Linear(
            self.model.classifier[1].in_features, len(self.class_to_idx)
        )
        self.model.load_state_dict(checkpoint["model_state_dict"], strict=True)
        self.model.to(self.device).eval()
        self.is_loaded = True

    @staticmethod
    def _normalized_entropy(probs: torch.Tensor) -> float:
        if probs.numel() <= 1:
            return 0.0
        safe = probs.clamp_min(1e-12)
        entropy = -(safe * safe.log()).sum()
        max_entropy = torch.log(torch.tensor(float(probs.numel()), device=probs.device))
        return float((entropy / max_entropy).clamp(0.0, 1.0).item())

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
        global_probs = F.softmax(logits, dim=0)

        global_idx = int(torch.argmax(global_probs).item())
        global_raw = self.id2label[global_idx]
        global_crop, global_condition = _parse_class_label(global_raw)
        global_confidence = float(global_probs[global_idx].item())

        requested_crop = (crop_filter or "").strip().lower()
        use_crop_filter = requested_crop not in ("", "all", "general", "auto")
        matching_indices = []
        if use_crop_filter:
            for idx, raw_label in self.id2label.items():
                crop, _ = _parse_class_label(str(raw_label))
                if requested_crop == crop.lower() or requested_crop in crop.lower():
                    matching_indices.append(idx)

        crop_probability_mass = (
            float(global_probs[matching_indices].sum().item()) if matching_indices else 0.0
        )
        crop_match = (
            not use_crop_filter
            or requested_crop == global_crop.lower()
            or crop_probability_mass >= 0.50
        )

        candidates = []
        indices = matching_indices if use_crop_filter and matching_indices else list(range(len(global_probs)))
        for idx in indices:
            probability = float(global_probs[idx].item())
            raw = self.id2label[idx]
            crop, condition = _parse_class_label(raw)
            candidates.append((probability, idx, raw, crop, condition))

        candidates.sort(reverse=True, key=lambda x: x[0])
        top = candidates[: max(1, top_k)]
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

        # Entropy is calculated over the global calibrated distribution, not
        # the crop-filtered subset. This prevents a crop filter from making an
        # uncertain image appear artificially certain.
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
                "normalized_entropy": round(self._normalized_entropy(global_probs), 4),
                "temperature": self.temperature,
                "crop_probability_mass": round(crop_probability_mass, 4),
                "requested_crop": crop_filter,
                "crop_match": crop_match,
                "global_top_crop": global_crop,
                "global_top_condition": global_condition,
                "global_top_probability": round(global_confidence, 4),
                "calibration_status": "temperature_scaled" if self.calibration else "not_calibrated",
                "confidence_type": "global_calibrated_probability",
            },
        }
