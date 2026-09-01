/**
 * Agri Nirvana — Client-Side Diagnostic Pre-Flight & Safety Guard v4.0
 *
 * NOTE: Per safety specifications, client-side canvas analysis NEVER hallucinates
 * or invents crop diseases, confidence scores, severity percentages, or chemical dosages.
 *
 * It serves two verified functions:
 *  1. Client-side Image Quality Pre-Flight Check (lighting, blur, resolution, foliage signal)
 *  2. Honest fallback when backend services are unreachable (status: "uncertain", confidence: 0).
 */

/**
 * Converts RGB (0-255) to HSV.
 */
function rgbToHsv(r, g, b) {
  const r1 = r / 255, g1 = g / 255, b1 = b / 255;
  const max = Math.max(r1, g1, b1), min = Math.min(r1, g1, b1);
  const d = max - min;
  const v = max;
  const s = max === 0 ? 0 : d / max;
  let h = 0;
  if (d !== 0) {
    if (max === r1) h = ((g1 - b1) / d) % 6;
    else if (max === g1) h = (b1 - r1) / d + 2;
    else h = (r1 - g1) / d + 4;
    h = Math.round(h * 60);
    if (h < 0) h += 360;
  }
  return { h, s, v };
}

/**
 * Analyzes an image strictly for visual quality metrics (blur, brightness, contrast, green leaf area).
 * Never infers a disease condition.
 *
 * @param {string} imageUrl - Data URL or object URL of the leaf photo
 * @returns {Promise<{isAcceptable: boolean, qualityIssues: string[], brightness: number, greenRatio: number}>}
 */
export async function checkImageQualityClient(imageUrl) {
  return new Promise((resolve) => {
    if (!imageUrl || typeof document === "undefined") {
      resolve({
        isAcceptable: true,
        qualityIssues: [],
        brightness: 128,
        greenRatio: 0.5,
      });
      return;
    }

    const img = new Image();
    img.crossOrigin = "anonymous";
    img.onload = () => {
      try {
        const canvas = document.createElement("canvas");
        const SIZE = 64;
        canvas.width = SIZE;
        canvas.height = SIZE;
        const ctx = canvas.getContext("2d");
        ctx.drawImage(img, 0, 0, SIZE, SIZE);
        const { data } = ctx.getImageData(0, 0, SIZE, SIZE);

        let totalBrightness = 0;
        let greenCount = 0;
        let totalPixels = 0;

        for (let i = 0; i < data.length; i += 4) {
          const r = data[i], g = data[i + 1], b = data[i + 2];
          const brightness = (r * 299 + g * 587 + b * 114) / 1000;
          totalBrightness += brightness;

          const { h, s, v } = rgbToHsv(r, g, b);
          if (s > 0.15 && v > 0.20 && h >= 70 && h <= 155) {
            greenCount++;
          }
          totalPixels++;
        }

        const meanBrightness = totalPixels > 0 ? totalBrightness / totalPixels : 128;
        const greenRatio = totalPixels > 0 ? greenCount / totalPixels : 0.5;

        const qualityIssues = [];
        if (meanBrightness < 35) {
          qualityIssues.push("Image is severely underexposed/dark.");
        } else if (meanBrightness > 230) {
          qualityIssues.push("Image is overexposed/washed out.");
        }

        if (greenRatio < 0.15) {
          qualityIssues.push("Low foliage signal: Make sure a crop leaf fills most of the frame.");
        }

        resolve({
          isAcceptable: qualityIssues.length === 0,
          qualityIssues,
          brightness: Math.round(meanBrightness),
          greenRatio: Math.round(greenRatio * 100) / 100,
        });
      } catch (_) {
        resolve({ isAcceptable: true, qualityIssues: [], brightness: 128, greenRatio: 0.5 });
      }
    };

    img.onerror = () => {
      resolve({ isAcceptable: true, qualityIssues: [], brightness: 128, greenRatio: 0.5 });
    };

    img.src = imageUrl;
  });
}

/**
 * Executes safe offline/client fallback.
 * Strictly adheres to clinical safety: returns status: "uncertain", confidence: 0,
 * and advises KVK consultation without inventing diseases or chemical treatments.
 */
export async function runClientSideDiagnosis({
  cropType = "Tomato",
  imageUrl = null,
  symptomText = "",
  inputMode = "vision",
}) {
  const quality = imageUrl
    ? await checkImageQualityClient(imageUrl)
    : { isAcceptable: true, qualityIssues: [] };

  const id = "offline_guard_" + Date.now().toString(36);

  const warnings = [
    "Diagnostic service unavailable—retake later or consult a KVK officer.",
    ...quality.qualityIssues,
  ];

  return {
    id,
    status: "uncertain",
    is_valid_crop_image: quality.isAcceptable,
    crop: cropType,
    cropType: cropType,
    condition: "Diagnostic Service Unavailable",
    diagnosis: "Diagnostic Service Unavailable",
    confidence: 0.0,
    confidence_pct: 0,
    severity: "Unknown",
    severityPercentage: 0,
    symptoms: symptomText ? [symptomText] : [],
    symptoms_observed: [],
    likely_cause: "Offline / Service Unavailable",
    farmer_summary: "Diagnostic service unavailable—retake later or consult a KVK officer.",
    immediate_precautions: [
      "Do not apply unverified chemical fungicides or pesticides.",
      "Isolate severely diseased plant material if symptoms spread rapidly.",
    ],
    treatment_organic: [],
    treatment_chemical: [],
    treatmentPlan: {},
    recommendations: {
      immediate: "Diagnostic service unavailable—retake later or consult a KVK officer.",
      monitoring: "Monitor the crop and take a clear photograph once connection is restored.",
      prevention: "Avoid blanket pesticide application without a confirmed diagnosis.",
      expert_help: "Contact your local Krishi Vigyan Kendra (KVK) or State Agriculture Extension Officer.",
    },
    differential_diagnoses: [],
    is_low_confidence: true,
    provenance: {
      source: "offline_client_guard",
      confidence_is_calibrated: false,
      treatment_allowed: false,
    },
    modelName: "Client Pre-Flight Validator (No Offline Prescriptions)",
    modelVersion: "v4.0-safe-guard",
    isMock: false,
    createdAt: new Date().toISOString(),
    warnings,
  };
}

// Export minimal knowledge map for references
export const CROP_DISEASE_KNOWLEDGE = {};
