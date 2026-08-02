# 🌾 Agri Nirvana — Flagship Precision Agriculture & 3D AI Platform

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-emerald.svg)](LICENSE)
[![React](https://img.shields.io/badge/React-18.3-blue.svg?logo=react)](https://reactjs.org/)
[![Vite](https://img.shields.io/badge/Vite-8.2-purple.svg?logo=vite)](https://vitejs.dev/)
[![Three.js](https://img.shields.io/badge/Three.js-WebGL-black.svg?logo=three.js)](https://threejs.org/)
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-AI%20Inference-yellow.svg)](https://huggingface.co/)
[![Build Status](https://img.shields.io/badge/Build-Passing-brightgreen.svg)]()

**Agri Nirvana** is a production-ready **Precision Agriculture, AI Crop Care, AgFintech, Market Linkage, and GIS Outbreak Radar Platform** equipped with **4 Production 3D Visual Systems**, powered by Three.js, Hugging Face AI, and pre-processed Kaggle datasets.

[Live Demo](https://agri-nirvana.vercel.app) • [Architecture](#-architecture) • [3D Visual Features](#-3d-visual-systems) • [Getting Started](#-getting-started)

</div>

---

## 🌟 Architectural Highlights

```
+-----------------------------------------------------------------------------------+
|                                  AGRI NIRVANA                                     |
|                    Precision Agriculture & AI Vision Engine                       |
+------------------------------------+----------------------------------------------+
                                     |
    +--------------------------------+--------------------------------+
    |                                |                                |
+---v------------------+  +----------v-----------+  +-----------------v------------+
| 3D WebGL Engine      |  | AI Vision & LLM      |  | Telemetry & AgFintech        |
| (Three.js Shaders)   |  | (ResNet-50 + HF API) |  | (Sentinel-2 + Kaggle Mandi)  |
+----------------------+  +----------------------+  +------------------------------+
| • Hero Crop Model    |  | • Leaf Pathology     |  | • 25km GIS Radar             |
| • 3D Disease Leaf    |  | • 3D AI Bot Avatar   |  | • e-NAM Price Discovery      |
| • 3D NDVI Terrain    |  | • Voice Advisory     |  | • Kisan Credit Score (0-100) |
| • Autonomous Drone   |  |   (6 Languages)      |  | • Parametric Drought Cover   |
+----------------------+  +----------------------+  +------------------------------+
```

---

## 🌾 3D Visual Systems & WebGL Engine

1. **Hero 3D Rotating Crop Model** ([`Hero3DCropModel.jsx`](file:///c:/Users/Sujit/.gemini/antigravity-ide/scratch/Agri%20Nirvana/src/components/Hero3DCropModel.jsx)): Low-poly wheat stalk model with continuous Y-axis rotation, levitation, and dynamic material lighting.
2. **3D Disease Leaf Inspector** ([`DiseaseLeaf3DModel.jsx`](file:///c:/Users/Sujit/.gemini/antigravity-ide/scratch/Agri%20Nirvana/src/components/DiseaseLeaf3DModel.jsx)): Extruded organic 3D leaf geometry with **glowing red/amber pulsating lesion zones** (`#ef4444` / `#f97316`) tied to neural vision diagnosis output, featuring 360° mouse drag rotation.
3. **3D Field Terrain & NDVI Heatmap** ([`NDVITerrain3DModel.jsx`](file:///c:/Users/Sujit/.gemini/antigravity-ide/scratch/Agri%20Nirvana/src/components/NDVITerrain3DModel.jsx)): 3D terrain heightmap mesh draped with Sentinel-2 NDVI health color scale (emerald green for optimal, yellow for moderate, red for stress) + 3D soil sensor markers.
4. **3D Autonomous Drone Flyover**: Looping 3D quadcopter drone with 4 spinning rotors flying an autonomous scanning flight pattern over the field terrain, casting a vertical laser scanning beam.

---

## 🚀 Key Modules & Features

- 🤖 **3D Animated Hugging Face AI Assistant**: Powered by `mistralai/Mistral-7B-Instruct-v0.2`, `meta-llama/Llama-3.2-3B-Instruct`, and `HuggingFaceH4/zephyr-7b-beta` pre-processed with Kaggle APMC market data.
- 📡 **25km GIS Outbreak Radar**: Concentric GIS radar card displaying real-time disease outbreak clusters with a **"+ Report Outbreak to Community"** modal dialog.
- 📈 **Predictive Yield Analytics Engine**: 5-Year historical and AI-projected crop yield trajectory graphs (38.4 Q/Acre AI target), harvest date counter, and gross revenue calculator.
- 📈 **e-NAM Mandi Market Linkage**: Direct APMC mandi prices, best-price recommendations, and direct harvest produce listing portal connecting farmers with corporate buyers (*BigBasket, Sahyadri FPO, Reliance*).
- 💳 **Kisan Credit Score & Parametric Insurance**: Bank-grade 0–100 weighted credit score + PMFBY Parametric Weather Drought Cover claim payout simulator (₹15,000).
- 🍃 **Carbon ESG & Impact Certificate**: Water conservation tracker (42,800+ L) + 1-click printable Impact Certificate.

---

## 💻 Getting Started

### Prerequisites
- Node.js 18+ or 20+
- npm or yarn or pnpm

### Installation

```bash
# 1. Clone the Repository
git clone https://github.com/Sujitkarad/agri-nirvana.git

# 2. Navigate to Project Directory
cd agri-nirvana

# 3. Install Dependencies
npm install

# 4. Start Local Development Server
npm run dev
```

The application will be accessible at `http://localhost:5173/`.

### Production Build

```bash
# Build production bundle
npm run build
```

---

## 🛡️ License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for more details.
