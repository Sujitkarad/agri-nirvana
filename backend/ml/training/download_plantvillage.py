"""Download PlantVillage from Hugging Face and materialize ImageFolder splits.

Usage:
    python -m backend.ml.training.download_plantvillage \
      --output backend/ml/datasets/plant_disease

The dataset provides 38 crop/disease classes. It is useful for pretraining,
but it is not a substitute for a field-image test set.
"""
from __future__ import annotations

import argparse
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="backend/ml/datasets/plant_disease")
    parser.add_argument("--max-per-class", type=int, default=0,
                        help="Optional cap for quick experiments; 0 keeps all images")
    args = parser.parse_args()

    from datasets import load_dataset

    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    print("Downloading PlantVillage color images from Hugging Face...")
    ds = load_dataset("mohanty/PlantVillage", "color")

    # Preserve the dataset's official train/test split. Create validation from
    # train so test remains untouched for final evaluation.
    train = ds["train"]
    test = ds["test"]
    rng = train.shuffle(seed=42)
    n_val = max(1, int(len(rng) * 0.15))
    val = rng.select(range(n_val))
    train = rng.select(range(n_val, len(rng)))

    def write_split(split, name: str) -> None:
        counts = {}
        for row in split:
            label = row["label"]
            class_name = split.features["label"].int2str(label)
            limit = args.max_per_class
            if limit and counts.get(class_name, 0) >= limit:
                continue
            image = row["image"].convert("RGB")
            idx = counts.get(class_name, 0)
            dest = out / name / class_name
            dest.mkdir(parents=True, exist_ok=True)
            image.save(dest / f"{idx:06d}.jpg", quality=95)
            counts[class_name] = idx + 1
        print(f"{name}: {sum(counts.values())} images across {len(counts)} classes")

    write_split(train, "train")
    write_split(val, "val")
    write_split(test, "test")
    print(f"Dataset ready at: {out}")


if __name__ == "__main__":
    main()
