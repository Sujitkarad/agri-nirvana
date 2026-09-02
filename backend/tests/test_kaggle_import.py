"""Unit test for Kaggle plant disease dataset import pipeline."""
import unittest
from pathlib import Path
from backend.ml.models.disease_classifier import PLANTVILLAGE_CLASSES
from backend.ml.training.import_kaggle_dataset import EXPECTED_38_CLASSES, DATASET_HANDLE


class TestKaggleDatasetImport(unittest.TestCase):
    def test_kagglehub_installed(self):
        import kagglehub
        self.assertIsNotNone(kagglehub.__version__)

    def test_class_names_align_with_classifier(self):
        # Verify all 38 classes match the model's target taxonomy
        self.assertEqual(len(EXPECTED_38_CLASSES), 38)
        self.assertEqual(len(PLANTVILLAGE_CLASSES), 38)
        self.assertEqual(set(EXPECTED_38_CLASSES), set(PLANTVILLAGE_CLASSES))

    def test_dataset_handle(self):
        self.assertEqual(DATASET_HANDLE, "vipoooool/new-plant-diseases-dataset")


if __name__ == "__main__":
    unittest.main()
