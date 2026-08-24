"""
Stage B — Plant Disease Classification.

Uses a HuggingFace-hosted MobileNetV2 model fine-tuned on the
PlantVillage dataset (38 disease classes) for real disease diagnosis.

The model is downloaded and cached automatically on first run (~14MB).
Subsequent runs load from local cache without internet.
"""

import torch
import torch.nn.functional as F
from PIL import Image
from typing import Dict, List, Tuple, Optional

# Attempt to load transformers; provide clear error if missing
try:
    from transformers import AutoModelForImageClassification, AutoImageProcessor
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False
    print("[DiseaseClassifier] WARNING: 'transformers' package not installed. "
          "Run: pip install transformers")

# Primary model: well-maintained HuggingFace PlantVillage model
PRIMARY_MODEL_ID = "linkanjarad/mobilenet_v2_1.0_224-plant-disease-identification"

# Fallback models in order of preference
FALLBACK_MODEL_IDS = [
    "Abuzaid01/plant-disease-classifier",
    "Daksh159/plant-disease-mobilenetv2",
]

# The canonical 38 PlantVillage class names (used for knowledge base lookup)
PLANTVILLAGE_CLASSES = [
    "Apple___Apple_scab",
    "Apple___Black_rot",
    "Apple___Cedar_apple_rust",
    "Apple___healthy",
    "Blueberry___healthy",
    "Cherry_(including_sour)___Powdery_mildew",
    "Cherry_(including_sour)___healthy",
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot",
    "Corn_(maize)___Common_rust_",
    "Corn_(maize)___Northern_Leaf_Blight",
    "Corn_(maize)___healthy",
    "Grape___Black_rot",
    "Grape___Esca_(Black_Measles)",
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)",
    "Grape___healthy",
    "Orange___Haunglongbing_(Citrus_greening)",
    "Peach___Bacterial_spot",
    "Peach___healthy",
    "Pepper,_bell___Bacterial_spot",
    "Pepper,_bell___healthy",
    "Potato___Early_blight",
    "Potato___Late_blight",
    "Potato___healthy",
    "Raspberry___healthy",
    "Soybean___healthy",
    "Squash___Powdery_mildew",
    "Strawberry___Leaf_scorch",
    "Strawberry___healthy",
    "Tomato___Bacterial_spot",
    "Tomato___Early_blight",
    "Tomato___Late_blight",
    "Tomato___Leaf_Mold",
    "Tomato___Septoria_leaf_spot",
    "Tomato___Spider_mites Two-spotted_spider_mite",
    "Tomato___Target_Spot",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus",
    "Tomato___Tomato_mosaic_virus",
    "Tomato___healthy",
]


def _parse_class_label(raw_label: str) -> Tuple[str, str]:
    """
    Parse a PlantVillage class label into (crop_name, condition_name).

    Examples:
        "Tomato___Early_blight" -> ("Tomato", "Early Blight")
        "Corn_(maize)___Common_rust_" -> ("Corn (Maize)", "Common Rust")
        "Tomato___healthy" -> ("Tomato", "Healthy")
    """
    parts = raw_label.split("___")
    if len(parts) == 2:
        crop_raw, condition_raw = parts
    else:
        crop_raw = parts[0]
        condition_raw = "___".join(parts[1:]) if len(parts) > 1 else "Unknown"

    # Clean up crop name
    crop = crop_raw.replace("_", " ").strip()
    crop = crop.replace("(including sour)", "(incl. sour)")
    crop = crop.replace(",  bell", ", Bell")
    crop = crop.replace(", bell", ", Bell")

    # Clean up condition name
    condition = condition_raw.replace("_", " ").strip()
    # Title case but preserve known acronyms
    condition = " ".join(
        w.capitalize() if w.lower() not in ("of", "the", "and", "in") else w
        for w in condition.split()
    )

    return crop, condition


class DiseaseClassifier:
    """
    PlantVillage disease classifier using a HuggingFace pretrained model.
    Downloads and caches the model on first run.
    """

    def __init__(self, model_id: Optional[str] = None):
        self.model = None
        self.processor = None
        self.transform = None
        self.id2label = {}
        self.label2id = {}
        self.model_id = model_id or PRIMARY_MODEL_ID
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.is_loaded = False

        if not HAS_TRANSFORMERS:
            print("[DiseaseClassifier] Cannot load — transformers package missing")
            return

        self._load_model()

    def _load_model(self):
        """Try loading the primary model, fall back to alternatives if needed."""
        from torchvision import transforms

        model_ids_to_try = [self.model_id] + [
            m for m in FALLBACK_MODEL_IDS if m != self.model_id
        ]

        for mid in model_ids_to_try:
            try:
                print(f"[DiseaseClassifier] Loading model: {mid}...")
                self.model = AutoModelForImageClassification.from_pretrained(mid)
                
                try:
                    self.processor = AutoImageProcessor.from_pretrained(mid)
                except Exception as pe:
                    print(f"[DiseaseClassifier] AutoImageProcessor unavailable for {mid}, using torchvision transforms: {pe}")
                    self.transform = transforms.Compose([
                        transforms.Resize((224, 224)),
                        transforms.ToTensor(),
                        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
                    ])

                self.model.to(self.device)
                self.model.eval()

                # Extract label mappings from model config
                if hasattr(self.model.config, 'id2label') and self.model.config.id2label:
                    self.id2label = self.model.config.id2label
                    self.label2id = self.model.config.label2id
                else:
                    # Fallback: use canonical PlantVillage class list
                    self.id2label = {i: c for i, c in enumerate(PLANTVILLAGE_CLASSES)}
                    self.label2id = {c: i for i, c in enumerate(PLANTVILLAGE_CLASSES)}

                self.model_id = mid
                self.is_loaded = True
                num_labels = len(self.id2label)
                print(f"[DiseaseClassifier] Loaded {mid} ({num_labels} classes) on {self.device}")
                return

            except Exception as e:
                print(f"[DiseaseClassifier] Failed to load {mid}: {e}")
                continue

        print("[DiseaseClassifier] WARNING: No model could be loaded. "
              "Disease classification will not be available.")

    @torch.no_grad()
    def classify(
        self,
        pil_image: Image.Image,
        top_k: int = 5,
        crop_filter: Optional[str] = None
    ) -> Dict:
        """
        Classify a plant leaf image for disease with optional crop prior conditioning.
        """
        if not self.is_loaded or self.model is None:
            return {
                "raw_label": "model_not_loaded",
                "crop": crop_filter or "Unknown",
                "condition": "Model Not Available",
                "confidence": 0.0,
                "is_healthy": False,
                "top_predictions": [],
                "error": "Disease classification model is not loaded."
            }

        # Preprocess with processor or fallback torchvision transform
        if self.processor is not None:
            inputs = self.processor(images=pil_image, return_tensors="pt")
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            outputs = self.model(**inputs)
            logits = outputs.logits[0]
        else:
            tensor = self.transform(pil_image).unsqueeze(0).to(self.device)
            outputs = self.model(pixel_values=tensor)
            logits = outputs.logits[0]

        # ── Global unconditioned probabilities ──────────────────
        global_probs = F.softmax(logits, dim=0)

        # ── Crop-Prior Conditioning ──────────────────────────────
        # If farmer selected a known crop, boost/condition on matching crop classes
        crop_mask = torch.zeros_like(logits, dtype=torch.bool)
        has_crop_matches = False

        if crop_filter and crop_filter.lower() not in ["all", "general", "auto", ""]:
            filter_lower = crop_filter.lower().split()[0] # e.g. "tomato", "cotton", "potato", "corn"
            for idx_str, label in self.id2label.items():
                idx_int = int(idx_str) if isinstance(idx_str, str) and idx_str.isdigit() else idx_str
                if isinstance(idx_int, int) and idx_int < len(crop_mask):
                    crop_name, _ = _parse_class_label(str(label))
                    if filter_lower in crop_name.lower() or filter_lower in str(label).lower():
                        crop_mask[idx_int] = True
                        has_crop_matches = True

        if has_crop_matches:
            # Calibrate within the target crop prior (temperature scaled)
            conditioned_logits = logits.clone()
            conditioned_logits[~crop_mask] = -1e4
            probabilities = F.softmax(conditioned_logits, dim=0)
        else:
            probabilities = global_probs

        # Top-k predictions
        top_probs, top_indices = torch.topk(probabilities, min(top_k, len(probabilities)))

        top_predictions = []
        for prob, idx in zip(top_probs, top_indices):
            raw_label = self.id2label.get(str(idx.item()), self.id2label.get(idx.item(), f"class_{idx.item()}"))
            crop, condition = _parse_class_label(str(raw_label))
            top_predictions.append({
                "raw_label": str(raw_label),
                "crop": crop_filter if (has_crop_matches and crop_filter) else crop,
                "condition": condition,
                "confidence": round(prob.item(), 4)
            })

        # Best prediction
        best = top_predictions[0] if top_predictions else {
            "raw_label": "unknown", "crop": crop_filter or "Unknown",
            "condition": "Unknown", "confidence": 0.0
        }

        is_healthy = "healthy" in best["raw_label"].lower() or "healthy" in best["condition"].lower()

        return {
            "raw_label": best["raw_label"],
            "crop": best["crop"],
            "condition": best["condition"],
            "confidence": best["confidence"],
            "is_healthy": is_healthy,
            "top_predictions": top_predictions
        }
