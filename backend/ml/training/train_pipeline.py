"""High-accuracy Agri Nirvana crop-disease training pipeline.

Designed for real evaluation rather than leaderboard-style overfitting:
- EfficientNetV2-S ImageNet transfer learning
- 384x384 inputs
- class-balanced cross entropy
- realistic augmentation
- progressive fine-tuning
- AdamW + warmup + cosine decay
- AMP on CUDA
- best-checkpoint selection by validation Macro-F1
- temperature calibration on validation logits
- final metrics on a held-out test set
"""
from __future__ import annotations

import argparse
import copy
import json
import math
import os
import random
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import torch
from PIL import ImageFile
from torch import nn
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingLR
from torch.utils.data import DataLoader
from torchvision import datasets, models, transforms

from backend.ml.calibration.temperature_scaling import ModelCalibrator

ImageFile.LOAD_TRUNCATED_IMAGES = False
IMAGENET_MEAN = (0.485, 0.456, 0.406)
IMAGENET_STD = (0.229, 0.224, 0.225)


class MLTrainingPipeline:
    """Evaluation metrics for crop-disease classification."""

    def __init__(self, num_classes: int):
        self.num_classes = num_classes

    def evaluate_metrics(
        self,
        y_true: Any,
        y_pred: Any,
        y_probs: Optional[Any] = None,
        class_names: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        y_true = np.asarray(y_true, dtype=int)
        y_pred = np.asarray(y_pred, dtype=int)
        if len(y_true) == 0:
            return {"error": "Empty evaluation dataset"}

        n = max(self.num_classes, int(y_true.max()) + 1, int(y_pred.max()) + 1)
        cm = np.zeros((n, n), dtype=int)
        for t, p in zip(y_true, y_pred):
            cm[t, p] += 1

        precision, recall, f1 = [], [], []
        per_class = {}
        for c in range(n):
            tp = cm[c, c]
            fp = cm[:, c].sum() - tp
            fn = cm[c, :].sum() - tp
            pr = tp / (tp + fp) if tp + fp else 0.0
            rc = tp / (tp + fn) if tp + fn else 0.0
            f = 2 * pr * rc / (pr + rc) if pr + rc else 0.0
            name = class_names[c] if class_names and c < len(class_names) else f"class_{c}"
            per_class[name] = {
                "precision": round(float(pr), 4),
                "recall": round(float(rc), 4),
                "f1_score": round(float(f), 4),
                "support": int(cm[c, :].sum()),
            }
            if cm[c, :].sum() > 0:
                precision.append(pr)
                recall.append(rc)
                f1.append(f)

        top3 = None
        ece = None
        if y_probs is not None:
            probs = np.asarray(y_probs)
            top3_idx = np.argsort(probs, axis=1)[:, -min(3, probs.shape[1]) :]
            top3 = float(np.mean([t in top3_idx[i] for i, t in enumerate(y_true)]))
            ece = ModelCalibrator.calculate_ece(probs, y_true, n_bins=15)

        return {
            "total_test_samples": int(len(y_true)),
            "accuracy_top1": round(float(np.mean(y_true == y_pred)), 4),
            "accuracy_top3": round(top3, 4) if top3 is not None else None,
            "macro_precision": round(float(np.mean(precision)), 4),
            "macro_recall": round(float(np.mean(recall)), 4),
            "macro_f1": round(float(np.mean(f1)), 4),
            "expected_calibration_error": round(float(ece), 4) if ece is not None else None,
            "per_class_metrics": per_class,
            "confusion_matrix": cm.tolist(),
        }


def seed_everything(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.benchmark = True


def build_transforms(image_size: int = 384):
    train = transforms.Compose([
        transforms.RandomResizedCrop(image_size, scale=(0.70, 1.0), ratio=(0.85, 1.15)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomVerticalFlip(p=0.10),
        transforms.RandomRotation(15),
        transforms.ColorJitter(brightness=0.18, contrast=0.18, saturation=0.15, hue=0.03),
        transforms.RandomApply([transforms.GaussianBlur(kernel_size=3)], p=0.08),
        transforms.ToTensor(),
        transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
        transforms.RandomErasing(p=0.08, scale=(0.01, 0.06), ratio=(0.5, 2.0)),
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
        a, b = int(len(files) * 0.70), int(len(files) * 0.85)
        for split, subset in (("train", files[:a]), ("val", files[a:b]), ("test", files[b:])):
            dest = output / split / class_dir.name
            dest.mkdir(parents=True, exist_ok=True)
            for i, src in enumerate(subset):
                target = dest / src.name
                if target.exists():
                    target = dest / f"{src.stem}_{i}{src.suffix}"
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
        raise ValueError("Class mappings differ between train/val/test")
    if min(len(train_ds), len(val_ds), len(test_ds)) == 0:
        raise ValueError("train, val and test must all contain images")
    return root, train_ds, val_ds, test_ds


def build_model(num_classes: int) -> nn.Module:
    model = models.efficientnet_v2_s(weights=models.EfficientNet_V2_S_Weights.DEFAULT)
    model.classifier[1] = nn.Linear(model.classifier[1].in_features, num_classes)
    return model


def make_class_weights(ds: datasets.ImageFolder, device: torch.device) -> torch.Tensor:
    counts = np.bincount(ds.targets, minlength=len(ds.classes)).astype(np.float32)
    weights = np.zeros_like(counts)
    nonzero = counts > 0
    weights[nonzero] = len(ds.targets) / (len(counts) * counts[nonzero])
    weights = weights / max(weights.mean(), 1e-8)
    return torch.tensor(weights, dtype=torch.float32, device=device)


def freeze_backbone(model: nn.Module) -> None:
    for p in model.features.parameters():
        p.requires_grad = False
    for p in model.classifier.parameters():
        p.requires_grad = True


def unfreeze_all(model: nn.Module) -> None:
    for p in model.parameters():
        p.requires_grad = True


def collect_outputs(model, loader, device):
    model.eval()
    logits_all, labels_all = [], []
    with torch.no_grad():
        for images, labels in loader:
            images = images.to(device, non_blocking=True)
            with torch.autocast(device_type="cuda", enabled=device.type == "cuda"):
                logits = model(images)
            logits_all.append(logits.float().cpu().numpy())
            labels_all.append(labels.numpy())
    return np.concatenate(logits_all), np.concatenate(labels_all)


def train(args) -> Dict[str, Any]:
    seed_everything(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[Train] device={device}")
    if device.type == "cuda":
        print(f"[Train] GPU={torch.cuda.get_device_name(0)}")

    data_root, train_ds, val_ds, test_ds = prepare_datasets(args.data, args.seed, args.image_size, args.split)
    loader_kwargs = {
        "batch_size": args.batch_size,
        "num_workers": args.workers,
        "pin_memory": device.type == "cuda",
        "persistent_workers": args.workers > 0,
    }
    train_loader = DataLoader(train_ds, shuffle=True, **loader_kwargs)
    val_loader = DataLoader(val_ds, shuffle=False, **loader_kwargs)
    test_loader = DataLoader(test_ds, shuffle=False, **loader_kwargs)

    model = build_model(len(train_ds.classes)).to(device)
    freeze_backbone(model)
    class_weights = make_class_weights(train_ds, device)
    criterion = nn.CrossEntropyLoss(weight=class_weights, label_smoothing=args.label_smoothing)

    optimizer = AdamW(
        [
            {"params": model.features.parameters(), "lr": args.lr * 0.1},
            {"params": model.classifier.parameters(), "lr": args.lr},
        ],
        weight_decay=args.weight_decay,
    )
    scheduler = CosineAnnealingLR(optimizer, T_max=max(1, args.epochs - args.warmup_epochs), eta_min=args.min_lr)
    scaler = torch.amp.GradScaler("cuda", enabled=device.type == "cuda")

    evaluator = MLTrainingPipeline(len(train_ds.classes))
    best_f1 = -1.0
    best_epoch = 0
    best_state = None
    patience_left = args.patience
    history = []

    for epoch in range(1, args.epochs + 1):
        if epoch == args.freeze_epochs + 1:
            print("[Train] Progressive fine-tuning: unfreezing EfficientNetV2-S backbone")
            unfreeze_all(model)

        # Linear warmup for all optimizer groups.
        if epoch <= args.warmup_epochs:
            warm = epoch / max(1, args.warmup_epochs)
            optimizer.param_groups[0]["lr"] = args.lr * 0.1 * warm
            optimizer.param_groups[1]["lr"] = args.lr * warm
        elif epoch == args.warmup_epochs + 1:
            optimizer.param_groups[0]["lr"] = args.lr * 0.1
            optimizer.param_groups[1]["lr"] = args.lr

        model.train()
        running_loss, seen = 0.0, 0
        for images, labels in train_loader:
            images = images.to(device, non_blocking=True)
            labels = labels.to(device, non_blocking=True)
            optimizer.zero_grad(set_to_none=True)
            with torch.autocast(device_type="cuda", enabled=device.type == "cuda"):
                logits = model(images)
                loss = criterion(logits, labels)
            scaler.scale(loss).backward()
            scaler.unscale_(optimizer)
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            scaler.step(optimizer)
            scaler.update()
            running_loss += loss.item() * labels.size(0)
            seen += labels.size(0)

        if epoch > args.warmup_epochs:
            scheduler.step()

        val_logits, val_labels = collect_outputs(model, val_loader, device)
        val_probs = torch.softmax(torch.from_numpy(val_logits), dim=1).numpy()
        val_preds = val_probs.argmax(1)
        val_metrics = evaluator.evaluate_metrics(val_labels, val_preds, val_probs, train_ds.classes)
        train_loss = running_loss / max(1, seen)
        history.append({
            "epoch": epoch,
            "train_loss": round(float(train_loss), 5),
            "val_macro_f1": val_metrics["macro_f1"],
            "val_accuracy": val_metrics["accuracy_top1"],
            "lr_classifier": optimizer.param_groups[1]["lr"],
        })
        print(
            f"epoch={epoch:03d} train_loss={train_loss:.4f} "
            f"val_acc={val_metrics['accuracy_top1']:.4f} val_macro_f1={val_metrics['macro_f1']:.4f}"
        )

        if val_metrics["macro_f1"] > best_f1 + args.min_delta:
            best_f1 = val_metrics["macro_f1"]
            best_epoch = epoch
            patience_left = args.patience
            best_state = copy.deepcopy(model.state_dict())
        else:
            patience_left -= 1
            if patience_left <= 0:
                print(f"[Train] Early stopping at epoch {epoch}; best epoch={best_epoch}")
                break

    if best_state is None:
        raise RuntimeError("No best checkpoint was produced")

    model.load_state_dict(best_state)
    model.to(device).eval()

    # Fit calibration on validation only; test remains untouched until final evaluation.
    val_logits, val_labels = collect_outputs(model, val_loader, device)
    calibrator = ModelCalibrator(artifact_path=os.path.join(str(Path(args.output).parent), "temperature_calibration.json"))
    calibration = calibrator.fit_temperature(val_logits, val_labels)

    test_logits, test_labels = collect_outputs(model, test_loader, device)
    scaled = test_logits / float(calibration["temperature"])
    scaled -= scaled.max(axis=1, keepdims=True)
    test_probs = np.exp(scaled)
    test_probs /= test_probs.sum(axis=1, keepdims=True)
    test_preds = test_probs.argmax(1)
    test_metrics = evaluator.evaluate_metrics(test_labels, test_preds, test_probs, train_ds.classes)

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    checkpoint = {
        "architecture": "efficientnet_v2_s",
        "model_state_dict": model.state_dict(),
        "class_to_idx": train_ds.class_to_idx,
        "idx_to_class": {str(v): k for k, v in train_ds.class_to_idx.items()},
        "image_size": args.image_size,
        "mean": IMAGENET_MEAN,
        "std": IMAGENET_STD,
        "num_classes": len(train_ds.classes),
        "classes": train_ds.classes,
        "best_epoch": best_epoch,
        "best_validation_macro_f1": best_f1,
        "validation_samples": len(val_ds),
        "test_samples": len(test_ds),
        "metrics": test_metrics,
        "calibration": calibration,
        "training": vars(args),
        "dataset_root": str(data_root),
        "warning": "Metrics are meaningful only when the held-out test set is representative and leakage-free.",
    }
    torch.save(checkpoint, output)
    metadata = {k: v for k, v in checkpoint.items() if k != "model_state_dict"}
    output.with_suffix(".json").write_text(json.dumps(metadata, indent=2, default=str), encoding="utf-8")
    Path(args.history_output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.history_output).write_text(json.dumps({"history": history, "final_test_metrics": test_metrics, "calibration": calibration}, indent=2), encoding="utf-8")

    print("[Train] FINAL HELD-OUT TEST METRICS")
    print(json.dumps(test_metrics, indent=2))
    print(f"[Train] Saved model: {output}")
    return metadata


def parse_args():
    p = argparse.ArgumentParser(description="Train Agri Nirvana high-accuracy EfficientNetV2-S classifier")
    p.add_argument("--data", required=True)
    p.add_argument("--output", default="backend/ml/models/weights/agri_nirvana_efficientnet_b0.pt")
    p.add_argument("--history-output", default="backend/ml/training/training_report.json")
    p.add_argument("--epochs", type=int, default=80)
    p.add_argument("--batch-size", type=int, default=16)
    p.add_argument("--workers", type=int, default=2)
    p.add_argument("--lr", type=float, default=1e-4)
    p.add_argument("--min-lr", type=float, default=1e-6)
    p.add_argument("--weight-decay", type=float, default=1e-4)
    p.add_argument("--label-smoothing", type=float, default=0.05)
    p.add_argument("--patience", type=int, default=12)
    p.add_argument("--min-delta", type=float, default=1e-4)
    p.add_argument("--image-size", type=int, default=384)
    p.add_argument("--warmup-epochs", type=int, default=5)
    p.add_argument("--freeze-epochs", type=int, default=5)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--split", action="store_true")
    return p.parse_args()


if __name__ == "__main__":
    train(parse_args())
