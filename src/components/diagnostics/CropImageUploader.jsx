import React, { useRef, useState } from "react";
import { Upload, Camera, Image as ImageIcon, AlertTriangle, X, CheckCircle2, RefreshCw } from "lucide-react";

export default function CropImageUploader({
  imagePreview = null,
  onImageSelected = () => {},
  onClearImage = () => {},
  isDark = true,
  maxSizeMb = 10
}) {
  const [isDragging, setIsDragging] = useState(false);
  const [qualityWarning, setQualityWarning] = useState(null);
  const fileInputRef = useRef(null);

  const processFile = (file) => {
    if (!file) return;

    // 1. File Size Check
    const sizeMb = file.size / (1024 * 1024);
    if (sizeMb > maxSizeMb) {
      setQualityWarning(`File size (${sizeMb.toFixed(1)} MB) exceeds maximum allowed limit of ${maxSizeMb} MB.`);
      return;
    }

    // 2. MIME Type Check
    if (!file.type.startsWith("image/")) {
      setQualityWarning("Invalid file type. Please upload a JPG, JPEG, PNG, or WebP crop leaf photo.");
      return;
    }

    setQualityWarning(null);

    const reader = new FileReader();
    reader.onload = (e) => {
      const img = new Image();
      img.onload = () => {
        // Pre-flight Dimension & Quality Check
        if (img.width < 150 || img.height < 150) {
          setQualityWarning("Image resolution is very low (<150x150px). For best AI accuracy, please upload a clearer photo.");
        }
        onImageSelected(file, e.target.result);
      };
      img.src = e.target.result;
    };
    reader.readAsDataURL(file);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files?.[0];
    if (file) processFile(file);
  };

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file) processFile(file);
  };

  return (
    <div className="space-y-3">
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        accept="image/jpeg,image/png,image/webp,image/jpg"
        className="hidden"
      />

      {imagePreview ? (
        <div className={`relative overflow-hidden rounded-2xl border p-4 transition-all ${
          isDark ? "border-emerald-700/60 bg-[#04160f]" : "border-slate-300 bg-slate-50"
        }`}>
          <div className="relative mx-auto aspect-[16/10] max-w-md overflow-hidden rounded-xl bg-slate-950 shadow-inner group">
            <img src={imagePreview} alt="Crop Leaf Preview" className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105" />
            <div className="absolute inset-0 bg-gradient-to-t from-slate-950/80 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity p-4 flex items-end justify-between">
              <span className="text-xs font-mono font-bold text-emerald-300">Ready for AI Vision Analysis</span>
              <button
                type="button"
                onClick={onClearImage}
                className="rounded-lg bg-rose-500/90 text-white p-1.5 hover:bg-rose-600 transition shadow"
              >
                <X size={16} />
              </button>
            </div>
          </div>

          <div className="mt-3 flex items-center justify-between gap-3 text-xs">
            <div className="flex items-center gap-1.5 text-emerald-400 font-bold">
              <CheckCircle2 size={16} />
              <span>Image loaded & validated</span>
            </div>
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              className="flex items-center gap-1 font-bold text-slate-400 hover:text-white transition"
            >
              <RefreshCw size={12} />
              Change Photo
            </button>
          </div>
        </div>
      ) : (
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={`relative cursor-pointer overflow-hidden rounded-2xl border-2 border-dashed p-8 text-center transition-all ${
            isDragging
              ? "border-emerald-400 bg-emerald-500/10 scale-[1.01]"
              : isDark
              ? "border-emerald-800/60 bg-[#04160f] hover:border-emerald-500/60 hover:bg-emerald-950/30"
              : "border-slate-300 bg-slate-50 hover:border-emerald-500 hover:bg-emerald-50/50"
          }`}
        >
          <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 mb-3">
            <Upload size={28} />
          </div>

          <h4 className={`text-sm font-black ${isDark ? "text-white" : "text-slate-900"}`}>
            Drag & Drop your crop leaf photo here
          </h4>
          <p className={`text-xs mt-1 max-w-sm mx-auto ${isDark ? "text-emerald-200/60" : "text-slate-500"}`}>
            Or click to browse files (JPG, PNG, WebP up to {maxSizeMb}MB)
          </p>

          <div className="mt-4 flex items-center justify-center gap-3">
            <span className="inline-flex items-center gap-1.5 rounded-xl bg-emerald-600 px-4 py-2 text-xs font-black text-white hover:bg-emerald-700 shadow-md">
              <ImageIcon size={14} /> Browse Photo
            </span>
            <span className="inline-flex items-center gap-1.5 rounded-xl border border-emerald-500/30 bg-emerald-500/10 px-4 py-2 text-xs font-bold text-emerald-300 hover:bg-emerald-500/20">
              <Camera size={14} /> Use Camera
            </span>
          </div>
        </div>
      )}

      {qualityWarning && (
        <div className="flex items-center gap-2.5 rounded-xl border border-amber-500/40 bg-amber-500/10 p-3 text-xs text-amber-300">
          <AlertTriangle size={18} className="shrink-0 text-amber-400" />
          <span>{qualityWarning}</span>
        </div>
      )}
    </div>
  );
}
