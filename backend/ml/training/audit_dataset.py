"""
Dataset audit utilities: deduplication, leakage checks, manifest validation.
Generates a DATASET_AUDIT_REPORT.md in the dataset manifest folder describing duplicates,
class imbalance, and simple leakage checks based on filename or provided metadata grouping.

Usage:
  python audit_dataset.py --dataset /path/to/imagefolder --out report_folder

Exits with code 0 when audit passes light checks, non-zero when failures found (leakage or empty).
"""

import os
import sys
import json
import argparse
import logging
from collections import defaultdict
from datetime import datetime

try:
    from PIL import Image
except Exception:
    Image = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def sha256_file(path: str) -> str:
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024*64), b""):
            h.update(chunk)
    return h.hexdigest()


def simple_image_hash(path: str):
    # Use PIL to compute a very simple perceptual hash (avg hash) if available
    try:
        if Image is None:
            return None
        im = Image.open(path).convert('L').resize((8,8), Image.BILINEAR)
        pixels = list(im.getdata())
        avg = sum(pixels)/len(pixels)
        bits = ''.join('1' if p>avg else '0' for p in pixels)
        return hex(int(bits,2))
    except Exception:
        return None


def scan_dataset(root: str):
    # Walk dataset and collect file info
    info = []
    for dirpath, _, files in os.walk(root):
        for f in files:
            if f.lower().endswith(('.jpg','.jpeg','.png')):
                p = os.path.join(dirpath, f)
                rel = os.path.relpath(p, root)
                parts = rel.split(os.sep)
                cls = parts[0] if len(parts)>1 else 'unknown'
                info.append({'path': p, 'rel': rel, 'class': cls})
    return info


def find_duplicates(files):
    by_sha = defaultdict(list)
    by_phash = defaultdict(list)
    for it in files:
        p = it['path']
        try:
            s = sha256_file(p)
            by_sha[s].append(it)
        except Exception:
            continue
        ph = simple_image_hash(p)
        if ph:
            by_phash[ph].append(it)
    exact_dups = {k:v for k,v in by_sha.items() if len(v)>1}
    ph_dups = {k:v for k,v in by_phash.items() if len(v)>1}
    return exact_dups, ph_dups


def class_distribution(files):
    from collections import Counter
    cnt = Counter([f['class'] for f in files])
    total = sum(cnt.values())
    return dict(cnt), total


def basic_leakage_check(files):
    # Simple heuristic: detect identical filenames across train/val/test splits
    groups = defaultdict(list)
    for f in files:
        fname = os.path.basename(f['path']).lower()
        groups[fname].append(f['rel'])
    collisions = {k:v for k,v in groups.items() if len(v)>1}
    return collisions


def write_report(out_dir, report):
    os.makedirs(out_dir, exist_ok=True)
    md = []
    md.append(f"# Dataset Audit Report\nGenerated: {datetime.utcnow().isoformat()}\n")
    md.append(f"## Summary\n- root: {report['root']}\n- total_files: {report['total_files']}\n- classes: {len(report['classes'])}\n")
    md.append("## Class distribution\n")
    for cls, c in report['classes'].items():
        md.append(f"- {cls}: {c}\n")
    md.append("\n## Exact duplicates (SHA256)\n")
    if report['exact_duplicates']:
        for k, v in report['exact_duplicates'].items():
            md.append(f"- SHA {k}:\n")
            for it in v[:10]:
                md.append(f"  - {it['rel']}\n")
    else:
        md.append("- None found\n")
    md.append("\n## Perceptual duplicates (approx)\n")
    if report['phash_duplicates']:
        for k, v in report['phash_duplicates'].items():
            md.append(f"- pHash {k}:\n")
            for it in v[:10]:
                md.append(f"  - {it['rel']}\n")
    else:
        md.append("- None found\n")
    md.append("\n## Filename collisions across splits (possible leakage)\n")
    if report['filename_collisions']:
        for k, v in report['filename_collisions'].items():
            md.append(f"- {k}: appears in {len(v)} locations\n")
            for loc in v[:6]:
                md.append(f"  - {loc}\n")
    else:
        md.append("- None found\n")

    with open(os.path.join(out_dir, 'DATASET_AUDIT_REPORT.md'), 'w', encoding='utf-8') as f:
        f.writelines(md)
    with open(os.path.join(out_dir, 'dataset_audit.json'), 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    logger.info("Wrote audit report to %s", out_dir)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset', required=True, help='Path to dataset (ImageFolder layout)')
    parser.add_argument('--out', default=None, help='Output folder for report (defaults to dataset folder)')
    parser.add_argument('--fail-on-leakage', action='store_true', help='Exit non-zero if filename collisions detected')
    args = parser.parse_args()

    root = args.dataset
    if not os.path.exists(root):
        logger.error('Dataset root does not exist: %s', root); sys.exit(2)

    files = scan_dataset(root)
    if not files:
        logger.error('No image files found under %s', root); sys.exit(3)

    exact_dups, ph_dups = find_duplicates(files)
    dist, total = class_distribution(files)
    collisions = basic_leakage_check(files)

    report = {
        'root': root,
        'total_files': total,
        'classes': dist,
        'exact_duplicates': {k:[{'rel':x['rel'],'path':x['path']} for x in v] for k,v in exact_dups.items()},
        'phash_duplicates': {k:[{'rel':x['rel'],'path':x['path']} for x in v] for k,v in ph_dups.items()},
        'filename_collisions': collisions
    }

    out = args.out or root
    write_report(out, report)

    if args.fail_on_leakage and collisions:
        logger.error('Leakage collisions detected; failing as requested')
        sys.exit(4)

    logger.info('Dataset audit completed successfully')
    sys.exit(0)

if __name__ == '__main__':
    main()
