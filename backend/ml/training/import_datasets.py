"""
Dataset discovery and import utilities for Agri Nirvana.
This script provides a safe scaffold to discover/download datasets from Hugging Face and Kaggle,
create manifest files and store provenance metadata.

It intentionally does NOT automatically download large datasets unless valid credentials are
present as environment variables. Use --download to perform real downloads when ready.

Usage examples:
  python import_datasets.py --list-hf "plantvillage"     # query HF for dataset metadata
  python import_datasets.py --download-hf "plant_village" --out data/raw/plantvillage
  python import_datasets.py --manifest --out data/manifests

"""

import os
import sys
import json
import hashlib
import argparse
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

HF_TOKEN = os.environ.get("HF_TOKEN")
KAGGLE_USER = os.environ.get("KAGGLE_USERNAME")
KAGGLE_KEY = os.environ.get("KAGGLE_KEY")


def write_manifest(out_path: str, manifest: dict):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    logger.info(f"Wrote manifest: {out_path}")


def compute_file_sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 64), b""):
            h.update(chunk)
    return h.hexdigest()


def query_huggingface_dataset(dataset_name: str) -> dict:
    """Query Hugging Face datasets API for basic metadata. Requires HF_TOKEN to fetch private info.
    Falls back to unauthenticated public metadata when token is missing.
    """
    try:
        from huggingface_hub import hf_hub_url, HfApi
        api = HfApi()
        meta = api.dataset_info(dataset_name)
        return {
            "id": dataset_name,
            "cardData": getattr(meta, "cardData", None),
            "size": getattr(meta, "size_in_bytes", None),
            "splits": [s.name for s in meta.splits] if getattr(meta, "splits", None) else None,
            "downloadUrl": None,
        }
    except Exception as e:
        logger.warning("huggingface_hub unavailable or query failed: %s", e)
        return {"id": dataset_name, "note": "Could not query HF metadata locally"}


def download_hf_dataset(dataset_name: str, out_dir: str) -> dict:
    if not HF_TOKEN:
        raise RuntimeError("HF_TOKEN not set in environment; cannot download Hugging Face datasets")
    try:
        # Prefer using the huggingface_hub datasets API if available
        from huggingface_hub import snapshot_download
        os.makedirs(out_dir, exist_ok=True)
        path = snapshot_download(repo_id=dataset_name, cache_dir=out_dir, token=HF_TOKEN)
        manifest = {"source": "huggingface", "id": dataset_name, "downloaded_at": datetime.utcnow().isoformat(), "path": path}
        return manifest
    except Exception as e:
        logger.exception("Failed to download HF dataset: %s", e)
        raise


def download_kaggle_dataset(dataset_ref: str, out_dir: str) -> dict:
    if not (KAGGLE_USER and KAGGLE_KEY):
        raise RuntimeError("KAGGLE_USERNAME / KAGGLE_KEY not set; cannot download Kaggle datasets")
    try:
        # Use the kaggle CLI if available in the runner
        import subprocess
        os.makedirs(out_dir, exist_ok=True)
        cmd = ["kaggle", "datasets", "download", "-d", dataset_ref, "-p", out_dir, "--unzip"]
        subprocess.check_call(cmd)
        manifest = {"source": "kaggle", "id": dataset_ref, "downloaded_at": datetime.utcnow().isoformat(), "path": out_dir}
        return manifest
    except Exception as e:
        logger.exception("Failed to download Kaggle dataset: %s", e)
        raise


def create_dataset_manifest_for_folder(folder: str, out_manifest: str):
    """Create a lightweight manifest for a local ImageFolder-style dataset.
    Collects class counts, file counts and sample SHA256 for provenance.
    """
    classes = {}
    total_files = 0
    for root, _, files in os.walk(folder):
        for f in files:
            if f.lower().endswith(('.jpg', '.jpeg', '.png')):
                total_files += 1
                rel = os.path.relpath(os.path.join(root, f), folder)
                parts = rel.split(os.sep)
                if len(parts) >= 2:
                    cls = parts[0]
                else:
                    cls = "unknown"
                classes.setdefault(cls, 0)
                classes[cls] += 1
    manifest = {
        "dataset_root": folder,
        "generated_at": datetime.utcnow().isoformat(),
        "total_files": total_files,
        "classes": classes,
    }
    write_manifest(out_manifest, manifest)
    return manifest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--list-hf", help="Query HF dataset metadata by name", default=None)
    parser.add_argument("--download-hf", help="Download HF dataset by id", default=None)
    parser.add_argument("--download-kaggle", help="Download Kaggle dataset by ref (owner/dataset)", default=None)
    parser.add_argument("--out", help="Output directory or manifest path", default="data")
    parser.add_argument("--manifest", action="store_true", help="Create manifest for local folder specified by --out")
    args = parser.parse_args()

    if args.list_hf:
        info = query_huggingface_dataset(args.list_hf)
        logger.info(json.dumps(info, indent=2, ensure_ascii=False))
        return

    if args.download_hf:
        if not HF_TOKEN:
            logger.error("HF_TOKEN not found; set HF_TOKEN to download"); sys.exit(2)
        manifest = download_hf_dataset(args.download_hf, args.out)
        write_manifest(os.path.join(args.out, "manifest.hf.json"), manifest)
        return

    if args.download_kaggle:
        if not (KAGGLE_USER and KAGGLE_KEY):
            logger.error("Kaggle credentials not found; set KAGGLE_USERNAME and KAGGLE_KEY"); sys.exit(2)
        manifest = download_kaggle_dataset(args.download_kaggle, args.out)
        write_manifest(os.path.join(args.out, "manifest.kaggle.json"), manifest)
        return

    if args.manifest:
        folder = args.out
        if not os.path.exists(folder):
            logger.error("Folder %s does not exist", folder); sys.exit(2)
        out_manifest = os.path.join(folder, "dataset_manifest.json")
        m = create_dataset_manifest_for_folder(folder, out_manifest)
        logger.info(json.dumps(m, indent=2))
        return

    parser.print_help()


if __name__ == "__main__":
    main()
