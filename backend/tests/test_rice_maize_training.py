"""Unit tests for Rice & Maize dataset ingestion and PyTorch model artifact."""

import json
from pathlib import Path
import unittest
import torch
from backend.ml.training.train_rice_and_maize import create_model

WEIGHTS_PATH = Path("backend/ml/models/weights/rice_and_maize_classifier.pt")
METADATA_PATH = Path("backend/ml/models/weights/rice_and_maize_classifier.json")
DATASET_PATH = Path("backend/ml/datasets/rice_and_maize")


class TestRiceMaizeModel(unittest.TestCase):
    def test_checkpoint_exists(self):
        """Verify the trained PyTorch checkpoint file exists and is non-empty."""
        self.assertTrue(WEIGHTS_PATH.is_file(), f"Model checkpoint missing at {WEIGHTS_PATH}")
        self.assertGreater(WEIGHTS_PATH.stat().st_size, 1_000_000, "Checkpoint is unusually small")

    def test_metadata_summary(self):
        """Verify the JSON metadata artifact contains the 17 classes and metrics."""
        self.assertTrue(METADATA_PATH.is_file(), f"Metadata JSON missing at {METADATA_PATH}")
        with open(METADATA_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertEqual(data["num_classes"], 17)
        self.assertEqual(len(data["classes"]), 17)
        self.assertIn("Maize___healthy", data["classes"])
        self.assertIn("Rice___healthy", data["classes"])
        self.assertIn("Rice___bacterial_leaf_blight", data["classes"])
        self.assertIn("Maize___fall_armyworm", data["classes"])

        # Validate metrics
        self.assertGreater(data["metrics"]["test"]["test_accuracy"], 60.0)
        self.assertGreater(data["metrics"]["test"]["test_macro_f1"], 60.0)

    def test_model_inference_dry_run(self):
        """Load checkpoint into PyTorch and perform dry-run inference on dummy input."""
        checkpoint = torch.load(str(WEIGHTS_PATH), map_location="cpu")
        self.assertIn("model_state_dict", checkpoint)

        model = create_model(checkpoint["num_classes"])
        model.load_state_dict(checkpoint["model_state_dict"])
        model.eval()

        dummy_batch = torch.randn(2, 3, 224, 224)
        with torch.no_grad():
            outputs = model(dummy_batch)

        self.assertEqual(outputs.shape, (2, 17))
        probs = torch.softmax(outputs, dim=-1)
        self.assertAlmostEqual(probs[0].sum().item(), 1.0, places=4)


if __name__ == "__main__":
    unittest.main()
