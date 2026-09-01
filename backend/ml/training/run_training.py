"""
Training runner for Agri Nirvana EfficientNet-B3 transfer learning.
Adds resume-from-checkpoint, TensorBoard logging, and optional AMP (mixed-precision).
Usage examples (local, with GPU):
  python backend/ml/training/run_training.py --data /path/to/plantvillage --epochs 10 --batch-size 32 --lr 1e-4 --out checkpoints/efficientnet_b3.pth --log-dir runs/exp1 --pretrained

Notes:
- Data directory must be ImageFolder layout: <data_root>/train/<class>/* and <data_root>/val/<class>/*
- Script writes model.state_dict() to --out for inference compatibility and also a meta checkpoint at --out + '.ckpt.pth' for resume.
"""

import argparse
import os
import time
from typing import Tuple

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torchvision import datasets, transforms, models

try:
    from torch.utils.tensorboard import SummaryWriter
    TENSORBOARD_AVAILABLE = True
except Exception:
    TENSORBOARD_AVAILABLE = False


def get_dataloaders(data_root: str, image_size: int, batch_size: int, num_workers: int = 4) -> Tuple[DataLoader, DataLoader, list]:
    train_dir = os.path.join(data_root, "train")
    val_dir = os.path.join(data_root, "val")

    mean = [0.485, 0.456, 0.406]
    std = [0.229, 0.224, 0.225]

    train_transforms = transforms.Compose([
        transforms.Resize((image_size, image_size)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(10),
        transforms.ToTensor(),
        transforms.Normalize(mean=mean, std=std)
    ])

    val_transforms = transforms.Compose([
        transforms.Resize((image_size, image_size)),
        transforms.ToTensor(),
        transforms.Normalize(mean=mean, std=std)
    ])

    train_ds = datasets.ImageFolder(train_dir, transform=train_transforms)
    val_ds = datasets.ImageFolder(val_dir, transform=val_transforms)

    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True, num_workers=num_workers)
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False, num_workers=num_workers)

    num_classes = len(train_ds.classes)
    classes = train_ds.classes
    print(f"Loaded data. Train classes: {num_classes}, train samples: {len(train_ds)}, val samples: {len(val_ds)}")
    return train_loader, val_loader, classes


def build_model(num_classes: int, pretrained: bool = False) -> nn.Module:
    model = models.efficientnet_b3(weights=models.EfficientNet_B3_Weights.DEFAULT if pretrained else None)
    in_features = model.classifier[1].in_features
    model.classifier[1] = nn.Linear(in_features, num_classes)
    return model


def train_one_epoch(model, device, loader, criterion, optimizer, scaler=None, use_amp=False):
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0
    for imgs, labels in loader:
        imgs = imgs.to(device)
        labels = labels.to(device)
        optimizer.zero_grad()
        if use_amp and scaler is not None:
            with torch.cuda.amp.autocast():
                outputs = model(imgs)
                loss = criterion(outputs, labels)
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
        else:
            outputs = model(imgs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

        running_loss += loss.item() * imgs.size(0)
        _, preds = torch.max(outputs, 1)
        correct += (preds == labels).sum().item()
        total += labels.size(0)
    avg_loss = running_loss / total if total else 0.0
    acc = correct / total if total else 0.0
    return avg_loss, acc


def validate(model, device, loader, criterion, scaler=None, use_amp=False):
    model.eval()
    running_loss = 0.0
    correct = 0
    total = 0
    with torch.no_grad():
        for imgs, labels in loader:
            imgs = imgs.to(device)
            labels = labels.to(device)
            if use_amp and scaler is not None:
                with torch.cuda.amp.autocast():
                    outputs = model(imgs)
                    loss = criterion(outputs, labels)
            else:
                outputs = model(imgs)
                loss = criterion(outputs, labels)
            running_loss += loss.item() * imgs.size(0)
            _, preds = torch.max(outputs, 1)
            correct += (preds == labels).sum().item()
            total += labels.size(0)
    avg_loss = running_loss / total if total else 0.0
    acc = correct / total if total else 0.0
    return avg_loss, acc


def save_state_and_checkpoint(model, optimizer, meta_out_path, state_out_path, epoch, best_val_acc, classes=None):
    # Save model.state_dict() for inference compatibility
    os.makedirs(os.path.dirname(state_out_path), exist_ok=True)
    torch.save(model.state_dict(), state_out_path)
    # Save meta checkpoint for resume
    meta = {
        "model_state_dict": model.state_dict(),
        "optimizer_state_dict": optimizer.state_dict(),
        "epoch": epoch,
        "best_val_acc": best_val_acc,
        "classes": classes if classes is not None else []
    }
    torch.save(meta, meta_out_path)
    print(f"Saved state to {state_out_path} and meta checkpoint to {meta_out_path}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True, help="Data root path with train/val splits (ImageFolder layout)")
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--lr", type=float, default=1e-4)
    parser.add_argument("--image-size", type=int, default=300)
    parser.add_argument("--out", default="backend/ml/models/checkpoints/efficientnet_b3.pth", help="Path to write model.state_dict() for inference")
    parser.add_argument("--num-workers", type=int, default=4)
    parser.add_argument("--pretrained", action="store_true", help="Start from torchvision pretrained weights")
    parser.add_argument("--device", default=None, help="cuda or cpu; autodetect if omitted")
    parser.add_argument("--resume", default=None, help="Path to meta checkpoint (.ckpt.pth) to resume from")
    parser.add_argument("--log-dir", default="runs/exp", help="TensorBoard log dir")
    parser.add_argument("--amp", action="store_true", help="Enable mixed-precision training (requires CUDA)")
    args = parser.parse_args()

    device = args.device or ("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    if args.amp and device == "cpu":
        print("AMP requested but no CUDA available; proceeding without AMP")
        use_amp = False
    else:
        use_amp = args.amp

    train_loader, val_loader, classes = get_dataloaders(args.data, args.image_size, args.batch_size, args.num_workers)
    num_classes = len(classes)

    model = build_model(num_classes, pretrained=args.pretrained)
    model = model.to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)

    scaler = torch.cuda.amp.GradScaler() if use_amp and device != "cpu" else None

    best_val_acc = 0.0
    start_epoch = 1

    # TensorBoard setup
    writer = None
    if TENSORBOARD_AVAILABLE:
        writer = SummaryWriter(log_dir=args.log_dir)
        print(f"TensorBoard enabled; logs at {args.log_dir}")
    else:
        print("TensorBoard not available; skipping logging")

    # Resume if requested
    meta_checkpoint_path = None
    if args.resume:
        meta_checkpoint_path = args.resume
    else:
        meta_checkpoint_path = args.out + ".ckpt.pth"

    if meta_checkpoint_path and os.path.exists(meta_checkpoint_path):
        print(f"Resuming from checkpoint {meta_checkpoint_path}")
        ckpt = torch.load(meta_checkpoint_path, map_location=device)
        if 'model_state_dict' in ckpt:
            model.load_state_dict(ckpt['model_state_dict'])
        else:
            model.load_state_dict(ckpt)
        if 'optimizer_state_dict' in ckpt:
            try:
                optimizer.load_state_dict(ckpt['optimizer_state_dict'])
            except Exception:
                print("Warning: optimizer state could not be loaded")
        start_epoch = int(ckpt.get('epoch', 0)) + 1
        best_val_acc = float(ckpt.get('best_val_acc', 0.0))
        print(f"Resumed. Starting epoch {start_epoch}, best_val_acc={best_val_acc}")

    total_start = time.time()
    for epoch in range(start_epoch, args.epochs + 1):
        t0 = time.time()
        train_loss, train_acc = train_one_epoch(model, device, train_loader, criterion, optimizer, scaler=scaler, use_amp=use_amp)
        val_loss, val_acc = validate(model, device, val_loader, criterion, scaler=scaler, use_amp=use_amp)
        elapsed = time.time() - t0
        print(f"Epoch {epoch}/{args.epochs} - {elapsed:.1f}s - train_loss={train_loss:.4f} train_acc={train_acc:.4f} val_loss={val_loss:.4f} val_acc={val_acc:.4f}")

        # TensorBoard logging
        if writer:
            writer.add_scalar('train/loss', train_loss, epoch)
            writer.add_scalar('train/accuracy', train_acc, epoch)
            writer.add_scalar('val/loss', val_loss, epoch)
            writer.add_scalar('val/accuracy', val_acc, epoch)

        # Save last meta checkpoint and state dict every epoch (best also saved separately)
        meta_out = args.out + ".ckpt.pth"
        state_out = args.out  # state_dict for inference
        save_state_and_checkpoint(model, optimizer, meta_out, state_out, epoch, best_val_acc, classes=classes)

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            best_out = args.out.replace('.pth', '.best.pth') if args.out.endswith('.pth') else args.out + '.best'
            # save best state_dict
            torch.save(model.state_dict(), best_out)
            print(f"New best model saved to {best_out}")

    total_time = time.time() - total_start
    print(f"Training completed in {total_time/60:.2f} minutes. Best val acc: {best_val_acc:.4f}")

    if writer:
        writer.close()


if __name__ == "__main__":
    main()
