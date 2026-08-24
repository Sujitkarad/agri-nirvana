"""
Severity Estimator via HSV Color Segmentation.

Estimates leaf disease severity by analyzing the ratio of
damaged (brown/yellow/necrotic) tissue vs. healthy green tissue
using HSV color space thresholding.

Falls back to confidence-band severity if color analysis is unreliable
(e.g., image has too little green, or is a non-standard leaf color).
"""

import numpy as np
from PIL import Image
from typing import Dict, Tuple

try:
    import cv2
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False


def _estimate_via_hsv(image_np: np.ndarray) -> Tuple[str, float, bool]:
    """
    Estimate leaf damage percentage using HSV color segmentation.

    Segments the image into:
    - Healthy green tissue (H: 25-90, S: 30-255, V: 30-255)
    - Necrotic brown/yellow tissue (H: 5-25, S: 30-255, V: 30-200)
    - Dead/dry brown tissue (H: 0-20, S: 20-180, V: 20-160)

    Returns:
        (severity_label, affected_percentage, is_reliable)
    """
    if not HAS_CV2:
        return "moderate", 30.0, False

    hsv = cv2.cvtColor(image_np, cv2.COLOR_RGB2HSV)

    # ── Green / Healthy tissue mask ──
    green_lower = np.array([25, 30, 30])
    green_upper = np.array([90, 255, 255])
    green_mask = cv2.inRange(hsv, green_lower, green_upper)

    # ── Yellow / Early damage mask ──
    yellow_lower = np.array([15, 30, 50])
    yellow_upper = np.array([30, 255, 240])
    yellow_mask = cv2.inRange(hsv, yellow_lower, yellow_upper)

    # ── Brown / Necrotic tissue mask ──
    brown_lower1 = np.array([0, 30, 20])
    brown_upper1 = np.array([18, 200, 180])
    brown_mask1 = cv2.inRange(hsv, brown_lower1, brown_upper1)

    brown_lower2 = np.array([160, 30, 20])
    brown_upper2 = np.array([180, 200, 180])
    brown_mask2 = cv2.inRange(hsv, brown_lower2, brown_upper2)

    brown_mask = cv2.bitwise_or(brown_mask1, brown_mask2)

    # ── Dark spots / severe necrosis ──
    dark_lower = np.array([0, 0, 0])
    dark_upper = np.array([180, 255, 30])
    dark_mask = cv2.inRange(hsv, dark_lower, dark_upper)

    # Pixel counts
    total_pixels = image_np.shape[0] * image_np.shape[1]
    green_pixels = int(np.sum(green_mask > 0))
    damaged_pixels = int(np.sum(yellow_mask > 0)) + int(np.sum(brown_mask > 0))
    dark_pixels = int(np.sum(dark_mask > 0))

    # Calculate leaf-relevant pixels (exclude pure background)
    leaf_pixels = green_pixels + damaged_pixels
    if leaf_pixels < total_pixels * 0.05:
        # Less than 5% of image is leaf-like — unreliable
        return "moderate", 30.0, False

    # Affected percentage = damaged / (damaged + healthy)
    if leaf_pixels > 0:
        affected_pct = (damaged_pixels / leaf_pixels) * 100.0
    else:
        affected_pct = 0.0

    # Clamp to reasonable range
    affected_pct = max(0.0, min(100.0, affected_pct))

    # Classify severity
    if affected_pct < 15.0:
        severity = "early"
    elif affected_pct < 40.0:
        severity = "moderate"
    else:
        severity = "severe"

    return severity, round(affected_pct, 1), True


def _estimate_via_confidence(confidence: float) -> Tuple[str, float]:
    """
    Fallback severity estimation based on model confidence bands.

    Higher confidence in a disease class often correlates with more
    visually obvious (= more severe) symptoms.
    """
    if confidence >= 0.90:
        return "severe", 55.0
    elif confidence >= 0.70:
        return "moderate", 35.0
    else:
        return "early", 15.0


def estimate_severity(
    pil_image: Image.Image,
    model_confidence: float = 0.5,
    is_healthy: bool = False
) -> Dict:
    """
    Estimate disease severity from leaf image.

    Attempts HSV color segmentation first. Falls back to
    confidence-band estimation if segmentation is unreliable.

    Args:
        pil_image: PIL Image (RGB)
        model_confidence: Disease model's confidence score (0-1)
        is_healthy: Whether the model predicted "healthy"

    Returns:
        Dict with:
            - severity: "early" | "moderate" | "severe"
            - severity_percentage: float (0-100)
            - estimation_method: "hsv_segmentation" | "confidence_band"
    """
    if is_healthy:
        return {
            "severity": "healthy",
            "severity_percentage": 0.0,
            "estimation_method": "classification"
        }

    image_np = np.array(pil_image)

    # Try HSV segmentation first
    severity, pct, is_reliable = _estimate_via_hsv(image_np)

    if is_reliable:
        return {
            "severity": severity,
            "severity_percentage": pct,
            "estimation_method": "hsv_segmentation"
        }

    # Fallback to confidence bands
    severity, pct = _estimate_via_confidence(model_confidence)
    return {
        "severity": severity,
        "severity_percentage": pct,
        "estimation_method": "confidence_band"
    }
