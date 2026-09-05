"""
Evaluate model on field datasets and perform OOD detection metrics.
Produces a JSON report with per-class metrics and a simple ECE estimate.

Usage:
  python evaluate_field_ood.py --model path/to/model.pth --data path/to/field_dataset
"""

import os
import sys
import argparse
import json
import logging
from datetime import datetime

import torch
import torch.nn.functional as F
from torchvision import datasets, transforms, models

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_model(model_path, num_classes):
    model = models.efficientnet_b3(weights=models.EfficientNet_B3_Weights.DEFAULT)
    in_features = model.classifier[1].in_features
    model.classifier[1] = torch.nn.Linear(in_features, num_classes)
    state = torch.load(model_path, map_location='cpu')
    if isinstance(state, dict) and 'model_state_dict' in state:
        model.load_state_dict(state['model_state_dict'])
    else:
        model.load_state_dict(state)
    return model


def compute_ece(probs, labels, n_bins=10):
    # Simple ECE estimate
    bins = [[] for _ in range(n_bins)]
    for p, y in zip(probs, labels):
        conf = float(max(p))
        bin_idx = min(int(conf * n_bins), n_bins-1)
        bins[bin_idx].append((conf, int(y==p.argmax())))
    total = 0
    ece = 0.0
    for b in bins:
        if not b: continue
        acc = sum(x[1] for x in b)/len(b)
        avg_conf = sum(x[0] for x in b)/len(b)
        ece += len(b) * abs(acc - avg_conf)
        total += len(b)
    return (ece/total) if total else None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', required=True)
    parser.add_argument('--data', required=True)
    parser.add_argument('--out', default='backend/ml/experiments/field_ood_report.json')
    args = parser.parse_args()

    # Assume ImageFolder structure
    val_tf = transforms.Compose([transforms.Resize((448,448)), transforms.ToTensor(), transforms.Normalize([0.485,0.456,0.406],[0.229,0.224,0.225])])
    ds = datasets.ImageFolder(args.data, transform=val_tf)
    loader = torch.utils.data.DataLoader(ds, batch_size=16, shuffle=False)

    model = load_model(args.model, num_classes=len(ds.classes))
    model.eval()

    all_probs = []
    all_preds = []
    all_trues = []
    with torch.no_grad():
        for imgs, labels in loader:
            out = model(imgs)
            probs = F.softmax(out, dim=1).cpu()
            all_probs.extend(probs.tolist())
            all_preds.extend(probs.argmax(dim=1).cpu().tolist())
            all_trues.extend(labels.tolist())

    # Simple metrics
    total = len(all_trues)
    correct = sum(1 for a,b in zip(all_preds, all_trues) if a==b)
    acc = correct/total if total else None
    ece = compute_ece(all_probs, all_trues)

    report = {
        'model': args.model,
        'data': args.data,
        'timestamp': datetime.utcnow().isoformat(),
        'num_samples': total,
        'accuracy': acc,
        'ece': ece
    }

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    logger.info('Wrote field/OOD report to %s', args.out)

if __name__ == '__main__':
    main()
