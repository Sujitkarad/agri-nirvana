# Agri Nirvana model training

This directory contains the real PyTorch training pipeline for the production crop-disease classifier.

## 1. Prepare the dataset

Preferred layout:

```text
plant_disease/
  train/
    Tomato___healthy/
    Tomato___Early_blight/
    ...
  val/
    Tomato___healthy/
    Tomato___Early_blight/
    ...
  test/
    Tomato___healthy/
    Tomato___Early_blight/
    ...
```

The same class names must exist in every split. Keep images from the same plant/field in one split. A random image-level split can leak near-duplicate images and make results look much better than real farm performance.

### Quick Import via Kaggle (vipoooool/new-plant-diseases-dataset)

To download and materialize the 38-class Kaggle dataset directly:

```bash
# Automated download via kagglehub and preparation into train/val/test splits:
python -m backend.ml.training.import_kaggle_dataset --dest backend/ml/datasets/plant_disease
```

Or using Python:

```python
import kagglehub
path = kagglehub.dataset_download("vipoooool/new-plant-diseases-dataset")
print("Path to dataset files:", path)
```

If you only have an ImageFolder root (`class_name/*.jpg`), you can use `--split` to create a stratified 70/15/15 split. For a production claim, replace that test set with a genuinely field-separated test set.

The production path is **EfficientNetV2-L**. Training is intentionally GPU-oriented because the L variant is large.

From the repository root:

```bash
python -m backend.ml.training.train_pipeline_large \
  --data backend/ml/datasets/plant_disease \
  --output backend/ml/models/weights/agri_nirvana_efficientnet_v2_l.pt \
  --epochs 100 \
  --batch-size 8 \
  --image-size 448
```

The pipeline uses CUDA automatically when available and enables mixed precision on CUDA. The production checkpoint is accepted by the inference engine only when it contains the expected EfficientNetV2-L architecture and metadata.

## 3. What the pipeline does

- EfficientNetV2-L transfer learning from ImageNet
- 448px training/evaluation input
- Realistic crop-image augmentation
- Class-balanced cross-entropy
- Label smoothing
- AdamW + cosine learning-rate schedule
- Warmup and staged backbone unfreezing
- Gradient clipping
- Mixed precision on CUDA
- Validation Macro-F1 checkpoint selection
- Validation-only temperature calibration
- Held-out test evaluation after calibration
- Accuracy, macro precision, macro recall, macro F1 and ECE
- Checkpoint with class mapping and preprocessing/calibration metadata

## 4. Accuracy and safety rules

Do not put a claimed accuracy into the product unless it was measured on a leakage-free, representative test set. Metrics must come from actual held-out predictions.

For Agri Nirvana's real target, maintain a separate **Indian field test set** containing images from farms, phones, different lighting, backgrounds and disease stages. Do not use that set during training or model selection.

The production inference engine abstains when crop evidence, calibrated confidence, top-2 margin, entropy, image quality, plant validation or severity evidence is insufficient. An uncertain result must not produce disease-specific treatment instructions.

## 5. Deploying the trained model

The generated `.pt` file is intentionally ignored by git. Store large weights in a model registry/object store and configure the runtime to load that artifact. Do not commit datasets or multi-hundred-MB checkpoints to the source repository.
