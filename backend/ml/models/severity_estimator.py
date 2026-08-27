"""Image-based severity estimation with explicit reliability provenance.

Severity is an image-derived estimate, not a clinical/agronomic ground truth.
The estimator never fabricates a percentage when segmentation is unavailable.
"""

import numpy as np
from PIL import Image
from typing import Dict, Tuple

try:
    import cv2
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False


def _estimate_via_hsv(image_np: np.ndarray) -> Tuple[str, float, bool, str]:
    if not HAS_CV2:
        return "unknown", 0.0, False, "OpenCV is unavailable; pixel segmentation could not be performed."

    hsv = cv2.cvtColor(image_np, cv2.COLOR_RGB2HSV)
    green_mask = cv2.inRange(hsv, np.array([25, 30, 30]), np.array([90, 255, 255]))
    yellow_mask = cv2.inRange(hsv, np.array([15, 30, 50]), np.array([35, 255, 240]))
    brown_mask1 = cv2.inRange(hsv, np.array([0, 30, 20]), np.array([18, 200, 180]))
    brown_mask2 = cv2.inRange(hsv, np.array([160, 30, 20]), np.array([180, 200, 180]))
    brown_mask = cv2.bitwise_or(brown_mask1, brown_mask2)

    total_pixels = image_np.shape[0] * image_np.shape[1]
    green_pixels = int(np.sum(green_mask > 0))
    damaged_pixels = int(np.sum(yellow_mask > 0)) + int(np.sum(brown_mask > 0))
    leaf_pixels = green_pixels + damaged_pixels

    if total_pixels == 0 or leaf_pixels < total_pixels * 0.05:
        return "unknown", 0.0, False, "Too little leaf-like tissue was segmented for a reliable severity estimate."

    affected_pct = max(0.0, min(100.0, (damaged_pixels / leaf_pixels) * 100.0))
    if affected_pct < 15.0:
        severity = "early"
    elif affected_pct < 40.0:
        severity = "moderate"
    else:
        severity = "severe"
    return severity, round(affected_pct, 1), True, "HSV green/damaged tissue segmentation."


def estimate_severity(pil_image: Image.Image, model_confidence: float = 0.5, is_healthy: bool = False) -> Dict:
    """Return severity plus provenance; never use disease confidence as severity."""
    if is_healthy:
        return {
            "severity": "healthy",
            "severity_percentage": 0.0,
            "estimation_method": "classification",
            "reliable": True,
            "confidence_basis": "classifier healthy state",
        }

    if pil_image is None:
        return {
            "severity": "unknown", "severity_percentage": 0.0,
            "estimation_method": "unavailable", "reliable": False,
            "confidence_basis": "no image",
        }

    image_np = np.array(pil_image.convert("RGB"))
    severity, pct, reliable, reason = _estimate_via_hsv(image_np)
    if reliable:
        return {
            "severity": severity,
            "severity_percentage": pct,
            "estimation_method": "hsv_segmentation",
            "reliable": True,
            "confidence_basis": reason,
        }

    # Never convert classifier confidence into a fake damage percentage.
    return {
        "severity": "unknown",
        "severity_percentage": 0.0,
        "estimation_method": "unavailable",
        "reliable": False,
        "confidence_basis": reason,
    }
