import React, { useEffect, useRef } from "react";

export default function DiseaseHeatmapCanvas({ imageSrc, disease, isDark = false }) {
  const canvasRef = useRef(null);

  useEffect(() => {
    if (!imageSrc || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    const img = new Image();
    img.crossOrigin = "anonymous";
    img.src = imageSrc;

    img.onload = () => {
      canvas.width = img.width || 600;
      canvas.height = img.height || 400;

      // Draw base image
      ctx.drawImage(img, 0, 0, canvas.width, canvas.height);

      // Extract pixel data for heatmap processing
      const imgData = ctx.getImageData(0, 0, canvas.width, canvas.height);
      const data = imgData.data;

      // Create glowing heatmap overlay canvas
      const overlayCanvas = document.createElement("canvas");
      overlayCanvas.width = canvas.width;
      overlayCanvas.height = canvas.height;
      const overlayCtx = overlayCanvas.getContext("2d");
      const overlayData = overlayCtx.createImageData(canvas.width, canvas.height);
      const oData = overlayData.data;

      const isHealthy = disease?.severity === "Healthy";

      for (let i = 0; i < data.length; i += 4) {
        const r = data[i];
        const g = data[i + 1];
        const b = data[i + 2];

        // Chromaticity formulas
        const total = r + g + b || 1;
        const rNorm = r / total;
        const gNorm = g / total;
        const bNorm = b / total;

        const isNecroticSpot = (r > g * 0.85 && rNorm > 0.35 && gNorm < 0.45) || (r < 70 && g < 70 && b < 70);
        const isChloroticYellow = gNorm > 0.4 && rNorm > 0.38 && bNorm < 0.25;

        if (!isHealthy && (isNecroticSpot || isChloroticYellow)) {
          // Highlight lesion zones with bright glowing orange/red
          oData[i] = 239;     // Red
          oData[i + 1] = 68;  // Green
          oData[i + 2] = 68;  // Blue
          oData[i + 3] = isNecroticSpot ? 210 : 140; // Alpha intensity
        } else if (isHealthy) {
          // Healthy leaf matrix glowing emerald
          if (gNorm > rNorm && gNorm > bNorm) {
            oData[i] = 16;
            oData[i + 1] = 185;
            oData[i + 2] = 129;
            oData[i + 3] = 90;
          }
        }
      }

      overlayCtx.putImageData(overlayData, 0, 0);

      // Composite base image with heatmap blur
      ctx.globalAlpha = 0.55;
      ctx.filter = "blur(4px)";
      ctx.drawImage(overlayCanvas, 0, 0);
      ctx.filter = "none";
      ctx.globalAlpha = 1.0;

      // Draw contour boundaries around lesion clusters
      ctx.strokeStyle = isHealthy ? "rgba(16, 185, 129, 0.9)" : "rgba(245, 158, 11, 0.95)";
      ctx.lineWidth = 2;
      ctx.setLineDash([4, 4]);

      // Grid overlay for spatial scan telemetry
      const stepX = canvas.width / 6;
      const stepY = canvas.height / 4;
      ctx.strokeStyle = "rgba(255, 255, 255, 0.15)";
      ctx.lineWidth = 1;
      ctx.setLineDash([]);

      for (let x = stepX; x < canvas.width; x += stepX) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, canvas.height);
        ctx.stroke();
      }
      for (let y = stepY; y < canvas.height; y += stepY) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(canvas.width, y);
        ctx.stroke();
      }
    };
  }, [imageSrc, disease]);

  return (
    <div className="relative w-full overflow-hidden rounded-xl bg-slate-950 shadow-inner">
      <canvas ref={canvasRef} className="h-full w-full object-cover aspect-[16/10]" />
      <div className="absolute top-3 left-3 rounded-lg bg-slate-950/80 px-2.5 py-1 text-[10px] font-mono font-bold text-amber-400 border border-amber-500/40 backdrop-blur">
        AI LESION HEATMAP MASK • 4K VISION MATRIX
      </div>
    </div>
  );
}
