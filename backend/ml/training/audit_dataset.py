"""Fail-fast audit for ImageFolder train/val/test datasets.

Checks class-map consistency, empty splits, minimum support, and exact image
hash collisions across splits. Exact duplicates across train/val/test are a
hard failure because they invalidate held-out evaluation.
"""

from __future__ import annotations

import argparse
import hashlib
from collections import defaultdict
from pathlib import Path

VALID_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


def image_files(root: Path):
    return sorted(p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in VALID_EXTENSIONS)


def audit(root: Path, min_per_class: int = 5) -> dict:
    splits = {name: root / name for name in ("train", "val", "test")}
    if not all(p.is_dir() for p in splits.values()):
        raise ValueError("Dataset must contain train/, val/ and test/ directories")

    class_sets = {}
    counts = {}
    hashes = defaultdict(list)
    for split, path in splits.items():
        classes = sorted(p.name for p in path.iterdir() if p.is_dir())
        if not classes:
            raise ValueError(f"{split} has no class directories")
        class_sets[split] = classes
        counts[split] = {}
        for cls in classes:
            files = image_files(path / cls)
            counts[split][cls] = len(files)
            if len(files) < min_per_class:
                raise ValueError(f"{split}/{cls} has only {len(files)} images; minimum is {min_per_class}")
            for file in files:
                digest = hashlib.sha256(file.read_bytes()).hexdigest()
                hashes[digest].append((split, cls, str(file)))

    if not (class_sets["train"] == class_sets["val"] == class_sets["test"]):
        raise ValueError(f"Class mappings differ between splits: {class_sets}")

    cross_split_duplicates = [items for items in hashes.values() if len({x[0] for x in items}) > 1]
    if cross_split_duplicates:
        examples = cross_split_duplicates[:5]
        raise ValueError(f"Found {len(cross_split_duplicates)} exact duplicate image hashes across splits; examples={examples}")

    total = {split: sum(values.values()) for split, values in counts.items()}
    return {"classes": class_sets["train"], "counts": counts, "totals": total, "exact_duplicate_groups": 0}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True)
    parser.add_argument("--min-per-class", type=int, default=5)
    args = parser.parse_args()
    result = audit(Path(args.data), args.min_per_class)
    print("Dataset audit passed")
    print(f"Classes: {len(result['classes'])}")
    print(f"Totals: {result['totals']}")


if __name__ == "__main__":
    main()
