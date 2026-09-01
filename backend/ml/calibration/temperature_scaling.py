"""Temperature Scaling & Model Confidence Calibration for Agri Nirvana.

Provides post-hoc calibration via temperature scaling:
    p_i = exp(z_i / T) / sum_j exp(z_j / T)

Minimizes Negative Log-Likelihood (NLL) and calculates Expected Calibration Error (ECE)
to ensure output probabilities reflect true empirical accuracy.
"""

import json
import math
import os
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
import numpy as np


class ModelCalibrator:
    """Manages versioned temperature scaling calibration artifacts."""

    def __init__(self, artifact_path: Optional[str] = None):
        self.artifact_path = artifact_path or os.path.join(
            os.path.dirname(__file__), "calibration_v1.json"
        )
        self.temperature: float = 1.0
        self.is_calibrated: bool = False
        self.metadata: Dict[str, Any] = {}
        self.load_calibration()

    def load_calibration(self) -> bool:
        """Load versioned calibration parameters from JSON artifact."""
        if not os.path.exists(self.artifact_path):
            self.temperature = 1.0
            self.is_calibrated = False
            return False

        try:
            with open(self.artifact_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.temperature = float(data.get("temperature", 1.0))
            self.is_calibrated = bool(data.get("calibrated", False))
            self.metadata = data
            return self.is_calibrated
        except Exception as e:
            print(f"[ModelCalibrator] Error loading calibration artifact: {e}")
            self.temperature = 1.0
            self.is_calibrated = False
            return False

    def scale_probabilities(self, logits: np.ndarray) -> np.ndarray:
        """Apply temperature scaling to raw logits and return calibrated probabilities."""
        if not self.is_calibrated or self.temperature <= 0:
            # Standard uncalibrated softmax
            exp_z = np.exp(logits - np.max(logits))
            return exp_z / np.sum(exp_z)

        scaled_z = logits / self.temperature
        exp_scaled = np.exp(scaled_z - np.max(scaled_z))
        return exp_scaled / np.sum(exp_scaled)

    @staticmethod
    def calculate_ece(probs: np.ndarray, labels: np.ndarray, n_bins: int = 10) -> float:
        """Calculate Expected Calibration Error (ECE) across confidence bins.

        Args:
            probs: (N, C) probability array or (N,) top-1 confidence array
            labels: (N,) true class indices
        """
        if probs.ndim == 2:
            confidences = np.max(probs, axis=1)
            predictions = np.argmax(probs, axis=1)
        else:
            confidences = probs
            predictions = labels

        accuracies = (predictions == labels).astype(float)
        bin_boundaries = np.linspace(0.0, 1.0, n_bins + 1)
        ece = 0.0
        total_samples = len(labels)

        if total_samples == 0:
            return 0.0

        for i in range(n_bins):
            bin_lower = bin_boundaries[i]
            bin_upper = bin_boundaries[i + 1]
            in_bin = (confidences > bin_lower) & (confidences <= bin_upper)
            bin_size = np.sum(in_bin)

            if bin_size > 0:
                bin_acc = np.mean(accuracies[in_bin])
                bin_conf = np.mean(confidences[in_bin])
                ece += (bin_size / total_samples) * abs(bin_acc - bin_conf)

        return float(ece)

    def fit_temperature(
        self,
        val_logits: np.ndarray,
        val_labels: np.ndarray,
        lr: float = 0.01,
        max_iter: int = 150
    ) -> Dict[str, Any]:
        """Fit optimal temperature on held-out validation set logits using gradient descent."""
        N, C = val_logits.shape
        T = 1.5  # Initial temperature guess

        uncalibrated_probs = np.zeros_like(val_logits)
        for i in range(N):
            ez = np.exp(val_logits[i] - np.max(val_logits[i]))
            uncalibrated_probs[i] = ez / np.sum(ez)

        ece_before = self.calculate_ece(uncalibrated_probs, val_labels)

        # Simple 1D line search / gradient descent to minimize NLL
        best_t = T
        best_nll = float("inf")

        for candidate_t in np.linspace(0.5, 3.5, 60):
            scaled = val_logits / candidate_t
            # Stable log-softmax
            log_sum_exp = np.max(scaled, axis=1, keepdims=True) + np.log(
                np.sum(np.exp(scaled - np.max(scaled, axis=1, keepdims=True)), axis=1, keepdims=True)
            )
            log_probs = scaled - log_sum_exp
            nll = -np.mean(log_probs[np.arange(N), val_labels])

            if nll < best_nll:
                best_nll = nll
                best_t = candidate_t

        self.temperature = float(round(best_t, 3))
        self.is_calibrated = True

        calibrated_probs = np.zeros_like(val_logits)
        for i in range(N):
            scaled_z = val_logits[i] / self.temperature
            ez = np.exp(scaled_z - np.max(scaled_z))
            calibrated_probs[i] = ez / np.sum(ez)

        ece_after = self.calculate_ece(calibrated_probs, val_labels)

        result = {
            "version": "v1.0-temperature-scaling",
            "calibrated": True,
            "temperature": self.temperature,
            "ece_before": round(ece_before, 4),
            "ece_after": round(ece_after, 4),
            "validation_samples": int(N),
            "validation_classes": int(C),
            "timestamp": "2026-09-01T23:00:00Z"
        }

        # Save versioned artifact
        os.makedirs(os.path.dirname(self.artifact_path), exist_ok=True)
        with open(self.artifact_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)

        self.metadata = result
        return result


calibrator = ModelCalibrator()
