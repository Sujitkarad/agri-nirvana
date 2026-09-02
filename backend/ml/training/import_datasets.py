"""Download and materialize public plant-disease datasets for Agri Nirvana.

Datasets are intentionally NOT committed to Git. This script creates a local
workspace under backend/ml/datasets/ and records provenance in
`dataset_manifest.json`.

Sources:
- PlantVillage: mohanty/PlantVillage, color config (leaf-grouped 80/20 split)
- PlantDoc: geraldmc/plantdoc-full @ v0.1.0 (field-condition evaluation data)
- Crop Disease Expert Annotations: DigiGreen/Crop_Disease_Images

PlantVillage is used for training/benchmarking. PlantDoc and the DigiGreen
smallholder/expert-reviewed images are kept outside the training set. The
DigiGreen images are split into known-class field evaluation images and
unmatched images used as OOD, using deterministic label matching against the
PlantVillage production taxonomy.
"""
from __future__ import annotations

import argparse
import json
import random
import re
import shutil
from pathlib import Path
from typing import Any

from datasets import load_dataset

IMAGE_EXT = ".jpg"
VALID_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


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


def _split_train_into_train_val(root: Path, val_fraction: float = 0.15, seed: int = 42) -> tuple[int, int]:
    rng = random.Random(seed)
    train_total = val_total = 0
    for class_dir in sorted((root / "train").iterdir()):
        files = list(class_dir.glob("*.jpg"))
        rng.shuffle(files)
        val_count = max(1, int(len(files) * val_fraction))
        for src in files[:val_count]:
            dest = root / "val" / class_dir.name
            dest.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dest / src.name))
            val_total += 1
        train_total += len(files) - val_count
    return train_total, val_total


def import_plantvillage(root: Path) -> dict[str, Any]:
    out = root / "plant_disease"
    if out.exists():
        shutil.rmtree(out)
    ds = load_dataset("mohanty/PlantVillage", "color")
    train_n = _save_hf_split(ds["train"], out, "label", "train")
    test_n = _save_hf_split(ds["test"], out, "label", "test")
    train_after, val_n = _split_train_into_train_val(out)
    return {
        "dataset": "mohanty/PlantVillage",
        "config": "color",
        "source_train": train_n,
        "source_test": test_n,
        "materialized_train": train_after,
        "materialized_val": val_n,
        "materialized_test": test_n,
        "materialized": str(out),
    }


def import_plantdoc(root: Path) -> dict[str, Any]:
    out = root / "plantdoc"
    if out.exists():
        shutil.rmtree(out)
    ds = load_dataset("geraldmc/plantdoc-full", revision="v0.1.0", split="train")
    train_n = _save_hf_split(
        ds.filter(lambda x: x["split"] == "train"), out, "class_label", "train"
    )
    test_n = _save_hf_split(
        ds.filter(lambda x: x["split"] == "test"), out, "class_label", "test"
    )
    train_after, val_n = _split_train_into_train_val(out)
    return {
        "dataset": "geraldmc/plantdoc-full",
        "revision": "v0.1.0",
        "source_train": train_n,
        "source_test": test_n,
        "materialized_train": train_after,
        "materialized_val": val_n,
        "materialized_test": test_n,
        "materialized": str(out),
    }


def _norm(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def _field_class_match(crop: str, diagnosis: str, production_classes: list[str]) -> str | None:
    """Map expert crop/diagnosis text to a production class conservatively.

    Only a unique, high-overlap match is accepted. Ambiguous/unmatched expert
    images remain OOD rather than being force-labelled.
    """
    text = _norm(f"{crop} {diagnosis}")
    if not text or diagnosis.strip().lower() == "healthy":
        diagnosis_text = _norm(crop + " healthy")
    else:
        diagnosis_text = text

    best: tuple[float, str] | None = None
    second = 0.0
    text_tokens = set(diagnosis_text.split())
    stop = {"leaf", "leaves", "plant", "disease", "diseases", "symptom", "symptoms", "crop"}
    text_tokens -= stop

    for cls in production_classes:
        cls_tokens = set(_norm(cls.replace("___", " ")).split()) - stop
        if not cls_tokens:
            continue
        overlap = len(text_tokens & cls_tokens) / len(cls_tokens)
        crop_hint = _norm(crop)
        if crop_hint and crop_hint in _norm(cls):
            overlap += 0.35
        score = min(1.0, overlap)
        if best is None or score > best[0]:
            second = best[0] if best else 0.0
            best = (score, cls)
        elif score > second:
            second = score

    if best is None or best[0] < 0.75 or best[0] - second < 0.10:
        return None
    return best[1]


def import_farmer_expert_field(root: Path) -> dict[str, Any]:
    """Materialize expert-reviewed smallholder photos as field/OOD evaluation."""
    out = root / "field_ood"
    if out.exists():
        shutil.rmtree(out)
    field_root = out / "field"
    ood_root = out / "ood" / "expert_unmatched"
    ds = load_dataset("DigiGreen/Crop_Disease_Images", split="train")

    production = load_dataset("mohanty/PlantVillage", "color", split="train")
    production_classes = sorted({str(x["label"]) for x in production})

    matched = unmatched = 0
    for i, row in enumerate(ds):
        image = row["image"].convert("RGB")
        crop = str(row.get("crop", ""))
        diagnosis = str(row.get("diagnosis", ""))
        label = _field_class_match(crop, diagnosis, production_classes)
        if label is None:
            dest = ood_root
            unmatched += 1
        else:
            dest = field_root / _safe_name(label)
            matched += 1
        dest.mkdir(parents=True, exist_ok=True)
        image.save(dest / f"{i:07d}{IMAGE_EXT}", quality=95)

    manifest = {
        "dataset": "DigiGreen/Crop_Disease_Images",
        "purpose": "field_evaluation_and_ood",
        "source_images": len(ds),
        "known_class_field_images": matched,
        "unmatched_ood_images": unmatched,
        "training_contamination": False,
        "labeling": "expert-reviewed annotations; unmatched/ambiguous labels are retained as OOD",
        "materialized": str(out),
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="backend/ml/datasets")
    parser.add_argument("--plantvillage", action="store_true")
    parser.add_argument("--plantdoc", action="store_true")
    parser.add_argument("--farmer-field", action="store_true")
    args = parser.parse_args()
    if not args.plantvillage and not args.plantdoc and not args.farmer_field:
        args.plantvillage = args.plantdoc = args.farmer_field = True

    root = Path(args.output)
    root.mkdir(parents=True, exist_ok=True)
    manifest: dict[str, Any] = {"schema_version": 2, "datasets": []}
    if args.plantvillage:
        manifest["datasets"].append(import_plantvillage(root))
    if args.plantdoc:
        manifest["datasets"].append(import_plantdoc(root))
    if args.farmer_field:
        manifest["datasets"].append(import_farmer_expert_field(root))
    (root / "dataset_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
