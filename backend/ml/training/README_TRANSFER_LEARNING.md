# Agri Nirvana pretrained model training

Agri Nirvana trains its disease classifier with transfer learning from ImageNet-pretrained **EfficientNetV2-L**. The backbone is not trained from random initialization.

## Pipeline

1. Load `EfficientNetV2-L` with torchvision ImageNet weights.
2. Replace the final classifier with the production disease taxonomy.
3. Freeze the feature extractor for the initial warm-up/frozen stage.
4. Train the classifier head with class-balanced cross entropy and label smoothing.
5. Progressively unfreeze the backbone and fine-tune with a lower backbone learning rate.
6. Use realistic image augmentation, AdamW, warmup and cosine decay.
7. Select the checkpoint using validation Macro-F1 and early stopping.
8. Fit temperature scaling on validation logits only.
9. Evaluate the calibrated model once on the untouched test set.
10. Run separate field and OOD evaluation before production release.

## Maximum-capacity training settings

- Architecture: EfficientNetV2-L
- Pretraining: ImageNet
- Resolution: 448x448
- Epochs: 100
- Batch size: 8
- Classifier learning rate: 7.5e-5
- Backbone learning rate after unfreezing: 7.5e-6
- Warm-up: 8 epochs
- Frozen stage: 8 epochs
- Early stopping patience: 15
- AMP: enabled automatically when CUDA is available

## Compute requirement

EfficientNetV2-L at 448x448 is intentionally a high-capacity training configuration. The workflow requires CUDA and must be routed to a CUDA-capable GitHub larger runner or self-hosted GPU runner. Standard `ubuntu-latest` is not a GPU runner, so selecting it will fail fast rather than silently running an impractical CPU training job.

## Dataset policy

- PlantVillage is the primary training/benchmark dataset.
- PlantDoc is retained as a separate field-condition evaluation dataset.
- DigiGreen expert-reviewed crop-disease images are materialized into known-class field evaluation and unmatched OOD evaluation sets.
- Field/OOD images are never silently added to training.
- Ambiguous expert labels are retained as OOD rather than force-labelled.

## Quality gates

The training workflow requires:

- Macro-F1 >= 0.70
- ECE <= 0.15
- non-empty field evaluation data
- non-empty OOD evaluation data
- exact-duplicate leakage audit
- calibrated field/OOD evaluation

PlantVillage/PlantDoc/DigiGreen results must not be presented as Maharashtra field accuracy. A production checkpoint must pass the repository quality gates and representative field/OOD evaluation. Never bypass missing or ambiguous evaluation data with synthetic or fabricated images.
