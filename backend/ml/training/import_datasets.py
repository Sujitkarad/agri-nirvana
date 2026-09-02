"""Download and materialize public plant-disease datasets for Agri Nirvana.

Datasets are intentionally NOT committed to Git. This script creates a local
workspace under backend/ml/datasets/ and records provenance in dataset_manifest.json.

Sources:
- PlantVillage: mohanty/PlantVillage, color config (leaf-grouped 80/20 split)
- PlantDoc: geraldmc/plantdoc-full @ v0.1.0 (field-condition evaluation data)

PlantVillage is suitable for training/benchmarking. PlantDoc is kept separate
from the training set by default so field-domain performance can be measured
without silently contaminating the training data.
"""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any

from datasets import load_dataset

IMAGE_EXT = ".jpg"


def _safe_name(value: str) -> str:
    return "_".join(value.replace("/", "_").split())


def _save_hf_split(ds: Any, output: Path, label_key: str, split_name: str) -> int:
    count = 0
    for i, row in enumerate(ds):
        image = row["image"].convert("RGB")
        label = _safe_name(str(row[label_key]))
        dest = output / split_name / label
        dest.mkdir(parents=True, exist_ok=True)
        image.save(dest / f"{i:07d}{IMAGE_EXT}", quality=95)
        count += 1
    return count


def import_plantvillage(root: Path) -> dict[str, Any]:
    out = root / "plantvillage"
    if out.exists():
        shutil.rmtree(out)
    ds = load_dataset("mohanty/PlantVillage", "color")
    train_n = _save_hf_split(ds["train"], out, "label", "train")
    test_n = _save_hf_split(ds["test"], out, "label", "test")

    # Keep a validation set derived only from the training partition. The
    # official PlantVillage test partition remains untouched for evaluation.
    from random import Random
    rng = Random(42)
    val_root = root / "plantvillage_validation"
    if val_root.exists():
        shutil.rmtree(val_root)
    for class_dir in sorted((out / "train").iterdir()):
        files = list(class_dir.glob("*.jpg"))
        rng.shuffle(files)
        val_count = max(1, int(len(files) * 0.15))
        for src in files[:val_count]:
            dest = val_root / "val" / class_dir.name
            dest.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest / src.name)
        # The remaining training images stay in out/train.
        for src in files[:val_count]:
            src.unlink()
    # Restore the training directory to the canonical train/val/test layout.
    merged = root / "plantvillage_training"
    if merged.exists():
        shutil.rmtree(merged)
    (merged / "train").mkdir(parents=True)
    for class_dir in sorted((out / "train").iterdir()):
        dest = merged / "train" / class_dir.name
        dest.mkdir(parents=True, exist_ok=True)
        for src in class_dir.glob("*.jpg"):
            shutil.copy2(src, dest / src.name)
    for class_dir in sorted((val_root / "val").iterdir()):
        dest = merged / "val" / class_dir.name
        dest.mkdir(parents=True, exist_ok=True)
        for src in class_dir.glob("*.jpg"):
            shutil.copy2(src, dest / src.name)
    for class_dir in sorted((out / "test").iterdir()):
        dest = merged / "test" / class_dir.name
        dest.mkdir(parents=True, exist_ok=True)
        for src in class_dir.glob("*.jpg"):
            shutil.copy2(src, dest / src.name)

    shutil.rmtree(out)
    shutil.rmtree(val_root)
    return {"dataset": "mohanty/PlantVillage", "config": "color", "train": train_n, "test": test_n, "materialized": str(merged)}


def import_plantdoc(root: Path) -> dict[str, Any]:
    out = root / "plantdoc"
    if out.exists():
        shutil.rmtree(out)
    ds = load_dataset("geraldmc/plantdoc-full", revision="v0.1.0", split="train")
    train_n = _save_hf_split(ds.filter(lambda x: x["split"] == "train"), out, "class_label", "train")
    test_n = _save_hf_split(ds.filter(lambda x: x["split"] == "test"), out, "class_label", "test")
    return {"dataset": "geraldmc/plantdoc-full", "revision": "v0.1.0", "train": train_n, "test": test_n, "materialized": str(out)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="backend/ml/datasets")
    parser.add_argument("--plantvillage", action="store_true")
    parser.add_argument("--plantdoc", action="store_true")
    args = parser.parse_args()
    if not args.plantvillage and not args.plantdoc:
        args.plantvillage = args.plantdoc = True

    root = Path(args.output)
    root.mkdir(parents=True, exist_ok=True)
    manifest: dict[str, Any] = {"schema_version": 1, "datasets": []}
    if args.plantvillage:
        manifest["datasets"].append(import_plantvillage(root))
    if args.plantdoc:
        manifest["datasets"].append(import_plantdoc(root))
    (root / "dataset_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
