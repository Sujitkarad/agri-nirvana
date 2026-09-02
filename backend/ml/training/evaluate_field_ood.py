"""Evaluate a trained classifier on field and unknown/OOD datasets."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

import numpy as np
import torch
from sklearn.metrics import accuracy_score, f1_score
from torchvision import datasets, models, transforms

VALID_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


def _safe_name(value: str) -> str:
    return "_".join(value.replace("/", "_").split())


def _count_images(root: Path) -> int:
    return sum(1 for p in root.rglob("*") if p.is_file() and p.suffix.lower() in VALID_EXTENSIONS)


def _load_model(checkpoint_path: Path, device: torch.device):
    ckpt = torch.load(checkpoint_path, map_location=device, weights_only=False)
    architecture = ckpt.get("architecture")
    if architecture == "efficientnet_v2_l":
        model = models.efficientnet_v2_l(weights=None)
    elif architecture == "efficientnet_v2_s":
        model = models.efficientnet_v2_s(weights=None)
    else:
        raise ValueError(f"Unsupported checkpoint architecture: {architecture}")
    class_to_idx = ckpt["class_to_idx"]
    model.classifier[1] = torch.nn.Linear(model.classifier[1].in_features, len(class_to_idx))
    model.load_state_dict(ckpt["model_state_dict"], strict=True)
    model.to(device).eval()
    calibration = ckpt.get("calibration", {}) or {}
    temperature = float(calibration.get("temperature", 1.0))
    if temperature <= 0:
        temperature = 1.0
    return model, class_to_idx, int(ckpt.get("image_size", 448)), temperature


def _probs(logits: torch.Tensor, temperature: float) -> torch.Tensor:
    return torch.softmax(logits / max(temperature, 1e-6), dim=1)


def _predict(model, root: Path, image_size: int, temperature: float, device: torch.device):
    if not root.is_dir() or _count_images(root) == 0:
        raise ValueError(f"Evaluation dataset is missing or empty: {root}")
    tfm = transforms.Compose([
        transforms.Resize(int(image_size * 1.14)),
        transforms.CenterCrop(image_size),
        transforms.ToTensor(),
        transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225)),
    ])
    ds = datasets.ImageFolder(root, transform=tfm)
    loader = torch.utils.data.DataLoader(ds, batch_size=32, shuffle=False, num_workers=2)
    y_true, y_pred, max_prob = [], [], []
    with torch.no_grad():
        for images, labels in loader:
            probs = _probs(model(images.to(device)), temperature)
            y_true.extend(labels.numpy().tolist())
            y_pred.extend(probs.argmax(1).cpu().numpy().tolist())
            max_prob.extend(probs.max(1).values.cpu().numpy().tolist())
    return np.asarray(y_true), np.asarray(y_pred), np.asarray(max_prob), ds.classes


def evaluate_field(model, class_to_idx, image_size, temperature, root, device):
    y_true, y_pred, max_prob, classes = _predict(model, root, image_size, temperature, device)
    known = {_safe_name(name): idx for name, idx in class_to_idx.items()}
    overlap = sorted(set(classes) & set(known))
    if not overlap:
        raise ValueError("Field dataset has no class overlap with the production taxonomy")
    keep = np.asarray([classes[int(i)] in known for i in y_true])
    if not keep.any():
        raise ValueError("Field dataset contains no evaluable known classes")
    remap = np.asarray([known[classes[int(i)]] if classes[int(i)] in known else -1 for i in y_true])
    return {
        "samples": int(keep.sum()),
        "coverage": round(float(keep.mean()), 4),
        "top1_accuracy": round(float(accuracy_score(remap[keep], y_pred[keep])), 4),
        "macro_f1": round(float(f1_score(remap[keep], y_pred[keep], average="macro", zero_division=0)), 4),
        "mean_max_probability": round(float(max_prob[keep].mean()), 4),
        "classes_evaluated": overlap,
    }


def evaluate_ood(model, image_size, temperature, root, device):
    if not root.is_dir() or _count_images(root) == 0:
        raise ValueError(f"OOD dataset is missing or empty: {root}")
    tfm = transforms.Compose([
        transforms.Resize(int(image_size * 1.14)),
        transforms.CenterCrop(image_size),
        transforms.ToTensor(),
        transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225)),
    ])
    from PIL import Image
    paths = [p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in VALID_EXTENSIONS]
    scores = []
    with torch.no_grad():
        for path in paths:
            image = tfm(Image.open(path).convert("RGB")).unsqueeze(0).to(device)
            scores.append(float(_probs(model(image), temperature).max().item()))
    scores = np.asarray(scores)
    return {"samples": int(len(scores)), "mean_max_probability": round(float(scores.mean()), 4), "p95_max_probability": round(float(np.percentile(scores, 95)), 4), "p99_max_probability": round(float(np.percentile(scores, 99)), 4)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--field-data", required=True)
    parser.add_argument("--ood-data", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model, class_to_idx, image_size, temperature = _load_model(Path(args.checkpoint), device)
    result: dict[str, Any] = {"checkpoint": str(args.checkpoint), "temperature": temperature, "field": evaluate_field(model, class_to_idx, image_size, temperature, Path(args.field_data), device), "ood": evaluate_ood(model, image_size, temperature, Path(args.ood_data), device)}
    Path(args.output).write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
