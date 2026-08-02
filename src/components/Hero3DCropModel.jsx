import React, { useEffect, useRef, useState } from "react";

// WebGL Capability Detector
function detectWebGL() {
  try {
    const canvas = document.createElement("canvas");
    return !!(
      window.WebGLRenderingContext &&
      (canvas.getContext("webgl") || canvas.getContext("experimental-webgl"))
    );
  } catch (e) {
    return false;
  }
}

export default function Hero3DCropModel({ theme = "light" }) {
  const mountRef = useRef(null);
  const [webglSupported, setWebglSupported] = useState(true);
  const isDark = theme === "dark";

  useEffect(() => {
    if (!detectWebGL()) {
      setWebglSupported(false);
      return;
    }

    let THREE;
    let scene, camera, renderer, animationFrameId;
    let plantGroup;

    import("three").then((threeModule) => {
      THREE = threeModule;
      const container = mountRef.current;
      if (!container) return;

      const width = container.clientWidth || 320;
      const height = container.clientHeight || 320;

      scene = new THREE.Scene();
      camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
      camera.position.set(0, 0.5, 6.5);

      renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
      renderer.setSize(width, height);
      renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

      container.innerHTML = "";
      container.appendChild(renderer.domElement);

      // Lights
      const ambientLight = new THREE.AmbientLight(
        isDark ? 0x064e3b : 0xdcfce7,
        isDark ? 1.8 : 2.2
      );
      scene.add(ambientLight);

      const dirLight = new THREE.DirectionalLight(
        isDark ? 0xf59e0b : 0x10b981,
        isDark ? 2.5 : 2.0
      );
      dirLight.position.set(5, 8, 5);
      scene.add(dirLight);

      const backLight = new THREE.DirectionalLight(0x38bdf8, 1.2);
      backLight.position.set(-5, -2, -4);
      scene.add(backLight);

      // Create Low-Poly Crop Plant (Wheat / Grain Stalk)
      plantGroup = new THREE.Group();

      // Stem Material
      const stemMat = new THREE.MeshStandardMaterial({
        color: isDark ? 0x10b981 : 0x16a34a,
        roughness: 0.4,
        metalness: 0.1,
        flatShading: true
      });

      // Stem Mesh
      const stemGeo = new THREE.CylinderGeometry(0.06, 0.09, 3.2, 8);
      const stemMesh = new THREE.Mesh(stemGeo, stemMat);
      stemMesh.position.y = -0.5;
      plantGroup.add(stemMesh);

      // Leaves (4 Low-Poly Curved Leaves)
      const leafMat = new THREE.MeshStandardMaterial({
        color: isDark ? 0x34d399 : 0x22c55e,
        roughness: 0.3,
        flatShading: true
      });

      for (let i = 0; i < 4; i++) {
        const leafGeo = new THREE.ConeGeometry(0.35, 1.4, 5);
        const leafMesh = new THREE.Mesh(leafGeo, leafMat);
        leafMesh.scale.set(1, 1, 0.15);
        leafMesh.position.set(
          Math.sin((i * Math.PI) / 2) * 0.3,
          -1.0 + i * 0.4,
          Math.cos((i * Math.PI) / 2) * 0.3
        );
        leafMesh.rotation.z = (Math.PI / 4) * (i % 2 === 0 ? 1 : -1);
        leafMesh.rotation.y = (i * Math.PI) / 2;
        plantGroup.add(leafMesh);
      }

      // Wheat Ear Grains (Helical Arrangement at top)
      const grainMat = new THREE.MeshStandardMaterial({
        color: isDark ? 0xf59e0b : 0xeab308,
        roughness: 0.2,
        metalness: 0.2,
        flatShading: true
      });

      const grainCount = 18;
      for (let g = 0; g < grainCount; g++) {
        const grainGeo = new THREE.ConeGeometry(0.12, 0.4, 5);
        const grainMesh = new THREE.Mesh(grainGeo, grainMat);
        const angle = g * 0.7;
        const radius = 0.18;
        const yPos = 0.4 + g * 0.08;

        grainMesh.position.set(
          Math.cos(angle) * radius,
          yPos,
          Math.sin(angle) * radius
        );
        grainMesh.rotation.z = Math.cos(angle) * 0.5;
        grainMesh.rotation.x = Math.sin(angle) * 0.5;
        plantGroup.add(grainMesh);
      }

      // Ground Aura Ring Pedestal
      const ringGeo = new THREE.RingGeometry(0.8, 1.0, 32);
      const ringMat = new THREE.MeshBasicMaterial({
        color: isDark ? 0x10b981 : 0x059669,
        side: THREE.DoubleSide,
        transparent: true,
        opacity: 0.4
      });
      const ringMesh = new THREE.Mesh(ringGeo, ringMat);
      ringMesh.rotation.x = Math.PI / 2;
      ringMesh.position.y = -2.1;
      plantGroup.add(ringMesh);

      scene.add(plantGroup);

      // Render Loop
      let clock = new THREE.Clock();
      const animate = () => {
        animationFrameId = requestAnimationFrame(animate);
        const elapsedTime = clock.getElapsedTime();

        if (plantGroup) {
          plantGroup.rotation.y = elapsedTime * 0.6;
          plantGroup.position.y = Math.sin(elapsedTime * 1.5) * 0.12;
        }

        renderer.render(scene, camera);
      };
      animate();
    }).catch(() => {
      setWebglSupported(false);
    });

    return () => {
      if (animationFrameId) cancelAnimationFrame(animationFrameId);
      if (renderer) renderer.dispose();
    };
  }, [theme]);

  // 2D Static / CSS Animated Fallback for low-end devices without WebGL
  if (!webglSupported) {
    return (
      <div className="relative flex h-72 w-72 items-center justify-center rounded-3xl border border-emerald-500/30 bg-emerald-950/20 p-6 text-center shadow-xl backdrop-blur-md">
        <div className="relative flex flex-col items-center">
          <div className="h-28 w-28 rounded-full bg-emerald-500/20 border border-emerald-400/40 flex items-center justify-center animate-pulse shadow-[0_0_30px_#10b981]">
            <span className="text-4xl">🌾</span>
          </div>
          <p className="mt-3 text-xs font-mono font-bold text-emerald-400">
            Precision Ag 2D Telemetry View
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="relative flex h-80 w-80 items-center justify-center">
      {/* Glow Halo behind 3D Model */}
      <div
        className={`absolute h-64 w-64 rounded-full blur-3xl transition-colors duration-500 ${
          isDark ? "bg-emerald-500/20" : "bg-emerald-400/25"
        }`}
      />
      <div ref={mountRef} className="relative h-full w-full cursor-grab active:cursor-grabbing" />
    </div>
  );
}
