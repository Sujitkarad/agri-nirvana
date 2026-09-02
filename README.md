# 🌾 Agri Nirvana

<div align="center">

## Precision Agriculture • AI Crop Care • Market Intelligence • GIS

[![License: MIT](https://img.shields.io/badge/License-MIT-emerald.svg)](LICENSE)
[![React](https://img.shields.io/badge/React-18.3-blue.svg?logo=react)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-8.2-purple.svg?logo=vite)](https://vitejs.dev/)
[![Three.js](https://img.shields.io/badge/Three.js-WebGL-black.svg?logo=three.js)](https://threejs.org/)
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-AI%20Inference-yellow.svg?logo=huggingface)](https://huggingface.co/)
[![Vercel](https://img.shields.io/badge/Vercel-Live%20Demo-brightgreen.svg?logo=vercel)](https://agri-nirvana.vercel.app)

**Agri Nirvana** is a precision-agriculture platform that combines AI-assisted crop diagnostics, 3D/WebGL visualization, field-health analytics, market intelligence, and farmer-focused financial tools in a single experience.

[🚀 Live Demo](https://agri-nirvana.vercel.app) · [📦 Repository](https://github.com/Sujitkarad/agri-nirvana) · [🐛 Issues](https://github.com/Sujitkarad/agri-nirvana/issues)

</div>

---

## 📸 Platform Showcase

<div align="center">

| AI Crop Diagnostics | 3D Field Intelligence |
|---|---|
| ![AI Leaf Diagnostics](https://raw.githubusercontent.com/Sujitkarad/agri-nirvana/main/public/screenshots/ai-leaf-diagnostics-3d.png) | ![NDVI Terrain](https://raw.githubusercontent.com/Sujitkarad/agri-nirvana/main/public/screenshots/satellite-ndvi-3d-drone.png) |

| Predictive Yield Analytics | Market Linkage |
|---|---|
| ![Yield Analytics](https://raw.githubusercontent.com/Sujitkarad/agri-nirvana/main/public/screenshots/yield-analytics-dashboard.png) | ![e-NAM Linkage](https://raw.githubusercontent.com/Sujitkarad/agri-nirvana/main/public/screenshots/enam-mandi-linkage.png) |

</div>

---

## 🎯 Why Agri Nirvana?

Farmers often need to move between separate tools for crop diagnosis, field monitoring, market prices, and financial planning. Agri Nirvana is designed around a single workflow:

**Observe → Diagnose → Understand → Decide → Act**

The platform brings those stages together through a visual, farmer-oriented interface.

> **Important:** Agri Nirvana is an educational/prototype platform. AI predictions, market information, credit scoring, insurance simulations, and recommendations should not be treated as professional agricultural, financial, insurance, or medical advice. Where a feature uses simulated or pre-processed data, the UI/documentation should be interpreted accordingly.

---

## ✨ Core Capabilities

### 🤖 AI Crop Diagnostics

- AI-assisted leaf/crop disease classification workflow.
- Hugging Face inference integration.
- 3D disease-leaf visualization with highlighted lesion zones.
- AI assistant interface for farmer-facing explanations and recommendations.
- Model layer designed to support multiple instruction/vision workflows.

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

### 📡 GIS Outbreak Radar

- 25 km-radius outbreak radar visualization.
- Spatial disease-cluster presentation.
- Community outbreak reporting interaction.

### 📈 Yield Intelligence

- Historical yield visualization.
- AI/projected yield trajectory presentation.
- Harvest-date and revenue calculation interfaces.
- Designed to make agricultural analytics understandable to non-technical users.

### 🏪 Market Linkage

- APMC/e-NAM-oriented mandi price presentation.
- Best-price discovery workflow.
- Harvest listing concept for connecting producers with buyers.

### 💳 Farmer Finance Concepts

- Kisan Credit Score visualization.
- Parametric drought-insurance simulation.
- Claim/payout calculation interface.

### 🌱 Sustainability

- Water-conservation tracking.
- Carbon/ESG impact visualization.
- Printable impact certificate experience.

---

## 🏗️ Architecture

```text
┌──────────────────────────────────────────────────────────────┐
│                       AGRI NIRVANA                           │
│              Precision Agriculture Platform                  │
└───────────────────────────────┬──────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
        ▼                       ▼                       ▼
┌───────────────┐       ┌────────────────┐      ┌──────────────────┐
│ 3D / WebGL    │       │ AI / Inference │      │ Data & Analytics │
│ Three.js      │       │ HF Models      │      │ GIS / Market     │
└───────┬───────┘       └───────┬────────┘      └────────┬─────────┘
        │                       │                        │
        ├─ Crop Model           ├─ Disease workflow     ├─ NDVI views
        ├─ Disease Leaf         ├─ AI Assistant         ├─ Outbreak radar
        ├─ NDVI Terrain         └─ Recommendations      ├─ Mandi prices
        └─ Drone Flyover                                 └─ Yield analytics
                                │
                                ▼
                    ┌─────────────────────┐
                    │ Farmer-facing UI    │
                    │ Dashboards / Actions│
                    └─────────────────────┘
```

### AI workflow

```text
Farmer Image
     ↓
Pre-processing
     ↓
AI / Vision Inference
     ↓
Disease / Health Prediction
     ↓
Confidence + Explanation
     ↓
Farmer-facing Recommendation
```

### Field-health workflow

```text
Satellite / Pre-processed Field Data
                ↓
          NDVI Processing
                ↓
       Field Health Metrics
                ↓
       3D Terrain Rendering
                ↓
        Farmer Visualization
```

---

## 🧠 AI & Data Layer

The current implementation references the following technologies/models in the application:

- **Hugging Face Inference** for AI model access.
- **Mistral-7B-Instruct-v0.2** for instruction-style AI interaction.
- **Llama-3.2-3B-Instruct** for lightweight language interaction.
- **Zephyr-7B-Beta** for conversational experimentation.
- **ResNet-50** as part of the documented vision architecture.
- **Kaggle/APMC-oriented pre-processed datasets** for market-data experimentation.
- **Sentinel-2/NDVI concepts** for field-health visualization.

### Transparency

Not every displayed metric represents a continuously live production data feed. Some platform experiences use pre-processed, historical, simulated, or demonstration data so the end-to-end product workflow can be evaluated without requiring a production agricultural data infrastructure.

If you extend this project for production, replace demonstration data with authenticated, versioned sources and publish model evaluation metrics for every predictive feature.

---

## 🎨 3D Visual Systems

Agri Nirvana currently documents four primary 3D/WebGL experiences:

1. **Hero 3D Crop Model** — rotating/levitating low-poly crop visualization with dynamic lighting.
2. **3D Disease Leaf Inspector** — interactive organic leaf geometry with highlighted lesion zones.
3. **3D NDVI Terrain** — field terrain visualization with health-oriented NDVI color mapping and sensor markers.
4. **Autonomous Drone Flyover** — animated drone scanning sequence over the field terrain.

The implementation is built around Three.js/WebGL concepts to make agricultural data more visual and approachable.

---

## 🧩 Technology Stack

| Layer | Technology |
|---|---|
| Frontend | React 18 + Vite |
| Styling/UI | CSS / project UI components |
| 3D Graphics | Three.js / WebGL |
| AI | Hugging Face inference + referenced open models |
| Vision | ResNet-50 architecture reference |
| Data Visualization | Frontend chart/visualization components |
| Deployment | Vercel |
| Version Control | Git + GitHub |

---

## 🚀 Getting Started

### Prerequisites

- Node.js 18+ (Node.js 20+ recommended)
- npm, pnpm, or yarn
- Git

### Installation

```bash
git clone https://github.com/Sujitkarad/agri-nirvana.git
cd agri-nirvana
npm install
npm run dev
```

Open the local development URL shown by Vite (normally `http://localhost:5173`).

### Production build

```bash
npm run build
npm run preview
```

Before running production features that depend on external services, configure the required environment variables from the project's environment configuration.

---

## 🔐 Environment & Secrets

Never commit API keys, tokens, credentials, or private service URLs to GitHub.

For local development, use a `.env.local`/`.env` file as appropriate for the project's configuration and add it to `.gitignore`.

Recommended production practice:

```text
Browser
   ↓
Frontend
   ↓
Secure server/API layer
   ↓
AI provider / external data source
```

Do not expose privileged API keys directly in client-side JavaScript.

---

## 📊 Evaluation & Reproducibility

For future production/academic validation, every predictive module should publish:

- Dataset name and version
- Train/validation/test split
- Number of classes/samples
- Pre-processing pipeline
- Model architecture and version
- Accuracy
- Precision
- Recall
- F1 score
- Confusion matrix
- Inference latency
- Known failure cases

**No fabricated metrics are listed here.** Metrics should be added only after being measured against a documented evaluation dataset.

---

## 🗺️ Roadmap

- [ ] Production-grade crop disease dataset pipeline
- [ ] Calibrated confidence scoring for diagnosis
- [ ] Real agricultural data integrations
- [ ] Offline/low-connectivity farmer workflow
- [ ] Marathi/Hindi voice-first assistant improvements
- [ ] Field-level satellite data ingestion
- [ ] Model evaluation dashboard
- [ ] Secure backend for farmer data
- [ ] Authentication and role-based access
- [ ] Automated testing and end-to-end QA
- [ ] Accessibility audit
- [ ] Performance optimization for low-end mobile devices

---

## ⚠️ Limitations

Agri Nirvana is currently a prototype/engineering demonstration rather than a certified agricultural decision system.

- Disease predictions require real-world validation before operational use.
- Demonstration/pre-processed datasets may not represent current local field conditions.
- Market information should be independently verified before financial decisions.
- Credit-score and insurance modules are simulations, not banking/insurance underwriting systems.
- Satellite/NDVI visualizations should not be interpreted as certified agronomic measurements without validated data processing.

---

## 🤝 Contributing

Contributions are welcome.

1. Fork the repository.
2. Create a feature branch.
3. Make focused changes.
4. Run the project's checks/build locally.
5. Open a pull request with a clear description of the change.

For substantial architectural changes, open an issue first so the approach can be discussed.

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

### 🌾 From crop diagnosis to better agricultural decisions.

**Agri Nirvana — making agricultural intelligence more visual, accessible, and actionable.**

</div>
