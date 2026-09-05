"""
Larger training pipeline that wraps run_training logic with experiment tracking,
class-balanced sampling, scheduler, AdamW, warmup cosine annealing, and richer evaluation.

This is a high-level orchestrator that can be adapted to run on local or CI/GPU runners.
"""

import os
import json
import argparse
import logging
from datetime import datetime

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, WeightedRandomSampler
from torchvision import datasets, transforms, models

try:
    from sklearn.metrics import precision_recall_fscore_support, confusion_matrix
    SKLEARN_AVAILABLE = True
except Exception:
    SKLEARN_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

EXPERIMENTS_DIR = 'backend/ml/experiments'


def save_experiment_record(record: dict):
    os.makedirs(EXPERIMENTS_DIR, exist_ok=True)
    ts = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    out = os.path.join(EXPERIMENTS_DIR, f'experiment_{ts}.json')
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(record, f, indent=2)
    logger.info('Saved experiment record: %s', out)


def get_datasets(data_root, image_size, batch_size, num_workers=4):
    train_dir = os.path.join(data_root, 'train')
    val_dir = os.path.join(data_root, 'val')
    mean = [0.485, 0.456, 0.406]
    std = [0.229, 0.224, 0.225]

    train_tf = transforms.Compose([
        transforms.RandomResizedCrop(image_size, scale=(0.8,1.0)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(15),
        transforms.ColorJitter(brightness=0.2, contrast=0.15, saturation=0.15, hue=0.02),
        transforms.ToTensor(),
        transforms.Normalize(mean, std)
    ])
    val_tf = transforms.Compose([
        transforms.Resize((image_size, image_size)),
        transforms.ToTensor(),
        transforms.Normalize(mean, std)
    ])

    train_ds = datasets.ImageFolder(train_dir, transform=train_tf)
    val_ds = datasets.ImageFolder(val_dir, transform=val_tf)

    # Weighted sampler to handle class imbalance
    labels = [y for _, y in train_ds.samples]
    class_sample_count = torch.tensor([(labels == torch.tensor(i)).sum().item() if False else labels.count(i) for i in range(len(train_ds.classes))])
    class_sample_count = [labels.count(i) for i in range(len(train_ds.classes))]
    weights = [1.0 / class_sample_count[label] if class_sample_count[label] > 0 else 0.0 for _, label in train_ds.samples]
    sampler = WeightedRandomSampler(weights, num_samples=len(weights), replacement=True)

    train_loader = DataLoader(train_ds, batch_size=batch_size, sampler=sampler, num_workers=num_workers)
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False, num_workers=num_workers)

    return train_loader, val_loader, train_ds.classes


def build_model(num_classes, image_size=448, pretrained=True):
    model = models.efficientnet_b3(weights=models.EfficientNet_B3_Weights.DEFAULT if pretrained else None)
    in_features = model.classifier[1].in_features
    model.classifier[1] = nn.Linear(in_features, num_classes)
    return model


def evaluate_model(model, device, loader):
    model.eval()
    preds = []
    trues = []
    logits = []
    with torch.no_grad():
        for imgs, labels in loader:
            imgs = imgs.to(device)
            out = model(imgs)
            logits.append(out.cpu())
            _, p = torch.max(out, 1)
            preds.extend(p.cpu().tolist())
            trues.extend(labels.tolist())
    if SKLEARN_AVAILABLE:
        p, r, f, _ = precision_recall_fscore_support(trues, preds, average='macro', zero_division=0)
        cm = confusion_matrix(trues, preds).tolist()
        return {'macro_precision': p, 'macro_recall': r, 'macro_f1': f, 'confusion_matrix': cm}
    else:
        # Fallback simple accuracy
        correct = sum(1 for a,b in zip(preds,trues) if a==b)
        acc = correct / len(trues) if trues else 0.0
        return {'accuracy': acc}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', required=True)
    parser.add_argument('--epochs', type=int, default=10)
    parser.add_argument('--batch-size', type=int, default=32)
    parser.add_argument('--lr', type=float, default=1e-4)
    parser.add_argument('--image-size', type=int, default=448)
    parser.add_argument('--out', default='backend/ml/models/checkpoints/efficientnet_b3.pth')
    parser.add_argument('--pretrained', action='store_true')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()

    train_loader, val_loader, classes = get_datasets(args.data, args.image_size, args.batch_size)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = build_model(len(classes), image_size=args.image_size, pretrained=args.pretrained)
    model = model.to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=args.epochs)

    experiment = {
        'data_root': args.data,
        'classes': classes,
        'epochs': args.epochs,
        'batch_size': args.batch_size,
        'lr': args.lr,
        'image_size': args.image_size,
        'device': str(device),
        'start_time': datetime.utcnow().isoformat()
    }

    best_val = -1.0
    for epoch in range(1, args.epochs+1):
        logger.info('Epoch %d/%d', epoch, args.epochs)
        model.train()
        running_loss = 0.0
        total=0
        correct=0
        for imgs, labels in train_loader:
            imgs = imgs.to(device)
            labels = labels.to(device)
            optimizer.zero_grad()
            out = model(imgs)
            loss = criterion(out, labels)
            loss.backward()
            optimizer.step()
            running_loss += loss.item() * imgs.size(0)
            _, p = torch.max(out,1)
            correct += (p==labels).sum().item()
            total += labels.size(0)
        train_loss = running_loss/total if total else 0.0
        train_acc = correct/total if total else 0.0
        val_metrics = evaluate_model(model, device, val_loader)
        logger.info('Train loss %.4f acc %.4f; Val metrics: %s', train_loss, train_acc, val_metrics)

        # Save checkpoint and meta
        out_dir = os.path.dirname(args.out)
        os.makedirs(out_dir, exist_ok=True)
        torch.save(model.state_dict(), args.out)
        meta = {'model_state_dict': None, 'classes': classes, 'epoch': epoch, 'val_metrics': val_metrics}
        try:
            torch.save({'model_state_dict': model.state_dict(), 'meta': meta}, args.out + '.ckpt.pth')
        except Exception:
            pass

        if 'macro_f1' in val_metrics:
            score = val_metrics['macro_f1']
        elif 'accuracy' in val_metrics:
            score = val_metrics['accuracy']
        else:
            score = -1.0
        if score > best_val:
            best_val = score
            torch.save(model.state_dict(), args.out + '.best.pth')

        scheduler.step()
        experiment.setdefault('epochs_run', []).append({'epoch': epoch, 'train_loss': train_loss, 'train_acc': train_acc, 'val': val_metrics})
        save_experiment_record(experiment)

        if args.dry_run:
            logger.info('Dry-run requested; exiting after first epoch')
            break

    logger.info('Training complete; best_val=%s', str(best_val))

if __name__ == '__main__':
    main()
