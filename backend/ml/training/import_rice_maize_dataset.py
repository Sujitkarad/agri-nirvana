"""Agri Nirvana - Rice & Maize Dataset Import and Split Pipeline.

Imports images from the user's Rice_and_Maize_Dataset directory,
validates every image for corruption/format, normalizes class labels into
canonical Agri Nirvana taxonomy ('Crop___Condition'), and creates
stratified 70% train / 15% val / 15% test splits.
"""

from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import random
import shutil
from typing import Dict, List, Tuple
from PIL import Image

DEFAULT_SOURCE_PATH = Path(r"C:\Users\Sujit\Downloads\Rice_and_Maize_Dataset")
DEFAULT_DEST_PATH = Path("backend/ml/datasets/rice_and_maize")

# Canonical class naming map
CLASS_MAP = {
    # Maize
    "Maize_Healthy": "Maize___healthy",
    "Maize_01_maydis_leaf_blight": "Maize___maydis_leaf_blight",
    "Maize_02_turcicum_leaf_blight": "Maize___turcicum_leaf_blight",
    "Maize_03_curvularia_leaf_spot": "Maize___curvularia_leaf_spot",
    "Maize_04_sorghum_downy_mildew": "Maize___sorghum_downy_mildew",
    "Maize_01_aphid": "Maize___aphid",
    "Maize_02_fall_armyworm": "Maize___fall_armyworm",
    "Maize_03_FAW_symptoms": "Maize___FAW_symptoms",
    # Rice
    "Rice_Healthy": "Rice___healthy",
    "Rice_01_Bacterial_leaf_blight": "Rice___bacterial_leaf_blight",
    "Rice_02_Brown_spot": "Rice___brown_spot",
    "Rice_03_False_smut": "Rice___false_smut",
    "Rice_04_leaf_sheath_blight": "Rice___leaf_sheath_blight",
    "Rice_05_Leaf_folder": "Rice___leaf_folder",
    "Rice_06_Rice_skipper": "Rice___rice_skipper",
    "Rice_07_White_stem_borer": "Rice___white_stem_borer",
    "Rice_08_Yellow_stem_borer": "Rice___yellow_stem_borer",
}


def discover_and_map_classes(source_root: Path) -> Dict[str, List[Path]]:
    """Walk through source dataset directory and collect valid image files grouped by canonical class."""
    class_images: Dict[str, List[Path]] = {}

    for root_dir, _, files in os.walk(source_root):
        curr_path = Path(root_dir)
        valid_files = [
            curr_path / f
            for f in files
            if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))
        ]
        if not valid_files:
            continue

        rel_parts = curr_path.relative_to(source_root).parts
        if not rel_parts:
            continue

        crop = rel_parts[0]  # "Maize" or "Rice"
        category = rel_parts[-1]  # subfolder name e.g. "01_maydis_leaf_blight" or "Healthy"

        key = f"{crop}_{category}"
        canonical_class = CLASS_MAP.get(key)
        if not canonical_class:
            # Fallback formatting
            canonical_class = f"{crop}___{category.lower()}"

        if canonical_class not in class_images:
            class_images[canonical_class] = []

        for img_path in valid_files:
            try:
                # Fast validation that file is readable image
                with Image.open(img_path) as img:
                    img.verify()
                class_images[canonical_class].append(img_path)
            except Exception as err:
                print(f"[Warning] Skipping corrupted image {img_path}: {err}")

    return class_images


def materialize_splits(
    class_images: Dict[str, List[Path]],
    dest_root: Path,
    train_pct: float = 0.70,
    val_pct: float = 0.15,
    seed: int = 42,
) -> Dict[str, Any]:
    """Stratify and copy images into train/val/test directories."""
    rng = random.Random(seed)
    stats: Dict[str, Dict[str, int]] = {"train": {}, "val": {}, "test": {}}

    for split in ["train", "val", "test"]:
        split_dir = dest_root / split
        if split_dir.exists():
            shutil.rmtree(split_dir)
        split_dir.mkdir(parents=True, exist_ok=True)

    manifest = {
        "classes": sorted(list(class_images.keys())),
        "total_classes": len(class_images),
        "split_counts": {},
        "per_class_counts": {},
    }

    total_copied = 0
    for cls_name, img_paths in sorted(class_images.items()):
        shuffled = list(img_paths)
        rng.shuffle(shuffled)
        total_n = len(shuffled)

        n_train = max(1, int(total_n * train_pct))
        n_val = max(1, int(total_n * val_pct))

        train_files = shuffled[:n_train]
        val_files = shuffled[n_train : n_train + n_val]
        test_files = shuffled[n_train + n_val :]

        # Guarantee at least 1 image in test
        if not test_files and len(train_files) > 1:
            test_files.append(train_files.pop())

        splits = {
            "train": train_files,
            "val": val_files,
            "test": test_files,
        }

        manifest["per_class_counts"][cls_name] = {
            "train": len(train_files),
            "val": len(val_files),
            "test": len(test_files),
            "total": total_n,
        }

        for split_name, files in splits.items():
            target_dir = dest_root / split_name / cls_name
            target_dir.mkdir(parents=True, exist_ok=True)
            for idx, src_file in enumerate(files):
                dest_file = target_dir / f"{cls_name}_{idx:04d}{src_file.suffix.lower()}"
                shutil.copy2(src_file, dest_file)
                total_copied += 1

    manifest["total_images"] = total_copied
    manifest["dest_directory"] = str(dest_root.resolve())

    # Write dataset manifest
    manifest_path = dest_root / "dataset_manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    return manifest


def main():
    parser = argparse.ArgumentParser(description="Import Rice & Maize Dataset into Agri Nirvana")
    parser.add_argument("--source", type=str, default=str(DEFAULT_SOURCE_PATH), help="Source directory")
    parser.add_argument("--dest", type=str, default=str(DEFAULT_DEST_PATH), help="Destination directory")
    args = parser.parse_args()

    src = Path(args.source)
    dst = Path(args.dest)

    if not src.exists():
        raise FileNotFoundError(f"Source dataset directory not found: {src}")

    print(f"[*] Scanning source dataset: {src}")
    class_images = discover_and_map_classes(src)
    print(f"[+] Found {len(class_images)} classes with {sum(len(v) for v in class_images.values())} valid images:")
    for cls, files in sorted(class_images.items()):
        print(f"    - {cls}: {len(files)} images")

    print(f"\n[*] Materializing stratified splits into {dst}...")
    manifest = materialize_splits(class_images, dst)
    print(f"[+] Complete! Copied {manifest['total_images']} images into train/val/test splits.")
    print(f"[+] Dataset manifest written to {dst / 'dataset_manifest.json'}")


if __name__ == "__main__":
    main()
