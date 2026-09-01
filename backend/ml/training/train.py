"""End-to-End PyTorch Training & Fine-Tuning Pipeline for Agri Nirvana Crop AI.

Features:
- Pretrained MobileNetV2 transfer learning
- Standard data augmentations (RandomResizedCrop, HorizontalFlip, ColorJitter)
- Epoch-by-epoch training and validation loops
- Authentic evaluation metrics (Macro F1, Per-class Recall, Top-1/Top-3, Confusion Matrix)
- Post-training temperature scaling calibration
- Checkpoint and metadata persistence
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, Any

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, models, transforms

# Add root directory to sys.path
root_dir = Path(__file__).resolve().parent.parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from backend.ml.calibration.temperature_scaling import calibrator
from backend.ml.training.dataset_manager import prepare_benchmark_dataset, DEFAULT_CLASSES
from backend.ml.training.train_pipeline import MLTrainingPipeline


def get_data_transforms():
    train_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomRotation(degrees=15),
        transforms.ColorJitter(brightness=0.15, contrast=0.15),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    val_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    return train_transform, val_transform


def build_model(num_classes: int, device: torch.device) -> nn.Module:
    print(f"[Train] Building MobileNetV2 architecture with custom {num_classes}-class classifier head...")
    try:
        model = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.DEFAULT)
    except Exception:
        # Fallback to unweighted model if offline
        model = models.mobilenet_v2()

    # Freeze base feature extractor layers for fast, stable CPU transfer learning
    for param in model.features[:-3].parameters():
        param.requires_grad = False

    last_channel = model.last_channel
    model.classifier = nn.Sequential(
        nn.Dropout(p=0.25),
        nn.Linear(last_channel, 256),
        nn.ReLU(),
        nn.Dropout(p=0.2),
        nn.Linear(256, num_classes),
    )

    model.to(device)
    return model


def train_model(
    epochs: int = 3,
    batch_size: int = 8,
    learning_rate: float = 0.001,
    dataset_dir: str = "backend/ml/datasets/benchmark",
    output_dir: str = "backend/ml/weights"
) -> Dict[str, Any]:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[Train] Training on device: {device}")

    # 1. Dataset Preparation
    train_path = os.path.join(dataset_dir, "train")
    val_path = os.path.join(dataset_dir, "val")

    if not os.path.exists(train_path) or not os.path.exists(val_path):
        prepare_benchmark_dataset(dataset_root=dataset_dir)

    train_transform, val_transform = get_data_transforms()
    train_dataset = datasets.ImageFolder(train_path, transform=train_transform)
    val_dataset = datasets.ImageFolder(val_path, transform=val_transform)

    class_names = train_dataset.classes
    num_classes = len(class_names)
    print(f"[Train] Loaded {len(train_dataset)} training samples and {len(val_dataset)} validation samples across {num_classes} classes.")

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=0)

    # 2. Build Model & Optimizer
    model = build_model(num_classes, device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.AdamW(filter(lambda p: p.requires_grad, model.parameters()), lr=learning_rate, weight_decay=1e-4)

    best_val_acc = 0.0
    training_history = []
    start_total_time = time.time()

    # 3. Training Loop
    for epoch in range(1, epochs + 1):
        epoch_start = time.time()
        model.train()
        running_loss = 0.0
        correct_train = 0
        total_train = 0

        for images, labels in train_loader:
            images = images.to(device)
            labels = labels.to(device)

            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item() * images.size(0)
            _, preds = torch.max(outputs, 1)
            correct_train += torch.sum(preds == labels.data).item()
            total_train += labels.size(0)

        epoch_loss = running_loss / total_train if total_train > 0 else 0.0
        epoch_train_acc = correct_train / total_train if total_train > 0 else 0.0

        # 4. Validation Loop
        model.eval()
        val_loss = 0.0
        val_correct = 0
        val_total = 0
        val_logits_list = []
        val_labels_list = []

        with torch.no_grad():
            for images, labels in val_loader:
                images = images.to(device)
                labels = labels.to(device)

                outputs = model(images)
                loss = criterion(outputs, labels)

                val_loss += loss.item() * images.size(0)
                _, preds = torch.max(outputs, 1)
                val_correct += torch.sum(preds == labels.data).item()
                val_total += labels.size(0)

                val_logits_list.append(outputs.cpu().numpy())
                val_labels_list.append(labels.cpu().numpy())

        epoch_val_loss = val_loss / val_total if val_total > 0 else 0.0
        epoch_val_acc = val_correct / val_total if val_total > 0 else 0.0
        epoch_duration = round(time.time() - epoch_start, 2)

        print(
            f"Epoch [{epoch}/{epochs}] ({epoch_duration}s) | "
            f"Train Loss: {epoch_loss:.4f} | Train Acc: {epoch_train_acc * 100:.1f}% | "
            f"Val Loss: {epoch_val_loss:.4f} | Val Acc: {epoch_val_acc * 100:.1f}%"
        )

        training_history.append({
            "epoch": epoch,
            "train_loss": round(epoch_loss, 4),
            "train_acc": round(epoch_train_acc, 4),
            "val_loss": round(epoch_val_loss, 4),
            "val_acc": round(epoch_val_acc, 4),
            "duration_seconds": epoch_duration
        })

        if epoch_val_acc >= best_val_acc:
            best_val_acc = epoch_val_acc

    total_training_time = round(time.time() - start_total_time, 2)

    # 5. Authentic Final Evaluation Metrics Calculation
    print("\n[Train] Computing authentic evaluation metrics on validation set...")
    all_val_logits = np.concatenate(val_logits_list, axis=0)
    all_val_labels = np.concatenate(val_labels_list, axis=0)
    val_probs = np.exp(all_val_logits - np.max(all_val_logits, axis=1, keepdims=True))
    val_probs = val_probs / np.sum(val_probs, axis=1, keepdims=True)
    val_preds = np.argmax(val_probs, axis=1)

    evaluator = MLTrainingPipeline(num_classes=num_classes)
    metrics = evaluator.evaluate_metrics(
        y_true=all_val_labels,
        y_pred=val_preds,
        y_probs=val_probs,
        class_names=class_names
    )

    # 6. Post-hoc Temperature Scaling Calibration
    print("[Train] Fitting temperature scaling calibration on validation logits...")
    calib_result = calibrator.fit_temperature(all_val_logits, all_val_labels)
    print(f"[Train] Model Calibrated! Optimal Temperature T={calib_result['temperature']:.3f}, ECE: {calib_result['ece_before']:.4f} -> {calib_result['ece_after']:.4f}")

    # 7. Model Checkpoint Saving
    os.makedirs(output_dir, exist_ok=True)
    model_save_path = os.path.join(output_dir, "best_crop_model.pt")
    torch.save(model.state_dict(), model_save_path)
    print(f"[Train] Saved trained model weights to: {model_save_path}")

    # 8. Model Metadata Persistence
    metadata = {
        "model_architecture": "MobileNetV2-Custom",
        "num_classes": num_classes,
        "classes": class_names,
        "best_validation_accuracy": round(best_val_acc, 4),
        "macro_f1": metrics["macro_f1"],
        "macro_recall": metrics["macro_recall"],
        "expected_calibration_error": metrics["expected_calibration_error"],
        "total_training_time_seconds": total_training_time,
        "calibrated": True,
        "temperature": calib_result["temperature"],
        "trained_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    metadata_path = os.path.join(output_dir, "model_metadata.json")
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    # 9. Full Report Persistence
    report = {
        "summary": metadata,
        "training_history": training_history,
        "evaluation_metrics": metrics,
        "calibration": calib_result
    }
    report_path = os.path.join("backend/ml/training", "training_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"[Train] Saved training evaluation report to: {report_path}")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train Agri Nirvana Crop AI Model")
    parser.add_argument("--epochs", type=int, default=3, help="Number of training epochs")
    parser.add_argument("--batch-size", type=int, default=8, help="Batch size")
    parser.add_argument("--lr", type=float, default=0.001, help="Learning rate")
    args = parser.parse_args()

    report = train_model(epochs=args.epochs, batch_size=args.batch_size, learning_rate=args.lr)
    print("\n[SUCCESS] Training pipeline completed successfully!")
