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

### 🤖 AI Crop Diagnostics

The diagnostic pipeline is the core AI feature.

### 🌦️ Real-Time Farm Weather Intelligence

- Live agro-meteorological intelligence powered by Open-Meteo with zero API key dependencies.
- Real-time farm telemetry: Temperature, Feels-like, Relative Humidity, Wind Speed, Direction, Gusts, and Precipitation.
- Next 24-hour hourly forecast timeline with weather conditions and precipitation chance.
- 7-Day agricultural outlook including maximum/minimum temperatures, rain sums ($mm$), and FAO-56 Reference Evapotranspiration ($ET_0$).
- 5 deterministic agricultural rules:
  - **Best Field Activity Window**: Dynamic *Good / Caution / Poor* spray and operational window based on wind drift thresholds ($> 18\text{ km/h}$) and rain wash-off risk.
  - **Rain & Moisture Outlook**: Field surface moisture accumulation indicators.
  - **Irrigation Management**: Data-driven water balance guidance comparing incoming precipitation against $ET_0$.
  - **Heat & Solar Radiation Stress**: Warnings for heat spikes and excessive solar radiation.
  - **Disease-Favorable Weather Signal**: Transparent micro-climate risk indicators (humidity $>80\%$ and moderate temperatures favoring fungal development) with explicit symptom-verification disclaimers.
- Fast backend TTL caching ($10\text{ minutes}$) with coordinate rounding deduplication and direct browser-fallback resilience.

### 🚁 3D Drone & Field Avionics

- Autonomous drone survey flyover and waypoint mission visualization.
- Precision multi-spectral field index simulation (NDVI/NDRE vegetation stress).
- Interactive 3D terrain and flight path controls for field scouting.

The application includes a farmer-facing conversational assistant connected to the backend AI layer.

The assistant is designed to:

- explain crop-diagnostic results in simpler language;
- answer agriculture-related questions;
- use supplied diagnostic context when available;
- avoid inventing disease diagnoses when no authoritative diagnostic result exists;
- keep privileged provider credentials on the server side.

### 🌱 Field & Agronomy Tools

The frontend includes several agriculture-oriented workflows, including:

- field intelligence;
- crop and disease information;
- NPK/fertilizer calculation interfaces;
- outbreak/risk visualization concepts;
- yield analytics;
- farmer-oriented agronomy workflows.

Some existing field-intelligence and visualization experiences remain demonstration-oriented and must not be interpreted as certified measurements unless backed by validated data sources.

### 🏪 Market Intelligence

The platform contains market/mandi-oriented workflows for:

- APMC/e-NAM-style price presentation;
- crop price comparison;
- harvest listing concepts;
- buyer/market-linkage workflows.

Where data is simulated, historical, pre-processed, or demonstration-only, it must be labelled accordingly and should not be presented as a guaranteed live market feed.

### 💳 Farmer Finance & Sustainability Concepts

The application also contains prototype interfaces for:

- Kisan credit/eligibility concepts;
- parametric weather-insurance simulations;
- sustainability and water/carbon impact visualization.

These are product concepts, not banking, underwriting, or certified environmental accounting systems.

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
- [ ] Production weather API integration
- [ ] Farm weather intelligence dashboard
- [ ] Stronger mobile/low-connectivity workflow
- [ ] Full end-to-end QA
- [ ] Production security review
- [ ] Accessibility audit
- [ ] Performance optimization

---

## ⚠️ Current Limitations

- The production EfficientNetV2-L architecture is implemented, but a deployed checkpoint must be trained and evaluated before making accuracy claims.
- Field performance may differ substantially from laboratory-style datasets.
- Existing market, field, finance, insurance, and visualization modules can contain demonstration/pre-processed data and should not automatically be interpreted as live official feeds.
- Agricultural recommendations require local agronomic verification and applicable product-label/regulatory checks.
- Weather intelligence is planned as the replacement for the current satellite-focused user experience; it should only be described as live after a real provider integration is operational.

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
