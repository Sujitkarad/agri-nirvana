# 🌾 Agri Nirvana

<div align="center">

## AI Crop Diagnostics • Precision Agriculture • Market Intelligence

[![License: MIT](https://img.shields.io/badge/License-MIT-emerald.svg)](LICENSE)
[![React](https://img.shields.io/badge/React-18-blue.svg?logo=react)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-purple.svg?logo=vite)](https://vitejs.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-backend-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com/)
[![PyTorch](https://img.shields.io/badge/PyTorch-ML-ee4c2c.svg?logo=pytorch)](https://pytorch.org/)
[![Three.js](https://img.shields.io/badge/Three.js-WebGL-black.svg?logo=three.js)](https://threejs.org/)
[![Vercel](https://img.shields.io/badge/Vercel-Live%20Demo-brightgreen.svg?logo=vercel)](https://agri-nirvana.vercel.app)

**Agri Nirvana** is an agriculture-focused platform that combines crop-image diagnostics, confidence-aware AI inference, farmer-facing agronomic guidance, field intelligence, market workflows, and agricultural calculators in one application.

[🚀 Live Demo](https://agri-nirvana.vercel.app) · [📦 Repository](https://github.com/Sujitkarad/agri-nirvana) · [🐛 Issues](https://github.com/Sujitkarad/agri-nirvana/issues)

</div>

---

## 🎯 Product Vision

Agri Nirvana is built around a simple workflow:

**Observe → Diagnose → Understand → Decide → Act**

The current engineering direction prioritizes **trustworthy AI diagnostics over simulated telemetry**. Production diagnosis is designed to abstain when the image, crop evidence, model confidence, or uncertainty signals are insufficient instead of presenting an unreliable prediction as a fact.

> **Important:** Agri Nirvana is an engineering/prototype platform and is not a certified agricultural, financial, insurance, or medical decision system. Predictive results and recommendations require appropriate real-world validation before operational use.

---

## ✨ Current Capabilities

### 🤖 Crop Image Diagnostics
- Upload or capture a crop image and request an AI-supported assessment from the configured backend.
- Review confidence, uncertainty notices, and saved device/cloud diagnosis history where available.
- Offline mode checks image quality only; it does not infer a disease.
- Results are advisory and require field or agricultural-extension confirmation. Chemical treatment guidance remains disabled until product-label and crop-specific validation is available.

### 🌦️ Farm Weather
- Current conditions and forecasts using the configured weather service.
- Agricultural context for rainfall, heat, humidity, wind, and field activity.
- Weather-driven rules are decision-support signals, not guarantees of disease occurrence or safe pesticide application.

### 🛰️ Field Intelligence Scenario Preview
- Explore preset field scenarios and their visual overlays.
- Scenario values are illustrative examples, not verified satellite imagery, live NDVI measurements, surveyed boundaries, or executable drone flight plans.
- Drone control, autonomous missions, and operational export are not part of the current application.

### 🌱 Soil Nutrient Planning Estimate
- Compare generic crop nutrient defaults across a selected crop and land area.
- Outputs are planning estimates, not soil-test-based fertilizer prescriptions. Confirm real input decisions with a soil test and a local KVK/agricultural-extension officer.

### 🏪 Mandi Price View
- Query the configured mandi API and filter the returned market records.
- When the API is unavailable, the interface labels preset prices as static references and warns that they are not today's verified prices.
- Trend, arrival, and “best price” badges are hidden for fallback records. No farmer listing, trade execution, payment, or buyer-broadcast service is provided.

### 💬 Agricultural AI Assistant
- Ask agriculture-related questions and request explanations of available diagnostic context.
- The assistant is not a substitute for a validated crop classifier, local agronomist, or official product label.

The current UI intentionally excludes simulated subscription activation, mock outbreak broadcasting, and the local-only produce marketplace. Those workflows should return only when backed by real services, verified data, and appropriate security controls.

---

## 🧠 AI Architecture

```text
                    ┌────────────────────────────┐
                    │       Agri Nirvana UI      │
                    │   React + Vite + WebGL     │
                    └─────────────┬──────────────┘
                                  │
                    ┌─────────────▼──────────────┐
                    │       FastAPI Backend      │
                    │ Auth / AI / Data Services  │
                    └─────────────┬──────────────┘
                                  │
             ┌────────────────────┼────────────────────┐
             ▼                    ▼                    ▼
      Image Validation     Production Vision      AI Assistant
             │              EfficientNetV2-L            │
             ▼                    │                    ▼
      Plant / Quality             ▼              Safety-aware
          Gates             Calibration +          conversation
             │             Uncertainty Gates
             └────────────────────┬───────────────────┘
                                  ▼
                         Diagnosis / Abstention
                                  │
                    ┌─────────────▼──────────────┐
                    │ Disease Knowledge +        │
                    │ Severity + Agronomy Context │
                    └────────────────────────────┘
```

### Production diagnosis flow

```text
Crop Image
    ↓
Image Quality Validation
    ↓
Plant Validation
    ↓
Crop Compatibility Check
    ↓
EfficientNetV2-L Inference
    ↓
Temperature Calibration
    ↓
Confidence / Margin / Entropy Gates
    ↓
        ┌───────────────┐
        │ Reliable?     │
        └───────┬───────┘
          No    │    Yes
          ↓     │     ↓
       Abstain  │  Disease Knowledge
                │      ↓
                │  Severity Estimation
                │      ↓
                └── Farmer-facing Result
```

The important design principle is **fail-safe inference**: missing models, unsupported crops, poor images, weak crop evidence, low confidence, or excessive uncertainty should not become fake diagnoses.

---

## 🔬 Model & Data Strategy

The repository is being structured for a reproducible training pipeline rather than a single untracked dataset dump.

### Current production model direction

- Architecture: **EfficientNetV2-L**
- Production input target: **448 × 448**
- Transfer learning with staged backbone unfreezing
- AdamW optimization
- Learning-rate warmup + cosine decay
- Class-balanced training
- Label smoothing
- Automatic mixed precision when CUDA is available
- Gradient clipping
- Early stopping
- Validation Macro-F1 checkpoint selection
- Validation-only temperature-scaling calibration
- Untouched test-set evaluation after calibration

### Dataset architecture

The training/data pipeline separates different data roles instead of assuming every agricultural image belongs in the same production training set:

```text
Production Training
└── PlantVillage-aligned disease taxonomy

Field Evaluation
└── PlantDoc / field-condition images

Indian Field / Expert OOD
└── DigiGreen and other verified field sources

Specialist Training
└── Sugarcane specialist dataset

OOD / Unknown
└── Unsupported crops / diseases / non-plant imagery
```

Datasets should be evaluated for provenance, licensing, label quality, field realism, duplication, leakage, and taxonomy compatibility before being added to production training.

### Dataset quality rules

The training pipeline is intended to enforce:

- train/validation/test separation;
- exact duplicate detection using SHA-256;
- consistent class directories;
- minimum class coverage;
- canonical label mapping;
- separation of field/OOD evaluation from production training where appropriate;
- reproducible dataset manifests;
- no automatic production promotion without measured improvement.

Near-duplicate detection and stronger farm/plant/session-level grouping remain important areas for continued dataset hardening.

---

## 🛡️ AI Safety & Reliability

The production inference configuration currently uses explicit uncertainty controls, including:

```text
Confidence threshold          0.70
Minimum top-2 margin           0.10
Maximum normalized entropy     0.90
Minimum crop probability mass  0.45
Local production checkpoint    Required
```

These values are **acceptance gates**, not claims about real-world model accuracy.

A model must be trained and evaluated on documented datasets before accuracy or field-performance claims are made.

### No fabricated metrics

The project does **not** claim a specific diagnostic accuracy until it has been measured against a documented evaluation protocol.

Production evaluation should report, at minimum:

- accuracy;
- macro precision;
- macro recall;
- macro F1;
- per-class performance;
- confusion matrix;
- calibration/ECE;
- Brier score where appropriate;
- abstention/coverage statistics;
- field-condition performance;
- OOD performance where the evaluation design supports it.

---

## 🏗️ Repository Structure

```text
agri-nirvana/
├── src/
│   ├── components/
│   ├── data/
│   ├── lib/
│   ├── services/
│   ├── App.jsx
│   └── index.css
│
├── backend/
│   ├── routes/
│   ├── services/
│   ├── db/
│   ├── ml/
│   │   ├── config/
│   │   ├── inference/
│   │   ├── models/
│   │   ├── training/
│   │   └── datasets/
│   └── tests/
│
├── .github/
│   └── workflows/
│
├── public/
├── package.json
└── README.md
```

---

## 🧩 Technology Stack

| Layer | Technology |
|---|---|
| Frontend | React 18 + Vite |
| Backend | FastAPI + Python |
| ML | PyTorch + TorchVision |
| Production vision | EfficientNetV2-L |
| Image processing | Pillow / TorchVision transforms |
| 3D/WebGL | Three.js |
| AI assistant | Backend AI provider integration |
| Database | MongoDB with SQLite fallback configuration |
| Deployment | Vercel frontend + backend deployment configuration |
| CI | GitHub Actions |
| Version control | Git + GitHub |

---

## 🚀 Getting Started

### Prerequisites

- Node.js 20+ recommended
- Python 3.11 recommended
- npm
- Git
- CUDA-capable GPU recommended for full EfficientNetV2-L training

### Frontend

```bash
git clone https://github.com/Sujitkarad/agri-nirvana.git
cd agri-nirvana
npm install
npm run dev
```

The Vite development server normally runs on:

```text
http://localhost:5173
```

### Backend

Install the backend requirements according to the repository's current requirements files, configure the required environment variables, and start the FastAPI application using the project's backend entrypoint.

### Production build

```bash
npm run build
npm run preview
```

---

## 🔐 Environment & Security

Never commit:

- API keys;
- JWT secrets;
- database credentials;
- provider tokens;
- private URLs;
- farmer PII.

Production secrets belong in the server environment or an appropriate secret-management system.

The production AI configuration intentionally requires a real local trained checkpoint when `AI_MODEL_PROVIDER=real` rather than silently substituting a fake model.

JWT configuration must use a strong production secret. Client-side code must never contain privileged provider credentials.

---

## 🧪 Testing & CI

The repository contains backend tests and GitHub Actions workflows for automated checks.

Recommended local checks:

```bash
python -m compileall -q backend
pytest -q backend/tests
npm run build
```

CI should validate:

- frontend installation/build;
- backend dependency installation;
- Python syntax;
- backend tests;
- production inference safety expectations.

Training is a separate workflow from normal application CI and requires an appropriate CUDA-capable runner for practical EfficientNetV2-L training.

**Do not treat a successful frontend build as proof that the ML training pipeline is complete.**

---

## 🏋️ Model Training

The repository includes a high-capacity transfer-learning pipeline for the production disease classifier.

The intended training configuration is approximately:

```text
Model:            EfficientNetV2-L
Input:            448 × 448
Epochs:           100
Batch size:       8
Classifier LR:    7.5e-5
Backbone LR:      7.5e-6
Warmup:           8 epochs
Frozen stage:     8 epochs
Early stopping:   15 epochs
```

Exact training parameters should be recorded with each experiment rather than assumed from this README.

A CUDA-capable GPU is strongly recommended. Running the full configuration on a normal CPU runner is not a practical production-training strategy.

Training should produce versioned checkpoints plus metadata, calibration information, metrics, and dataset manifests.

---

## 🌦️ Weather Roadmap

The next major product direction is to replace the current satellite-focused user experience with **Farm Weather Intelligence**.

Planned weather capabilities:

- current local weather;
- hourly forecast;
- multi-day forecast;
- rainfall probability and accumulation;
- temperature and humidity;
- wind speed and gusts;
- agricultural weather signals;
- irrigation/field-activity guidance;
- weather-aware agronomic context;
- clear weather-data provenance.

The weather feature should use real provider data and must never present fabricated temperatures, rainfall, or forecasts as live information.

Weather context should support agricultural decisions but must not be treated as a crop disease diagnosis.

---

## 🗺️ Roadmap

- [x] Production-oriented EfficientNetV2-L inference architecture
- [x] Image and plant validation gates
- [x] Confidence, margin, entropy, and crop-evidence gates
- [x] Model checkpoint validation
- [x] Dataset audit foundation
- [x] Transfer-learning training pipeline
- [x] Field/OOD evaluation structure
- [x] Backend AI-chat safety architecture
- [ ] Complete production model training on CUDA hardware
- [ ] Publish measured validation/test metrics
- [ ] Expand real Indian field/OOD evaluation
- [ ] Near-duplicate and farm/session-level leakage detection
- [x] Farm weather dashboard UI and provider-backed forecast workflow
- [ ] Production monitoring, reliability fallbacks, and end-to-end validation for weather services
- [ ] Stronger mobile/low-connectivity workflow
- [ ] Full end-to-end QA
- [ ] Production security review
- [ ] Accessibility audit
- [ ] Performance optimization

---

## ⚠️ Current Limitations

- The production EfficientNetV2-L architecture is implemented, but a deployed checkpoint must be trained and evaluated before making accuracy claims.
- Field performance may differ substantially from laboratory-style datasets.
- The field preview uses illustrative presets; fallback mandi prices are static references, not verified current quotes. Treat data as live only when the configured provider confirms its source and freshness.
- Agricultural recommendations require local agronomic verification and applicable product-label/regulatory checks.
- The weather dashboard is available, but operational decisions still require local verification. Provider outages and cached/fallback values must be disclosed clearly.

---

## 🤝 Contributing

1. Fork the repository.
2. Create a focused feature branch.
3. Make the smallest appropriate change.
4. Add or update tests.
5. Run the relevant build/checks locally.
6. Open a pull request with a clear description.

For ML changes, include dataset provenance, training configuration, evaluation methodology, and reproducible metrics whenever applicable.

---

## 📄 License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for details.

---

## 👨‍💻 Author

**Sujit Karad**

- GitHub: [@Sujitkarad](https://github.com/Sujitkarad)
- Project: [Agri Nirvana](https://github.com/Sujitkarad/agri-nirvana)
- Live Demo: [agri-nirvana.vercel.app](https://agri-nirvana.vercel.app)

---

<div align="center">

### 🌾 AI Crop Diagnostics + Better Agricultural Decisions

**Agri Nirvana — building practical, transparent, and farmer-focused agricultural intelligence.**

</div>
