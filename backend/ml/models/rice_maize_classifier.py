"""Rice and Maize Crop Pathology Inference Classifier Adapter.

Loads the trained PyTorch MobileNetV3 checkpoint for Rice and Maize,
maps the 17 pathology & insect-pest classes, and exposes a standard
classify() interface matching Agri Nirvana's production inference engine.
"""

from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from PIL import Image
import torch
import torch.nn.functional as F
from torchvision import transforms

from backend.ml.models.disease_classifier import _parse_class_label, normalize_crop_name
from backend.ml.training.train_rice_and_maize import create_model, get_data_transforms

DEFAULT_CHECKPOINT_PATH = Path("backend/ml/models/weights/rice_and_maize_classifier.pt")


class RiceMaizeClassifier:
    """Inference wrapper for trained Rice and Maize pathology model."""

    def __init__(self, checkpoint_path: Optional[str | Path] = None):
        self.checkpoint_path = Path(checkpoint_path or DEFAULT_CHECKPOINT_PATH)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.is_loaded = False
        self.model = None
        self.id2label: Dict[int, str] = {}
        self.label2id: Dict[str, int] = {}
        self.model_id = "agri-nirvana-rice-and-maize-v1"

        if self.checkpoint_path.is_file():
            self._load_checkpoint()

    def _load_checkpoint(self) -> None:
        try:
            checkpoint = torch.load(str(self.checkpoint_path), map_location=self.device, weights_only=False)
            self.num_classes = int(checkpoint.get("num_classes", 17))
            self.classes = checkpoint.get("classes", [])
            self.class_to_idx = checkpoint.get("class_to_idx", {})
            self.idx_to_class = checkpoint.get("idx_to_class", {})

            # Standardize id2label mapping
            self.id2label = {int(k): v for k, v in self.idx_to_class.items()}
            self.label2id = {v: k for k, v in self.id2label.items()}

            self.model = create_model(self.num_classes)
            self.model.load_state_dict(checkpoint["model_state_dict"])
            self.model.to(self.device)
            self.model.eval()

            self.transform = get_data_transforms()["eval"]
            self.is_loaded = True
            print(f"[RiceMaizeClassifier] Successfully loaded {self.num_classes} classes from {self.checkpoint_path}")
        except Exception as exc:
            self.is_loaded = False
            print(f"[RiceMaizeClassifier] Warning: Could not load checkpoint {self.checkpoint_path}: {exc}")

    @torch.no_grad()
    def classify(
        self,
        pil_image: Image.Image,
        top_k: int = 5,
        crop_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """Classify a leaf image and return top-k predictions with diagnostics."""
        if not self.is_loaded or self.model is None:
            return {
                "raw_label": "model_not_loaded",
                "crop": crop_filter or "Unknown",
                "condition": "Model Not Loaded",
                "confidence": 0.0,
                "is_healthy": False,
                "top_predictions": [],
                "error": "Rice & Maize model is not loaded.",
            }

        if pil_image is None:
            return {
                "raw_label": "invalid_image",
                "crop": crop_filter or "Unknown",
                "condition": "Invalid Image",
                "confidence": 0.0,
                "is_healthy": False,
                "top_predictions": [],
                "error": "No image was provided.",
            }

        img = pil_image.convert("RGB")
        tensor = self.transform(img).unsqueeze(0).to(self.device)
        logits = self.model(tensor)[0]
        probs = F.softmax(logits, dim=0)

        # Apply crop filter if specified
        norm_filter = normalize_crop_name(crop_filter or "").lower()
        active_indices = []
        for idx, label in self.id2label.items():
            crop_name, _ = _parse_class_label(label)
            if not norm_filter or norm_filter in ["all", "general", "auto", ""]:
                active_indices.append(idx)
            elif norm_filter == crop_name.lower() or (norm_filter == "corn" and crop_name.lower() == "maize"):
                active_indices.append(idx)

        if not active_indices:
            active_indices = list(range(len(probs)))

        sub_probs = probs[active_indices]
        top_sub_probs, top_sub_sub_indices = torch.topk(sub_probs, min(top_k, len(sub_probs)))

        top_predictions = []
        for p, sub_idx in zip(top_sub_probs, top_sub_sub_indices):
            orig_idx = active_indices[sub_idx.item()]
            raw_label = self.id2label[orig_idx]
            crop, condition = _parse_class_label(raw_label)
            top_predictions.append({
                "raw_label": raw_label,
                "crop": crop,
                "condition": condition,
                "confidence": round(p.item(), 4),
            })

        top1 = top_predictions[0]
        top1_conf = top1["confidence"]
        top2_conf = top_predictions[1]["confidence"] if len(top_predictions) > 1 else 0.0
        margin = round(top1_conf - top2_conf, 4)

        # Compute entropy across active classes
        p_active = sub_probs / (sub_probs.sum() + 1e-7)
        entropy = -torch.sum(p_active * torch.log(p_active + 1e-7)).item()
        max_entropy = torch.log(torch.tensor(len(active_indices), dtype=torch.float)).item()
        norm_entropy = round(entropy / (max_entropy + 1e-7), 4)

        crop_mass = round(probs[active_indices].sum().item(), 4)
        is_healthy = "healthy" in top1["raw_label"].lower()

        return {
            "raw_label": top1["raw_label"],
            "crop": top1["crop"],
            "condition": top1["condition"],
            "confidence": top1_conf,
            "is_healthy": is_healthy,
            "top_predictions": top_predictions,
            "confidence_diagnostics": {
                "top1_probability": top1_conf,
                "top2_margin": margin,
                "normalized_entropy": norm_entropy,
                "crop_probability_mass": crop_mass,
                "crop_match": True,
            },
        }
