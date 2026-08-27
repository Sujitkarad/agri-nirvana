"""
Stage B — Plant Disease Classification.

Uses a HuggingFace image-classification model for disease diagnosis.
Confidence is exposed as model probability plus reliability diagnostics;
it is not presented as independently validated clinical/agronomic accuracy.
"""

import torch
import torch.nn.functional as F
from PIL import Image
from typing import Dict, List, Tuple, Optional

try:
    from transformers import AutoModelForImageClassification, AutoImageProcessor
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False
    print("[DiseaseClassifier] WARNING: 'transformers' package not installed.")

PRIMARY_MODEL_ID = "linkanjarad/mobilenet_v2_1.0_224-plant-disease-identification"
FALLBACK_MODEL_IDS = [
    "Abuzaid01/plant-disease-classifier",
    "Daksh159/plant-disease-mobilenetv2",
]

PLANTVILLAGE_CLASSES = [
    "Apple___Apple_scab", "Apple___Black_rot", "Apple___Cedar_apple_rust", "Apple___healthy",
    "Blueberry___healthy", "Cherry_(including_sour)___Powdery_mildew", "Cherry_(including_sour)___healthy",
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot", "Corn_(maize)___Common_rust_",
    "Corn_(maize)___Northern_Leaf_Blight", "Corn_(maize)___healthy", "Grape___Black_rot",
    "Grape___Esca_(Black_Measles)", "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)", "Grape___healthy",
    "Orange___Haunglongbing_(Citrus_greening)", "Peach___Bacterial_spot", "Peach___healthy",
    "Pepper,_bell___Bacterial_spot", "Pepper,_bell___healthy", "Potato___Early_blight",
    "Potato___Late_blight", "Potato___healthy", "Raspberry___healthy", "Soybean___healthy",
    "Squash___Powdery_mildew", "Strawberry___Leaf_scorch", "Strawberry___healthy",
    "Tomato___Bacterial_spot", "Tomato___Early_blight", "Tomato___Late_blight", "Tomato___Leaf_Mold",
    "Tomato___Septoria_leaf_spot", "Tomato___Spider_mites Two-spotted_spider_mite",
    "Tomato___Target_Spot", "Tomato___Tomato_Yellow_Leaf_Curl_Virus", "Tomato___Tomato_mosaic_virus",
    "Tomato___healthy",
]

LABEL_PARSER_MAP: Dict[str, Tuple[str, str, str]] = {
    "apple scab": ("Apple", "Apple Scab", "Apple___Apple_scab"),
    "apple with black rot": ("Apple", "Black Rot", "Apple___Black_rot"),
    "cedar apple rust": ("Apple", "Cedar Apple Rust", "Apple___Cedar_apple_rust"),
    "healthy apple": ("Apple", "Healthy", "Apple___healthy"),
    "healthy blueberry plant": ("Blueberry", "Healthy", "Blueberry___healthy"),
    "cherry with powdery mildew": ("Cherry", "Powdery Mildew", "Cherry_(including_sour)___Powdery_mildew"),
    "healthy cherry plant": ("Cherry", "Healthy", "Cherry_(including_sour)___healthy"),
    "corn (maize) with cercospora and gray leaf spot": ("Corn", "Cercospora and Gray Leaf Spot", "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot"),
    "corn (maize) with common rust": ("Corn", "Common Rust", "Corn_(maize)___Common_rust_"),
    "corn (maize) with northern leaf blight": ("Corn", "Northern Leaf Blight", "Corn_(maize)___Northern_Leaf_Blight"),
    "healthy corn (maize) plant": ("Corn", "Healthy", "Corn_(maize)___healthy"),
    "grape with black rot": ("Grape", "Black Rot", "Grape___Black_rot"),
    "grape with esca (black measles)": ("Grape", "Esca (Black Measles)", "Grape___Esca_(Black_Measles)"),
    "grape with isariopsis leaf spot": ("Grape", "Isariopsis Leaf Spot", "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)"),
    "healthy grape plant": ("Grape", "Healthy", "Grape___healthy"),
    "orange with citrus greening": ("Orange", "Citrus Greening", "Orange___Haunglongbing_(Citrus_greening)"),
    "peach with bacterial spot": ("Peach", "Bacterial Spot", "Peach___Bacterial_spot"),
    "healthy peach plant": ("Peach", "Healthy", "Peach___healthy"),
    "bell pepper with bacterial spot": ("Pepper", "Bacterial Spot", "Pepper,_bell___Bacterial_spot"),
    "healthy bell pepper plant": ("Pepper", "Healthy", "Pepper,_bell___healthy"),
    "potato with early blight": ("Potato", "Early Blight", "Potato___Early_blight"),
    "potato with late blight": ("Potato", "Late Blight", "Potato___Late_blight"),
    "healthy potato plant": ("Potato", "Healthy", "Potato___healthy"),
    "healthy raspberry plant": ("Raspberry", "Healthy", "Raspberry___healthy"),
    "healthy soybean plant": ("Soybean", "Healthy", "Soybean___healthy"),
    "squash with powdery mildew": ("Squash", "Powdery Mildew", "Squash___Powdery_mildew"),
    "strawberry with leaf scorch": ("Strawberry", "Leaf Scorch", "Strawberry___Leaf_scorch"),
    "healthy strawberry plant": ("Strawberry", "Healthy", "Strawberry___healthy"),
    "tomato with bacterial spot": ("Tomato", "Bacterial Spot", "Tomato___Bacterial_spot"),
    "tomato with early blight": ("Tomato", "Early Blight", "Tomato___Early_blight"),
    "tomato with late blight": ("Tomato", "Late Blight", "Tomato___Late_blight"),
    "tomato with leaf mold": ("Tomato", "Leaf Mold", "Tomato___Leaf_Mold"),
    "tomato with septoria leaf spot": ("Tomato", "Septoria Leaf Spot", "Tomato___Septoria_leaf_spot"),
    "tomato with spider mites or two-spotted spider mite": ("Tomato", "Spider Mites", "Tomato___Spider_mites Two-spotted_spider_mite"),
    "tomato with target spot": ("Tomato", "Target Spot", "Tomato___Target_Spot"),
    "tomato yellow leaf curl virus": ("Tomato", "Yellow Leaf Curl Virus", "Tomato___Tomato_Yellow_Leaf_Curl_Virus"),
    "tomato mosaic virus": ("Tomato", "Mosaic Virus", "Tomato___Tomato_mosaic_virus"),
    "healthy tomato plant": ("Tomato", "Healthy", "Tomato___healthy"),
}

CROP_ALIASES = {"grapes": "Grape", "grape": "Grape", "maize": "Corn", "corn": "Corn", "corn (maize)": "Corn", "bell pepper": "Pepper", "pepper": "Pepper", "citrus": "Orange", "orange": "Orange", "paddy": "Rice", "rice": "Rice"}


def normalize_crop_name(crop: str) -> str:
    c = crop.strip().lower()
    return CROP_ALIASES.get(c, crop.strip().capitalize())


def _parse_class_label(raw_label: str) -> Tuple[str, str]:
    clean_k = raw_label.lower().strip()
    if clean_k in LABEL_PARSER_MAP:
        return LABEL_PARSER_MAP[clean_k][0], LABEL_PARSER_MAP[clean_k][1]
    if "___" in raw_label:
        crop_raw, condition_raw = raw_label.split("___", 1)
        crop = crop_raw.replace("_", " ").replace("(including sour)", "").replace("(maize)", "").replace(", bell", "").strip()
        crop = normalize_crop_name(crop)
        condition = " ".join(w.capitalize() if w.lower() not in ("of", "the", "and", "in", "or", "with") else w for w in condition_raw.replace("_", " ").strip().split())
        return crop, condition
    if raw_label.isdigit():
        idx = int(raw_label)
        if 0 <= idx < len(PLANTVILLAGE_CLASSES):
            return _parse_class_label(PLANTVILLAGE_CLASSES[idx])
    for kc in ["Apple", "Blueberry", "Cherry", "Corn", "Grape", "Orange", "Peach", "Pepper", "Potato", "Raspberry", "Soybean", "Squash", "Strawberry", "Tomato", "Cotton", "Rice", "Wheat", "Onion", "Sugarcane", "Pomegranate"]:
        if kc.lower() in clean_k:
            cond = "Healthy" if "healthy" in clean_k else clean_k.replace(kc.lower(), "").replace("with", "").replace("plant", "").strip().title()
            return kc, cond or "Unknown"
    return "Crop", raw_label.replace("_", " ").title()


class DiseaseClassifier:
    def __init__(self, model_id: Optional[str] = None):
        self.model = None
        self.processor = None
        self.transform = None
        self.id2label = {}
        self.label2id = {}
        self.model_id = model_id or PRIMARY_MODEL_ID
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.is_loaded = False
        if HAS_TRANSFORMERS:
            self._load_model()

    def _load_model(self):
        from torchvision import transforms
        for mid in [self.model_id] + [m for m in FALLBACK_MODEL_IDS if m != self.model_id]:
            try:
                self.model = AutoModelForImageClassification.from_pretrained(mid)
                try:
                    self.processor = AutoImageProcessor.from_pretrained(mid)
                except Exception:
                    self.transform = transforms.Compose([
                        transforms.Resize((224, 224)), transforms.ToTensor(),
                        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
                    ])
                self.model.to(self.device)
                self.model.eval()
                self.id2label = getattr(self.model.config, "id2label", None) or {i: c for i, c in enumerate(PLANTVILLAGE_CLASSES)}
                self.label2id = getattr(self.model.config, "label2id", None) or {c: i for i, c in enumerate(PLANTVILLAGE_CLASSES)}
                self.model_id = mid
                self.is_loaded = True
                return
            except Exception as exc:
                print(f"[DiseaseClassifier] Failed to load {mid}: {exc}")
        print("[DiseaseClassifier] No model could be loaded.")

    @torch.no_grad()
    def classify(self, pil_image: Image.Image, top_k: int = 5, crop_filter: Optional[str] = None) -> Dict:
        if not self.is_loaded or self.model is None:
            return {"raw_label": "model_not_loaded", "crop": crop_filter or "Unknown", "condition": "Model Not Available", "confidence": 0.0, "is_healthy": False, "top_predictions": [], "error": "Disease classification model is not loaded."}

        if pil_image is None:
            return {"raw_label": "invalid_image", "crop": crop_filter or "Unknown", "condition": "Invalid Image", "confidence": 0.0, "is_healthy": False, "top_predictions": [], "error": "No image was provided."}

        pil_image = pil_image.convert("RGB")
        if self.processor is not None:
            inputs = self.processor(images=pil_image, return_tensors="pt")
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            logits = self.model(**inputs).logits[0]
        else:
            tensor = self.transform(pil_image).unsqueeze(0).to(self.device)
            logits = self.model(pixel_values=tensor).logits[0]

        global_probs = F.softmax(logits, dim=0)
        crop_mask = torch.zeros_like(logits, dtype=torch.bool)
        has_crop_matches = False
        if crop_filter and crop_filter.lower() not in ["all", "general", "auto", ""]:
            filter_lower = crop_filter.lower()
            for idx_key, label in self.id2label.items():
                try:
                    idx = int(idx_key)
                except (TypeError, ValueError):
                    continue
                if 0 <= idx < len(crop_mask):
                    crop_name, _ = _parse_class_label(str(label))
                    if filter_lower == crop_name.lower() or filter_lower in crop_name.lower():
                        crop_mask[idx] = True
                        has_crop_matches = True

        if has_crop_matches:
            conditioned_logits = logits.clone()
            conditioned_logits[~crop_mask] = -1e4
            probabilities = F.softmax(conditioned_logits, dim=0)
        else:
            probabilities = global_probs

        top_probs, top_indices = torch.topk(probabilities, min(top_k, len(probabilities)))
        top_predictions = []
        for prob, idx in zip(top_probs, top_indices):
            raw_label = self.id2label.get(str(idx.item()), self.id2label.get(idx.item(), f"class_{idx.item()}"))
            crop, condition = _parse_class_label(str(raw_label))
            top_predictions.append({"raw_label": str(raw_label), "crop": crop, "condition": condition, "confidence": round(float(prob.item()), 4)})

        best = top_predictions[0] if top_predictions else {"raw_label": "unknown", "crop": crop_filter or "Unknown", "condition": "Unknown", "confidence": 0.0}
        confidence = float(best["confidence"])
        margin = confidence - float(top_predictions[1]["confidence"]) if len(top_predictions) > 1 else confidence
        entropy = float(-(probabilities.clamp_min(1e-12) * probabilities.clamp_min(1e-12).log()).sum().item())
        max_entropy = float(torch.log(torch.tensor(float(len(probabilities)))).item()) if len(probabilities) > 1 else 1.0
        normalized_entropy = min(1.0, entropy / max_entropy) if max_entropy > 0 else 0.0
        is_healthy = "healthy" in best["raw_label"].lower() or "healthy" in best["condition"].lower()

        return {
            "raw_label": best["raw_label"], "crop": best["crop"], "condition": best["condition"],
            "confidence": round(confidence, 4), "is_healthy": is_healthy, "top_predictions": top_predictions,
            "confidence_diagnostics": {
                "top1_probability": round(confidence, 4),
                "top2_margin": round(margin, 4),
                "normalized_entropy": round(normalized_entropy, 4),
                "calibration_status": "not_calibrated",
                "note": "Softmax probability is a model score, not validated field accuracy. Calibrate on an independent validation set before deployment claims."
            }
        }
