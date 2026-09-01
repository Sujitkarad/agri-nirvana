"""Real training and evaluation pipeline for Agri Nirvana crop-disease image classification.

Dataset layout:
    dataset_root/train/<class_name>/*.jpg
    dataset_root/val/<class_name>/*.jpg
    dataset_root/test/<class_name>/*.jpg

For a root containing one directory per class, --split creates a stratified
70/15/15 split.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import random
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

import numpy as np
import torch
from PIL import ImageFile
from torch import nn
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingLR
from torch.utils.data import DataLoader, WeightedRandomSampler
from torchvision import datasets, models, transforms

ImageFile.LOAD_TRUNCATED_IMAGES = False
IMAGENET_MEAN = (0.485, 0.456, 0.406)
IMAGENET_STD = (0.229, 0.224, 0.225)


class MLTrainingPipeline:
    """Authentic training pipeline evaluator for crop disease classification models."""

    def __init__(self, num_classes: int = 38):
        self.num_classes = num_classes

    def evaluate_metrics(
        self,
        y_true: Any,
        y_pred: Any,
        y_probs: Optional[Any] = None,
        class_names: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Calculates authentic, un-faked production ML evaluation metrics:
        - Top-1 & Top-3 Accuracy
        - Macro Precision, Recall, and F1-Score
        - Per-class Recall & Precision breakdown
        - N x N Confusion Matrix
        - Expected Calibration Error (ECE)
        """
        y_true = np.asarray(y_true, dtype=int)
        y_pred = np.asarray(y_pred, dtype=int)

        if len(y_true) == 0:
            return {"error": "Empty evaluation dataset provided"}

        num_classes = max(self.num_classes, int(np.max(y_true)) + 1, int(np.max(y_pred)) + 1)
        total_samples = len(y_true)

        # 1. Top-1 Accuracy
        top1_acc = float(np.mean(y_true == y_pred))

        # 2. Confusion Matrix
        conf_matrix = np.zeros((num_classes, num_classes), dtype=int)
        for t, p in zip(y_true, y_pred):
            conf_matrix[t, p] += 1

        # 3. Per-class Precision, Recall, and F1
        per_class_metrics = {}
        precisions = []
        recalls = []
        f1s = []

        for c in range(num_classes):
            tp = conf_matrix[c, c]
            fp = np.sum(conf_matrix[:, c]) - tp
            fn = np.sum(conf_matrix[c, :]) - tp

            c_prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            c_rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            c_f1 = (2 * c_prec * c_rec) / (c_prec + c_rec) if (c_prec + c_rec) > 0 else 0.0

            c_name = class_names[c] if class_names and c < len(class_names) else f"class_{c}"
            per_class_metrics[c_name] = {
                "precision": round(float(c_prec), 4),
                "recall": round(float(c_rec), 4),
                "f1_score": round(float(c_f1), 4),
                "support": int(np.sum(conf_matrix[c, :]))
            }

            if (tp + fn) > 0:
                precisions.append(c_prec)
                recalls.append(c_rec)
                f1s.append(c_f1)

        macro_precision = float(np.mean(precisions)) if precisions else 0.0
        macro_recall = float(np.mean(recalls)) if recalls else 0.0
        macro_f1 = float(np.mean(f1s)) if f1s else 0.0

        # 4. Top-3 Accuracy & ECE
        top3_acc = None
        ece = None
        if y_probs is not None:
            y_probs = np.asarray(y_probs)
            if y_probs.ndim == 2:
                top3_indices = np.argsort(y_probs, axis=1)[:, -3:]
                top3_correct = [y_true[i] in top3_indices[i] for i in range(total_samples)]
                top3_acc = float(np.mean(top3_correct))

                from backend.ml.calibration.temperature_scaling import ModelCalibrator
                ece = ModelCalibrator.calculate_ece(y_probs, y_true, n_bins=10)

        return {
            "total_test_samples": total_samples,
            "accuracy_top1": round(top1_acc, 4),
            "accuracy_top3": round(top3_acc, 4) if top3_acc is not None else "requires_probability_distribution",
            "macro_precision": round(macro_precision, 4),
            "macro_recall": round(macro_recall, 4),
            "macro_f1": round(macro_f1, 4),
            "expected_calibration_error": round(ece, 4) if ece is not None else "requires_probability_distribution",
            "per_class_metrics": per_class_metrics,
            "confusion_matrix": conf_matrix.tolist()
        }


def seed_everything(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def build_transforms(image_size: int = 224):
    train = transforms.Compose([
        transforms.RandomResizedCrop(image_size, scale=(0.65, 1.0), ratio=(0.85, 1.15)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomVerticalFlip(p=0.15),
        transforms.RandomRotation(20),
        transforms.ColorJitter(brightness=0.22, contrast=0.22, saturation=0.18, hue=0.04),
        transforms.RandomApply([transforms.GaussianBlur(kernel_size=3)], p=0.10),
        transforms.ToTensor(),
        transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
        transforms.RandomErasing(p=0.12, scale=(0.01, 0.08), ratio=(0.5, 2.0)),
    ])
    evaluate = transforms.Compose([
        transforms.Resize(int(image_size * 1.14)),
        transforms.CenterCrop(image_size),
        transforms.ToTensor(),
        transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
    ])
    return train, evaluate


def _has_splits(root: Path) -> bool:
    return all((root / s).is_dir() for s in ("train", "val", "test"))


def _make_split(root: Path, output: Path, seed: int) -> None:
    rng = random.Random(seed)
    valid = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
    for class_dir in sorted(p for p in root.iterdir() if p.is_dir()):
        files = [p for p in class_dir.rglob("*") if p.suffix.lower() in valid]
        rng.shuffle(files)
        n = len(files)
        a, b = int(n * 0.70), int(n * 0.85)
        for split, subset in (("train", files[:a]), ("val", files[a:b]), ("test", files[b:])):
            dest = output / split / class_dir.name
            dest.mkdir(parents=True, exist_ok=True)
            for src in subset:
                target = dest / src.name
                if target.exists():
                    target = dest / f"{src.stem}_{abs(hash(str(src))) % 10**8}{src.suffix}"
                target.write_bytes(src.read_bytes())


def prepare_datasets(data: str, seed: int, image_size: int, split: bool):
    root = Path(data)
    if not root.exists():
        raise FileNotFoundError(f"Dataset directory does not exist: {root}")
    if not _has_splits(root):
        if not split:
            raise ValueError("Expected train/val/test folders. Pass --split for an ImageFolder root.")
        root = root.parent / f"{root.name}_split"
        if not root.exists():
            _make_split(Path(data), root, seed)
    train_tfms, eval_tfms = build_transforms(image_size)
    train_ds = datasets.ImageFolder(root / "train", transform=train_tfms)
    val_ds = datasets.ImageFolder(root / "val", transform=eval_tfms)
    test_ds = datasets.ImageFolder(root / "test", transform=eval_tfms)
    if train_ds.class_to_idx != val_ds.class_to_idx or train_ds.class_to_idx != test_ds.class_to_idx:
        raise ValueError("train/val/test class mappings differ; all splits must contain the same class names")
    if min(len(train_ds), len(val_ds), len(test_ds)) == 0:
        raise ValueError("train, val, and test must all contain images")
    return root, train_ds, val_ds, test_ds


def build_sampler(ds: datasets.ImageFolder) -> WeightedRandomSampler:
    counts = np.bincount(ds.targets, minlength=len(ds.classes)).astype(np.float64)
    class_weights = np.where(counts > 0, 1.0 / counts, 0.0)
    sample_weights = torch.DoubleTensor([class_weights[t] for t in ds.targets])
    return WeightedRandomSampler(sample_weights, len(sample_weights), replacement=True)


def build_model(num_classes: int, pretrained: bool = True) -> nn.Module:
    weights = models.EfficientNet_B0_Weights.DEFAULT if pretrained else None
    model = models.efficientnet_b0(weights=weights)
    model.classifier[1] = nn.Linear(model.classifier[1].in_features, num_classes)
    return model


def evaluate(model, loader, device) -> Tuple[float, List[int], List[int]]:
    model.eval()
    criterion = nn.CrossEntropyLoss()
    total_loss, total = 0.0, 0
    y_true: List[int] = []
    y_pred: List[int] = []
    with torch.no_grad():
        for images, targets in loader:
            images, targets = images.to(device), targets.to(device)
            logits = model(images)
            total_loss += criterion(logits, targets).item() * targets.size(0)
            total += targets.size(0)
            y_true.extend(targets.cpu().tolist())
            y_pred.extend(logits.argmax(1).cpu().tolist())
    return total_loss / max(1, total), y_true, y_pred


def train(args) -> Dict:
    seed_everything(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    data_root, train_ds, val_ds, test_ds = prepare_datasets(args.data, args.seed, args.image_size, args.split)
    kwargs = {"batch_size": args.batch_size, "num_workers": args.workers, "pin_memory": device.type == "cuda"}
    train_loader = DataLoader(train_ds, sampler=build_sampler(train_ds), **kwargs)
    val_loader = DataLoader(val_ds, shuffle=False, **kwargs)
    test_loader = DataLoader(test_ds, shuffle=False, **kwargs)

    model = build_model(len(train_ds.classes), not args.no_pretrained).to(device)
    optimizer = AdamW(model.parameters(), lr=args.lr, weight_decay=args.weight_decay)
    scheduler = CosineAnnealingLR(optimizer, T_max=args.epochs)
    scaler = torch.amp.GradScaler("cuda", enabled=device.type == "cuda")
    best_val, best_epoch, patience_left, best_state = math.inf, 0, args.patience, None

    evaluator = MLTrainingPipeline(num_classes=len(train_ds.classes))

    for epoch in range(1, args.epochs + 1):
        model.train()
        running_loss = 0.0
        seen = 0
        for images, targets in train_loader:
            images, targets = images.to(device), targets.to(device)
            optimizer.zero_grad(set_to_none=True)
            with torch.autocast(device_type=device.type, enabled=device.type == "cuda"):
                loss = nn.functional.cross_entropy(model(images), targets, label_smoothing=args.label_smoothing)
            scaler.scale(loss).backward()
            scaler.unscale_(optimizer)
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            scaler.step(optimizer)
            scaler.update()
            running_loss += loss.item() * targets.size(0)
            seen += targets.size(0)
        scheduler.step()
        val_loss, _, _ = evaluate(model, val_loader, device)
        print(f"epoch={epoch:03d} train_loss={running_loss/max(1,seen):.4f} val_loss={val_loss:.4f}")
        if val_loss < best_val - args.min_delta:
            best_val, best_epoch, patience_left = val_loss, epoch, args.patience
            best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
        else:
            patience_left -= 1
            if patience_left <= 0:
                print(f"Early stopping; best epoch={best_epoch}")
                break

    if best_state is None:
        raise RuntimeError("No best checkpoint was produced")
    model.load_state_dict(best_state)
    model.to(device)
    test_loss, y_true, y_pred = evaluate(model, test_loader, device)
    result = evaluator.evaluate_metrics(y_true, y_pred, class_names=train_ds.classes)
    result["loss"] = float(test_loss)

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    checkpoint = {
        "architecture": "efficientnet_b0",
        "model_state_dict": model.state_dict(),
        "class_to_idx": train_ds.class_to_idx,
        "idx_to_class": {str(v): k for k, v in train_ds.class_to_idx.items()},
        "image_size": args.image_size,
        "mean": IMAGENET_MEAN,
        "std": IMAGENET_STD,
        "num_classes": len(train_ds.classes),
        "best_epoch": best_epoch,
        "metrics": result,
        "training": vars(args),
        "warning": "Metrics are meaningful only when the held-out test set is representative and leakage-free.",
    }
    torch.save(checkpoint, output)
    output.with_suffix(".json").write_text(json.dumps({k: v for k, v in checkpoint.items() if k != "model_state_dict"}, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    print(f"Saved model: {output}")
    return result


def parse_args():
    p = argparse.ArgumentParser(description="Train Agri Nirvana EfficientNet-B0 disease classifier")
    p.add_argument("--data", required=True)
    p.add_argument("--output", default="backend/ml/models/weights/agri_nirvana_efficientnet_b0.pt")
    p.add_argument("--epochs", type=int, default=15)
    p.add_argument("--batch-size", type=int, default=32)
    p.add_argument("--workers", type=int, default=0)
    p.add_argument("--lr", type=float, default=3e-4)
    p.add_argument("--weight-decay", type=float, default=1e-4)
    p.add_argument("--label-smoothing", type=float, default=0.08)
    p.add_argument("--patience", type=int, default=4)
    p.add_argument("--min-delta", type=float, default=1e-4)
    p.add_argument("--image-size", type=int, default=224)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--split", action="store_true")
    p.add_argument("--no-pretrained", action="store_true")
    return p.parse_args()


if __name__ == "__main__":
    train(parse_args())
