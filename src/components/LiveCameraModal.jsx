import React, { useState, useEffect, useRef } from "react";
import { Camera, RefreshCw, X, Sparkles, AlertCircle, CheckCircle } from "lucide-react";

export default function LiveCameraModal({ isOpen, onClose, onCapture, isDark = false }) {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [stream, setStream] = useState(null);
  const [facingMode, setFacingMode] = useState("environment"); // 'environment' | 'user'
  const [cameraError, setCameraError] = useState(null);
  const [isCapturing, setIsCapturing] = useState(false);

  useEffect(() => {
    if (!isOpen) {
      stopCamera();
      return;
    }

    startCamera();

    return () => {
      stopCamera();
    };
  }, [isOpen, facingMode]);

  const startCamera = async () => {
    setCameraError(null);
    stopCamera();

    try {
      const constraints = {
        video: {
          facingMode: facingMode,
          width: { ideal: 1280 },
          height: { ideal: 720 },
        },
      };

      const mediaStream = await navigator.mediaDevices.getUserMedia(constraints);
      setStream(mediaStream);

      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
        videoRef.current.play();
      }
    } catch (err) {
      console.error("Camera access error:", err);
      setCameraError("Unable to access camera. Please check permissions or upload a photo manually.");
    }
  };

  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach((track) => track.stop());
      setStream(null);
    }
  };

  const toggleFacingMode = () => {
    setFacingMode((prev) => (prev === "environment" ? "user" : "environment"));
  };

  const handleCapture = () => {
    if (!videoRef.current || !canvasRef.current) return;
    setIsCapturing(true);

    const video = videoRef.current;
    const canvas = canvasRef.current;
    canvas.width = video.videoWidth || 800;
    canvas.height = video.videoHeight || 600;

    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    const dataUrl = canvas.toDataURL("image/jpeg", 0.92);
    
    setTimeout(() => {
      setIsCapturing(false);
      onCapture(dataUrl);
      onClose();
    }, 400);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-fade-in">
      <div
        className={`relative w-full max-w-xl overflow-hidden rounded-3xl border shadow-2xl transition-all ${
          isDark ? "border-emerald-800/60 bg-[#061e15]" : "border-slate-200 bg-white"
        }`}
      >
        {/* MODAL HEADER */}
        <div className={`flex items-center justify-between p-4 px-6 border-b ${isDark ? "border-emerald-900/50 text-white" : "border-slate-200 text-slate-900"}`}>
          <div className="flex items-center gap-2">
            <div className="h-3 w-3 rounded-full bg-emerald-500 animate-ping" />
            <h3 className="text-base font-black flex items-center gap-2">
              <Camera size={18} className="text-emerald-500" />
              Live AI Leaf Viewfinder
            </h3>
          </div>
          <button
            onClick={onClose}
            className={`rounded-full p-2 transition ${isDark ? "hover:bg-emerald-900/40 text-slate-400 hover:text-white" : "hover:bg-slate-100 text-slate-600"}`}
          >
            <X size={18} />
          </button>
        </div>

        {/* CAMERA PREVIEW CONTAINER */}
        <div className="relative aspect-[4/3] bg-black overflow-hidden">
          {cameraError ? (
            <div className="absolute inset-0 flex flex-col items-center justify-center p-6 text-center text-white bg-slate-900">
              <AlertCircle size={40} className="text-amber-400 mb-3" />
              <p className="text-sm font-bold max-w-xs">{cameraError}</p>
              <button
                onClick={startCamera}
                className="mt-4 flex items-center gap-2 rounded-xl bg-emerald-600 px-4 py-2 text-xs font-bold text-white hover:bg-emerald-700"
              >
                <RefreshCw size={14} /> Retry Camera
              </button>
            </div>
          ) : (
            <>
              <video ref={videoRef} playsInline autoPlay muted className="h-full w-full object-cover" />
              <canvas ref={canvasRef} className="hidden" />

              {/* OVERLAY RETICLE & FRAMING ASSISTANT */}
              <div className="absolute inset-0 pointer-events-none border-[16px] border-black/40 flex flex-col items-center justify-between p-4">
                {/* TOP STATUS BAR */}
                <div className="flex items-center justify-between w-full">
                  <span className="rounded-full bg-black/60 backdrop-blur px-3 py-1 text-[10px] font-mono font-bold text-emerald-400 border border-emerald-500/40 flex items-center gap-1.5">
                    <CheckCircle size={12} className="text-emerald-400" /> Live HD Feed
                  </span>
                  <span className="rounded-full bg-black/60 backdrop-blur px-3 py-1 text-[10px] font-mono text-slate-300 border border-slate-700">
                    {facingMode === "environment" ? "Rear Lens" : "Front Lens"}
                  </span>
                </div>

                {/* TARGET LEAF SCANNING FRAME */}
                <div className="relative w-64 h-64 sm:w-72 sm:h-72 border-2 border-dashed border-emerald-400/80 rounded-2xl flex items-center justify-center shadow-[0_0_20px_rgba(16,185,129,0.3)]">
                  {/* Corner accents */}
                  <div className="absolute -top-1 -left-1 w-5 h-5 border-t-4 border-l-4 border-emerald-400 rounded-tl-lg" />
                  <div className="absolute -top-1 -right-1 w-5 h-5 border-t-4 border-r-4 border-emerald-400 rounded-tr-lg" />
                  <div className="absolute -bottom-1 -left-1 w-5 h-5 border-b-4 border-l-4 border-emerald-400 rounded-bl-lg" />
                  <div className="absolute -bottom-1 -right-1 w-5 h-5 border-b-4 border-r-4 border-emerald-400 rounded-br-lg" />

                  {/* Pulsing Scan Line */}
                  <div className="absolute left-2 right-2 h-0.5 bg-gradient-to-r from-transparent via-emerald-400 to-transparent shadow-[0_0_12px_#10b981] animate-laser" />

                  <span className="bg-black/60 backdrop-blur text-[10px] font-bold text-emerald-300 px-3 py-1 rounded-full border border-emerald-500/30">
                    Align leaf inside box
                  </span>
                </div>

                {/* BOTTOM HINT */}
                <p className="text-[11px] font-bold text-white/90 bg-black/60 backdrop-blur px-3 py-1 rounded-full border border-white/20">
                  Ensure good lighting & steady focus
                </p>
              </div>

              {isCapturing && (
                <div className="absolute inset-0 bg-emerald-500/30 backdrop-blur-sm flex items-center justify-center">
                  <div className="h-12 w-12 rounded-full border-4 border-white border-t-transparent animate-spin" />
                </div>
              )}
            </>
          )}
        </div>

        {/* MODAL FOOTER CONTROLS */}
        <div className={`flex items-center justify-between p-4 px-6 border-t ${isDark ? "border-emerald-900/50 bg-[#04160f]" : "border-slate-200 bg-slate-50"}`}>
          <button
            onClick={toggleFacingMode}
            className={`flex items-center gap-2 rounded-xl px-4 py-2.5 text-xs font-bold border transition ${
              isDark ? "border-emerald-900 bg-emerald-950/60 text-emerald-300 hover:bg-emerald-900/60" : "border-slate-200 bg-white text-slate-700 hover:bg-slate-100"
            }`}
          >
            <RefreshCw size={15} /> Switch Lens
          </button>

          <button
            onClick={handleCapture}
            disabled={!!cameraError || isCapturing}
            className="flex items-center gap-2 rounded-2xl bg-emerald-500 px-6 py-3 text-xs font-black text-slate-950 hover:bg-emerald-400 active:scale-95 transition shadow-lg shadow-emerald-500/30 disabled:opacity-50"
          >
            <Sparkles size={16} /> Capture & AI Diagnose
          </button>
        </div>
      </div>
    </div>
  );
}
