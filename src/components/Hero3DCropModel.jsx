import React, { useEffect, useRef, useState } from "react";
import { Sparkles, Layers, Activity, Eye, Zap, RefreshCw } from "lucide-react";

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
  const [activeLayer, setActiveLayer] = useState("all"); // 'all' | 'bio' | 'spectral' | 'cellular'
  const [timeTravelHour, setTimeTravelHour] = useState(12); // 4D: 0h to 24h diurnal growth & daylight cycle
  const [isScanning, setIsScanning] = useState(true);
  const [hoverData, setHoverData] = useState({
    vitality: "99.4%",
    chlorophyllIndex: "0.86 NDVI",
    cellularStatus: "Active Photophosphorylation",
    pathogenRisk: "0.02% (Protected)",
  });

  const isDark = theme === "cyber" || theme === "dark" || theme === "monochrome";

  // References to communicate with the Three.js render loop
  const configRef = useRef({
    activeLayer: "all",
    timeTravelHour: 12,
    isScanning: true,
  });

  useEffect(() => {
    configRef.current = { activeLayer, timeTravelHour, isScanning };
  }, [activeLayer, timeTravelHour, isScanning]);

  useEffect(() => {
    if (!detectWebGL()) {
      setWebglSupported(false);
      return;
    }

    let isMounted = true;
    let THREE;
    let scene, camera, renderer, animationFrameId;
    let mainRig, plantGroup, cellularCoreGroup, spectralFieldGroup, auraRingsGroup, particleCloud;
    let laserBeamPlane, groundHoloGrid, sunLight, pointGlow;
    let isDragging = false;
    let previousMousePosition = { x: 0, y: 0 };
    let targetRotationX = 0.05;
    let targetRotationY = 0;
    let autoRotate = true;

    import("three").then((threeModule) => {
      if (!isMounted) return;
      THREE = threeModule;
      const container = mountRef.current;
      if (!container) return;

      const width = container.clientWidth || 440;
      const height = container.clientHeight || 480;

      // ── SCENE, CAMERA & RENDERER ──
      scene = new THREE.Scene();
      camera = new THREE.PerspectiveCamera(36, width / height, 0.1, 1000);
      camera.position.set(0, 0.5, 7.8);

      renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true, powerPreference: "high-performance" });
      renderer.setSize(width, height);
      renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
      renderer.toneMapping = THREE.ACESFilmicToneMapping;
      renderer.toneMappingExposure = isDark ? 1.4 : 1.7;

      container.innerHTML = "";
      container.appendChild(renderer.domElement);

      // ── 5D MULTI-SPECTRAL DYNAMIC LIGHTING RIG ──
      const ambientLight = new THREE.AmbientLight(
        isDark ? 0x064e3b : 0xf0fdf4,
        isDark ? 1.6 : 2.2
      );
      scene.add(ambientLight);

      sunLight = new THREE.DirectionalLight(0x34d399, isDark ? 3.4 : 2.8);
      sunLight.position.set(4, 9, 5);
      scene.add(sunLight);

      const spectralFill = new THREE.DirectionalLight(0x06b6d4, isDark ? 2.2 : 1.4);
      spectralFill.position.set(-5, 2, -4);
      scene.add(spectralFill);

      const goldEarLight = new THREE.PointLight(0xf59e0b, 3.2, 7);
      goldEarLight.position.set(0, 2.4, 1.2);
      scene.add(goldEarLight);

      pointGlow = new THREE.PointLight(0x10b981, 4.0, 5);
      pointGlow.position.set(0, -2.1, 0);
      scene.add(pointGlow);

      // ── ROOT RIG ──
      mainRig = new THREE.Group();
      scene.add(mainRig);

      plantGroup = new THREE.Group();
      cellularCoreGroup = new THREE.Group();
      spectralFieldGroup = new THREE.Group();
      auraRingsGroup = new THREE.Group();

      mainRig.add(plantGroup);
      mainRig.add(cellularCoreGroup);
      mainRig.add(spectralFieldGroup);
      mainRig.add(auraRingsGroup);

      // ── 1. LAYER A: PHYSICAL PLANT STEM & VASCULAR BUNDLES ──
      const stemPoints = [
        new THREE.Vector3(0, -2.1, 0),
        new THREE.Vector3(0.04, -1.2, 0.02),
        new THREE.Vector3(-0.03, -0.2, 0.01),
        new THREE.Vector3(0.02, 0.9, -0.01),
        new THREE.Vector3(0, 2.2, 0),
      ];
      const stemCurve = new THREE.CatmullRomCurve3(stemPoints);
      const stemGeo = new THREE.TubeGeometry(stemCurve, 36, 0.058, 14, false);
      const stemMat = new THREE.MeshStandardMaterial({
        color: isDark ? 0x059669 : 0x15803d,
        roughness: 0.28,
        metalness: 0.12,
        emissive: isDark ? 0x064e3b : 0x059669,
        emissiveIntensity: isDark ? 0.35 : 0.15,
      });
      const stemMesh = new THREE.Mesh(stemGeo, stemMat);
      plantGroup.add(stemMesh);

      // Node rings (vascular nodes)
      [-1.4, -0.6, 0.2, 1.0, 1.8].forEach((h) => {
        const knotGeo = new THREE.TorusGeometry(0.066, 0.018, 8, 20);
        const knotMesh = new THREE.Mesh(knotGeo, stemMat);
        knotMesh.rotation.x = Math.PI / 2;
        knotMesh.position.y = h;
        plantGroup.add(knotMesh);
      });

      // ── 2. LAYER A: HIGH-PRECISION BIO-ORGANIC ARCHED LEAVES ──
      function createParametricLeaf(length, maxWidth, arch, twist) {
        const segU = 20;
        const segV = 8;
        const pos = [];
        const uvs = [];
        const indices = [];

        for (let i = 0; i <= segU; i++) {
          const t = i / segU;
          const spineX = Math.sin(t * Math.PI * 0.55) * length * 0.72;
          const spineY = (t - Math.pow(t, 2.2) * arch) * length;
          const spineZ = Math.sin(t * Math.PI) * twist * 0.18;
          const wFactor = Math.sin(t * Math.PI) * (1 - t * 0.28);
          const currentW = maxWidth * wFactor;

          for (let j = 0; j <= segV; j++) {
            const v = j / segV - 0.5;
            const ribDip = Math.abs(v) * 0.09 * currentW;
            pos.push(spineX, spineY - ribDip, spineZ + v * currentW);
            uvs.push(t, j / segV);
          }
        }

        for (let i = 0; i < segU; i++) {
          for (let j = 0; j < segV; j++) {
            const a = i * (segV + 1) + j;
            const b = (i + 1) * (segV + 1) + j;
            const c = (i + 1) * (segV + 1) + (j + 1);
            const d = i * (segV + 1) + (j + 1);
            indices.push(a, b, d);
            indices.push(b, c, d);
          }
        }

        const geo = new THREE.BufferGeometry();
        geo.setAttribute("position", new THREE.Float32BufferAttribute(pos, 3));
        geo.setAttribute("uv", new THREE.Float32BufferAttribute(uvs, 2));
        geo.setIndex(indices);
        geo.computeVertexNormals();
        return geo;
      }

      const leafMatHealthy = new THREE.MeshStandardMaterial({
        color: isDark ? 0x10b981 : 0x16a34a,
        roughness: 0.22,
        metalness: 0.06,
        side: THREE.DoubleSide,
      });

      const leafMatGlow = new THREE.MeshStandardMaterial({
        color: isDark ? 0x34d399 : 0x22c55e,
        roughness: 0.18,
        metalness: 0.1,
        emissive: isDark ? 0x059669 : 0x10b981,
        emissiveIntensity: isDark ? 0.35 : 0.12,
        side: THREE.DoubleSide,
      });

      const leafConfigs = [
        { y: -1.3, angle: 0, len: 1.6, w: 0.38, arch: 1.15, twist: 0.2 },
        { y: -0.9, angle: Math.PI * 0.65, len: 1.8, w: 0.42, arch: 1.25, twist: -0.28 },
        { y: -0.4, angle: Math.PI * 1.35, len: 1.7, w: 0.40, arch: 1.20, twist: 0.22 },
        { y: 0.1, angle: Math.PI * 0.2, len: 1.85, w: 0.44, arch: 1.30, twist: -0.18 },
        { y: 0.6, angle: Math.PI * 0.9, len: 1.5, w: 0.35, arch: 1.10, twist: 0.25 },
        { y: 1.1, angle: Math.PI * 1.6, len: 1.3, w: 0.30, arch: 0.95, twist: -0.15 },
      ];

      leafConfigs.forEach((cfg, idx) => {
        const lGeo = createParametricLeaf(cfg.len, cfg.w, cfg.arch, cfg.twist);
        const lMesh = new THREE.Mesh(lGeo, idx % 2 === 0 ? leafMatHealthy : leafMatGlow);
        lMesh.position.set(0, cfg.y, 0);
        lMesh.rotation.y = cfg.angle;
        plantGroup.add(lMesh);
      });

      // ── 3. LAYER A: GOLDEN WHEAT/GRAIN HEAD WITH AWN BRISTLES ──
      const earGroup = new THREE.Group();
      earGroup.position.set(0, 1.85, 0);

      const grainMat = new THREE.MeshStandardMaterial({
        color: 0xf59e0b,
        roughness: 0.15,
        metalness: 0.3,
      });

      const ripeGlowMat = new THREE.MeshStandardMaterial({
        color: 0xfbbf24,
        roughness: 0.1,
        metalness: 0.45,
        emissive: 0xf59e0b,
        emissiveIntensity: 0.4,
      });

      const awnMat = new THREE.LineBasicMaterial({
        color: isDark ? 0xfcd34d : 0xb45309,
        transparent: true,
        opacity: isDark ? 0.7 : 0.45,
      });

      const spikeletCount = 28;
      for (let i = 0; i < spikeletCount; i++) {
        const t = i / spikeletCount;
        const angle = i * 2.39996;
        const radius = (1 - t * 0.38) * 0.17;
        const y = t * 1.6;

        const grainScale = 0.082 * (1 - t * 0.2);
        const grainGeo = new THREE.SphereGeometry(grainScale, 10, 8);
        grainGeo.scale(1.0, 1.7, 0.8);
        const grain = new THREE.Mesh(grainGeo, i < 7 ? ripeGlowMat : grainMat);

        const gx = Math.cos(angle) * radius;
        const gz = Math.sin(angle) * radius;
        grain.position.set(gx, y, gz);
        grain.rotation.y = angle;
        grain.rotation.z = Math.cos(angle) * 0.38;
        grain.rotation.x = Math.sin(angle) * 0.38;
        earGroup.add(grain);

        const awnCurve = new THREE.LineCurve3(
          new THREE.Vector3(gx, y + 0.05, gz),
          new THREE.Vector3(gx * 2.7, y + 0.4 + t * 0.22, gz * 2.7)
        );
        const awnGeo = new THREE.BufferGeometry().setFromPoints(awnCurve.getPoints(4));
        const awnLine = new THREE.Line(awnGeo, awnMat);
        earGroup.add(awnLine);
      }
      plantGroup.add(earGroup);

      // ── 4. LAYER B: 5D CELLULAR & CHLOROPHYLL LATTICE (X-Ray Mode) ──
      // Internal DNA-like cellular helical nodes inside the plant stem
      const helixPoints1 = [];
      const helixPoints2 = [];
      for (let i = -2.0; i <= 2.1; i += 0.08) {
        const a = i * 4.5;
        helixPoints1.push(new THREE.Vector3(Math.cos(a) * 0.09, i, Math.sin(a) * 0.09));
        helixPoints2.push(new THREE.Vector3(Math.cos(a + Math.PI) * 0.09, i, Math.sin(a + Math.PI) * 0.09));
      }
      const helixMat = new THREE.LineBasicMaterial({
        color: 0x38bdf8,
        transparent: true,
        opacity: 0.85,
        linewidth: 2,
      });
      const hLine1 = new THREE.Line(new THREE.BufferGeometry().setFromPoints(helixPoints1), helixMat);
      const hLine2 = new THREE.Line(new THREE.BufferGeometry().setFromPoints(helixPoints2), helixMat);
      cellularCoreGroup.add(hLine1);
      cellularCoreGroup.add(hLine2);

      // Cellular Chloroplast Orbs floating inside nodes
      for (let i = -1.8; i <= 2.0; i += 0.4) {
        const orbGeo = new THREE.IcosahedronGeometry(0.065, 1);
        const orbMat = new THREE.MeshBasicMaterial({
          color: 0x06b6d4,
          wireframe: true,
          transparent: true,
          opacity: 0.75,
        });
        const orbMesh = new THREE.Mesh(orbGeo, orbMat);
        orbMesh.position.y = i;
        cellularCoreGroup.add(orbMesh);
      }

      // ── 5. LAYER C: 5D SPECTRAL ENERGY FIELD (NDVI / Thermal Aura) ──
      const auraShellGeo = new THREE.CylinderGeometry(0.7, 1.4, 4.2, 24, 8, true);
      const auraShellMat = new THREE.MeshBasicMaterial({
        color: isDark ? 0x10b981 : 0x0284c7,
        wireframe: true,
        transparent: true,
        opacity: 0.18,
        side: THREE.DoubleSide,
      });
      const auraShell = new THREE.Mesh(auraShellGeo, auraShellMat);
      auraShell.position.y = 0.1;
      spectralFieldGroup.add(auraShell);

      // ── 6. 5D LASER DIAGNOSTIC SCANNER BEAM ──
      const beamGeo = new THREE.RingGeometry(0.2, 1.9, 48);
      const beamMat = new THREE.MeshBasicMaterial({
        color: 0x22d3ee,
        side: THREE.DoubleSide,
        transparent: true,
        opacity: 0.45,
      });
      laserBeamPlane = new THREE.Mesh(beamGeo, beamMat);
      laserBeamPlane.rotation.x = Math.PI / 2;
      laserBeamPlane.position.y = 0;
      mainRig.add(laserBeamPlane);

      // ── 7. HOLOGRAPHIC BIO-BASE PLATFORM WITH HUD GRID ──
      auraRingsGroup.position.set(0, -2.15, 0);

      const baseDiscGeo = new THREE.CylinderGeometry(1.45, 1.6, 0.08, 64);
      const baseDiscMat = new THREE.MeshStandardMaterial({
        color: isDark ? 0x032114 : 0xe2e8f0,
        roughness: 0.2,
        metalness: 0.8,
        emissive: isDark ? 0x064e3b : 0x059669,
        emissiveIntensity: isDark ? 0.4 : 0.1,
      });
      const baseDisc = new THREE.Mesh(baseDiscGeo, baseDiscMat);
      auraRingsGroup.add(baseDisc);

      // Radar / telemetry rings
      function createRing(r1, r2, col, op) {
        const rGeo = new THREE.RingGeometry(r1, r2, 64);
        const rMat = new THREE.MeshBasicMaterial({
          color: col,
          side: THREE.DoubleSide,
          transparent: true,
          opacity: op,
        });
        const rm = new THREE.Mesh(rGeo, rMat);
        rm.rotation.x = Math.PI / 2;
        rm.position.y = 0.045;
        return rm;
      }
      const ring1 = createRing(1.2, 1.32, 0x10b981, 0.6);
      const ring2 = createRing(1.7, 1.82, 0x06b6d4, 0.35);
      const ring3 = createRing(2.3, 2.38, 0x34d399, 0.2);
      auraRingsGroup.add(ring1);
      auraRingsGroup.add(ring2);
      auraRingsGroup.add(ring3);

      // ── 8. QUANTUM SPORE / BIO-PARTICLE CLOUD ──
      const pCount = 90;
      const pPositions = new Float32Array(pCount * 3);
      const pVelocities = [];

      for (let i = 0; i < pCount; i++) {
        const r = 0.7 + Math.random() * 2.3;
        const theta = Math.random() * Math.PI * 2;
        const y = -1.8 + Math.random() * 5.0;
        pPositions[i * 3] = Math.cos(theta) * r;
        pPositions[i * 3 + 1] = y;
        pPositions[i * 3 + 2] = Math.sin(theta) * r;
        pVelocities.push({
          angle: theta,
          speed: 0.12 + Math.random() * 0.2,
          radius: r,
          yOffset: y,
          bobSpeed: 0.8 + Math.random() * 1.6,
        });
      }

      const pGeo = new THREE.BufferGeometry();
      pGeo.setAttribute("position", new THREE.BufferAttribute(pPositions, 3));
      const pMat = new THREE.PointsMaterial({
        color: isDark ? 0x6ee7b7 : 0x059669,
        size: 0.058,
        transparent: true,
        opacity: isDark ? 0.85 : 0.6,
      });
      particleCloud = new THREE.Points(pGeo, pMat);
      mainRig.add(particleCloud);

      // ── INTERACTIVE MOUSE / TOUCH POINTER CONTROLS ──
      const dom = renderer.domElement;

      const onPointerDown = (e) => {
        isDragging = true;
        autoRotate = false;
        previousMousePosition = {
          x: e.clientX || (e.touches && e.touches[0].clientX) || 0,
          y: e.clientY || (e.touches && e.touches[0].clientY) || 0,
        };
      };

      const onPointerMove = (e) => {
        const clientX = e.clientX || (e.touches && e.touches[0].clientX) || 0;
        const clientY = e.clientY || (e.touches && e.touches[0].clientY) || 0;

        if (isDragging) {
          const deltaX = clientX - previousMousePosition.x;
          const deltaY = clientY - previousMousePosition.y;

          targetRotationY += deltaX * 0.01;
          targetRotationX = Math.max(-0.4, Math.min(0.45, targetRotationX + deltaY * 0.008));
          previousMousePosition = { x: clientX, y: clientY };
        } else {
          const rect = dom.getBoundingClientRect();
          const normX = ((clientX - rect.left) / rect.width - 0.5) * 2;
          const normY = ((clientY - rect.top) / rect.height - 0.5) * 2;
          targetRotationX = -normY * 0.18;
          targetRotationY = normX * 0.3;
        }
      };

      const onPointerUp = () => {
        isDragging = false;
        setTimeout(() => { autoRotate = true; }, 2500);
      };

      dom.addEventListener("mousedown", onPointerDown);
      window.addEventListener("mousemove", onPointerMove);
      window.addEventListener("mouseup", onPointerUp);

      dom.addEventListener("touchstart", onPointerDown, { passive: true });
      window.addEventListener("touchmove", onPointerMove, { passive: true });
      window.addEventListener("touchend", onPointerUp);

      // ── 5D TEMPORAL TICK & DYNAMIC LAYER DISPATCH ──
      const clock = new THREE.Clock();
      const animate = () => {
        animationFrameId = requestAnimationFrame(animate);
        const elapsed = clock.getElapsedTime();
        const cfg = configRef.current;

        // Auto-rotation & smooth drag damping
        if (autoRotate) {
          targetRotationY += 0.0065;
        }
        mainRig.rotation.y += (targetRotationY - mainRig.rotation.y) * 0.06;
        mainRig.rotation.x += (targetRotationX - mainRig.rotation.x) * 0.06;

        // 4D Diurnal Growth / Sunlight Simulation based on timeTravelHour
        const hour = cfg.timeTravelHour;
        const sunAngle = ((hour - 6) / 12) * Math.PI; // Peak at 12 PM
        const sunIntensity = Math.max(0.6, Math.sin(sunAngle) * 3.5);
        sunLight.intensity = sunIntensity;
        sunLight.color.setHSL(0.35 - (hour - 12) * 0.01, 0.8, 0.5);

        // 5D Active Layer Visibility Dispatch
        if (cfg.activeLayer === "bio") {
          plantGroup.visible = true;
          cellularCoreGroup.visible = false;
          spectralFieldGroup.visible = false;
        } else if (cfg.activeLayer === "spectral") {
          plantGroup.visible = true;
          cellularCoreGroup.visible = false;
          spectralFieldGroup.visible = true;
        } else if (cfg.activeLayer === "cellular") {
          plantGroup.visible = false;
          cellularCoreGroup.visible = true;
          spectralFieldGroup.visible = true;
        } else {
          // 'all'
          plantGroup.visible = true;
          cellularCoreGroup.visible = true;
          spectralFieldGroup.visible = true;
        }

        // 5D Scanning Laser Beam Sweep
        if (cfg.isScanning) {
          laserBeamPlane.visible = true;
          const scanY = Math.sin(elapsed * 2.2) * 1.8;
          laserBeamPlane.position.y = scanY;
          laserBeamPlane.material.opacity = 0.25 + Math.abs(Math.cos(elapsed * 4.0)) * 0.35;
        } else {
          laserBeamPlane.visible = false;
        }

        // Plant gentle bio-breathing float
        plantGroup.position.y = Math.sin(elapsed * 1.5) * 0.07;
        cellularCoreGroup.position.y = plantGroup.position.y;

        // Animate aura rings & telemetry
        ring1.scale.setScalar(1 + Math.sin(elapsed * 2.5) * 0.04);
        ring2.rotation.z = elapsed * 0.3;
        ring3.rotation.z = -elapsed * 0.2;

        // Cellular helix spin
        hLine1.rotation.y = elapsed * 0.8;
        hLine2.rotation.y = elapsed * 0.8;

        // Spectral shell breathing
        auraShell.rotation.y = -elapsed * 0.4;
        auraShell.scale.set(
          1 + Math.sin(elapsed * 1.8) * 0.05,
          1,
          1 + Math.sin(elapsed * 1.8) * 0.05
        );

        // Pulse ground glow
        pointGlow.intensity = (isDark ? 3.8 : 2.2) + Math.sin(elapsed * 2.5) * 0.9;

        // Animate Spore Particles
        const pArr = pGeo.attributes.position.array;
        for (let i = 0; i < pCount; i++) {
          const v = pVelocities[i];
          v.angle += v.speed * 0.007;
          pArr[i * 3] = Math.cos(v.angle) * v.radius;
          pArr[i * 3 + 2] = Math.sin(v.angle) * v.radius;
          pArr[i * 3 + 1] = v.yOffset + Math.sin(elapsed * v.bobSpeed) * 0.18;
        }
        pGeo.attributes.position.needsUpdate = true;

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
        if (renderer.domElement?.parentElement) {
          renderer.domElement.parentElement.removeChild(renderer.domElement);
        }
      }
    };
  }, [theme]);

  if (!webglSupported) {
    return (
      <div className={`relative flex h-full w-full items-center justify-center p-8 ${isDark ? "bg-[#040f08]" : "bg-emerald-50"}`}>
        <div className="relative flex flex-col items-center gap-4">
          <div className={`h-32 w-32 rounded-full border-2 flex items-center justify-center animate-pulse ${isDark ? "border-emerald-500/40 bg-emerald-900/30 shadow-[0_0_40px_#10b981]" : "border-emerald-300 bg-emerald-100"}`}>
            <span className="text-5xl">🌾</span>
          </div>
          <div className={`text-xs font-mono font-bold ${isDark ? "text-emerald-400" : "text-emerald-700"}`}>Agri Nirvana · 5D Precision Crop AI</div>
        </div>
      </div>
    );
  }

  return (
    <div className="relative w-full h-full flex flex-col items-center justify-center select-none">
      {/* Radial soft backdrop glow */}
      <div
        className={`absolute inset-0 pointer-events-none transition-colors duration-500 ${
          isDark
            ? "bg-[radial-gradient(circle_at_50%_55%,rgba(16,185,129,0.22),transparent_72%)]"
            : "bg-[radial-gradient(circle_at_50%_55%,rgba(74,222,128,0.25),transparent_72%)]"
        }`}
      />

      {/* 5D HUD TOP CONTROLS: SPECTRAL LAYER SWITCHER */}
      <div className="absolute top-3 inset-x-3 z-20 flex flex-wrap items-center justify-between gap-2 pointer-events-auto">
        <div className="flex items-center gap-1 p-1 rounded-2xl bg-black/60 backdrop-blur-md border border-emerald-500/30 shadow-lg">
          {[
            { id: "all", label: "5D Composite", icon: Sparkles },
            { id: "bio", label: "Physical Bio", icon: Layers },
            { id: "spectral", label: "NDVI Aura", icon: Eye },
            { id: "cellular", label: "Cellular DNA", icon: Activity },
          ].map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              type="button"
              onClick={() => setActiveLayer(id)}
              className={`flex items-center gap-1.5 px-2.5 py-1 rounded-xl text-[10px] font-mono font-bold transition-all ${
                activeLayer === id
                  ? "bg-emerald-500 text-slate-950 shadow-md shadow-emerald-500/40 font-black scale-[1.02]"
                  : "text-slate-300 hover:text-white hover:bg-white/10"
              }`}
            >
              <Icon size={12} />
              <span>{label}</span>
            </button>
          ))}
        </div>

        {/* Laser Scanner Toggle */}
        <button
          type="button"
          onClick={() => setIsScanning(!isScanning)}
          title="Toggle 5D Diagnostic Laser Sweep"
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-[10px] font-mono font-bold border transition-all ${
            isScanning
              ? "bg-cyan-500/20 border-cyan-400/50 text-cyan-300 shadow-[0_0_15px_rgba(6,182,212,0.3)]"
              : "bg-black/50 border-white/10 text-slate-400"
          }`}
        >
          <Zap size={12} className={isScanning ? "animate-pulse text-cyan-400" : ""} />
          <span>{isScanning ? "Scanner Active" : "Scanner Paused"}</span>
        </button>
      </div>

      {/* 3D Canvas Mount Point */}
      <div
        ref={mountRef}
        className="w-full h-full cursor-grab active:cursor-grabbing"
        style={{ minHeight: "470px" }}
        title="Click and drag to rotate 3D crop in 360°"
      />

      {/* 5D HUD BOTTOM BAR: 4D TIME-TRAVEL SLIDER & TELEMETRY */}
      <div className="absolute bottom-3 inset-x-3 z-20 flex flex-col gap-2 pointer-events-auto">
        {/* 4D Diurnal Time Travel Slider */}
        <div className="flex items-center justify-between gap-3 px-3 py-2 rounded-2xl bg-black/65 backdrop-blur-md border border-emerald-500/30">
          <div className="flex items-center gap-2 shrink-0">
            <span className="text-[10px] font-mono font-bold text-emerald-400 flex items-center gap-1">
              <RefreshCw size={11} className="animate-spin" style={{ animationDuration: "8s" }} />
              4D Diurnal Cycle:
            </span>
            <span className="text-[11px] font-mono font-extrabold text-white">
              {timeTravelHour < 10 ? `0${timeTravelHour}:00` : `${timeTravelHour}:00`}{" "}
              {timeTravelHour >= 6 && timeTravelHour <= 18 ? "☀️ Day" : "🌙 Night"}
            </span>
          </div>

          <input
            type="range"
            min="0"
            max="24"
            value={timeTravelHour}
            onChange={(e) => setTimeTravelHour(Number(e.target.value))}
            className="w-full h-1.5 accent-emerald-400 bg-white/20 rounded-lg cursor-pointer"
            title="Slide to simulate full 24-hour crop sunlight and diurnal metabolism"
          />

          <span className="text-[9px] font-mono font-bold text-emerald-400/80 shrink-0">
            Drag 360°
          </span>
        </div>

        {/* 5th Dimension Telemetry Metrics Pills */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-1.5 text-center">
          <div className="px-2 py-1 rounded-xl bg-black/55 backdrop-blur-sm border border-emerald-500/20">
            <div className="text-[8px] font-mono uppercase text-slate-400">Vitality Index</div>
            <div className="text-[11px] font-mono font-extrabold text-emerald-400">{hoverData.vitality}</div>
          </div>
          <div className="px-2 py-1 rounded-xl bg-black/55 backdrop-blur-sm border border-cyan-500/20">
            <div className="text-[8px] font-mono uppercase text-slate-400">NDVI Chlorophyll</div>
            <div className="text-[11px] font-mono font-extrabold text-cyan-300">{hoverData.chlorophyllIndex}</div>
          </div>
          <div className="px-2 py-1 rounded-xl bg-black/55 backdrop-blur-sm border border-amber-500/20">
            <div className="text-[8px] font-mono uppercase text-slate-400">Cellular State</div>
            <div className="text-[11px] font-mono font-extrabold text-amber-300 truncate">{hoverData.cellularStatus}</div>
          </div>
          <div className="px-2 py-1 rounded-xl bg-black/55 backdrop-blur-sm border border-emerald-500/20">
            <div className="text-[8px] font-mono uppercase text-slate-400">Pathogen Risk</div>
            <div className="text-[11px] font-mono font-extrabold text-emerald-300">{hoverData.pathogenRisk}</div>
          </div>
        </div>
      </div>
    </div>
  );
}
