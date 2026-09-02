# Field + OOD evaluation datasets

These directories are intentionally kept out of Git because the evaluation data must be real and provenance-controlled.

Expected local layout:

```text
backend/ml/datasets/field_ood/
├── field/
│   ├── <production-class>/
│   └── ...
└── ood/
    ├── unknown_crop/
    ├── non_plant/
    └── unknown_disease/
```

## Field data requirements

- Images captured in natural field conditions.
- Expert/agronomist verified labels.
- Record crop, disease, severity, district, date, farm/plant/session ID and source in an external manifest.
- Keep farm/plant/session groups intact across evaluation splits.
- Do not reuse images that were used to train or tune the production checkpoint.

## OOD data requirements

Include examples outside the supported production taxonomy: other crops, non-plant images, unrelated objects, and diseases/classes intentionally excluded from training.

The evaluator reports the model's maximum softmax probability distribution. It does **not** manufacture AUROC from OOD-only data. For AUROC/FPR@95TPR, provide a matched known-vs-OOD benchmark and extend the evaluator with the corresponding labels.

## Privacy and safety

Do not commit farmer names, phone numbers, exact private addresses, faces, GPS coordinates, or other personally identifying information. Store consent and provenance outside the repository.

The evaluation gate must fail when these datasets are absent; benchmark datasets must not silently substitute for field/OOD evaluation.
