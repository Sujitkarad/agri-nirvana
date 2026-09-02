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

EfficientNetV2-L at 448x448 is intentionally a high-capacity training configuration. The repository workflow currently defaults to `ubuntu-latest`; standard GitHub-hosted runners are CPU machines, while GPU-backed larger runners are a separate GitHub feature. citeturn0search1turn0search4 For practical full training, use a CUDA-capable larger or self-hosted runner and route the workflow to it with the appropriate runner label. Self-hosted runners can be targeted with labels such as `self-hosted`, `linux`, `x64`, and `gpu`. citeturn0search2turn0search6

## Quality gates

The training workflow requires:

- Macro-F1 >= 0.70
- ECE <= 0.15
- real field evaluation data
- real OOD evaluation data
- exact-duplicate leakage audit

PlantVillage/PlantDoc results must not be presented as Maharashtra field accuracy. A production checkpoint must pass the repository quality gates and representative field/OOD evaluation. Never bypass missing field/OOD data with synthetic or fabricated images.
