"""Agri Nirvana - Rice & Maize Crop Pathology PyTorch Training Pipeline.

Trains a high-accuracy MobileNetV3 transfer-learning model on the 17 Rice & Maize
disease and insect-pest pathology classes with cosine annealing, data augmentation,
validation checkpoint selection, and test split evaluation.
"""

from __future__ import annotations
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
import time
from typing import Dict, List, Tuple

# Ensure stdout handles UTF-8 on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, models, transforms

DEFAULT_DATA_DIR = Path("backend/ml/datasets/rice_and_maize")
DEFAULT_WEIGHTS_DIR = Path("backend/ml/models/weights")
DEFAULT_OUTPUT_PATH = DEFAULT_WEIGHTS_DIR / "rice_and_maize_classifier.pt"


def get_data_transforms() -> Dict[str, transforms.Compose]:
    """Return training and evaluation image transformation pipelines."""
    return {
        "train": transforms.Compose([
            transforms.RandomResizedCrop(224, scale=(0.8, 1.0)),
            transforms.RandomHorizontalFlip(),
            transforms.RandomRotation(15),
            transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ]),
        "eval": transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ]),
    }


def create_model(num_classes: int) -> nn.Module:
    """Build MobileNetV3-Small transfer learning model with customized classification head."""
    model = models.mobilenet_v3_small(weights=models.MobileNet_V3_Small_Weights.DEFAULT)
    in_features = model.classifier[3].in_features
    # Replace final linear layer
    model.classifier[3] = nn.Sequential(
        nn.Dropout(p=0.3),
        nn.Linear(in_features, num_classes)
    )
    return model


def evaluate(
    model: nn.Module,
    dataloader: DataLoader,
    criterion: nn.Module,
    device: torch.device,
) -> Tuple[float, float, float, float, float]:
    """Compute loss, accuracy, macro precision, macro recall, and macro F1."""
    model.eval()
    total_loss = 0.0
    all_preds: List[int] = []
    all_targets: List[int] = []

    with torch.no_grad():
        for inputs, targets in dataloader:
            inputs = inputs.to(device)
            targets = targets.to(device)

            outputs = model(inputs)
            loss = criterion(outputs, targets)
            total_loss += loss.item() * inputs.size(0)

            _, preds = torch.max(outputs, 1)
            all_preds.extend(preds.cpu().numpy().tolist())
            all_targets.extend(targets.cpu().numpy().tolist())

    avg_loss = total_loss / len(dataloader.dataset) if dataloader.dataset else 0.0
    total_samples = len(all_targets)
    correct = sum(1 for t, p in zip(all_targets, all_preds) if t == p)
    acc = correct / total_samples if total_samples > 0 else 0.0

    # Determine unique classes present or total classes
    classes_present = set(all_targets) | set(all_preds)
    num_classes = max(classes_present) + 1 if classes_present else 1

    precisions: List[float] = []
    recalls: List[float] = []
    f1s: List[float] = []

    for c in range(num_classes):
        tp = sum(1 for t, p in zip(all_targets, all_preds) if t == c and p == c)
        fp = sum(1 for t, p in zip(all_targets, all_preds) if t != c and p == c)
        fn = sum(1 for t, p in zip(all_targets, all_preds) if t == c and p != c)

        prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * (prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0

        precisions.append(prec)
        recalls.append(rec)
        f1s.append(f1)

    macro_prec = sum(precisions) / len(precisions) if precisions else 0.0
    macro_rec = sum(recalls) / len(recalls) if recalls else 0.0
    macro_f1 = sum(f1s) / len(f1s) if f1s else 0.0

    return avg_loss, acc, macro_prec, macro_rec, macro_f1


def train_model(
    data_dir: Path,
    output_path: Path,
    epochs: int = 15,
    batch_size: int = 16,
    learning_rate: float = 1e-3,
    weight_decay: float = 1e-4,
    device_str: str = "auto",
):
    """Execute complete transfer-learning training loop with checkpoint persistence."""
    start_time = time.time()

    if device_str == "auto":
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    else:
        device = torch.device(device_str)

    print("=" * 70)
    print(f"[*] AGRI NIRVANA - RICE & MAIZE CROP PATHOLOGY TRAINING")
    print(f"[*] Target Device: {device}")
    print(f"[*] Dataset Root:  {data_dir}")
    print(f"[*] Target Checkpoint: {output_path}")
    print(f"[*] Training Hyperparameters: Epochs={epochs}, BatchSize={batch_size}, LR={learning_rate}")
    print("=" * 70)

    tforms = get_data_transforms()
    train_dir = data_dir / "train"
    val_dir = data_dir / "val"
    test_dir = data_dir / "test"

    train_ds = datasets.ImageFolder(str(train_dir), transform=tforms["train"])
    val_ds = datasets.ImageFolder(str(val_dir), transform=tforms["eval"])
    test_ds = datasets.ImageFolder(str(test_dir), transform=tforms["eval"])

    num_classes = len(train_ds.classes)
    class_names = train_ds.classes
    class_to_idx = train_ds.class_to_idx
    idx_to_class = {v: k for k, v in class_to_idx.items()}

    print(f"\n[+] Detected {num_classes} Classes:")
    for idx, cname in enumerate(class_names):
        print(f"    {idx:02d}: {cname}")

    print(f"\n[+] Dataset Splits: Train={len(train_ds)}, Val={len(val_ds)}, Test={len(test_ds)}")

    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False, num_workers=0)
    test_loader = DataLoader(test_ds, batch_size=batch_size, shuffle=False, num_workers=0)

    # Initialize model
    model = create_model(num_classes)
    model = model.to(device)

    # Loss with label smoothing to prevent overfitting on small datasets
    criterion = nn.CrossEntropyLoss(label_smoothing=0.1)

    # AdamW with cosine annealing schedule
    optimizer = optim.AdamW(model.parameters(), lr=learning_rate, weight_decay=weight_decay)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs, eta_min=1e-5)

    best_val_f1 = 0.0
    best_state = None
    best_metrics = {}

    print("\n[*] Commencing Training Loop...")
    print("-" * 70)
    header = f"{'Epoch':<8} | {'Train Loss':<12} | {'Val Loss':<10} | {'Val Acc':<9} | {'Val F1':<8} | {'LR':<10}"
    print(header)
    print("-" * 70)

    for epoch in range(1, epochs + 1):
        model.train()
        train_loss = 0.0

        for inputs, targets in train_loader:
            inputs = inputs.to(device)
            targets = targets.to(device)

            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, targets)
            loss.backward()

            nn.utils.clip_grad_norm_(model.parameters(), max_norm=2.0)
            optimizer.step()

            train_loss += loss.item() * inputs.size(0)

        scheduler.step()
        train_loss = train_loss / len(train_ds)

        val_loss, val_acc, val_prec, val_rec, val_f1 = evaluate(model, val_loader, criterion, device)
        current_lr = scheduler.get_last_lr()[0]

        is_best = val_f1 > best_val_f1
        if is_best:
            best_val_f1 = val_f1
            best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}
            best_metrics = {
                "epoch": epoch,
                "val_loss": round(val_loss, 4),
                "val_accuracy": round(val_acc * 100, 2),
                "val_macro_f1": round(val_f1 * 100, 2),
                "val_macro_precision": round(val_prec * 100, 2),
                "val_macro_recall": round(val_rec * 100, 2),
            }

        flag = " [BEST]" if is_best else ""
        print(f"{epoch:<8} | {train_loss:<12.4f} | {val_loss:<10.4f} | {val_acc*100:<8.2f}% | {val_f1*100:<7.2f}% | {current_lr:<10.6f}{flag}")

    print("-" * 70)
    print(f"\n[*] Training Complete in {time.time() - start_time:.1f}s!")
    print(f"[+] Best Validation Results (Epoch {best_metrics['epoch']}):")
    print(f"    - Accuracy:  {best_metrics['val_accuracy']}%")
    print(f"    - Macro F1:  {best_metrics['val_macro_f1']}%")

    # Evaluate best model on held-out test split
    if best_state is not None:
        model.load_state_dict(best_state)

    test_loss, test_acc, test_prec, test_rec, test_f1 = evaluate(model, test_loader, criterion, device)
    print(f"\n[+] Held-Out Test Split Performance:")
    print(f"    - Accuracy:  {test_acc * 100:.2f}%")
    print(f"    - Macro F1:  {test_f1 * 100:.2f}%")
    print(f"    - Precision: {test_prec * 100:.2f}%")
    print(f"    - Recall:    {test_rec * 100:.2f}%")

    # Save Checkpoint Artifact
    output_path.parent.mkdir(parents=True, exist_ok=True)
    checkpoint = {
        "model_id": "agri-nirvana-rice-and-maize-v1",
        "architecture": "mobilenet_v3_small",
        "num_classes": num_classes,
        "classes": class_names,
        "class_to_idx": class_to_idx,
        "idx_to_class": idx_to_class,
        "model_state_dict": best_state or model.state_dict(),
        "input_size": [3, 224, 224],
        "metrics": {
            "val": best_metrics,
            "test": {
                "test_loss": round(test_loss, 4),
                "test_accuracy": round(test_acc * 100, 2),
                "test_macro_f1": round(test_f1 * 100, 2),
                "test_macro_precision": round(test_prec * 100, 2),
                "test_macro_recall": round(test_rec * 100, 2),
            },
        },
        "training_metadata": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "epochs": epochs,
            "batch_size": batch_size,
            "device": str(device),
            "train_samples": len(train_ds),
            "val_samples": len(val_ds),
            "test_samples": len(test_ds),
        },
    }

    torch.save(checkpoint, str(output_path))
    print(f"\n[OK] Checkpoint saved successfully to: {output_path}")

    # Also save metadata JSON summary for fast inspection
    summary_path = output_path.with_suffix(".json")
    json_summary = {k: v for k, v in checkpoint.items() if k != "model_state_dict"}
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(json_summary, f, indent=2)
    print(f"[OK] Model metadata summary saved to: {summary_path}")

    return checkpoint


def main():
    parser = argparse.ArgumentParser(description="Train Rice & Maize Pathology Classifier")
    parser.add_argument("--data", type=str, default=str(DEFAULT_DATA_DIR), help="Dataset root directory")
    parser.add_argument("--output", type=str, default=str(DEFAULT_OUTPUT_PATH), help="Checkpoint output path")
    parser.add_argument("--epochs", type=int, default=12, help="Number of training epochs")
    parser.add_argument("--batch-size", type=int, default=16, help="Training batch size")
    parser.add_argument("--lr", type=float, default=1e-3, help="Initial learning rate")
    args = parser.parse_args()

    train_model(
        data_dir=Path(args.data),
        output_path=Path(args.output),
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.lr,
    )


if __name__ == "__main__":
    main()
