"""Import & Ingest Kaggle 'vipoooool/new-plant-diseases-dataset' for Agri Nirvana.

Downloads the dataset via kagglehub, validates the 38 plant pathology classes,
organizes them into standard train/val/test splits, and prepares them for
direct consumption by Agri Nirvana's training pipeline and diagnosis engine.

Usage:
    python -m backend.ml.training.import_kaggle_dataset
    python -m backend.ml.training.import_kaggle_dataset --dest backend/ml/datasets/plant_disease --mode link
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    import kagglehub
except ImportError:
    raise ImportError(
        "kagglehub is required. Please install it using: pip install kagglehub"
    )

DATASET_HANDLE = "vipoooool/new-plant-diseases-dataset"

# 38 canonical plant pathology classes matching Agri Nirvana's inference engine
EXPECTED_38_CLASSES = [
    "Apple___Apple_scab",
    "Apple___Black_rot",
    "Apple___Cedar_apple_rust",
    "Apple___healthy",
    "Blueberry___healthy",
    "Cherry_(including_sour)___Powdery_mildew",
    "Cherry_(including_sour)___healthy",
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot",
    "Corn_(maize)___Common_rust_",
    "Corn_(maize)___Northern_Leaf_Blight",
    "Corn_(maize)___healthy",
    "Grape___Black_rot",
    "Grape___Esca_(Black_Measles)",
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)",
    "Grape___healthy",
    "Orange___Haunglongbing_(Citrus_greening)",
    "Peach___Bacterial_spot",
    "Peach___healthy",
    "Pepper,_bell___Bacterial_spot",
    "Pepper,_bell___healthy",
    "Potato___Early_blight",
    "Potato___Late_blight",
    "Potato___healthy",
    "Raspberry___healthy",
    "Soybean___healthy",
    "Squash___Powdery_mildew",
    "Strawberry___Leaf_scorch",
    "Strawberry___healthy",
    "Tomato___Bacterial_spot",
    "Tomato___Early_blight",
    "Tomato___Late_blight",
    "Tomato___Leaf_Mold",
    "Tomato___Septoria_leaf_spot",
    "Tomato___Spider_mites Two-spotted_spider_mite",
    "Tomato___Target_Spot",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus",
    "Tomato___Tomato_mosaic_virus",
    "Tomato___healthy",
]


def download_dataset(handle: str = DATASET_HANDLE) -> Path:
    """Download or retrieve cached dataset via kagglehub."""
    print(f"[DatasetImport] Invoking kagglehub for '{handle}'...")
    raw_path = kagglehub.dataset_download(handle)
    path = Path(raw_path).resolve()
    print(f"Path to dataset files: {path}")
    return path


def locate_splits(root: Path) -> Tuple[Optional[Path], Optional[Path], Optional[Path]]:
    """Recursively search for train, valid/val, and test directories in the downloaded folder."""
    train_dir = None
    valid_dir = None
    test_dir = None

    # Search for directories that contain class folders matching known pathology patterns
    for candidate in root.rglob("*"):
        if not candidate.is_dir():
            continue
        c_name = candidate.name.lower()

        # Check if this folder has subdirectories looking like class folders
        subdirs = [d for d in candidate.iterdir() if d.is_dir()]
        subdir_names = {d.name for d in subdirs}
        has_classes = any(
            cls in subdir_names or "Tomato" in d or "Apple" in d
            for cls in EXPECTED_38_CLASSES
            for d in [cls]
        )

        if has_classes:
            if c_name in ("train", "training") and train_dir is None:
                train_dir = candidate
            elif c_name in ("valid", "val", "validation") and valid_dir is None:
                valid_dir = candidate
            elif c_name in ("test", "testing") and test_dir is None:
                test_dir = candidate

    # If test_dir has no subdirectories (e.g. flat loose test images), check test folder
    if test_dir is not None:
        subdirs = [d for d in test_dir.iterdir() if d.is_dir()]
        if not subdirs:
            # It's a flat folder of test images, not ImageFolder classes
            test_dir = None

    return train_dir, valid_dir, test_dir


def create_directory_link(src: Path, dest: Path) -> bool:
    """Create Windows directory junction or symlink to avoid duplicating gigabytes."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        if dest.is_symlink() or dest.is_dir():
            try:
                dest.rmdir()
            except OSError:
                shutil.rmtree(dest)

    # Try Windows directory junction first (requires no admin privileges on Windows NTFS)
    if os.name == "nt":
        try:
            res = subprocess.run(
                ["cmd", "/c", "mklink", "/J", str(dest), str(src)],
                capture_output=True,
                text=True,
                check=False,
            )
            if res.returncode == 0:
                return True
        except Exception:
            pass

    # Try standard symlink
    try:
        dest.symlink_to(src, target_is_directory=True)
        return True
    except (OSError, NotImplementedError):
        pass

    return False


def materialize_dataset(
    source_root: Path,
    dest_root: Path,
    mode: str = "link",
    val_test_split_ratio: float = 0.5,
) -> Dict[str, any]:
    """Organize raw Kaggle files into Agri Nirvana standard train/val/test splits."""
    dest_root = dest_root.resolve()
    dest_root.mkdir(parents=True, exist_ok=True)

    train_src, valid_src, test_src = locate_splits(source_root)

    if not train_src:
        raise FileNotFoundError(
            f"Could not locate 'train' folder with class subdirectories in {source_root}"
        )
    if not valid_src:
        raise FileNotFoundError(
            f"Could not locate 'valid' folder with class subdirectories in {source_root}"
        )

    print(f"[DatasetImport] Found train source: {train_src}")
    print(f"[DatasetImport] Found valid source: {valid_src}")

    target_train = dest_root / "train"
    target_val = dest_root / "val"
    target_test = dest_root / "test"

    for d in (target_train, target_val, target_test):
        d.mkdir(parents=True, exist_ok=True)

    classes_found = sorted([d.name for d in train_src.iterdir() if d.is_dir()])
    print(f"[DatasetImport] Identified {len(classes_found)} classes in train source.")

    # Link or copy train split
    linked_train = False
    if mode == "link":
        linked_train = create_directory_link(train_src, target_train)

    if not linked_train:
        print("[DatasetImport] Materializing train split by linking/copying classes...")
        for cls_name in classes_found:
            src_cls = train_src / cls_name
            dest_cls = target_train / cls_name
            if mode == "link" and create_directory_link(src_cls, dest_cls):
                continue
            # Fallback copy
            dest_cls.mkdir(parents=True, exist_ok=True)
            for img_file in src_cls.glob("*.*"):
                shutil.copy2(img_file, dest_cls / img_file.name)

    # In Kaggle's new-plant-diseases-dataset:
    # valid_src has ~17,572 images across 38 classes.
    # The Kaggle 'test' folder contains only 33 unlabelled individual images.
    # For a high-accuracy pipeline with real generalization evaluation,
    # split valid_src into balanced 'val' and held-out 'test' splits!
    print(
        f"[DatasetImport] Partitioning validation source into 'val' and held-out 'test' ({1.0 - val_test_split_ratio:.0%} / {val_test_split_ratio:.0%})..."
    )

    val_counts = {}
    test_counts = {}

    for cls_name in classes_found:
        src_cls = valid_src / cls_name
        dest_val_cls = target_val / cls_name
        dest_test_cls = target_test / cls_name
        dest_val_cls.mkdir(parents=True, exist_ok=True)
        dest_test_cls.mkdir(parents=True, exist_ok=True)

        if not src_cls.exists():
            continue

        images = sorted([p for p in src_cls.iterdir() if p.is_file() and p.suffix.lower() in (".jpg", ".jpeg", ".png")])
        cutoff = int(len(images) * (1.0 - val_test_split_ratio))

        val_images = images[:cutoff]
        test_images = images[cutoff:]

        # For val images
        for img in val_images:
            target_img = dest_val_cls / img.name
            if not target_img.exists():
                try:
                    os.link(str(img), str(target_img))  # Hard link if on same drive (instant, 0 disk space)
                except (OSError, AttributeError):
                    shutil.copy2(img, target_img)

        # For test images
        for img in test_images:
            target_img = dest_test_cls / img.name
            if not target_img.exists():
                try:
                    os.link(str(img), str(target_img))  # Hard link if on same drive
                except (OSError, AttributeError):
                    shutil.copy2(img, target_img)

        val_counts[cls_name] = len(val_images)
        test_counts[cls_name] = len(test_images)

    train_total = sum(len(list((target_train / c).glob("*.*"))) for c in classes_found if (target_train / c).is_dir())
    val_total = sum(val_counts.values())
    test_total = sum(test_counts.values())

    metadata = {
        "dataset_name": DATASET_HANDLE,
        "source_cache_path": str(source_root),
        "target_path": str(dest_root),
        "num_classes": len(classes_found),
        "classes": classes_found,
        "classes_match_agri_nirvana": set(classes_found) == set(EXPECTED_38_CLASSES),
        "train_samples": train_total,
        "val_samples": val_total,
        "test_samples": test_total,
        "total_samples": train_total + val_total + test_total,
    }

    meta_file = dest_root / "dataset_info.json"
    with open(meta_file, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print("\n" + "=" * 60)
    print("AGRI NIRVANA DATASET INGESTION COMPLETE")
    print("=" * 60)
    print(f"Dataset root:       {dest_root}")
    print(f"Total Classes:      {len(classes_found)} / 38 expected")
    print(f"Train Images:       {train_total:,}")
    print(f"Validation Images:  {val_total:,}")
    print(f"Held-out Test:      {test_total:,}")
    print(f"Total Images:       {metadata['total_samples']:,}")
    print(f"Metadata saved to:  {meta_file}")
    print("=" * 60 + "\n")

    return metadata


def main():
    parser = argparse.ArgumentParser(
        description="Download and import Kaggle's vipoooool/new-plant-diseases-dataset for Agri Nirvana"
    )
    parser.add_argument(
        "--dest",
        default="backend/ml/datasets/plant_disease",
        help="Target destination directory in Agri Nirvana",
    )
    parser.add_argument(
        "--mode",
        choices=["link", "copy"],
        default="link",
        help="Fast junction/link mode (preserves disk space) or full copy",
    )
    parser.add_argument(
        "--cached-path",
        default=None,
        help="Skip download and use an existing folder path if already downloaded",
    )
    args = parser.parse_args()

    # Step 1: Download or retrieve dataset via kagglehub
    if args.cached_path and Path(args.cached_path).exists():
        raw_path = Path(args.cached_path).resolve()
        print(f"[DatasetImport] Using provided local path: {raw_path}")
    else:
        raw_path = download_dataset(DATASET_HANDLE)

    # Step 2: Ingest and structure splits for Agri Nirvana
    dest_path = Path(args.dest)
    meta = materialize_dataset(raw_path, dest_path, mode=args.mode)
    print(f"Import finished successfully. Ready for training with:")
    print(f"  python -m backend.ml.training.train_pipeline --data {dest_path}")


if __name__ == "__main__":
    main()
