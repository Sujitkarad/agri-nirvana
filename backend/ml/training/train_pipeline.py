"""Real training pipeline for Agri Nirvana crop-disease image classification.

Dataset layout:
    dataset_root/train/<class_name>/*.jpg
    dataset_root/val/<class_name>/*.jpg
    dataset_root/test/<class_name>/*.jpg

For a root containing one directory per class, --split creates a stratified
70/15/15 split. For production evaluation, use a field/plant-grouped held-out
test set because random image splits can overestimate real-world performance.

Example:
    python -m backend.ml.training.train_pipeline --data backend/ml/datasets/plant_disease --epochs 15
"""
from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path
from typing import Dict, List, Tuple

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


def classification_metrics(y_true: List[int], y_pred: List[int], n: int) -> Dict:
    cm = np.zeros((n, n), dtype=np.int64)
    for t, p in zip(y_true, y_pred):
        cm[t, p] += 1
    ps, rs, fs = [], [], []
    for i in range(n):
        tp = cm[i, i]
        fp = cm[:, i].sum() - tp
        fn = cm[i, :].sum() - tp
        p = tp / max(1, tp + fp)
        r = tp / max(1, tp + fn)
        ps.append(p); rs.append(r); fs.append(2 * p * r / max(1e-12, p + r))
    return {
        "accuracy": float(np.trace(cm) / max(1, cm.sum())),
        "macro_precision": float(np.mean(ps)),
        "macro_recall": float(np.mean(rs)),
        "macro_f1": float(np.mean(fs)),
        "confusion_matrix": cm.tolist(),
    }


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

    for epoch in range(1, args.epochs + 1):
        model.train(); running_loss = 0.0; seen = 0
        for images, targets in train_loader:
            images, targets = images.to(device), targets.to(device)
            optimizer.zero_grad(set_to_none=True)
            with torch.autocast(device_type=device.type, enabled=device.type == "cuda"):
                loss = nn.functional.cross_entropy(model(images), targets, label_smoothing=args.label_smoothing)
            scaler.scale(loss).backward(); scaler.unscale_(optimizer)
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            scaler.step(optimizer); scaler.update()
            running_loss += loss.item() * targets.size(0); seen += targets.size(0)
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
    model.load_state_dict(best_state); model.to(device)
    test_loss, y_true, y_pred = evaluate(model, test_loader, device)
    result = classification_metrics(y_true, y_pred, len(train_ds.classes)); result["loss"] = float(test_loss)

    output = Path(args.output); output.parent.mkdir(parents=True, exist_ok=True)
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
        "warning": "Metrics are meaningful only when the held-out test set is representative and leakage-free; they are not a guarantee of field accuracy.",
    }
    torch.save(checkpoint, output)
    output.with_suffix(".json").write_text(json.dumps({k: v for k, v in checkpoint.items() if k != "model_state_dict"}, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2)); print(f"Saved model: {output}")
    return result


def parse_args():
    p = argparse.ArgumentParser(description="Train Agri Nirvana EfficientNet-B0 disease classifier")
    p.add_argument("--data", required=True)
    p.add_argument("--output", default="backend/ml/models/weights/agri_nirvana_efficientnet_b0.pt")
    p.add_argument("--epochs", type=int, default=15)
    p.add_argument("--batch-size", type=int, default=32)
    p.add_argument("--workers", type=int, default=2)
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
