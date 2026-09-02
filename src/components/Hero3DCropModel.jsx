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
  const isDark = theme === "cyber" || theme === "dark" || theme === "monochrome";

  useEffect(() => {
    if (!detectWebGL()) {
      setWebglSupported(false);
      return;
    }

    let isMounted = true;
    let THREE;
    let scene, camera, renderer, animationFrameId;
    let plantGroup, scanRingGroup, particleSystem, gridMesh;

    import("three").then((threeModule) => {
      if (!isMounted) return;
      THREE = threeModule;
      const container = mountRef.current;
      if (!container) return;

      const width = container.clientWidth || 360;
      const height = container.clientHeight || 360;

      scene = new THREE.Scene();
      camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
      camera.position.set(0, 0.6, 7.2);

      renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
      renderer.setSize(width, height);
      renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

      container.innerHTML = "";
      container.appendChild(renderer.domElement);

      // ── Lights ──────────────────────────────────────────────────────────
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

      const backLight = new THREE.DirectionalLight(0x38bdf8, 1.4);
      backLight.position.set(-5, -2, -4);
      scene.add(backLight);

      const scanLight = new THREE.PointLight(0x22d3ee, 2.2, 8);
      scanLight.position.set(0, 1, 2);
      scene.add(scanLight);

      // ── Crop Plant Group (Wheat / Grain Stalk) ─────────────────────────
      plantGroup = new THREE.Group();

      const stemMat = new THREE.MeshStandardMaterial({
        color: isDark ? 0x10b981 : 0x16a34a,
        roughness: 0.4,
        metalness: 0.1,
        flatShading: true
      });
      const stemGeo = new THREE.CylinderGeometry(0.06, 0.09, 3.2, 8);
      const stemMesh = new THREE.Mesh(stemGeo, stemMat);
      stemMesh.position.y = -0.5;
      plantGroup.add(stemMesh);

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

      scene.add(plantGroup);

      // ── Holographic AI-Scan Grid (floor) ───────────────────────────────
      const gridSize = 4.2;
      const gridDivisions = 14;
      gridMesh = new THREE.GridHelper(
        gridSize,
        gridDivisions,
        isDark ? 0x22d3ee : 0x0ea5e9,
        isDark ? 0x0e7490 : 0x67e8f9
      );
      gridMesh.position.y = -2.15;
      gridMesh.material.transparent = true;
      gridMesh.material.opacity = 0.45;
      scene.add(gridMesh);

      // Ground aura ring pedestal
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

      // ── Vertical AI-Diagnostic Scan Rings ──────────────────────────────
      scanRingGroup = new THREE.Group();
      const scanRingCount = 3;
      const scanRingMeshes = [];
      for (let s = 0; s < scanRingCount; s++) {
        const sRingGeo = new THREE.TorusGeometry(1.35, 0.012, 8, 48);
        const sRingMat = new THREE.MeshBasicMaterial({
          color: 0x22d3ee,
          transparent: true,
          opacity: 0.55
        });
        const sRingMesh = new THREE.Mesh(sRingGeo, sRingMat);
        sRingMesh.rotation.x = Math.PI / 2;
        sRingMesh.position.y = -2.0;
        scanRingGroup.add(sRingMesh);
        scanRingMeshes.push(sRingMesh);
      }
      scene.add(scanRingGroup);

      // ── Orbiting Telemetry Data-Particle Layer ─────────────────────────
      const particleCount = 90;
      const positions = new Float32Array(particleCount * 3);
      const particleData = [];
      for (let p = 0; p < particleCount; p++) {
        const radius = 1.6 + Math.random() * 1.4;
        const theta = Math.random() * Math.PI * 2;
        const yOff = (Math.random() - 0.5) * 3.2;
        positions[p * 3] = Math.cos(theta) * radius;
        positions[p * 3 + 1] = yOff;
        positions[p * 3 + 2] = Math.sin(theta) * radius;
        particleData.push({ radius, theta, yOff, speed: 0.15 + Math.random() * 0.35 });
      }
      const particleGeo = new THREE.BufferGeometry();
      particleGeo.setAttribute("position", new THREE.BufferAttribute(positions, 3));
      const particleMat = new THREE.PointsMaterial({
        color: isDark ? 0x67e8f9 : 0x0ea5e9,
        size: 0.045,
        transparent: true,
        opacity: 0.85,
        sizeAttenuation: true
      });
      particleSystem = new THREE.Points(particleGeo, particleMat);
      scene.add(particleSystem);

      // Amber "signal ping" particles
      const pingCount = 14;
      const pingPositions = new Float32Array(pingCount * 3);
      const pingData = [];
      for (let p = 0; p < pingCount; p++) {
        const radius = 2.0 + Math.random() * 0.6;
        const theta = Math.random() * Math.PI * 2;
        const yOff = (Math.random() - 0.5) * 2.2;
        pingPositions[p * 3] = Math.cos(theta) * radius;
        pingPositions[p * 3 + 1] = yOff;
        pingPositions[p * 3 + 2] = Math.sin(theta) * radius;
        pingData.push({ radius, theta, yOff, speed: 0.25 + Math.random() * 0.3 });
      }
      const pingGeo = new THREE.BufferGeometry();
      pingGeo.setAttribute("position", new THREE.BufferAttribute(pingPositions, 3));
      const pingMat = new THREE.PointsMaterial({
        color: 0xf59e0b,
        size: 0.07,
        transparent: true,
        opacity: 0.9,
        sizeAttenuation: true
      });
      const pingSystem = new THREE.Points(pingGeo, pingMat);
      scene.add(pingSystem);

      // ── Render Loop ─────────────────────────────────────────────────────
      let clock = new THREE.Clock();
      const animate = () => {
        animationFrameId = requestAnimationFrame(animate);
        const elapsedTime = clock.getElapsedTime();

        if (plantGroup) {
          plantGroup.rotation.y = elapsedTime * 0.6;
          plantGroup.position.y = Math.sin(elapsedTime * 1.5) * 0.12;
        }

        if (gridMesh) {
          gridMesh.rotation.y = elapsedTime * 0.05;
        }

        if (scanRingGroup) {
          scanRingMeshes.forEach((ring, i) => {
            const cycle = (elapsedTime * 0.5 + i * 0.6) % 2.6;
            ring.position.y = -2.0 + cycle * 1.9;
            const fade = 1 - Math.min(cycle / 2.6, 1);
            ring.material.opacity = 0.6 * fade;
            const scale = 1 + cycle * 0.08;
            ring.scale.set(scale, scale, scale);
          });
        }

        if (particleSystem) {
          const posAttr = particleSystem.geometry.attributes.position;
          for (let p = 0; p < particleData.length; p++) {
            const d = particleData[p];
            d.theta += d.speed * 0.01;
            posAttr.array[p * 3] = Math.cos(d.theta) * d.radius;
            posAttr.array[p * 3 + 2] = Math.sin(d.theta) * d.radius;
          }
          posAttr.needsUpdate = true;
          particleSystem.rotation.y = -elapsedTime * 0.03;
        }

        if (pingSystem) {
          const posAttr = pingSystem.geometry.attributes.position;
          for (let p = 0; p < pingData.length; p++) {
            const d = pingData[p];
            d.theta += d.speed * 0.012;
            posAttr.array[p * 3] = Math.cos(d.theta) * d.radius;
            posAttr.array[p * 3 + 2] = Math.sin(d.theta) * d.radius;
            posAttr.array[p * 3 + 1] = d.yOff + Math.sin(elapsedTime * 2 + p) * 0.15;
          }
          posAttr.needsUpdate = true;
        }

        if (scanLight) {
          scanLight.position.x = Math.sin(elapsedTime * 0.8) * 2;
          scanLight.position.z = Math.cos(elapsedTime * 0.8) * 2;
        }

        renderer.render(scene, camera);
      };
      animate();
    }).catch(() => {
      setWebglSupported(false);
    });

    return () => {
      isMounted = false;
      if (animationFrameId) cancelAnimationFrame(animationFrameId);
      if (renderer) {
        renderer.dispose();
        if (renderer.domElement && renderer.domElement.parentElement) {
          renderer.domElement.parentElement.removeChild(renderer.domElement);
        }
      }
    };
  }, [theme]);

  // 2D Static / CSS Animated Fallback for low-end devices without WebGL
  if (!webglSupported) {
    return (
      <div className="relative flex h-72 w-72 items-center justify-center rounded-3xl border border-cyan-500/30 bg-emerald-950/20 p-6 text-center shadow-xl backdrop-blur-md">
        <div className="relative flex flex-col items-center">
          <div className="h-28 w-28 rounded-full bg-emerald-500/20 border border-cyan-400/40 flex items-center justify-center animate-pulse shadow-[0_0_30px_#22d3ee]">
            <span className="text-4xl">🌾</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="relative flex h-full w-full items-center justify-center">
      {/* Glow Halo behind 5D Model */}
      <div
        className={`absolute h-64 w-64 rounded-full blur-3xl transition-colors duration-500 ${
          isDark ? "bg-cyan-500/20" : "bg-emerald-400/25"
        }`}
      />
      <div ref={mountRef} className="relative h-full w-full cursor-grab active:cursor-grabbing" />
    </div>
  );
}
