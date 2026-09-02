# Agri Nirvana model training

This directory contains the real PyTorch training pipeline for the crop-disease classifier.

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

## 2. Train

From the repository root:

```bash
python -m backend.ml.training.train_pipeline \
  --data backend/ml/datasets/plant_disease \
  --output backend/ml/models/weights/agri_nirvana_efficientnet_b0.pt \
  --epochs 15 \
  --batch-size 32
```

If CUDA is available, the script automatically uses GPU and mixed precision.

For an unsplit ImageFolder dataset:

```bash
python -m backend.ml.training.train_pipeline \
  --data backend/ml/datasets/plant_disease \
  --split
```

## 3. What the pipeline does

- EfficientNet-B0 transfer learning from ImageNet
- Realistic crop-image augmentation
- Class-balanced sampling
- Label smoothing
- AdamW + cosine learning-rate schedule
- Gradient clipping
- Mixed precision on CUDA
- Validation-loss early stopping
- Held-out test evaluation
- Accuracy, macro precision, macro recall, macro F1 and confusion matrix
- Checkpoint with class mapping and preprocessing metadata

## 4. Important accuracy rule

Do not put a claimed `94%` or similar accuracy into the product unless it was measured on a leakage-free, representative test set. The previous training file returned hard-coded placeholder metrics; this pipeline calculates metrics from the actual test predictions.

For Agri Nirvana's real target, maintain a second **Indian field test set** containing images from farms, phones, different lighting, backgrounds and disease stages. Do not use that set during training or model selection.

## 5. Deploying the trained model

The generated `.pt` file is intentionally ignored by git. Store large weights in a model registry/object store and configure the runtime to load that artifact. Do not commit datasets or multi-hundred-MB checkpoints to the source repository.
