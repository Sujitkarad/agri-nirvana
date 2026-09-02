"""High-capacity transfer-learning trainer for Agri Nirvana.

Uses the largest EfficientNetV2 variant exposed by torchvision: EfficientNetV2-L
with ImageNet pretrained weights. The goal is maximum model capacity within the
same production family, not a claim that a larger model is automatically more
accurate. The checkpoint is accepted by the production inference adapter only
after the normal quality and field/OOD gates pass.
"""
from __future__ import annotations

import argparse
import copy
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
from torch.utils.data import DataLoader
from torchvision import datasets, models, transforms

ImageFile.LOAD_TRUNCATED_IMAGES = False
MEAN = (0.485, 0.456, 0.406)
STD = (0.229, 0.224, 0.225)


def seed_everything(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.benchmark = True


def transforms_for(size: int):
    train = transforms.Compose([
        transforms.RandomResizedCrop(size, scale=(0.65, 1.0), ratio=(0.85, 1.15)),
        transforms.RandomHorizontalFlip(0.5),
        transforms.RandomVerticalFlip(0.10),
        transforms.RandomRotation(15),
        transforms.ColorJitter(0.18, 0.18, 0.15, 0.03),
        transforms.RandomApply([transforms.GaussianBlur(3)], p=0.08),
        transforms.ToTensor(),
        transforms.Normalize(MEAN, STD),
        transforms.RandomErasing(p=0.10, scale=(0.01, 0.06), ratio=(0.5, 2.0)),
    ])
    evaluate = transforms.Compose([
        transforms.Resize(int(size * 1.14)),
        transforms.CenterCrop(size),
        transforms.ToTensor(),
        transforms.Normalize(MEAN, STD),
    ])
    return train, evaluate


def load_data(root: Path, size: int, batch: int, workers: int, device: torch.device):
    if not all((root / s).is_dir() for s in ("train", "val", "test")):
        raise ValueError("Expected train/val/test ImageFolder directories")
    train_tf, eval_tf = transforms_for(size)
    train = datasets.ImageFolder(root / "train", transform=train_tf)
    val = datasets.ImageFolder(root / "val", transform=eval_tf)
    test = datasets.ImageFolder(root / "test", transform=eval_tf)
    if train.class_to_idx != val.class_to_idx or train.class_to_idx != test.class_to_idx:
        raise ValueError("Class mappings differ across train/val/test")
    if min(len(train), len(val), len(test)) == 0:
        raise ValueError("All splits must contain images")
    kw = dict(batch_size=batch, num_workers=workers,
              pin_memory=device.type == "cuda", persistent_workers=workers > 0)
    return train, val, test, DataLoader(train, shuffle=True, **kw), DataLoader(val, shuffle=False, **kw), DataLoader(test, shuffle=False, **kw)


def build_model(num_classes: int) -> nn.Module:
    model = models.efficientnet_v2_l(weights=models.EfficientNet_V2_L_Weights.DEFAULT)
    model.classifier[1] = nn.Linear(model.classifier[1].in_features, num_classes)
    return model


def class_weights(ds, device):
    counts = np.bincount(ds.targets, minlength=len(ds.classes)).astype(np.float32)
    w = np.zeros_like(counts)
    nz = counts > 0
    w[nz] = len(ds.targets) / (len(ds.classes) * counts[nz])
    w /= max(float(w[nz].mean()), 1e-8)
    return torch.tensor(w, dtype=torch.float32, device=device)


def outputs(model, loader, device):
    model.eval()
    logits, labels = [], []
    with torch.no_grad():
        for x, y in loader:
            x = x.to(device, non_blocking=True)
            with torch.autocast(device_type="cuda", enabled=device.type == "cuda"):
                z = model(x)
            logits.append(z.float().cpu())
            labels.append(y)
    return torch.cat(logits).numpy(), torch.cat(labels).numpy()


def ece(probs: np.ndarray, y: np.ndarray, bins: int = 15) -> float:
    conf = probs.max(1)
    pred = probs.argmax(1)
    edges = np.linspace(0.0, 1.0, bins + 1)
    total = 0.0
    for lo, hi in zip(edges[:-1], edges[1:]):
        mask = (conf > lo) & (conf <= hi if hi < 1 else conf <= hi)
        if mask.any():
            total += mask.mean() * abs(float((pred[mask] == y[mask]).mean()) - float(conf[mask].mean()))
    return float(total)


def metrics(logits: np.ndarray, y: np.ndarray, temperature: float = 1.0) -> Dict:
    z = logits / max(float(temperature), 1e-6)
    z -= z.max(1, keepdims=True)
    p = np.exp(z)
    p /= p.sum(1, keepdims=True)
    pred = p.argmax(1)
    n = p.shape[1]
    f1, precision, recall = [], [], []
    per_class = {}
    for c in range(n):
        tp = int(((y == c) & (pred == c)).sum())
        fp = int(((y != c) & (pred == c)).sum())
        fn = int(((y == c) & (pred != c)).sum())
        pr = tp / (tp + fp) if tp + fp else 0.0
        rc = tp / (tp + fn) if tp + fn else 0.0
        f = 2 * pr * rc / (pr + rc) if pr + rc else 0.0
        if (y == c).any():
            precision.append(pr); recall.append(rc); f1.append(f)
        per_class[str(c)] = {"precision": round(pr, 4), "recall": round(rc, 4), "f1": round(f, 4), "support": int((y == c).sum())}
    top3 = np.argsort(p, axis=1)[:, -min(3, n):]
    return {
        "total_samples": int(len(y)),
        "accuracy_top1": round(float((pred == y).mean()), 4),
        "accuracy_top3": round(float(np.mean([t in top3[i] for i, t in enumerate(y)])), 4),
        "macro_precision": round(float(np.mean(precision)), 4),
        "macro_recall": round(float(np.mean(recall)), 4),
        "macro_f1": round(float(np.mean(f1)), 4),
        "expected_calibration_error": round(ece(p, y), 4),
        "per_class_metrics": per_class,
    }


def fit_temperature(logits: np.ndarray, y: np.ndarray) -> float:
    # Deterministic validation-only grid search. Test data is never used here.
    best_t, best_nll = 1.0, float("inf")
    for t in np.exp(np.linspace(math.log(0.5), math.log(5.0), 80)):
        z = logits / t
        z -= z.max(1, keepdims=True)
        logp = z - np.log(np.exp(z).sum(1, keepdims=True))
        nll = -float(logp[np.arange(len(y)), y].mean())
        if nll < best_nll:
            best_nll, best_t = nll, float(t)
    return best_t


def freeze(model):
    for p in model.features.parameters(): p.requires_grad = False
    for p in model.classifier.parameters(): p.requires_grad = True


def unfreeze(model):
    for p in model.parameters(): p.requires_grad = True


def main(args):
    seed_everything(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[Train-L] device={device}")
    if device.type == "cuda": print(f"[Train-L] GPU={torch.cuda.get_device_name(0)}")
    root = Path(args.data)
    train, val, test, train_loader, val_loader, test_loader = load_data(root, args.image_size, args.batch_size, args.workers, device)

    model = build_model(len(train.classes)).to(device)
    freeze(model)
    weights = class_weights(train, device)
    loss_fn = nn.CrossEntropyLoss(weight=weights, label_smoothing=args.label_smoothing)
    opt = AdamW([
        {"params": model.features.parameters(), "lr": args.lr * 0.1},
        {"params": model.classifier.parameters(), "lr": args.lr},
    ], weight_decay=args.weight_decay)
    scheduler = CosineAnnealingLR(opt, T_max=max(1, args.epochs - args.warmup_epochs), eta_min=args.min_lr)
    scaler = torch.amp.GradScaler("cuda", enabled=device.type == "cuda")
    best_f1, best_epoch, best_state, stale = -1.0, 0, None, 0
    history = []

    for epoch in range(1, args.epochs + 1):
        if epoch == args.freeze_epochs + 1:
            print("[Train-L] Unfreezing full EfficientNetV2-L backbone")
            unfreeze(model)
        if epoch <= args.warmup_epochs:
            factor = epoch / max(1, args.warmup_epochs)
            opt.param_groups[0]["lr"] = args.lr * 0.1 * factor
            opt.param_groups[1]["lr"] = args.lr * factor
        elif epoch == args.warmup_epochs + 1:
            opt.param_groups[0]["lr"] = args.lr * 0.1
            opt.param_groups[1]["lr"] = args.lr

        model.train(); seen = 0; running = 0.0
        for x, y in train_loader:
            x, y = x.to(device, non_blocking=True), y.to(device, non_blocking=True)
            opt.zero_grad(set_to_none=True)
            with torch.autocast(device_type="cuda", enabled=device.type == "cuda"):
                loss = loss_fn(model(x), y)
            scaler.scale(loss).backward(); scaler.unscale_(opt)
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            scaler.step(opt); scaler.update()
            running += float(loss.item()) * y.size(0); seen += y.size(0)
        if epoch > args.warmup_epochs: scheduler.step()

        val_logits, val_y = outputs(model, val_loader, device)
        vm = metrics(val_logits, val_y)
        history.append({"epoch": epoch, "train_loss": round(running / max(1, seen), 5), "val_macro_f1": vm["macro_f1"], "val_accuracy": vm["accuracy_top1"]})
        print(f"epoch={epoch:03d} loss={running/max(1,seen):.4f} val_acc={vm['accuracy_top1']:.4f} val_f1={vm['macro_f1']:.4f}")
        if vm["macro_f1"] > best_f1 + args.min_delta:
            best_f1, best_epoch, best_state, stale = vm["macro_f1"], epoch, copy.deepcopy(model.state_dict()), 0
        else:
            stale += 1
            if stale >= args.patience: break

    if best_state is None: raise RuntimeError("No checkpoint produced")
    model.load_state_dict(best_state); model.eval()
    val_logits, val_y = outputs(model, val_loader, device)
    temperature = fit_temperature(val_logits, val_y)
    test_logits, test_y = outputs(model, test_loader, device)
    test_metrics = metrics(test_logits, test_y, temperature)

    out = Path(args.output); out.parent.mkdir(parents=True, exist_ok=True)
    checkpoint = {
        "architecture": "efficientnet_v2_l",
        "model_state_dict": model.state_dict(),
        "class_to_idx": train.class_to_idx,
        "idx_to_class": {str(v): k for k, v in train.class_to_idx.items()},
        "image_size": args.image_size, "mean": MEAN, "std": STD,
        "num_classes": len(train.classes), "classes": train.classes,
        "best_epoch": best_epoch, "best_validation_macro_f1": best_f1,
        "validation_samples": len(val), "test_samples": len(test),
        "metrics": test_metrics,
        "calibration": {"temperature": temperature, "method": "validation_grid_search"},
        "training": vars(args),
        "dataset_root": str(root),
        "warning": "Metrics require representative, leakage-free data and must not be interpreted as field accuracy without field validation.",
    }
    torch.save(checkpoint, out)
    meta = {k: v for k, v in checkpoint.items() if k != "model_state_dict"}
    out.with_suffix(".json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    report = {"architecture": checkpoint["architecture"], "model_id": "agri-nirvana-efficientnet-v2-l", "history": history, "best_epoch": best_epoch, "validation_macro_f1": best_f1, "temperature": temperature, "test_metrics": test_metrics}
    Path("backend/ml/training/training_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(test_metrics, indent=2))
    print(f"[Train-L] checkpoint={out}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--data", required=True)
    p.add_argument("--output", default="backend/ml/models/weights/agri_nirvana_efficientnet_v2_l.pt")
    p.add_argument("--epochs", type=int, default=100)
    p.add_argument("--batch-size", type=int, default=8)
    p.add_argument("--lr", type=float, default=7.5e-5)
    p.add_argument("--image-size", type=int, default=448)
    p.add_argument("--warmup-epochs", type=int, default=8)
    p.add_argument("--freeze-epochs", type=int, default=8)
    p.add_argument("--patience", type=int, default=15)
    p.add_argument("--workers", type=int, default=2)
    p.add_argument("--weight-decay", type=float, default=1e-4)
    p.add_argument("--min-lr", type=float, default=1e-7)
    p.add_argument("--label-smoothing", type=float, default=0.05)
    p.add_argument("--min-delta", type=float, default=1e-4)
    p.add_argument("--seed", type=int, default=42)
    main(p.parse_args())
