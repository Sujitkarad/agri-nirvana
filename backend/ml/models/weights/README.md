# Rice & Maize model artifacts

The trained model files are deliberately excluded from Git because the PyTorch
checkpoint is a large binary artifact and must be versioned and deployed
together with the exact training output. The production inference engine must
not silently substitute another model when the configured checkpoint is absent.

Expected outputs from the training pipeline:

- `rice_and_maize_classifier.pt` — trained PyTorch checkpoint.
- `rice_and_maize_classifier.json` — class names and held-out evaluation metrics.

## Train and validate

From the repository root, provide a dataset arranged as `train/`, `val/`, and
`test/` subdirectories with one class directory per label:

```bash
python -m backend.ml.training.train_rice_and_maize \
  --data backend/ml/datasets/rice_and_maize \
  --output backend/ml/models/weights/rice_and_maize_classifier.pt \
  --epochs 12 --batch-size 16 --lr 0.001
```

The dataset is not included in Git. Use an authorized, versioned dataset source
and verify the class mapping and evaluation metrics before promoting a model.

## Release validation

Normal CI tests model construction and a forward pass without downloading
ImageNet weights. Artifact-specific tests are skipped when the trained files
are absent, so CI does not pretend a model was trained.

After provisioning the intended model artifacts in the release runner, require
them explicitly:

```bash
REQUIRE_TRAINED_MODEL_ARTIFACTS=1 pytest -q backend/tests/test_rice_maize_training.py
```

A release must fail if either artifact is missing or if the metadata checks,
checkpoint loading, or inference smoke test fails. Keep the checkpoint and JSON
metadata from the same training run; do not create placeholder or random weights
to satisfy release checks.
