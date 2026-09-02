# Agri Nirvana pretrained model training

Agri Nirvana trains its disease classifier with transfer learning from ImageNet-pretrained EfficientNetV2-S. The backbone is not trained from random initialization.

## Pipeline

1. Load `EfficientNetV2-S` with torchvision ImageNet weights.
2. Replace the final classifier with the production disease taxonomy.
3. Freeze the feature extractor for the initial warm-up/frozen stage.
4. Train the classifier head with class-balanced cross entropy and label smoothing.
5. Progressively unfreeze the backbone and fine-tune with a lower backbone learning rate.
6. Use realistic image augmentation, AdamW, warmup and cosine decay.
7. Select the checkpoint using validation Macro-F1 and early stopping.
8. Fit temperature scaling on validation logits only.
9. Evaluate the calibrated model once on the untouched test set.
10. Run separate field and OOD evaluation before production release.

## Default training settings

- Architecture: EfficientNetV2-S
- Pretraining: ImageNet
- Resolution: 384x384
- Epochs: 80
- Batch size: 16
- Classifier learning rate: 1e-4
- Backbone learning rate after unfreezing: 1e-5
- Warm-up: 5 epochs
- Frozen stage: 5 epochs
- Early stopping patience: 12

## Important

PlantVillage/PlantDoc results must not be presented as Maharashtra field accuracy. A production checkpoint must pass the repository quality gates and representative field/OOD evaluation. Never bypass missing field/OOD data with synthetic or fabricated images.
