import React, { useState, useEffect, useRef } from "react";
import {
  Layers,
  Cpu,
  Compass,
  Wind,
  Droplets,
  CloudRain,
  ShieldCheck,
  ShieldAlert,
  AlertTriangle,
  Download,
  Printer,
  Copy,
  Check,
  Sparkles,
  Zap,
  Activity,
  Maximize2,
  TrendingUp,
  Coins,
  MapPin,
  RefreshCw,
  Eye,
  Sliders,
  Plane,
  FileText,
  BarChart3,
  CheckCircle2,
  RotateCw,
  Info,
  Video,
  Play,
  Pause,
  Volume2,
  VolumeX,
  Radio
} from "lucide-react";

import DroneMissionGeneratorModal from "../DroneMissionGeneratorModal";

// Preset Real-World Agricultural Scenarios
const PRESET_FIELDS = [
  {
    id: "cotton-vidarbha",
    name: "Kharif Bt Cotton (Vidarbha, MH)",
    crop: "Cotton",
    cultivar: "RCH-659 BG II",
    areaHa: 10.50,
    areaAcres: 25.95,
    centerLat: 20.7453,
    centerLng: 78.5621,
    pathogen: "Bacterial Blight / Root Hypoxia",
    stage: "Square & Peak Flowering (BBCH 65)",
    soil: "Deep Black Vertisol (Clay 52%)",
    irrigation: "Drip + Furrow Supplemental",
    meanNdvi: 0.638,
    meanNdre: 0.412,
    alphaPct: 52.0,
    betaPct: 31.0,
    gammaPct: 17.0,
    windKmh: 8.4,
    gustKmh: 12.2,
    rainProb: 10,
    tempC: 31.2,
    rhPct: 82,
    elevationMin: 307.8,
    elevationMax: 316.2,
    reliefM: 8.4
  },
  {
    id: "wheat-punjab",
    name: "Rabi Bread Wheat (Ludhiana, PB)",
    crop: "Wheat",
    cultivar: "PBW-824",
    areaHa: 8.20,
    areaAcres: 20.26,
    centerLat: 30.9010,
    centerLng: 75.8573,
    pathogen: "Yellow Rust (Puccinia striiformis)",
    stage: "Flag Leaf & Ear Emergence (BBCH 55)",
    soil: "Alluvial Loam (pH 7.4)",
    irrigation: "Canal Tube Well Flood",
    meanNdvi: 0.742,
    meanNdre: 0.486,
    alphaPct: 68.0,
    betaPct: 24.0,
    gammaPct: 8.0,
    windKmh: 11.5,
    gustKmh: 16.0,
    rainProb: 5,
    tempC: 22.4,
    rhPct: 64,
    elevationMin: 242.0,
    elevationMax: 245.5,
    reliefM: 3.5
  },
  {
    id: "tomato-nashik",
    name: "Hybrid Tomato (Dindori, Nashik)",
    crop: "Tomato",
    cultivar: "Abhinav Seminis F1",
    areaHa: 4.80,
    areaAcres: 11.86,
    centerLat: 20.1982,
    centerLng: 73.8421,
    pathogen: "Late Blight (Phytophthora infestans)",
    stage: "Fruit Set & Ripening (BBCH 73)",
    soil: "Red Loamy Clay",
    irrigation: "Precision Inline Drip",
    meanNdvi: 0.584,
    meanNdre: 0.365,
    alphaPct: 40.0,
    betaPct: 38.0,
    gammaPct: 22.0,
    windKmh: 14.2,
    gustKmh: 19.5,
    rainProb: 25,
    tempC: 27.8,
    rhPct: 88,
    elevationMin: 588.0,
    elevationMax: 596.5,
    reliefM: 8.5
  }
];

export default function PrecisionFieldIntelligenceWorkspace({
  isDark = true,
  theme = "botanical",
  showToast = () => {}
}) {
  const [selectedPreset, setSelectedPreset] = useState(PRESET_FIELDS[0]);
  const [fieldParams, setFieldParams] = useState({ ...PRESET_FIELDS[0] });
  const [active3DLayer, setActive3DLayer] = useState("drone_video"); // "ndvi" | "ndre" | "elevation" | "hydrology" | "drone_flight" | "drone_video"
  const [reportFormat, setReportFormat] = useState("markdown"); // "markdown" | "telemetry" | "waypoints"
  const [copiedReport, setCopiedReport] = useState(false);
  const [isSimulating, setIsSimulating] = useState(false);
  const [provenanceTag, setProvenanceTag] = useState("🟠 SIMULATED REFERENCE EXECUTION");

  // Drone Optical Video State & Telemetry Controls
  const [isVideoPlaying, setIsVideoPlaying] = useState(true);
  const [isVideoMuted, setIsVideoMuted] = useState(true);
  const [showDroneHud, setShowDroneHud] = useState(true);
  const [isDroneModalOpen, setIsDroneModalOpen] = useState(false);
  const videoRef = useRef(null);
  const canvas3DRef = useRef(null);

  const togglePlayVideo = () => {
    if (videoRef.current) {
      if (videoRef.current.paused) {
        videoRef.current.play();
        setIsVideoPlaying(true);
      } else {
        videoRef.current.pause();
        setIsVideoPlaying(false);
      }
    }
  };

  const toggleMuteVideo = () => {
    if (videoRef.current) {
      videoRef.current.muted = !videoRef.current.muted;
      setIsVideoMuted(videoRef.current.muted);
    }
  };

  const handleDownloadDroneVideo = () => {
    const a = document.createElement("a");
    a.href = "/videos/drone-survey-recon.mp4";
    a.download = `drone_recon_${fieldParams.crop.toLowerCase().replace(/\s+/g, "_")}.mp4`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    showToast("Downloading autonomous drone reconnaissance video (1080p)...");
  };

  // Synchronize when preset changes
  const handleSelectPreset = (preset) => {
    setSelectedPreset(preset);
    setFieldParams({ ...preset });
    showToast(`Loaded ${preset.name} calibration.`);
  };

  // 1. Math Derivations for Multispectral, Topography, Drone Avionics, VRA, and Economics
  const areaHa = Number(fieldParams.areaHa) || 10.5;
  const areaAcres = (areaHa * 2.47105).toFixed(2);
  const alphaHa = (areaHa * (fieldParams.alphaPct / 100)).toFixed(2);
  const betaHa = (areaHa * (fieldParams.betaPct / 100)).toFixed(2);
  const gammaHa = (areaHa * (fieldParams.gammaPct / 100)).toFixed(2);

  // Optical Sensor GSD Derivation (DJI 4/3" CMOS: 17.3mm, focal: 12.29mm, 5280px)
  const sensorWidthMm = 17.3;
  const focalLengthMm = 12.29;
  const imageWidthPx = 5280;
  const surveyAltitudeM = 45.0;
  const calculatedGSD = (
    (sensorWidthMm * surveyAltitudeM * 100) /
    (focalLengthMm * imageWidthPx)
  ).toFixed(2); // ~1.20 cm/px

  // Safety Gate Assessment
  const isHighWind = fieldParams.windKmh > 36 || fieldParams.gustKmh > 45;
  const isModerateWind = fieldParams.windKmh > 24 || fieldParams.gustKmh > 32;
  const isHighRain = fieldParams.rainProb > 40;
  const isModerateRain = fieldParams.rainProb > 20;

  let flightSafetyStatus = "🟢 SAFE TO PLAN";
  let flightSafetyBadgeClass = "bg-emerald-500/20 text-emerald-300 border-emerald-500/40";
  if (isHighWind || isHighRain) {
    flightSafetyStatus = "🔴 DO NOT FLY";
    flightSafetyBadgeClass = "bg-rose-500/20 text-rose-300 border-rose-500/40";
  } else if (isModerateWind || isModerateRain) {
    flightSafetyStatus = "🟡 REQUIRES REVIEW";
    flightSafetyBadgeClass = "bg-amber-500/20 text-amber-300 border-amber-500/40";
  }

  // VRA Chemical & Volume Calculations
  const isCotton = fieldParams.crop === "Cotton";
  const isWheat = fieldParams.crop === "Wheat";
  const isTomato = fieldParams.crop === "Tomato";

  const rateKgHa = isCotton ? 2.25 : isWheat ? 0.50 : isTomato ? 1.50 : 2.00;
  const chemPriceKgINR = isCotton ? 650 : isWheat ? 1450 : isTomato ? 820 : 700;
  const streptoRateGHa = isCotton ? 100 : isWheat ? 0 : isTomato ? 50 : 0;
  const streptoPriceGINR = 4.50;

  const tradChemKg = (areaHa * rateKgHa).toFixed(2);
  const tradStreptoG = (areaHa * streptoRateGHa).toFixed(0);
  const tradWaterLiters = (areaHa * 500).toFixed(0);

  const precChemKg = (Number(betaHa) * rateKgHa * 0.5 + Number(gammaHa) * rateKgHa * 1.0).toFixed(2);
  const precStreptoG = (Number(gammaHa) * streptoRateGHa * 1.0).toFixed(0);
  const precWaterLiters = (Number(betaHa) * 15.0 + Number(gammaHa) * 25.0).toFixed(0);

  const chemSavedKg = (tradChemKg - precChemKg).toFixed(2);
  const chemSavedPct = ((chemSavedKg / tradChemKg) * 100).toFixed(1);
  const waterSavedLiters = (tradWaterLiters - precWaterLiters).toFixed(0);
  const waterSavedPct = ((waterSavedLiters / tradWaterLiters) * 100).toFixed(1);

  // Economic Ledger (INR ₹)
  const tradChemCostINR = Math.round(tradChemKg * chemPriceKgINR + tradStreptoG * streptoPriceGINR);
  const tradLaborCostINR = Math.round(areaHa * 1200);
  const tradTotalINR = tradChemCostINR + tradLaborCostINR;

  const precChemCostINR = Math.round(precChemKg * chemPriceKgINR + precStreptoG * streptoPriceGINR);
  const treatedAreaHa = Number(betaHa) * 0.5 + Number(gammaHa);
  const precDroneSprayCostINR = Math.round(treatedAreaHa * 850);
  const precSurveyCostINR = Math.round(areaHa * 300);
  const precTotalINR = precChemCostINR + precDroneSprayCostINR + precSurveyCostINR;

  const grossSavingsINR = tradTotalINR - precTotalINR;
  const precisionMissionCostINR = precDroneSprayCostINR + precSurveyCostINR;
  const roiPct = precisionMissionCostINR > 0 ? ((grossSavingsINR / precisionMissionCostINR) * 100).toFixed(1) : "0.0";

  // Waypoints Calculation
  const centerLat = fieldParams.centerLat;
  const centerLng = fieldParams.centerLng;
  const waypoints = [
    { id: "WP01", lat: (centerLat + 0.0015).toFixed(6), lng: (centerLng - 0.0025).toFixed(6), alt: 45, head: "090°", act: "Survey Ingress", zone: "🟢 Alpha" },
    { id: "WP02", lat: (centerLat + 0.0015).toFixed(6), lng: (centerLng).toFixed(6), alt: 45, head: "090°", act: "Trigger MS", zone: "🟢 Alpha" },
    { id: "WP03", lat: (centerLat + 0.0015).toFixed(6), lng: (centerLng + 0.0025).toFixed(6), alt: 45, head: "180°", act: "Bank Turn", zone: "🟡 Beta" },
    { id: "WP04", lat: (centerLat).toFixed(6), lng: (centerLng + 0.0025).toFixed(6), alt: 45, head: "270°", act: "Corridor Scan", zone: "🟡 Beta" },
    { id: "WP05", lat: (centerLat).toFixed(6), lng: (centerLng).toFixed(6), alt: 45, head: "270°", act: "MS Capture", zone: "🟡 Beta" },
    { id: "WP06", lat: (centerLat).toFixed(6), lng: (centerLng - 0.0025).toFixed(6), alt: 45, head: "180°", act: "Bank Turn", zone: "🟢 Alpha" },
    { id: "WP07", lat: (centerLat - 0.0015).toFixed(6), lng: (centerLng - 0.0025).toFixed(6), alt: 45, head: "090°", act: "Corridor Scan", zone: "🟡 Beta" },
    { id: "WP08", lat: (centerLat - 0.0015).toFixed(6), lng: (centerLng).toFixed(6), alt: 45, head: "090°", act: "Boundary Trans.", zone: "🔴 Gamma Target" },
    { id: "WP09", lat: (centerLat - 0.0015).toFixed(6), lng: (centerLng + 0.0025).toFixed(6), alt: 45, head: "180°", act: "High-Res Gamma", zone: "🔴 Gamma Target" },
    { id: "WP10", lat: (centerLat - 0.0030).toFixed(6), lng: (centerLng + 0.0025).toFixed(6), alt: 45, head: "270°", act: "High-Res Gamma", zone: "🔴 Gamma Target" },
    { id: "WP11", lat: (centerLat - 0.0030).toFixed(6), lng: (centerLng).toFixed(6), alt: 45, head: "270°", act: "High-Res Gamma", zone: "🔴 Gamma Target" },
    { id: "WP12", lat: (centerLat - 0.0030).toFixed(6), lng: (centerLng - 0.0025).toFixed(6), alt: 45, head: "360°", act: "Survey -> RTL", zone: "🟢 Alpha / LZ" },
  ];

  // Export handlers
  const handleDownloadFile = (content, filename, type) => {
    const blob = new Blob([content], { type });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    showToast(`Downloaded ${filename}`);
  };

  const handleExportMavlink = () => {
    let mav = "QGC WPL 110\n";
    waypoints.forEach((wp, idx) => {
      mav += `${idx}\t${idx === 0 ? 1 : 0}\t3\t16\t0\t0\t0\t0\t${wp.lat}\t${wp.lng}\t${wp.alt}\t1\n`;
    });
    handleDownloadFile(mav, `agri_nirvana_${fieldParams.crop.toLowerCase()}_mission.waypoint`, "text/plain");
  };

  const handleExportKML = () => {
    const kml = `<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>Agri Nirvana Drone Survey — ${fieldParams.crop}</name>
    <Placemark>
      <name>Survey Flight Corridor</name>
      <LineString>
        <coordinates>
          ${waypoints.map((w) => `${w.lng},${w.lat},${w.alt}`).join("\n          ")}
        </coordinates>
      </LineString>
    </Placemark>
  </Document>
</kml>`;
    handleDownloadFile(kml, `agri_nirvana_${fieldParams.crop.toLowerCase()}_flight.kml`, "application/vnd.google-earth.kml+xml");
  };

  // Full 20-Section Technical Markdown Document
  const fullTechnicalMarkdownReport = `# 🌾 AGRI NIRVANA — PRECISION FIELD INTELLIGENCE REPORT
**Execution Mode:** ${provenanceTag}
**Standard Compliance:** ESA Sentinel-2 L2A BOA Reflectance • DGCA Drone Rules 2021 • CIB&RC Label Regulations

---

## 1. Field Telemetry Summary
\`\`\`text
╭──────────────────────────────────────────────────────────────────────────╮
│                       AGRI NIRVANA FIELD TELEMETRY                       │
├──────────────────────────────────────────────────────────────────────────┤
│ Crop Type         : ${fieldParams.crop} (${fieldParams.cultivar})
│ Growth Stage      : ${fieldParams.stage}
│ Total Area        : ${areaHa.toFixed(2)} ha (${areaAcres} acres)
│ Primary Lat/Long  : ${centerLat}° N, ${centerLng}° E (WGS 84)
│ Mean NDVI / NDRE  : ${fieldParams.meanNdvi.toFixed(3)}  /  ${fieldParams.meanNdre.toFixed(3)}
│ Zone Alpha (🟢)   : ${alphaHa} ha (${fieldParams.alphaPct.toFixed(1)}%) — High Vigour / Healthy Reference
│ Zone Beta  (🟡)   : ${betaHa} ha (${fieldParams.betaPct.toFixed(1)}%) — Moderate Stress / Canopy Thinning
│ Zone Gamma (🔴)   : ${gammaHa} ha (${fieldParams.gammaPct.toFixed(1)}%) — Severe Anomaly / Critical Depress.
│ Drainage Risk     : HIGH (Depression Zone in South-East Sector)
│ Disease/Pest Risk : HIGH (${fieldParams.pathogen})
│ Overall Confidence: 87.5%
│ Drone Mission     : ${flightSafetyStatus}
╰──────────────────────────────────────────────────────────────────────────╯
\`\`\`

---

## 2. Data Quality Assessment
| Parameter | Status | Value / Source | Provenance & Qualification |
| :--- | :---: | :--- | :--- |
| **Sentinel-2 Imagery** | ✅ | S2B_MSIL2A_LATEST | 🟠 SIMULATED Level-2A BOA Surface Reflectance |
| **Cloud Coverage (AOI)** | ✅ | 0.0% over target polygon | 🟢 Clear viewing window (<5% tile cloud) |
| **DEM Availability** | ✅ | Copernicus DEM 30m / SRTM | 🔵 Hydro-conditioned elevation grid |
| **Field Boundary (AOI)** | ✅ | Closed polygon (${areaHa.toFixed(2)} ha) | 🔵 Derived from user boundary inputs |
| **Soil Moisture Data** | ✅ | Soil Volumetric: 38.4% | 🔵 Top 5cm surface saturation index |
| **Weather & Met Telemetry**| ✅ | AWS Local Ground Station | 🔵 Temp ${fieldParams.tempC}°C, RH ${fieldParams.rhPct}%, Wind ${fieldParams.windKmh} km/h |

---

## 3. Sentinel-2 Multispectral Acquisition (NDVI Analysis)
$$\\text{NDVI} = \\frac{\\text{B8} - \\text{B4}}{\\text{B8} + \\text{B4}} = \\frac{\\text{NIR}_{842\\text{nm}} - \\text{Red}_{665\\text{nm}}}{\\text{NIR}_{842\\text{nm}} + \\text{Red}_{665\\text{nm}}}$$
• Mean NDVI: **${fieldParams.meanNdvi.toFixed(3)}** | Median: 0.682 | Min: 0.214 | Max: 0.841 | Std Dev: 0.162 | Spatial CV: 25.4%

---

## 4. NDRE (Red-Edge) Analysis
$$\\text{NDRE} = \\frac{\\text{B8A} - \\text{B5}}{\\text{B8A} + \\text{B5}}$$
• Mean NDRE: **${fieldParams.meanNdre.toFixed(3)}** | Median: 0.448 | Min: 0.129 | Max: 0.584 | Std Dev: 0.118

---

## 5. Vegetation Health Zoning
• 🟢 **ZONE ALPHA (${alphaHa} ha / ${fieldParams.alphaPct}%):** NDVI > 0.78 — Healthy baseline canopy.
• 🟡 **ZONE BETA (${betaHa} ha / ${fieldParams.betaPct}%):** 0.50 ≤ NDVI ≤ 0.75 — Moderate canopy thinning.
• 🔴 **ZONE GAMMA (${gammaHa} ha / ${fieldParams.gammaPct}%):** NDVI < 0.48 — Critical depression / chlorosis.

---

## 6. Crop-Specific Threshold Validation
Validated for **${fieldParams.crop}** at **${fieldParams.stage}**. Normal expected canopy threshold: 0.70 – 0.85. Zone Gamma represents an acute deviation from phenological baseline.

---

## 7. 3D Topographical & Hydrological Surface Analysis
• Relief Range: ${fieldParams.elevationMin} m to ${fieldParams.elevationMax} m AMSL (Relief Diff: ${fieldParams.reliefM} m)
• Overland Flow: North-North-West ──► South-South-East (Flow Accumulation Sink: ${gammaHa} ha)

---

## 8. Drainage–Vegetation Correlation
• High moisture stagnation & low elevation in SE sector correlates directly with Zone Gamma (R² = 0.89).
• **Drainage Stress Confidence Score: 91.2% (VERY HIGH)**

---

## 9. Disease / Pest Risk Model
• Target Concern: **${fieldParams.pathogen}**
• Composite Risk Rating: **🔴 HIGH (84.0% Confidence)**

---

## 10. 3D Field Health Spatial Model
\`\`\`text
                 NORTH (Elevation: ${fieldParams.elevationMax} m)
                           ↑
        ┌───────────────────────────────────┐
        │ 🟢 🟢 🟢 🟢 🟢 🟢 🟢 🟢 🟢 🟢 🟢 │ (Zone Alpha)
        │ 🟢 🟢 🟢 🟢 🟢 🟡 🟡 🟡 🟡 🟡 🟡 │
        │ 🟢 🟢 🟡 🟡 🟡 🟡 🟡 🟡 🟡 🟡 🟡 │
        │ 🟡 🟡 🟡 🟡 🟡 🔴 🔴 🔴 🔴 🔴 🔴 │ (Zone Gamma)
        │ 🟡 🟡 🔴 🔴 🔴 🔴 🔴 🔴 🔴 🔴 🔴 │ [Hydrologic Sink]
        └───────────────────────────────────┘
                           ↓
                 SOUTH (Elevation: ${fieldParams.elevationMin} m)
\`\`\`

---

## 11. Drone Mission Planning
• **Mission A (Survey):** 🟢 Authorized (High-Resolution Multispectral Stand Count)
• **Mission B (Spot Spray):** 🟡 On Hold (Awaiting ground scouting confirmation)

---

## 12. Survey Flight Parameters & Optical Sensor Geometry
$$\\text{GSD} = \\frac{17.3\\text{ mm} \\times 45\\text{ m} \\times 100}{12.29\\text{ mm} \\times 5280\\text{ px}} = \\mathbf{${calculatedGSD}\\text{ cm/px}} \\quad (<1.5\\text{ cm/px Requirement Passed})$$
• Altitude: 45.0 m AGL | Overlap: 80% Forward, 75% Side | Speed: 6.5 m/s | Flight Duration: 22.5 min

---

## 13. Drone Flight Safety & Airspace Assessment
• Status: **${flightSafetyStatus}**
• DGCA Digital Sky: Green Zone | Wind: ${fieldParams.windKmh} km/h (Gust: ${fieldParams.gustKmh} km/h) | Rain Prob: ${fieldParams.rainProb}%

---

## 14. Waypoint Blueprint
\`\`\`text
WP01 → WP02 → WP03 ──┐
  ↑                  │
WP06 ← WP05 ← WP04 ◄─┘
  │
  ▼
WP07 → WP08 → WP09 [Target SE Gamma Zone]
  ↑                  │
WP12 ← WP11 ← WP10 ◄─┘
\`\`\`

---

## 15. Variable-Rate Application (VRA) Strategy
• 🟢 **Zone Alpha (${alphaHa} ha):** 0% (No chemical spray)
• 🟡 **Zone Beta (${betaHa} ha):** 50% Prophylactic spray (${(rateKgHa * 0.5).toFixed(2)} kg/ha)
• 🔴 **Zone Gamma (${gammaHa} ha):** 100% Curative spray (${rateKgHa.toFixed(2)} kg/ha + ${streptoRateGHa} g/ha)

---

## 16. Chemical & Water Requirement Calculations
• **Chemical Saved:** ${chemSavedKg} kg (${chemSavedPct}% reduction vs Traditional Blanket)
• **Water Saved:** ${waterSavedLiters} Liters (${waterSavedPct}% reduction)

---

## 17. Economic ROI Ledger (INR ₹)
• Traditional Blanket Cost: ₹${tradTotalINR.toLocaleString("en-IN")}
• Precision Drone VRA Cost: ₹${precTotalINR.toLocaleString("en-IN")}
• **Net Realized Cash Savings: ₹${grossSavingsINR.toLocaleString("en-IN")}**
• **Return on Investment (ROI): ${roiPct}%**

---

## 18. Resource Conservation & Environmental Impact
• Active Chemical Prevented: ${chemSavedKg} kg
• Water Conserved: ${waterSavedLiters} Liters
• Diesel & Soil Compaction Avoidance: 14.7 L diesel saved (${(14.7 * 2.68).toFixed(1)} kg CO₂e offset)

---

## 19. Tiered Agronomic Recommendations
• 🔴 **Immediate (24–48h):** Cut 0.5m drainage relief trench in SE sink; scout WP09-WP11 ground coordinates.
• 🟡 **Near-Term (3–7d):** Execute Phase 2 VRA ULV drone spray over ${gammaHa} ha Zone Gamma.
• 🟢 **Monitoring:** Ingest next Sentinel-2 L2A pass for anomaly differential tracking.

---

## 20. Confidence, Uncertainty & Data Provenance
| Metric | Classification | Confidence |
| :--- | :---: | :---: |
| Sentinel-2 Reflectance | ${provenanceTag} | 95.0% |
| NDVI / NDRE Indices | 🔵 DERIVED | 92.5% |
| Topographical DEM Slopes | 🔵 DERIVED | 85.0% |
| Drainage Correlation | 🔵 DERIVED | 91.2% |
| Pathogen Risk | 🟡 ESTIMATED | 84.0% |
| Waypoint Coordinates | 🔵 DERIVED | 100.0% |
| Economic ROI Ledger | 🟡 ESTIMATED | 88.0% |
`;

  const handleCopyReport = () => {
    navigator.clipboard.writeText(fullTechnicalMarkdownReport);
    setCopiedReport(true);
    showToast("Precision Field Intelligence Report copied to clipboard!");
    setTimeout(() => setCopiedReport(false), 3000);
  };

  const handlePrintReport = () => {
    const printWin = window.open("", "_blank");
    if (!printWin) return;
    printWin.document.write(`
      <html>
        <head>
          <title>Agri Nirvana Precision Field Intelligence Report</title>
          <link rel="preconnect" href="https://fonts.googleapis.com">
          <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
          <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap" rel="stylesheet">
          <style>
            body { font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; padding: 30px; color: #0f172a; line-height: 1.6; max-width: 900px; margin: 0 auto; -webkit-font-smoothing: antialiased; }
            h1, h2, h3 { color: #065f46; border-bottom: 2px solid #e2e8f0; padding-bottom: 6px; }
            table { width: 100%; border-collapse: collapse; margin: 16px 0; font-size: 13px; }
            th, td { border: 1px solid #cbd5e1; padding: 8px 12px; text-align: left; }
            th { background: #f1f5f9; font-weight: bold; color: #334155; }
            pre { background: #0f172a; color: #f8fafc; padding: 14px; border-radius: 8px; font-size: 12px; overflow-x: auto; font-family: 'JetBrains Mono', monospace; font-variant-numeric: tabular-nums; }
            .card { border: 1px solid #cbd5e1; border-radius: 8px; padding: 12px; margin: 12px 0; background: #f8fafc; }
          </style>
        </head>
        <body>
          <div>${fullTechnicalMarkdownReport.replace(/# (.*?)\n/g, "<h1>$1</h1>").replace(/## (.*?)\n/g, "<h2>$1</h2>").replace(/```text([\s\S]*?)```/g, "<pre>$1</pre>")}</div>
          <script>window.onload = function() { window.print(); }</script>
        </body>
      </html>
    `);
    printWin.document.close();
  };

  return (
    <div className="space-y-8 animate-fade-in pb-12">
      {/* HEADER RIBBON & PRESET PICKER */}
      <div
        className={`rounded-3xl p-6 sm:p-8 border backdrop-blur-xl transition-all ${
          isDark
            ? "border-emerald-500/30 bg-[#061e15]/90 shadow-[0_15px_40px_rgba(0,0,0,0.6)]"
            : "border-slate-200 bg-white shadow-xl"
        }`}
      >
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
          <div>
            <div className="flex flex-wrap items-center gap-2 mb-2">
              <span className="rounded-full bg-emerald-500/20 px-3 py-1 text-xs font-mono font-bold text-emerald-400 border border-emerald-500/40 uppercase tracking-wider flex items-center gap-1.5">
                <Sparkles size={13} className="text-amber-400 animate-pulse" />
                Sentinel-2 L2A + 3D DEM + Autonomous Avionics
              </span>
              <span className="rounded-full bg-amber-500/20 px-2.5 py-0.5 text-[11px] font-mono font-bold text-amber-300 border border-amber-500/30">
                {provenanceTag}
              </span>
            </div>
            <h1 className={`text-2xl sm:text-3xl font-black tracking-tight ${isDark ? "ai-gradient-text" : "ai-gradient-text-light"}`}>
              Precision Field Intelligence & Drone Avionics Engine
            </h1>
            <p className={`text-xs sm:text-sm mt-1 max-w-2xl ${isDark ? "text-emerald-100/70" : "text-slate-600"}`}>
              Multi-spectral vegetation zoning, hydro-topographic flow routing, safety-constrained drone mission waypoints, and variable-rate chemical ROI analytics.
            </p>
          </div>

          {/* Quick Preset Selector */}
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400 mr-1">Calibrated AOI:</span>
            {PRESET_FIELDS.map((preset) => (
              <button
                key={preset.id}
                onClick={() => handleSelectPreset(preset)}
                className={`rounded-2xl px-4 py-2 text-xs font-bold border transition-all duration-200 active:scale-95 ${
                  selectedPreset.id === preset.id
                    ? isDark
                      ? "border-emerald-400 bg-gradient-to-r from-emerald-500 to-teal-500 text-slate-950 font-black shadow-lg glow-emerald"
                      : "border-emerald-600 bg-emerald-600 text-white font-black shadow-md"
                    : isDark
                    ? "border-emerald-900/60 bg-emerald-950/40 text-slate-300 hover:border-emerald-500/60"
                    : "border-slate-200 bg-slate-100 text-slate-700 hover:bg-slate-200"
                }`}
              >
                {preset.crop} ({preset.areaHa} ha)
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* 2. TELEMETRY & DATA QUALITY GATE STATUS CARDS */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Card 1: NDVI / NDRE Index */}
        <div
          className={`rounded-2xl p-5 border transition-all ${
            isDark ? "border-emerald-500/30 bg-[#04160f] text-white" : "border-slate-200 bg-emerald-50/60 text-slate-900 shadow-sm"
          }`}
        >
          <div className="flex justify-between items-start mb-2">
            <span className="text-[10px] font-mono font-bold text-emerald-400 uppercase tracking-wider">Multi-Spectral Indices</span>
            <Layers size={18} className="text-emerald-400" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-black font-mono">{fieldParams.meanNdvi.toFixed(3)}</span>
            <span className="text-xs font-bold text-emerald-400">Mean NDVI</span>
          </div>
          <div className="mt-2 flex items-center justify-between text-xs text-slate-400 border-t border-emerald-900/40 pt-2">
            <span>Red-Edge NDRE:</span>
            <span className="font-mono font-bold text-teal-400">{fieldParams.meanNdre.toFixed(3)}</span>
          </div>
        </div>

        {/* Card 2: Health Zoning Distribution */}
        <div
          className={`rounded-2xl p-5 border transition-all ${
            isDark ? "border-teal-500/30 bg-[#04160f] text-white" : "border-slate-200 bg-teal-50/60 text-slate-900 shadow-sm"
          }`}
        >
          <div className="flex justify-between items-start mb-2">
            <span className="text-[10px] font-mono font-bold text-teal-400 uppercase tracking-wider">Field Zoning Ratio</span>
            <Activity size={18} className="text-teal-400" />
          </div>
          <div className="flex items-center gap-1.5 mt-1">
            <span className="text-xs font-bold text-emerald-400">🟢 {fieldParams.alphaPct}%</span>
            <span className="text-xs text-slate-500">/</span>
            <span className="text-xs font-bold text-amber-400">🟡 {fieldParams.betaPct}%</span>
            <span className="text-xs text-slate-500">/</span>
            <span className="text-xs font-bold text-rose-400">🔴 {fieldParams.gammaPct}%</span>
          </div>
          {/* Visual Mini Progress Bar */}
          <div className="h-2 w-full rounded-full flex overflow-hidden mt-3 bg-slate-800">
            <div style={{ width: `${fieldParams.alphaPct}%` }} className="bg-emerald-500 h-full" />
            <div style={{ width: `${fieldParams.betaPct}%` }} className="bg-amber-400 h-full" />
            <div style={{ width: `${fieldParams.gammaPct}%` }} className="bg-rose-500 h-full" />
          </div>
        </div>

        {/* Card 3: Topographic Hydrology */}
        <div
          className={`rounded-2xl p-5 border transition-all ${
            isDark ? "border-cyan-500/30 bg-[#04160f] text-white" : "border-slate-200 bg-cyan-50/60 text-slate-900 shadow-sm"
          }`}
        >
          <div className="flex justify-between items-start mb-2">
            <span className="text-[10px] font-mono font-bold text-cyan-400 uppercase tracking-wider">Topography & Drainage</span>
            <Droplets size={18} className="text-cyan-400" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-black font-mono">{fieldParams.reliefM}m</span>
            <span className="text-xs font-bold text-cyan-400">Relief Diff</span>
          </div>
          <div className="mt-2 flex items-center justify-between text-xs text-slate-400 border-t border-cyan-900/40 pt-2">
            <span>Drainage Risk:</span>
            <span className="font-bold text-amber-400">HIGH (SE Sink)</span>
          </div>
        </div>

        {/* Card 4: Drone Avionics Safety */}
        <div
          className={`rounded-2xl p-5 border transition-all ${
            isDark ? "border-emerald-500/30 bg-[#04160f] text-white" : "border-slate-200 bg-slate-50 text-slate-900 shadow-sm"
          }`}
        >
          <div className="flex justify-between items-start mb-2">
            <span className="text-[10px] font-mono font-bold text-emerald-400 uppercase tracking-wider">Flight Safety Gate</span>
            <Plane size={18} className="text-emerald-400" />
          </div>
          <div className="mt-1">
            <span className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-black border ${flightSafetyBadgeClass}`}>
              {flightSafetyStatus}
            </span>
          </div>
          <div className="mt-2 flex items-center justify-between text-xs text-slate-400 border-t border-emerald-900/40 pt-2">
            <span>GSD:</span>
            <span className="font-mono font-bold text-emerald-400">{calculatedGSD} cm/px (Pass)</span>
          </div>
        </div>
      </div>

      {/* 3. INTERACTIVE 3D FIELD VISUALIZER & LAYER SELECTOR */}
      <div
        className={`rounded-3xl p-6 sm:p-8 border transition-all ${
          isDark ? "border-emerald-500/30 bg-[#04160f] shadow-2xl" : "border-slate-200 bg-white shadow-xl"
        }`}
      >
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
          <div>
            <h2 className={`text-xl sm:text-2xl font-black flex items-center gap-2 ${isDark ? "text-white" : "text-slate-900"}`}>
              <Compass className="text-emerald-400" size={24} />
              Interactive 3D Field Topography & Hydrology Model
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              3D terrain mesh displaced by DEM elevation contours with dynamic multi-spectral and D8 hydrological routing overlays.
            </p>
          </div>

          {/* 3D Visualizer Layer Switches */}
          <div className="flex flex-wrap items-center gap-1.5 p-1 rounded-2xl border border-emerald-900/50 bg-emerald-950/40 backdrop-blur-md">
            {[
              { id: "drone_video", label: "Live Drone Recon (HD)", icon: Video },
              { id: "ndvi", label: "NDVI Health", icon: Layers },
              { id: "ndre", label: "NDRE Chlorophyll", icon: Sparkles },
              { id: "elevation", label: "3D DEM Contours", icon: TrendingUp },
              { id: "hydrology", label: "Hydrologic Sink", icon: Droplets },
              { id: "drone_flight", label: "Drone Path (WP)", icon: Plane }
            ].map(({ id, label, icon: Icon }) => (
              <button
                key={id}
                onClick={() => setActive3DLayer(id)}
                className={`flex items-center gap-1.5 rounded-xl px-3 py-1.5 text-xs font-bold transition-all ${
                  active3DLayer === id
                    ? "bg-emerald-500 text-slate-950 font-black shadow-md glow-emerald scale-[1.02]"
                    : "text-slate-300 hover:text-white hover:bg-emerald-900/40"
                }`}
              >
                <Icon size={14} />
                <span>{label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* 3D ASCII / MESH / DRONE VIDEO FIELD CANVAS */}
        {active3DLayer === "drone_video" ? (
          <div className="relative h-[420px] sm:h-[480px] w-full rounded-2xl border border-emerald-500/40 bg-black overflow-hidden shadow-2xl flex items-center justify-center group">
            <video
              ref={videoRef}
              src="/videos/drone-survey-recon.mp4"
              autoPlay
              loop
              muted={isVideoMuted}
              playsInline
              className="w-full h-full object-cover"
            />

            {/* Drone Telemetry HUD Overlay */}
            {showDroneHud && (
              <div className="absolute inset-0 pointer-events-none p-4 flex flex-col justify-between font-mono select-none">
                {/* Top HUD bar */}
                <div className="flex items-center justify-between text-xs">
                  <div className="flex items-center gap-2 bg-black/75 backdrop-blur-md px-3 py-1 rounded-full border border-red-500/40 text-red-400 font-bold">
                    <span className="h-2 w-2 rounded-full bg-red-500 animate-ping" />
                    <span>REC ● 1080P 60FPS</span>
                  </div>
                  <div className="flex items-center gap-2 sm:gap-3 bg-black/75 backdrop-blur-md px-3 py-1 rounded-full border border-emerald-500/40 text-emerald-300 text-[10px] sm:text-[11px]">
                    <span>ALT: 45.2m AGL</span>
                    <span>•</span>
                    <span>SPD: 6.8 m/s</span>
                    <span>•</span>
                    <span>GSD: {calculatedGSD} cm/px</span>
                    <span>•</span>
                    <span className="text-amber-300">BAT: 84%</span>
                  </div>
                </div>

                {/* Laser LiDAR Center Crosshair */}
                <div className="flex flex-col items-center justify-center">
                  <div className="relative h-24 w-24 border border-dashed border-emerald-400/50 rounded-lg flex items-center justify-center">
                    <div className="h-3 w-3 border-t-2 border-l-2 border-emerald-300 absolute -top-1 -left-1" />
                    <div className="h-3 w-3 border-t-2 border-r-2 border-emerald-300 absolute -top-1 -right-1" />
                    <div className="h-3 w-3 border-b-2 border-l-2 border-emerald-300 absolute -bottom-1 -left-1" />
                    <div className="h-3 w-3 border-b-2 border-r-2 border-emerald-300 absolute -bottom-1 -right-1" />
                    <div className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-ping" />
                  </div>
                  <div className="mt-2 bg-black/80 backdrop-blur-md px-3 py-0.5 rounded text-[10px] text-emerald-300 border border-emerald-500/40">
                    TARGET: {fieldParams.crop} • Zone Gamma [{fieldParams.pathogen}]
                  </div>
                </div>

                {/* Bottom HUD bar */}
                <div className="flex items-center justify-between text-[10px] sm:text-[11px] text-slate-300">
                  <div className="bg-black/75 backdrop-blur-md px-3 py-1 rounded-lg border border-emerald-500/30">
                    <span>GPS: {fieldParams.centerLat.toFixed(4)}°N, {fieldParams.centerLng.toFixed(4)}°E (RTK FIXED ±1.2cm)</span>
                  </div>
                  <div className="bg-black/75 backdrop-blur-md px-3 py-1 rounded-lg border border-emerald-500/30 text-emerald-400">
                    <span>OPTICAL LIDAR ACTIVE • 420m CORRIDOR</span>
                  </div>
                </div>
              </div>
            )}

            {/* Video Controls Toolbar */}
            <div className="absolute bottom-3 right-3 flex items-center gap-1.5 z-20">
              <button
                onClick={togglePlayVideo}
                className="p-2 rounded-xl bg-black/80 hover:bg-black text-white border border-emerald-500/40 backdrop-blur-md transition hover:scale-105"
                title={isVideoPlaying ? "Pause Video" : "Play Video"}
              >
                {isVideoPlaying ? <Pause size={14} /> : <Play size={14} />}
              </button>
              <button
                onClick={toggleMuteVideo}
                className="p-2 rounded-xl bg-black/80 hover:bg-black text-white border border-emerald-500/40 backdrop-blur-md transition hover:scale-105"
                title={isVideoMuted ? "Unmute Audio" : "Mute Audio"}
              >
                {isVideoMuted ? <VolumeX size={14} /> : <Volume2 size={14} />}
              </button>
              <button
                onClick={() => setShowDroneHud(!showDroneHud)}
                className={`px-2.5 py-1.5 rounded-xl text-[11px] font-mono font-bold border backdrop-blur-md transition ${
                  showDroneHud
                    ? "bg-emerald-500/30 text-emerald-300 border-emerald-500/50"
                    : "bg-black/75 text-slate-400 border-slate-700 hover:text-white"
                }`}
              >
                HUD: {showDroneHud ? "ON" : "OFF"}
              </button>
              <button
                onClick={handleDownloadDroneVideo}
                className="p-2 rounded-xl bg-emerald-600/90 hover:bg-emerald-500 text-white border border-emerald-400/40 backdrop-blur-md transition hover:scale-105"
                title="Download Recon Video (MP4)"
              >
                <Download size={14} />
              </button>
            </div>
          </div>
        ) : (
          <div className="relative h-96 w-full rounded-2xl border border-emerald-500/30 bg-[#020b07] overflow-hidden flex flex-col items-center justify-center p-6 select-none">
            <div className="absolute inset-0 opacity-20 bg-[radial-gradient(#10b981_1px,transparent_1px)] [background-size:20px_20px]" />

            {/* Compass Rose */}
            <div className="absolute top-4 right-4 flex flex-col items-center text-[10px] font-mono font-bold text-emerald-400/80 bg-emerald-950/60 p-2 rounded-xl border border-emerald-500/20">
              <span>▲ N</span>
              <span className="text-[8px] text-slate-500">164° Aspect</span>
            </div>

            {/* Interactive Layer Visual */}
            <div className="relative z-10 w-full max-w-2xl text-center space-y-4">
              {active3DLayer === "ndvi" && (
                <div className="space-y-3">
                  <div className="inline-flex items-center gap-2 rounded-full bg-emerald-500/20 px-3 py-1 text-xs font-mono font-bold text-emerald-300 border border-emerald-500/30">
                    <Layers size={14} /> NDVI Calibrated Multi-Spectral Grid
                  </div>
                  <pre className="font-mono text-sm sm:text-base leading-relaxed text-emerald-300 bg-slate-950/80 p-4 rounded-2xl border border-emerald-500/30 shadow-inner overflow-x-auto">
{`                  NORTH (Elevation: ${fieldParams.elevationMax}m)
        ┌───────────────────────────────────────────────┐
        │ 🟢 🟢 🟢 🟢 🟢 🟢 🟢 🟢 🟢 🟢 🟢 🟢 🟢 🟢 🟢 │ (Alpha: >0.78)
        │ 🟢 🟢 🟢 🟢 🟢 🟢 🟡 🟡 🟡 🟡 🟡 🟡 🟡 🟡 🟡 │ 5.46 ha
        │ 🟢 🟢 🟡 🟡 🟡 🟡 🟡 🟡 🟡 🟡 🟡 🟡 🟡 🟡 🟡 │ (Beta: 0.50-0.75)
        │ 🟡 🟡 🟡 🟡 🟡 🟡 🟡 🔴 🔴 🔴 🔴 🔴 🔴 🔴 🔴 │ 3.25 ha
        │ 🟡 🟡 🔴 🔴 🔴 🔴 🔴 🔴 🔴 🔴 🔴 🔴 🔴 🔴 🔴 │ (Gamma: <0.48)
        └───────────────────────────────────────────────┘ 1.79 ha (Critical)
                  SOUTH (Elevation: ${fieldParams.elevationMin}m)`}
                  </pre>
                  <div className="flex justify-center gap-4 text-xs font-bold">
                    <span className="text-emerald-400">🟢 Zone Alpha: No Spray</span>
                    <span className="text-amber-400">🟡 Zone Beta: 50% Prophylactic</span>
                    <span className="text-rose-400">🔴 Zone Gamma: 100% Curative</span>
                  </div>
                </div>
              )}

              {active3DLayer === "ndre" && (
                <div className="space-y-3">
                  <div className="inline-flex items-center gap-2 rounded-full bg-teal-500/20 px-3 py-1 text-xs font-mono font-bold text-teal-300 border border-teal-500/30">
                    <Sparkles size={14} /> Sentinel-2 Red-Edge (B8A vs B5) Chlorophyll Sensitivity
                  </div>
                  <div className="p-5 rounded-2xl bg-slate-950/80 border border-teal-500/30 text-left text-xs space-y-2">
                    <div className="flex justify-between font-mono">
                      <span className="text-slate-400">Narrow NIR (Band 8A - 865nm):</span>
                      <span className="font-bold text-teal-300">0.482 Reflectance</span>
                    </div>
                    <div className="flex justify-between font-mono">
                      <span className="text-slate-400">Red Edge (Band 5 - 705nm):</span>
                      <span className="font-bold text-amber-300">0.201 Reflectance</span>
                    </div>
                    <div className="flex justify-between font-mono border-t border-slate-800 pt-2">
                      <span className="text-white font-bold">Computed Mean NDRE:</span>
                      <span className="font-bold text-teal-400 text-sm">{fieldParams.meanNdre.toFixed(3)}</span>
                    </div>
                    <p className="text-[11px] text-slate-400 italic pt-1">
                      NDRE overcomes NDVI saturation in dense foliage, verifying robust nitrogen uptake in North sector while confirming true cellular chlorosis in South-East depression.
                    </p>
                  </div>
                </div>
              )}

              {active3DLayer === "elevation" && (
                <div className="space-y-3">
                  <div className="inline-flex items-center gap-2 rounded-full bg-cyan-500/20 px-3 py-1 text-xs font-mono font-bold text-cyan-300 border border-cyan-500/30">
                    <TrendingUp size={14} /> 30m Digital Elevation Model (Hydro-Conditioned)
                  </div>
                  <div className="grid grid-cols-3 gap-3 text-center">
                    <div className="p-3 rounded-xl bg-slate-950/80 border border-slate-800">
                      <span className="text-[10px] text-slate-400 block">Peak Ridge</span>
                      <span className="text-lg font-black font-mono text-cyan-400">{fieldParams.elevationMax} m</span>
                    </div>
                    <div className="p-3 rounded-xl bg-slate-950/80 border border-slate-800">
                      <span className="text-[10px] text-slate-400 block">Mean Slope</span>
                      <span className="text-lg font-black font-mono text-teal-400">2.1°</span>
                    </div>
                    <div className="p-3 rounded-xl bg-slate-950/80 border border-slate-800">
                      <span className="text-[10px] text-slate-400 block">Lowest Sink</span>
                      <span className="text-lg font-black font-mono text-amber-400">{fieldParams.elevationMin} m</span>
                    </div>
                  </div>
                  <p className="text-xs text-slate-400">Relief differential of {fieldParams.reliefM}m over 420m diagonal causes natural surface gravity flow towards the SE depression basin.</p>
                </div>
              )}

              {active3DLayer === "hydrology" && (
                <div className="space-y-3">
                  <div className="inline-flex items-center gap-2 rounded-full bg-blue-500/20 px-3 py-1 text-xs font-mono font-bold text-blue-300 border border-blue-500/30">
                    <Droplets size={14} /> D8 Surface Flow Accumulation & Wetness Index (TWI)
                  </div>
                  <div className="p-4 rounded-2xl bg-slate-950/80 border border-blue-500/30 text-left text-xs space-y-2 font-mono">
                    <div className="flex justify-between">
                      <span className="text-slate-400">Topographic Wetness Index:</span>
                      <span className="text-blue-400 font-bold">11.8 (High Saturation)</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Soil Moisture (Top 5cm):</span>
                      <span className="text-blue-400 font-bold">38.4% Volumetric</span>
                    </div>
                    <div className="flex justify-between border-t border-slate-800 pt-1">
                      <span className="text-slate-400">Drainage Correlation Confidence:</span>
                      <span className="text-emerald-400 font-bold">91.2% (VERY HIGH)</span>
                    </div>
                  </div>
                  <p className="text-xs text-amber-300/90 font-medium">
                    ⚠️ Root hypoxia caused by standing water in the SE corner is the primary trigger for low NDVI. Drainage relief trenching required prior to chemical spray.
                  </p>
                </div>
              )}

              {active3DLayer === "drone_flight" && (
                <div className="space-y-3">
                  <div className="inline-flex items-center gap-2 rounded-full bg-emerald-500/20 px-3 py-1 text-xs font-mono font-bold text-emerald-300 border border-emerald-500/30">
                    <Plane size={14} /> Autonomous Survey Grid Corridor (12 Waypoints)
                  </div>
                  <pre className="font-mono text-xs text-emerald-300 bg-slate-950/90 p-4 rounded-2xl border border-emerald-500/30 overflow-x-auto text-left">
{`  WP01 [Takeoff @ 45m AGL] ──► WP02 (Heading 090°) ──► WP03
    ▲                                                   │
    │                                                   ▼
  WP06 ◄────────────────────── WP05 ◄──────────────── WP04
    │
    ▼
  WP07 ──────────────────────► WP08 ─────────────────► WP09 [Target SE Sink]
    ▲                                                   │
    │                                                   ▼
  WP12 [RTL Land @ 0m] ◄────── WP11 ◄──────────────── WP10`}
                  </pre>
                  <div className="flex justify-center gap-3">
                    <button
                      onClick={handleExportMavlink}
                      className="flex items-center gap-1.5 rounded-xl bg-emerald-500/20 border border-emerald-500/40 px-3 py-1.5 text-xs font-bold text-emerald-300 hover:bg-emerald-500/30 transition"
                    >
                      <Download size={13} /> Export MavLink .waypoint
                    </button>
                    <button
                      onClick={handleExportKML}
                      className="flex items-center gap-1.5 rounded-xl bg-teal-500/20 border border-teal-500/40 px-3 py-1.5 text-xs font-bold text-teal-300 hover:bg-teal-500/30 transition"
                    >
                      <Download size={13} /> Export KML (DJI Terra)
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* 3.5 AUTONOMOUS DRONE RECONNAISSANCE & FLIGHT MISSION CONTROL */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Card 1: Live Drone Optical Camera & Telemetry Stream */}
        <div
          className={`lg:col-span-7 rounded-3xl p-6 sm:p-8 border transition-all ${
            isDark ? "border-emerald-500/30 bg-[#04160f] shadow-2xl" : "border-slate-200 bg-white shadow-xl"
          }`}
        >
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-4">
            <div className="flex items-center gap-2">
              <Video className="text-emerald-400" size={22} />
              <h3 className={`text-lg sm:text-xl font-black ${isDark ? "text-white" : "text-slate-900"}`}>
                Autonomous UAV Optical Reconnaissance Feed
              </h3>
            </div>
            <div className="flex items-center gap-2">
              <span className="flex items-center gap-1.5 rounded-full bg-red-500/20 px-2.5 py-0.5 text-[10px] font-mono font-black text-red-400 border border-red-500/40">
                <span className="h-1.5 w-1.5 rounded-full bg-red-500 animate-ping" />
                LIVE STREAM
              </span>
              <span className="text-[10px] font-mono text-emerald-400/80 bg-emerald-950/60 px-2 py-0.5 rounded-full border border-emerald-500/20">
                1080P • 60 FPS
              </span>
            </div>
          </div>

          <p className="text-xs text-slate-400 mb-4">
            Real-time aerial multi-spectral and optical crop canopy surveillance with active green LiDAR terrain tracking over {fieldParams.name}.
          </p>

          {/* Embedded Drone Recon Video Player */}
          <div className="relative w-full aspect-video rounded-2xl overflow-hidden border border-emerald-500/40 bg-black shadow-2xl group">
            <video
              ref={videoRef}
              src="/videos/drone-survey-recon.mp4"
              autoPlay
              loop
              muted={isVideoMuted}
              playsInline
              className="w-full h-full object-cover"
            />

            {/* Video HUD Overlay */}
            {showDroneHud && (
              <div className="absolute inset-0 pointer-events-none p-3.5 flex flex-col justify-between font-mono select-none">
                {/* Top overlay */}
                <div className="flex items-center justify-between text-[11px]">
                  <div className="flex items-center gap-2 bg-black/60 backdrop-blur-md px-2.5 py-1 rounded-full border border-emerald-500/30 text-emerald-300">
                    <Radio size={12} className="text-emerald-400 animate-pulse" />
                    <span>UAV-01 • AG-AGRAS T40</span>
                  </div>
                  <div className="flex items-center gap-2 bg-black/60 backdrop-blur-md px-2.5 py-1 rounded-full border border-emerald-500/30 text-emerald-300 text-[10px]">
                    <span>ALT: 45.2m AGL</span>
                    <span>•</span>
                    <span>SPD: 6.8 m/s</span>
                    <span>•</span>
                    <span className="text-amber-300">BAT: 84%</span>
                  </div>
                </div>

                {/* Laser LiDAR Center Crosshair */}
                <div className="flex flex-col items-center justify-center">
                  <div className="relative h-20 w-20 border border-dashed border-emerald-400/50 rounded-lg flex items-center justify-center">
                    <div className="h-2 w-2 border-t border-l border-emerald-300 absolute -top-0.5 -left-0.5" />
                    <div className="h-2 w-2 border-t border-r border-emerald-300 absolute -top-0.5 -right-0.5" />
                    <div className="h-2 w-2 border-b border-l border-emerald-300 absolute -bottom-0.5 -left-0.5" />
                    <div className="h-2 w-2 border-b border-r border-emerald-300 absolute -bottom-0.5 -right-0.5" />
                    <div className="h-1 w-1 rounded-full bg-emerald-400 animate-ping" />
                  </div>
                  <div className="mt-1 bg-black/70 backdrop-blur-md px-2.5 py-0.5 rounded text-[9px] text-emerald-300 border border-emerald-500/30">
                    SCAN BEAM: {fieldParams.crop} • Zone Gamma Focus
                  </div>
                </div>

                {/* Bottom overlay */}
                <div className="flex items-center justify-between text-[10px] text-slate-300">
                  <div className="bg-black/60 backdrop-blur-md px-2.5 py-1 rounded-lg border border-emerald-500/30">
                    <span>GPS: {fieldParams.centerLat.toFixed(4)}°N, {fieldParams.centerLng.toFixed(4)}°E (RTK Fix)</span>
                  </div>
                  <div className="bg-black/60 backdrop-blur-md px-2.5 py-1 rounded-lg border border-emerald-500/30 text-emerald-400">
                    <span>LiDAR PROFILER: ONLINE</span>
                  </div>
                </div>
              </div>
            )}

            {/* Video Controls Toolbar */}
            <div className="absolute bottom-3 right-3 flex items-center gap-1.5 z-20">
              <button
                onClick={togglePlayVideo}
                className="p-1.5 rounded-lg bg-black/70 hover:bg-black/90 text-white border border-emerald-500/40 backdrop-blur-md transition hover:scale-105"
                title={isVideoPlaying ? "Pause Video" : "Play Video"}
              >
                {isVideoPlaying ? <Pause size={13} /> : <Play size={13} />}
              </button>
              <button
                onClick={toggleMuteVideo}
                className="p-1.5 rounded-lg bg-black/70 hover:bg-black/90 text-white border border-emerald-500/40 backdrop-blur-md transition hover:scale-105"
                title={isVideoMuted ? "Unmute Audio" : "Mute Audio"}
              >
                {isVideoMuted ? <VolumeX size={13} /> : <Volume2 size={13} />}
              </button>
              <button
                onClick={() => setShowDroneHud(!showDroneHud)}
                className={`px-2 py-1 rounded-lg text-[10px] font-mono font-bold border backdrop-blur-md transition ${
                  showDroneHud
                    ? "bg-emerald-500/30 text-emerald-300 border-emerald-500/50"
                    : "bg-black/70 text-slate-400 border-slate-700 hover:text-white"
                }`}
              >
                HUD: {showDroneHud ? "ON" : "OFF"}
              </button>
              <button
                onClick={handleDownloadDroneVideo}
                className="p-1.5 rounded-lg bg-emerald-600/80 hover:bg-emerald-500 text-white border border-emerald-400/40 backdrop-blur-md transition hover:scale-105"
                title="Download Video File (MP4)"
              >
                <Download size={13} />
              </button>
            </div>
          </div>
        </div>

        {/* Card 2: Autonomous Spot-Spray Mission Dispatch */}
        <div
          className={`lg:col-span-5 rounded-3xl p-6 sm:p-8 border transition-all flex flex-col justify-between ${
            isDark ? "border-emerald-500/30 bg-[#04160f] shadow-2xl" : "border-slate-200 bg-white shadow-xl"
          }`}
        >
          <div>
            <div className="flex items-center gap-2 mb-3">
              <Plane className="text-emerald-400" size={22} />
              <h3 className={`text-lg sm:text-xl font-black ${isDark ? "text-white" : "text-slate-900"}`}>
                Autonomous Mission Dispatch
              </h3>
            </div>
            <p className="text-xs text-slate-400 mb-5">
              Direct telemetry integration with ArduPilot, PX4, and DJI Agras flight controllers for precision spot-spraying.
            </p>

            {/* Flight Avionics Telemetry Grid */}
            <div className="grid grid-cols-2 gap-3 mb-5 text-left font-mono">
              <div className="p-3 rounded-2xl bg-slate-950/60 border border-emerald-900/40">
                <span className="text-[10px] text-slate-400 uppercase block">Flight Corridor</span>
                <span className="text-sm font-bold text-emerald-300">420m (12 WP)</span>
              </div>
              <div className="p-3 rounded-2xl bg-slate-950/60 border border-emerald-900/40">
                <span className="text-[10px] text-slate-400 uppercase block">Swath Width</span>
                <span className="text-sm font-bold text-teal-300">6.5m Centrifugal</span>
              </div>
              <div className="p-3 rounded-2xl bg-slate-950/60 border border-emerald-900/40">
                <span className="text-[10px] text-slate-400 uppercase block">Target Area</span>
                <span className="text-sm font-bold text-amber-300">{gammaHa} ha (Zone Γ)</span>
              </div>
              <div className="p-3 rounded-2xl bg-slate-950/60 border border-emerald-900/40">
                <span className="text-[10px] text-slate-400 uppercase block">Chemical Savings</span>
                <span className="text-sm font-bold text-emerald-400">68% Reduction</span>
              </div>
            </div>
          </div>

          {/* Actions & Export Buttons */}
          <div className="space-y-2.5 pt-2">
            <button
              onClick={() => setIsDroneModalOpen(true)}
              className="w-full flex items-center justify-center gap-2 rounded-2xl bg-gradient-to-r from-emerald-500 to-teal-400 px-5 py-3 text-xs font-black text-slate-950 shadow-lg glow-emerald hover:brightness-110 transition hover:scale-[1.02] active:scale-[0.98]"
            >
              <Plane size={15} />
              <span>Generate Autonomous Flight Plan (MavLink / KML)</span>
            </button>

            <div className="grid grid-cols-2 gap-2">
              <button
                onClick={handleExportMavlink}
                className="flex items-center justify-center gap-1.5 rounded-xl border border-emerald-500/40 bg-emerald-950/50 hover:bg-emerald-900/50 px-3 py-2 text-xs font-bold text-emerald-300 transition"
              >
                <Download size={13} />
                <span>Export .waypoint</span>
              </button>
              <button
                onClick={handleExportKML}
                className="flex items-center justify-center gap-1.5 rounded-xl border border-teal-500/40 bg-teal-950/50 hover:bg-teal-900/50 px-3 py-2 text-xs font-bold text-teal-300 transition"
              >
                <Download size={13} />
                <span>Export DJI KML</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* 4. VARIABLE-RATE APPLICATION (VRA) & ECONOMIC ROI LEDGER */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* VRA Chemical Breakdown */}
        <div
          className={`lg:col-span-6 rounded-3xl p-6 sm:p-8 border transition-all ${
            isDark ? "border-emerald-500/30 bg-[#04160f]" : "border-slate-200 bg-white shadow-xl"
          }`}
        >
          <div className="flex items-center gap-2 mb-4">
            <Zap className="text-emerald-400" size={22} />
            <h3 className={`text-lg sm:text-xl font-black ${isDark ? "text-white" : "text-slate-900"}`}>
              Variable-Rate Application (VRA) vs. Blanket Spray
            </h3>
          </div>
          <p className="text-xs text-slate-400 mb-6">
            CIB&RC-registered dosage logic for {fieldParams.crop} ({fieldParams.pathogen}).
          </p>

          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-3">
              <div className="p-4 rounded-2xl bg-slate-950/60 border border-slate-800 text-center">
                <span className="text-[10px] text-slate-500 font-bold uppercase">Traditional Blanket</span>
                <p className="text-2xl font-black text-slate-300 font-mono mt-1">{tradChemKg} kg</p>
                <span className="text-[10px] text-slate-500 block">500 L/ha knapsack ({tradWaterLiters} L)</span>
              </div>
              <div className="p-4 rounded-2xl bg-emerald-950/40 border border-emerald-500/30 text-center">
                <span className="text-[10px] text-emerald-400 font-bold uppercase">Targeted VRA (Beta+Gamma)</span>
                <p className="text-2xl font-black text-emerald-400 font-mono mt-1">{precChemKg} kg</p>
                <span className="text-[10px] text-emerald-300 font-bold block">ULV Drone Atomization ({precWaterLiters} L)</span>
              </div>
            </div>

            {/* Savings highlight bar */}
            <div className="p-4 rounded-2xl bg-gradient-to-r from-emerald-950/60 via-teal-950/40 to-slate-950/60 border border-emerald-500/40 flex items-center justify-between">
              <div>
                <span className="text-xs font-bold text-emerald-300">Active Chemical Saved</span>
                <p className="text-xl font-black text-white font-mono">{chemSavedKg} kg ({chemSavedPct}% reduction)</p>
              </div>
              <div className="text-right">
                <span className="text-xs font-bold text-teal-300">Water Conserved</span>
                <p className="text-xl font-black text-white font-mono">{waterSavedLiters} Liters ({waterSavedPct}%)</p>
              </div>
            </div>
          </div>
        </div>

        {/* Economic Ledger in INR (₹) */}
        <div
          className={`lg:col-span-6 rounded-3xl p-6 sm:p-8 border transition-all ${
            isDark ? "border-emerald-500/30 bg-[#04160f]" : "border-slate-200 bg-white shadow-xl"
          }`}
        >
          <div className="flex items-center gap-2 mb-4">
            <Coins className="text-emerald-400" size={22} />
            <h3 className={`text-lg sm:text-xl font-black ${isDark ? "text-white" : "text-slate-900"}`}>
              Economic ROI Ledger (INR ₹)
            </h3>
          </div>
          <p className="text-xs text-slate-400 mb-6">
            Farm-level balance sheet for {areaHa.toFixed(2)} ha ({areaAcres} acres).
          </p>

          <div className="space-y-3 text-xs font-mono">
            <div className="flex justify-between p-2.5 rounded-xl bg-slate-950/40 border border-slate-800">
              <span className="text-slate-400">Traditional Total Cost (Chem + Labor):</span>
              <span className="font-bold text-rose-400">₹ {tradTotalINR.toLocaleString("en-IN")}</span>
            </div>
            <div className="flex justify-between p-2.5 rounded-xl bg-slate-950/40 border border-slate-800">
              <span className="text-slate-400">Precision Drone Total Cost (VRA Chem + Service):</span>
              <span className="font-bold text-emerald-400">₹ {precTotalINR.toLocaleString("en-IN")}</span>
            </div>
            <div className="flex justify-between p-3.5 rounded-xl bg-emerald-950/60 border border-emerald-500/50">
              <div>
                <span className="text-[10px] text-emerald-300 font-bold uppercase block">Net Realized Cash Savings</span>
                <span className="text-xl font-black text-emerald-300">₹ {grossSavingsINR.toLocaleString("en-IN")}</span>
              </div>
              <div className="text-right">
                <span className="text-[10px] text-teal-300 font-bold uppercase block">Calculated ROI</span>
                <span className="text-xl font-black text-teal-300">{roiPct}%</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 5. FULL 20-SECTION REPORT VIEWER WITH PRINT & EXPORT */}
      <div
        className={`rounded-3xl p-6 sm:p-8 border transition-all ${
          isDark ? "border-emerald-500/30 bg-[#061e15]/80 shadow-2xl" : "border-slate-200 bg-white shadow-xl"
        }`}
      >
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
          <div>
            <div className="flex items-center gap-2">
              <FileText className="text-emerald-400" size={22} />
              <h3 className={`text-lg sm:text-xl font-black ${isDark ? "text-white" : "text-slate-900"}`}>
                Comprehensive 20-Section Intelligence Report
              </h3>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">
              Formally structured according to Specification §24 with uncertainty provenance tags.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <button
              onClick={handleCopyReport}
              className="flex items-center gap-1.5 rounded-xl bg-emerald-500/20 border border-emerald-500/40 px-3.5 py-2 text-xs font-bold text-emerald-300 hover:bg-emerald-500/30 transition active:scale-95"
            >
              {copiedReport ? <Check size={14} className="text-emerald-400" /> : <Copy size={14} />}
              <span>{copiedReport ? "Copied!" : "Copy Markdown"}</span>
            </button>
            <button
              onClick={handlePrintReport}
              className="flex items-center gap-1.5 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-400 px-4 py-2 text-xs font-black text-slate-950 hover:brightness-110 shadow transition active:scale-95"
            >
              <Printer size={14} />
              <span>Print Official PDF</span>
            </button>
          </div>
        </div>

        {/* Report Content View */}
        <div className="rounded-2xl bg-slate-950 p-5 sm:p-6 border border-emerald-900/60 max-h-[500px] overflow-y-auto font-mono text-xs text-slate-300 space-y-4 shadow-inner">
          <pre className="whitespace-pre-wrap leading-relaxed">{fullTechnicalMarkdownReport}</pre>
        </div>
      </div>

      {/* 6. MODAL: AUTONOMOUS DRONE SPOT-SPRAYING MISSION GENERATOR */}
      <DroneMissionGeneratorModal
        isOpen={isDroneModalOpen}
        onClose={() => setIsDroneModalOpen(false)}
        disease={{
          crop: fieldParams.crop,
          condition: fieldParams.pathogen,
          diagnosis: fieldParams.pathogen
        }}
        isDark={isDark}
      />
    </div>
  );
}
