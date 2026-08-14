import React, { useState, useEffect, useRef } from "react";
import { Clock, Play, RotateCcw, ShieldCheck, AlertTriangle, Sparkles } from "lucide-react";

export default function DiseaseTimeLapse4D({ disease, isDark = false }) {
  const mountRef = useRef(null);
  const [day, setDay] = useState(3);
  const [path, setPath] = useState("treated"); // 'treated' | 'untreated'
  const [isPlaying, setIsPlaying] = useState(false);

  useEffect(() => {
    let interval;
    if (isPlaying) {
      interval = setInterval(() => {
        setDay((prev) => {
          if (prev >= 14) {
            setIsPlaying(false);
            return 14;
          }
          return prev === 0 ? 1 : prev === 1 ? 3 : prev === 3 ? 7 : 14;
        });
      }, 1200);
    }
    return () => clearInterval(interval);
  }, [isPlaying]);

  useEffect(() => {
    let THREE, scene, camera, renderer, animationFrameId, leafMesh, lesionMesh;

    import("three").then((threeModule) => {
      THREE = threeModule;
      const container = mountRef.current;
      if (!container) return;

      const width = container.clientWidth || 340;
      const height = container.clientHeight || 280;

      scene = new THREE.Scene();
      camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
      camera.position.set(0, 0, 4.8);

      renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
      renderer.setSize(width, height);
      renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

      container.innerHTML = "";
      container.appendChild(renderer.domElement);

      const ambientLight = new THREE.AmbientLight(0xffffff, 1.8);
      scene.add(ambientLight);

      const dirLight = new THREE.DirectionalLight(0x10b981, 2.0);
      dirLight.position.set(4, 4, 4);
      scene.add(dirLight);

      // Curved Leaf Geometry
      const shape = new THREE.Shape();
      shape.moveTo(0, -1.6);
      shape.bezierCurveTo(0.8, -0.8, 1.1, 0.2, 0, 1.6);
      shape.bezierCurveTo(-1.1, 0.2, -0.8, -0.8, 0, -1.6);

      const leafGeo = new THREE.ExtrudeGeometry(shape, { depth: 0.06, bevelEnabled: true, bevelSize: 0.03 });

      // Determine color based on day and path
      let colorHex = 0x10b981; // Green
      if (path === "untreated") {
        colorHex = day >= 14 ? 0x451a03 : day >= 7 ? 0x854d0e : day >= 3 ? 0xb45309 : 0x10b981;
      } else {
        colorHex = day >= 7 ? 0x10b981 : day >= 3 ? 0x059669 : 0x047857;
      }

      const leafMat = new THREE.MeshStandardMaterial({
        color: colorHex,
        roughness: 0.4,
        metalness: 0.1,
      });

      leafMesh = new THREE.Mesh(leafGeo, leafMat);
      scene.add(leafMesh);

      // Lesion spot
      if (path === "untreated" || day < 7) {
        const spotRadius = path === "untreated" ? 0.2 + (day * 0.05) : Math.max(0.05, 0.35 - (day * 0.04));
        const lesionGeo = new THREE.SphereGeometry(spotRadius, 16, 16);
        const lesionMat = new THREE.MeshBasicMaterial({
          color: path === "untreated" ? 0xef4444 : 0xf59e0b,
          wireframe: true,
        });
        lesionMesh = new THREE.Mesh(lesionGeo, lesionMat);
        lesionMesh.position.set(0.2, 0.3, 0.08);
        scene.add(lesionMesh);
      }

      let angle = 0;
      const animate = () => {
        animationFrameId = requestAnimationFrame(animate);
        angle += 0.01;
        leafMesh.rotation.y = Math.sin(angle) * 0.2;
        renderer.render(scene, camera);
      };
      animate();
    });

    return () => {
      if (animationFrameId) cancelAnimationFrame(animationFrameId);
    };
  }, [day, path]);

  return (
    <div className={`rounded-2xl p-4 border transition-all ${isDark ? "border-emerald-800/40 bg-[#04160f]" : "border-slate-200 bg-slate-50"}`}>
      <div className="flex items-center justify-between mb-3 pb-2 border-b border-slate-200/50">
        <div className="flex items-center gap-2">
          <Clock size={16} className="text-amber-500" />
          <h4 className={`text-xs font-black uppercase tracking-wider ${isDark ? "text-emerald-300" : "text-slate-800"}`}>
            4D Temporal Disease Progression Time-Lapse (14-Day Simulation)
          </h4>
        </div>
        <div className="flex gap-1 bg-slate-200 dark:bg-emerald-950 p-1 rounded-xl text-[11px] font-bold">
          <button
            onClick={() => setPath("treated")}
            className={`px-3 py-1 rounded-lg transition ${path === "treated" ? "bg-emerald-600 text-white" : "text-slate-500"}`}
          >
            🟢 Treated Path
          </button>
          <button
            onClick={() => setPath("untreated")}
            className={`px-3 py-1 rounded-lg transition ${path === "untreated" ? "bg-red-600 text-white" : "text-slate-500"}`}
          >
            🔴 Untreated Path
          </button>
        </div>
      </div>

      {/* 3D CANVAS & TIMELINE CONTROLS */}
      <div className="relative aspect-[16/10] overflow-hidden rounded-xl bg-slate-950 shadow-inner flex items-center justify-center">
        <div ref={mountRef} className="h-full w-full" />
        <div className="absolute top-3 left-3 bg-black/70 backdrop-blur px-3 py-1 rounded-full border border-emerald-500/30 text-[10px] font-mono font-bold text-white flex items-center gap-1.5">
          <Sparkles size={12} className="text-amber-400" />
          Day {day}: {path === "treated" ? "Foliar Recovery Active (95% Chlorophyll)" : "Lesion Expansion & Necrosis"}
        </div>
      </div>

      {/* TIMELINE SLIDER */}
      <div className="mt-4 space-y-2">
        <div className="flex items-center justify-between text-[11px] font-mono font-bold">
          <span className="text-slate-400">Timeline Day Slider:</span>
          <span className="text-emerald-400">Day {day} / 14</span>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => setIsPlaying(!isPlaying)}
            className="rounded-xl bg-emerald-600 p-2 text-white hover:bg-emerald-700"
          >
            {isPlaying ? "Pause" : <Play size={14} />}
          </button>
          <input
            type="range"
            min="0"
            max="14"
            step="1"
            value={day}
            onChange={(e) => setDay(parseInt(e.target.value))}
            className="w-full accent-emerald-500 h-2 bg-slate-200 dark:bg-emerald-950 rounded-lg cursor-pointer"
          />
        </div>
        <div className="flex justify-between text-[10px] font-bold text-slate-500 px-1">
          <span>Day 0 (Scan)</span>
          <span>Day 3 (Spray Effect)</span>
          <span>Day 7 (Regeneration)</span>
          <span>Day 14 (Full Canopy)</span>
        </div>
      </div>
    </div>
  );
}
