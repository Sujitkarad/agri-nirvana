"""Tests for the Rice & Maize classifier and optional trained artifacts.

The trained checkpoint and metrics JSON are intentionally excluded from Git.
Set REQUIRE_TRAINED_MODEL_ARTIFACTS=1 in a release/deployment job to make the
artifact-presence checks mandatory; ordinary CI still tests model architecture
without downloading pretrained weights or fabricating trained artifacts.
"""

import json
import os
from pathlib import Path
import unittest

import torch

from backend.ml.training.train_rice_and_maize import create_model

WEIGHTS_PATH = Path("backend/ml/models/weights/rice_and_maize_classifier.pt")
METADATA_PATH = Path("backend/ml/models/weights/rice_and_maize_classifier.json")
REQUIRE_ARTIFACTS = os.getenv("REQUIRE_TRAINED_MODEL_ARTIFACTS", "").strip().lower() in {
    "1", "true", "yes"
}


class TestRiceMaizeModel(unittest.TestCase):
    def _require_artifact(self, path: Path) -> None:
        if path.is_file():
            return
        message = (
            f"Required model artifact missing: {path}. "
            "Publish the trained artifact before running the release validation job."
        )
        if REQUIRE_ARTIFACTS:
            self.fail(message)
        self.skipTest(
            f"{message} Artifact checks are optional in general CI; set "
            "REQUIRE_TRAINED_MODEL_ARTIFACTS=1 to require them."
        )

    def test_model_architecture_inference_dry_run(self):
        """Exercise the 17-class architecture without network or trained weights."""
        model = create_model(num_classes=17, pretrained=False)
        model.eval()

        dummy_batch = torch.randn(2, 3, 224, 224)
        with torch.no_grad():
            outputs = model(dummy_batch)

        self.assertEqual(tuple(outputs.shape), (2, 17))
        probabilities = torch.softmax(outputs, dim=-1)
        self.assertTrue(torch.isfinite(probabilities).all().item())
        self.assertTrue(torch.allclose(
            probabilities.sum(dim=-1),
            torch.ones(2),
            atol=1e-5,
        ))

    def test_checkpoint_exists(self):
        """Validate checkpoint presence/size when a trained artifact is supplied."""
        self._require_artifact(WEIGHTS_PATH)
        self.assertGreater(
            WEIGHTS_PATH.stat().st_size,
            1_000_000,
            "Checkpoint is unusually small",
        )

    def test_metadata_summary(self):
        """Validate the 17-class metadata and reported held-out metrics."""
        self._require_artifact(METADATA_PATH)
        with METADATA_PATH.open("r", encoding="utf-8") as file:
            data = json.load(file)

        self.assertEqual(data["num_classes"], 17)
        self.assertEqual(len(data["classes"]), 17)
        self.assertIn("Maize___healthy", data["classes"])
        self.assertIn("Rice___healthy", data["classes"])
        self.assertIn("Rice___bacterial_leaf_blight", data["classes"])
        self.assertIn("Maize___fall_armyworm", data["classes"])
        self.assertGreater(data["metrics"]["test"]["test_accuracy"], 60.0)
        self.assertGreater(data["metrics"]["test"]["test_macro_f1"], 60.0)

    def test_trained_checkpoint_inference(self):
        """Load and exercise the actual trained checkpoint when provided."""
        self._require_artifact(WEIGHTS_PATH)
        checkpoint = torch.load(str(WEIGHTS_PATH), map_location="cpu", weights_only=True)
        self.assertIn("model_state_dict", checkpoint)
        self.assertEqual(checkpoint["num_classes"], 17)

        model = create_model(checkpoint["num_classes"], pretrained=False)
        model.load_state_dict(checkpoint["model_state_dict"])
        model.eval()

        with torch.no_grad():
            outputs = model(torch.randn(2, 3, 224, 224))

        self.assertEqual(tuple(outputs.shape), (2, 17))
        probabilities = torch.softmax(outputs, dim=-1)
        self.assertTrue(torch.allclose(
            probabilities.sum(dim=-1),
            torch.ones(2),
            atol=1e-5,
        ))


if __name__ == "__main__":
    unittest.main()
