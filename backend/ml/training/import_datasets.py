"""Materialize relevant public crop-disease datasets with provenance.

Datasets are never committed to Git. The workflow downloads them into
backend/ml/datasets, audits them, and keeps incompatible taxonomies separate.
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
    return {"dataset": "mohanty/PlantVillage", "config": "color", "source_train": train_n, "source_test": test_n, "materialized_train": train_after, "materialized_val": val_n, "materialized_test": test_n, "materialized": str(out)}


def import_plantdoc(root: Path) -> dict[str, Any]:
    out = root / "plantdoc"
    if out.exists():
        shutil.rmtree(out)
    ds = load_dataset("geraldmc/plantdoc-full", revision="v0.1.0", split="train")
    train_n = _save_hf_split(ds.filter(lambda x: x["split"] == "train"), out, "class_label", "train")
    test_n = _save_hf_split(ds.filter(lambda x: x["split"] == "test"), out, "class_label", "test")
    train_after, val_n = _split_train_into_train_val(out)
    return {"dataset": "geraldmc/plantdoc-full", "revision": "v0.1.0", "source_train": train_n, "source_test": test_n, "materialized_train": train_after, "materialized_val": val_n, "materialized_test": test_n, "materialized": str(out)}


def _norm(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def _production_class_names() -> list[str]:
    ds = load_dataset("mohanty/PlantVillage", "color", split="train")
    feature = ds.features["label"]
    names = getattr(feature, "names", None)
    if not names:
        raise RuntimeError("PlantVillage label feature has no class names")
    return [str(name) for name in names]


def _field_class_match(crop: str, diagnosis: str, production_classes: list[str]) -> str | None:
    crop_text = _norm(crop)
    diagnosis_parts = [_norm(x) for x in diagnosis.split(";") if _norm(x)]
    if not crop_text or not diagnosis_parts:
        return None
    candidates: list[tuple[float, str]] = []
    aliases = {"maize": {"corn"}, "chilli": {"pepper", "chili", "hot pepper"}, "pepper": {"chilli", "chili", "hot pepper"}}
    for cls in production_classes:
        parts = cls.split("___", 1)
        if len(parts) != 2:
            continue
        cls_crop, cls_disease = map(_norm, parts)
        crop_score = 1.0 if crop_text == cls_crop else (0.85 if cls_crop in aliases.get(crop_text, set()) else 0.0)
        if crop_score == 0.0:
            continue
        disease_scores = []
        for diagnosis_text in diagnosis_parts:
            tokens, cls_tokens = set(diagnosis_text.split()), set(cls_disease.split())
            if tokens and cls_tokens:
                disease_scores.append(max(len(tokens & cls_tokens) / max(len(tokens | cls_tokens), 1), float(diagnosis_text == cls_disease)))
        if disease_scores:
            candidates.append((0.65 * crop_score + 0.35 * max(disease_scores), cls))
    candidates.sort(reverse=True)
    if not candidates:
        return None
    best, second = candidates[0], candidates[1][0] if len(candidates) > 1 else 0.0
    return best[1] if best[0] >= 0.80 and best[0] - second >= 0.10 else None


def import_farmer_expert_field(root: Path) -> dict[str, Any]:
    out = root / "field_ood"
    if out.exists():
        shutil.rmtree(out)
    field_root, ood_root = out / "field", out / "ood" / "expert_unmatched"
    ds = load_dataset("DigiGreen/Crop_Disease_Images", split="train")
    production_classes = _production_class_names()
    matched = unmatched = 0
    for i, row in enumerate(ds):
        image = row["image"].convert("RGB")
        label = _field_class_match(str(row.get("crop", "")), str(row.get("diagnosis", "")), production_classes)
        dest = field_root / _safe_name(label) if label else ood_root
        matched += int(label is not None)
        unmatched += int(label is None)
        dest.mkdir(parents=True, exist_ok=True)
        image.save(dest / f"{i:07d}{IMAGE_EXT}", quality=95)
    manifest = {"dataset": "DigiGreen/Crop_Disease_Images", "purpose": "field_evaluation_and_ood", "source_annotations": len(ds), "known_class_field_images": matched, "unmatched_ood_images": unmatched, "training_contamination": False, "license": "CC-BY-4.0", "source_url": "https://huggingface.co/datasets/DigiGreen/Crop_Disease_Images", "materialized": str(out)}
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def import_sugarcane_specialist(root: Path) -> dict[str, Any]:
    """Materialize the published 11-class sugarcane dataset for a specialist model.

    It is deliberately NOT merged into PlantVillage's 38-class production
    taxonomy. The specialist can be fine-tuned/evaluated independently until
    a reviewed multi-crop taxonomy is introduced.
    """
    out = root / "sugarcane_specialist"
    if out.exists():
        shutil.rmtree(out)
    ds = load_dataset("Project-AgML/sugarcane_leaf_disease_classification", split="train")
    count = _save_hf_split(ds, out, "label", "train")
    train_n, val_n = _split_train_into_train_val(out, val_fraction=0.15, seed=42)
    test_root = out / "test"
    test_root.mkdir(parents=True, exist_ok=True)
    manifest = {
        "dataset": "Project-AgML/sugarcane_leaf_disease_classification",
        "purpose": "sugarcane_specialist_training",
        "source_images": count,
        "classes": 11,
        "materialized_train": train_n,
        "materialized_val": val_n,
        "test_status": "held-out test must be created only from a group-safe source split before final reporting",
        "license": "CC-BY-4.0",
        "source_url": "https://huggingface.co/datasets/Project-AgML/sugarcane_leaf_disease_classification",
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
    parser.add_argument("--sugarcane-specialist", action="store_true")
    args = parser.parse_args()
    if not any((args.plantvillage, args.plantdoc, args.farmer_field, args.sugarcane_specialist)):
        args.plantvillage = args.plantdoc = args.farmer_field = args.sugarcane_specialist = True
    root = Path(args.output)
    root.mkdir(parents=True, exist_ok=True)
    manifest: dict[str, Any] = {"schema_version": 3, "datasets": []}
    if args.plantvillage: manifest["datasets"].append(import_plantvillage(root))
    if args.plantdoc: manifest["datasets"].append(import_plantdoc(root))
    if args.farmer_field: manifest["datasets"].append(import_farmer_expert_field(root))
    if args.sugarcane_specialist: manifest["datasets"].append(import_sugarcane_specialist(root))
    (root / "dataset_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
