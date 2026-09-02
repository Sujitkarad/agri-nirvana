import React, { useEffect, useRef, useState } from "react";

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
    let mainRig, plantGroup, particlesGroup, ringsGroup, groundGlow;
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

      const width = container.clientWidth || 420;
      const height = container.clientHeight || 460;

      // ── SCENE & CAMERA ──
      scene = new THREE.Scene();
      camera = new THREE.PerspectiveCamera(38, width / height, 0.1, 1000);
      camera.position.set(0, 0.6, 7.8);

      renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true, powerPreference: "high-performance" });
      renderer.setSize(width, height);
      renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
      renderer.toneMapping = THREE.ACESFilmicToneMapping;
      renderer.toneMappingExposure = isDark ? 1.35 : 1.7;

      container.innerHTML = "";
      container.appendChild(renderer.domElement);

      // ── LIGHTING RIG ──
      const ambientLight = new THREE.AmbientLight(
        isDark ? 0x052e16 : 0xf0fdf4,
        isDark ? 1.6 : 2.0
      );
      scene.add(ambientLight);

      // Sun key light (rich natural warm green-gold)
      const sunLight = new THREE.DirectionalLight(
        isDark ? 0x34d399 : 0x22c55e,
        isDark ? 3.6 : 3.0
      );
      sunLight.position.set(4, 9, 5);
      scene.add(sunLight);

      // Golden ear spotlight
      const goldSpot = new THREE.PointLight(
        0xf59e0b,
        isDark ? 3.0 : 2.2,
        6
      );
      goldSpot.position.set(0.5, 2.5, 1.5);
      scene.add(goldSpot);

      // Backlight / Rim light for chlorophyll translucency
      const rimLight = new THREE.DirectionalLight(0x38bdf8, isDark ? 2.2 : 1.4);
      rimLight.position.set(-4, -1, -5);
      scene.add(rimLight);

      // Base soil glow
      groundGlow = new THREE.PointLight(
        isDark ? 0x10b981 : 0x16a34a,
        isDark ? 3.5 : 2.0,
        5
      );
      groundGlow.position.set(0, -2.2, 0);
      scene.add(groundGlow);

      // ── MAIN RIG (for mouse tilt & rotation) ──
      mainRig = new THREE.Group();
      scene.add(mainRig);

      plantGroup = new THREE.Group();
      mainRig.add(plantGroup);

      // ── CUSTOM BOTANICAL GEOMETRY BUILDER ──

      // 1. Organic Stem with natural curve
      const stemCurve = new THREE.CatmullRomCurve3([
        new THREE.Vector3(0, -2.1, 0),
        new THREE.Vector3(0.04, -1.2, 0.02),
        new THREE.Vector3(-0.03, -0.2, 0.01),
        new THREE.Vector3(0.02, 0.9, -0.01),
        new THREE.Vector3(0, 2.2, 0),
      ]);

      const stemGeo = new THREE.TubeGeometry(stemCurve, 32, 0.055, 12, false);
      const stemMat = new THREE.MeshStandardMaterial({
        color: isDark ? 0x059669 : 0x15803d,
        roughness: 0.32,
        metalness: 0.08,
      });
      const stemMesh = new THREE.Mesh(stemGeo, stemMat);
      plantGroup.add(stemMesh);

      // Stem Nodes / Sheaths
      const nodeHeights = [-1.4, -0.6, 0.2, 1.0, 1.8];
      nodeHeights.forEach((nh) => {
        const knotGeo = new THREE.TorusGeometry(0.062, 0.02, 8, 16);
        const knotMesh = new THREE.Mesh(knotGeo, stemMat);
        knotMesh.rotation.x = Math.PI / 2;
        knotMesh.position.set(0, nh, 0);
        plantGroup.add(knotMesh);
      });

      // 2. Beautiful Organic Arched Leaves
      function createCurvedLeafGeometry(length, maxWidth, archAmount, twist) {
        const segmentsU = 18; // along leaf length
        const segmentsV = 6;  // across leaf width
        const positions = [];
        const normals = [];
        const uvs = [];
        const indices = [];

        for (let i = 0; i <= segmentsU; i++) {
          const t = i / segmentsU; // 0 to 1
          // Natural leaf spine curve (starts upward, arches outward & droops at tip)
          const spineX = Math.sin(t * Math.PI * 0.55) * length * 0.7;
          const spineY = (t - Math.pow(t, 2.2) * archAmount) * length;
          const spineZ = Math.sin(t * Math.PI) * twist * 0.15;

          // Width profile (narrow at base, swells in midsection, tapers to sharp tip)
          const widthFactor = Math.sin(t * Math.PI) * (1 - t * 0.3);
          const currentWidth = maxWidth * widthFactor;

          for (let j = 0; j <= segmentsV; j++) {
            const v = (j / segmentsV) - 0.5; // -0.5 to 0.5
            // Leaf cross-section has a slight V-groove / rib crease
            const ribDip = Math.abs(v) * 0.08 * currentWidth;
            const posX = spineX;
            const posY = spineY - ribDip;
            const posZ = spineZ + v * currentWidth;

            positions.push(posX, posY, posZ);
            normals.push(0, 1, 0);
            uvs.push(t, j / segmentsV);
          }
        }

        for (let i = 0; i < segmentsU; i++) {
          for (let j = 0; j < segmentsV; j++) {
            const a = i * (segmentsV + 1) + j;
            const b = (i + 1) * (segmentsV + 1) + j;
            const c = (i + 1) * (segmentsV + 1) + (j + 1);
            const d = i * (segmentsV + 1) + (j + 1);
            indices.push(a, b, d);
            indices.push(b, c, d);
          }
        }

        const geo = new THREE.BufferGeometry();
        geo.setAttribute("position", new THREE.Float32BufferAttribute(positions, 3));
        geo.setAttribute("uv", new THREE.Float32BufferAttribute(uvs, 2));
        geo.setIndex(indices);
        geo.computeVertexNormals();
        return geo;
      }

      const leafMaterial = new THREE.MeshStandardMaterial({
        color: isDark ? 0x10b981 : 0x16a34a,
        roughness: 0.28,
        metalness: 0.05,
        side: THREE.DoubleSide,
      });

      const leafHighlightMaterial = new THREE.MeshStandardMaterial({
        color: isDark ? 0x34d399 : 0x22c55e,
        roughness: 0.22,
        metalness: 0.08,
        side: THREE.DoubleSide,
      });

      // 6 Lush arching leaves around the stalk at different heights & azimuths
      const leafConfigs = [
        { y: -1.3, angle: 0, length: 1.55, width: 0.36, arch: 1.15, twist: 0.2 },
        { y: -0.9, angle: Math.PI * 0.65, length: 1.75, width: 0.40, arch: 1.25, twist: -0.3 },
        { y: -0.4, angle: Math.PI * 1.35, length: 1.65, width: 0.38, arch: 1.20, twist: 0.25 },
        { y: 0.1, angle: Math.PI * 0.2, length: 1.80, width: 0.42, arch: 1.30, twist: -0.2 },
        { y: 0.6, angle: Math.PI * 0.9, length: 1.45, width: 0.34, arch: 1.10, twist: 0.3 },
        { y: 1.1, angle: Math.PI * 1.6, length: 1.25, width: 0.28, arch: 0.95, twist: -0.15 },
      ];

      leafConfigs.forEach((cfg, idx) => {
        const lGeo = createCurvedLeafGeometry(cfg.length, cfg.width, cfg.arch, cfg.twist);
        const lMesh = new THREE.Mesh(lGeo, idx % 2 === 0 ? leafMaterial : leafHighlightMaterial);
        lMesh.position.set(0, cfg.y, 0);
        lMesh.rotation.y = cfg.angle;
        plantGroup.add(lMesh);
      });

      // 3. Golden Wheat / Grain Head (Authentic botanical spikelets with fine awn bristles)
      const earGroup = new THREE.Group();
      earGroup.position.set(0, 1.8, 0);

      const grainMat = new THREE.MeshStandardMaterial({
        color: isDark ? 0xf59e0b : 0xd97706,
        roughness: 0.2,
        metalness: 0.25,
      });

      const ripeGlowMat = new THREE.MeshStandardMaterial({
        color: 0xfbbf24,
        roughness: 0.15,
        metalness: 0.4,
        emissive: 0xf59e0b,
        emissiveIntensity: isDark ? 0.35 : 0.18,
      });

      const awnMat = new THREE.LineBasicMaterial({
        color: isDark ? 0xfcd34d : 0xb45309,
        transparent: true,
        opacity: isDark ? 0.65 : 0.45,
      });

      const spikeletCount = 26;
      for (let i = 0; i < spikeletCount; i++) {
        const t = i / spikeletCount;
        const angle = i * 2.39996; // Golden ratio spiral angle
        const radius = (1 - t * 0.35) * 0.16;
        const y = t * 1.55;

        // Plump grain ellipsoid
        const grainScale = 0.08 * (1 - t * 0.2);
        const grainGeo = new THREE.SphereGeometry(grainScale, 10, 8);
        grainGeo.scale(1.0, 1.7, 0.8);
        const grain = new THREE.Mesh(grainGeo, i < 6 ? ripeGlowMat : grainMat);

        const gx = Math.cos(angle) * radius;
        const gz = Math.sin(angle) * radius;
        grain.position.set(gx, y, gz);
        grain.rotation.y = angle;
        grain.rotation.z = Math.cos(angle) * 0.35;
        grain.rotation.x = Math.sin(angle) * 0.35;
        earGroup.add(grain);

        // Awn (delicate whisker bristling outward and upward)
        const awnCurve = new THREE.LineCurve3(
          new THREE.Vector3(gx, y + 0.05, gz),
          new THREE.Vector3(gx * 2.6, y + 0.38 + t * 0.2, gz * 2.6)
        );
        const awnGeo = new THREE.BufferGeometry().setFromPoints(awnCurve.getPoints(4));
        const awnLine = new THREE.Line(awnGeo, awnMat);
        earGroup.add(awnLine);
      }

      plantGroup.add(earGroup);

      // ── HOLOGRAPHIC BIO-BASE & RADIAL RINGS ──
      ringsGroup = new THREE.Group();
      ringsGroup.position.set(0, -2.1, 0);
      mainRig.add(ringsGroup);

      // Base pedestal disc
      const baseGeo = new THREE.CylinderGeometry(1.3, 1.45, 0.08, 48);
      const baseMat = new THREE.MeshStandardMaterial({
        color: isDark ? 0x064e3b : 0xe2e8f0,
        roughness: 0.25,
        metalness: 0.6,
        emissive: isDark ? 0x022c22 : 0x10b981,
        emissiveIntensity: isDark ? 0.3 : 0.08,
      });
      const baseDisc = new THREE.Mesh(baseGeo, baseMat);
      ringsGroup.add(baseDisc);

      // Concentric telemetry rings
      function createRingMesh(r1, r2, col, op) {
        const ringGeo = new THREE.RingGeometry(r1, r2, 64);
        const ringMat = new THREE.MeshBasicMaterial({
          color: col,
          side: THREE.DoubleSide,
          transparent: true,
          opacity: op,
        });
        const rm = new THREE.Mesh(ringGeo, ringMat);
        rm.rotation.x = Math.PI / 2;
        rm.position.y = 0.045;
        return rm;
      }

      const ring1 = createRingMesh(1.15, 1.25, isDark ? 0x10b981 : 0x059669, 0.45);
      const ring2 = createRingMesh(1.6, 1.72, isDark ? 0x06b6d4 : 0x0284c7, 0.25);
      const ring3 = createRingMesh(2.2, 2.28, isDark ? 0x34d399 : 0x16a34a, 0.15);
      ringsGroup.add(ring1);
      ringsGroup.add(ring2);
      ringsGroup.add(ring3);

      // ── PARTICLES (Glowing biological spores / pollen) ──
      particlesGroup = new THREE.Group();
      mainRig.add(particlesGroup);

      const pCount = 70;
      const pPositions = new Float32Array(pCount * 3);
      const pVelocities = [];

      for (let i = 0; i < pCount; i++) {
        const r = 0.8 + Math.random() * 2.2;
        const theta = Math.random() * Math.PI * 2;
        const y = -1.8 + Math.random() * 4.8;
        pPositions[i * 3] = Math.cos(theta) * r;
        pPositions[i * 3 + 1] = y;
        pPositions[i * 3 + 2] = Math.sin(theta) * r;
        pVelocities.push({
          angle: theta,
          speed: 0.12 + Math.random() * 0.18,
          radius: r,
          yOffset: y,
          bobSpeed: 0.8 + Math.random() * 1.5,
        });
      }

      const pGeo = new THREE.BufferGeometry();
      pGeo.setAttribute("position", new THREE.BufferAttribute(pPositions, 3));
      const pMat = new THREE.PointsMaterial({
        color: isDark ? 0x34d399 : 0x15803d,
        size: 0.05,
        transparent: true,
        opacity: isDark ? 0.75 : 0.5,
      });
      const pSystem = new THREE.Points(pGeo, pMat);
      particlesGroup.add(pSystem);

      // ── INTERACTIVE MOUSE / TOUCH DRAG & TILT ──
      const dom = renderer.domElement;

      const onPointerDown = (e) => {
        isDragging = true;
        autoRotate = false;
        previousMousePosition = { x: e.clientX || (e.touches && e.touches[0].clientX) || 0, y: e.clientY || (e.touches && e.touches[0].clientY) || 0 };
      };

      const onPointerMove = (e) => {
        const clientX = e.clientX || (e.touches && e.touches[0].clientX) || 0;
        const clientY = e.clientY || (e.touches && e.touches[0].clientY) || 0;

        if (isDragging) {
          const deltaX = clientX - previousMousePosition.x;
          const deltaY = clientY - previousMousePosition.y;

          targetRotationY += deltaX * 0.01;
          targetRotationX = Math.max(-0.35, Math.min(0.4, targetRotationX + deltaY * 0.008));

          previousMousePosition = { x: clientX, y: clientY };
        } else {
          // Subtle mouse parallax when simply hovering
          const rect = dom.getBoundingClientRect();
          const normX = ((clientX - rect.left) / rect.width - 0.5) * 2;
          const normY = ((clientY - rect.top) / rect.height - 0.5) * 2;
          targetRotationX = -normY * 0.15;
          targetRotationY = normX * 0.25;
        }
      };

      const onPointerUp = () => {
        isDragging = false;
        // Resume slow auto-rotate after 2 seconds idle
        setTimeout(() => { autoRotate = true; }, 2000);
      };

      dom.addEventListener("mousedown", onPointerDown);
      window.addEventListener("mousemove", onPointerMove);
      window.addEventListener("mouseup", onPointerUp);

      dom.addEventListener("touchstart", onPointerDown, { passive: true });
      window.addEventListener("touchmove", onPointerMove, { passive: true });
      window.addEventListener("touchend", onPointerUp);

      // ── ANIMATION TICK ──
      const clock = new THREE.Clock();
      const animate = () => {
        animationFrameId = requestAnimationFrame(animate);
        const elapsed = clock.getElapsedTime();

        if (autoRotate) {
          targetRotationY += 0.006;
        }

        // Smooth damping interpolation (lerp)
        mainRig.rotation.y += (targetRotationY - mainRig.rotation.y) * 0.06;
        mainRig.rotation.x += (targetRotationX - mainRig.rotation.x) * 0.06;

        // Gentle breathing float of the crop
        plantGroup.position.y = Math.sin(elapsed * 1.4) * 0.08;

        // Radial telemetry ring breathing & counter-rotation
        ring1.scale.setScalar(1 + Math.sin(elapsed * 2.2) * 0.04);
        ring2.rotation.z = elapsed * 0.25;
        ring3.rotation.z = -elapsed * 0.15;

        // Pulse ground glow
        groundGlow.intensity = (isDark ? 3.5 : 2.0) + Math.sin(elapsed * 2.0) * 0.7;

        // Animate floating pollen motes
        const pArr = pGeo.attributes.position.array;
        for (let i = 0; i < pCount; i++) {
          const vel = pVelocities[i];
          vel.angle += vel.speed * 0.006;
          pArr[i * 3] = Math.cos(vel.angle) * vel.radius;
          pArr[i * 3 + 2] = Math.sin(vel.angle) * vel.radius;
          pArr[i * 3 + 1] = vel.yOffset + Math.sin(elapsed * vel.bobSpeed) * 0.15;
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
          <div className={`text-xs font-mono font-bold ${isDark ? "text-emerald-400" : "text-emerald-700"}`}>Agri Nirvana · Precision Crop AI</div>
        </div>
      </div>
    );
  }

  return (
    <div className="relative w-full h-full group flex flex-col items-center justify-center">
      {/* Radial soft backdrop glow */}
      <div
        className={`absolute inset-0 pointer-events-none transition-colors duration-500 ${
          isDark
            ? "bg-[radial-gradient(circle_at_50%_60%,rgba(16,185,129,0.22),transparent_70%)]"
            : "bg-[radial-gradient(circle_at_50%_60%,rgba(74,222,128,0.25),transparent_70%)]"
        }`}
      />

      <div
        ref={mountRef}
        className="w-full h-full cursor-grab active:cursor-grabbing select-none"
        style={{ minHeight: "460px" }}
        title="Click and drag to rotate 3D crop"
      />

      {/* Subtle interactive hint */}
      <div className="absolute bottom-3 inset-x-0 flex justify-center pointer-events-none opacity-40 group-hover:opacity-80 transition-opacity">
        <span className={`text-[10px] font-mono tracking-wider px-3 py-1 rounded-full border ${
          isDark ? "bg-black/60 border-emerald-500/30 text-emerald-400" : "bg-white/80 border-slate-200 text-slate-600 shadow-xs"
        }`}>
          ✦ Drag to rotate 360°
        </span>
      </div>
    </div>
  );
}
