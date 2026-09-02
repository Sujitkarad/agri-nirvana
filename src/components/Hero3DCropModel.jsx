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
    let plantGroup, particles, scanRing1, scanRing2, scanRing3, platform;

    import("three").then((threeModule) => {
      if (!isMounted) return;
      THREE = threeModule;
      const container = mountRef.current;
      if (!container) return;

      const width = container.clientWidth || 380;
      const height = container.clientHeight || 460;

      // ── SCENE ──
      scene = new THREE.Scene();
      camera = new THREE.PerspectiveCamera(42, width / height, 0.1, 1000);
      camera.position.set(0, 0.8, 7.5);

      renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
      renderer.setSize(width, height);
      renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
      renderer.shadowMap.enabled = true;
      renderer.shadowMap.type = THREE.PCFSoftShadowMap;
      renderer.toneMapping = THREE.ACESFilmicToneMapping;
      renderer.toneMappingExposure = isDark ? 1.4 : 1.8;

      container.innerHTML = "";
      container.appendChild(renderer.domElement);

      // ── LIGHTS ──
      // Ambient
      const ambient = new THREE.AmbientLight(
        isDark ? 0x063520 : 0xd1fae5,
        isDark ? 2.0 : 2.4
      );
      scene.add(ambient);

      // Key light — warm sun/green top
      const keyLight = new THREE.DirectionalLight(
        isDark ? 0x10b981 : 0x22c55e,
        isDark ? 3.5 : 3.0
      );
      keyLight.position.set(4, 10, 6);
      keyLight.castShadow = true;
      scene.add(keyLight);

      // Fill light — cool sky
      const fillLight = new THREE.DirectionalLight(
        isDark ? 0x06b6d4 : 0x7dd3fc,
        isDark ? 1.5 : 1.0
      );
      fillLight.position.set(-6, 4, -3);
      scene.add(fillLight);

      // Rim light — warm amber backlight
      const rimLight = new THREE.DirectionalLight(
        isDark ? 0xf59e0b : 0xfbbf24,
        isDark ? 1.8 : 1.2
      );
      rimLight.position.set(-3, -2, -6);
      scene.add(rimLight);

      // Point light at base for glow
      const baseGlow = new THREE.PointLight(
        isDark ? 0x10b981 : 0x4ade80,
        isDark ? 4.0 : 2.5,
        8
      );
      baseGlow.position.set(0, -2.5, 0);
      scene.add(baseGlow);

      // ── PLANT GROUP ──
      plantGroup = new THREE.Group();

      // --- Stem (tapered, segmented) ---
      const stemMat = new THREE.MeshStandardMaterial({
        color: isDark ? 0x059669 : 0x15803d,
        roughness: 0.35,
        metalness: 0.08,
        flatShading: false,
      });

      for (let seg = 0; seg < 5; seg++) {
        const topR = 0.055 - seg * 0.006;
        const botR = 0.065 - seg * 0.006;
        const segGeo = new THREE.CylinderGeometry(topR, botR, 0.72, 10);
        const segMesh = new THREE.Mesh(segGeo, stemMat);
        segMesh.position.y = -1.6 + seg * 0.72;
        segMesh.castShadow = true;
        plantGroup.add(segMesh);

        // Stem node knot
        if (seg < 4) {
          const knotGeo = new THREE.SphereGeometry(0.075, 8, 6);
          const knotMesh = new THREE.Mesh(knotGeo, stemMat);
          knotMesh.position.y = -1.6 + seg * 0.72 + 0.36;
          plantGroup.add(knotMesh);
        }
      }

      // --- Broad leaves (maize/corn style, 6 leaves) ---
      const leafMat = new THREE.MeshStandardMaterial({
        color: isDark ? 0x34d399 : 0x16a34a,
        roughness: 0.25,
        metalness: 0.0,
        side: THREE.DoubleSide,
        flatShading: false,
      });
      const leafHighMat = new THREE.MeshStandardMaterial({
        color: isDark ? 0x6ee7b7 : 0x4ade80,
        roughness: 0.2,
        metalness: 0.0,
        side: THREE.DoubleSide,
      });

      const leafAngles = [0, Math.PI / 3, (2 * Math.PI) / 3, Math.PI, (4 * Math.PI) / 3, (5 * Math.PI) / 3];
      const leafHeights = [-0.9, -0.35, 0.2, -0.65, 0.45, -0.1];

      for (let i = 0; i < 6; i++) {
        const leafGeo = new THREE.ConeGeometry(0.38, 1.7, 6, 1, false);
        const mat = i % 3 === 0 ? leafHighMat : leafMat;
        const leaf = new THREE.Mesh(leafGeo, mat);
        const angle = leafAngles[i];
        leaf.position.set(
          Math.sin(angle) * 0.12,
          leafHeights[i],
          Math.cos(angle) * 0.12
        );
        // Droop outward and down
        leaf.rotation.z = (Math.PI / 2.6) * (Math.sin(angle) > 0 ? 1 : -1);
        leaf.rotation.y = angle;
        leaf.rotation.x = 0.25;
        leaf.scale.set(1, 1, 0.1);
        leaf.castShadow = true;
        plantGroup.add(leaf);
      }

      // --- Wheat/Grain Ear at top ---
      const earMat = new THREE.MeshStandardMaterial({
        color: isDark ? 0xfbbf24 : 0xd97706,
        roughness: 0.18,
        metalness: 0.3,
        flatShading: true,
      });
      const earGlowMat = new THREE.MeshStandardMaterial({
        color: isDark ? 0xf59e0b : 0xf59e0b,
        roughness: 0.1,
        metalness: 0.5,
        emissive: isDark ? 0xf59e0b : 0xfbbf24,
        emissiveIntensity: isDark ? 0.4 : 0.2,
        flatShading: true,
      });

      const earGrains = 22;
      for (let g = 0; g < earGrains; g++) {
        const gSize = 0.1 - g * 0.002;
        const grainGeo = new THREE.SphereGeometry(Math.max(gSize, 0.06), 6, 5);
        const grain = new THREE.Mesh(grainGeo, g < 4 ? earGlowMat : earMat);
        const angle = g * 0.65;
        const r = 0.14 - g * 0.003;
        grain.position.set(
          Math.cos(angle) * r,
          1.0 + g * 0.1,
          Math.sin(angle) * r
        );
        grain.castShadow = true;
        plantGroup.add(grain);
      }

      // Tip spike
      const tipGeo = new THREE.ConeGeometry(0.06, 0.5, 6);
      const tip = new THREE.Mesh(tipGeo, earGlowMat);
      tip.position.y = 3.3;
      plantGroup.add(tip);

      // ── GLOWING PLATFORM PEDESTAL ──
      const platformGroup = new THREE.Group();

      const discGeo = new THREE.CylinderGeometry(1.4, 1.6, 0.12, 48);
      const discMat = new THREE.MeshStandardMaterial({
        color: isDark ? 0x064e3b : 0xd1fae5,
        roughness: 0.2,
        metalness: 0.6,
        emissive: isDark ? 0x022c22 : 0x6ee7b7,
        emissiveIntensity: isDark ? 0.6 : 0.2,
      });
      const disc = new THREE.Mesh(discGeo, discMat);
      disc.receiveShadow = true;
      platformGroup.add(disc);

      // Inner disc
      const innerDiscGeo = new THREE.CylinderGeometry(0.85, 0.9, 0.14, 48);
      const innerDiscMat = new THREE.MeshStandardMaterial({
        color: isDark ? 0x10b981 : 0x4ade80,
        roughness: 0.1,
        metalness: 0.8,
        emissive: isDark ? 0x10b981 : 0x22c55e,
        emissiveIntensity: isDark ? 1.0 : 0.4,
      });
      const innerDisc = new THREE.Mesh(innerDiscGeo, innerDiscMat);
      innerDisc.position.y = 0.01;
      platformGroup.add(innerDisc);

      platformGroup.position.y = -2.2;
      scene.add(platformGroup);

      // ── SCAN RINGS ──
      const makeRing = (innerR, outerR, color, opacity) => {
        const geo = new THREE.RingGeometry(innerR, outerR, 64);
        const mat = new THREE.MeshBasicMaterial({
          color,
          side: THREE.DoubleSide,
          transparent: true,
          opacity,
        });
        const mesh = new THREE.Mesh(geo, mat);
        mesh.rotation.x = Math.PI / 2;
        return mesh;
      };

      scanRing1 = makeRing(1.3, 1.5, isDark ? 0x10b981 : 0x22c55e, 0.5);
      scanRing1.position.y = -2.15;
      scene.add(scanRing1);

      scanRing2 = makeRing(2.0, 2.15, isDark ? 0x06b6d4 : 0x38bdf8, 0.25);
      scanRing2.position.y = -2.15;
      scene.add(scanRing2);

      scanRing3 = makeRing(2.8, 2.9, isDark ? 0x10b981 : 0x4ade80, 0.12);
      scanRing3.position.y = -2.15;
      scene.add(scanRing3);

      // ── FLOATING PARTICLES ──
      const particleCount = 90;
      const positions = new Float32Array(particleCount * 3);
      const particleData = [];

      for (let i = 0; i < particleCount; i++) {
        const r = 1.8 + Math.random() * 2.2;
        const theta = Math.random() * Math.PI * 2;
        const phi = (Math.random() - 0.5) * Math.PI;
        positions[i * 3] = r * Math.cos(theta) * Math.cos(phi);
        positions[i * 3 + 1] = r * Math.sin(phi) * 1.5;
        positions[i * 3 + 2] = r * Math.sin(theta) * Math.cos(phi);
        particleData.push({ r, theta, phi, speed: 0.08 + Math.random() * 0.12 });
      }

      const pGeo = new THREE.BufferGeometry();
      pGeo.setAttribute("position", new THREE.BufferAttribute(positions, 3));
      const pMat = new THREE.PointsMaterial({
        color: isDark ? 0x10b981 : 0x4ade80,
        size: 0.055,
        transparent: true,
        opacity: 0.7,
        sizeAttenuation: true,
      });
      particles = new THREE.Points(pGeo, pMat);
      scene.add(particles);

      scene.add(plantGroup);
      plantGroup.position.y = 0;

      // ── ANIMATION LOOP ──
      const clock = new THREE.Clock();
      const animate = () => {
        animationFrameId = requestAnimationFrame(animate);
        const t = clock.getElapsedTime();

        // Plant: slow Y-rotate + gentle bob
        plantGroup.rotation.y = t * 0.45;
        plantGroup.position.y = Math.sin(t * 1.2) * 0.1;

        // Scan rings: pulse scale + opacity
        const pulse = 0.5 + Math.sin(t * 2.0) * 0.5;
        scanRing1.scale.set(1 + pulse * 0.06, 1, 1 + pulse * 0.06);
        scanRing1.material.opacity = 0.3 + pulse * 0.25;

        const pulse2 = 0.5 + Math.sin(t * 1.4 + 1) * 0.5;
        scanRing2.scale.set(1 + pulse2 * 0.04, 1, 1 + pulse2 * 0.04);
        scanRing2.material.opacity = 0.12 + pulse2 * 0.16;

        scanRing3.rotation.z = t * 0.3;
        scanRing3.material.opacity = 0.05 + Math.sin(t * 0.9) * 0.07;

        // Particles: slow orbit
        const pos = particles.geometry.attributes.position;
        for (let i = 0; i < particleCount; i++) {
          const d = particleData[i];
          d.theta += d.speed * 0.008;
          pos.setX(i, d.r * Math.cos(d.theta) * Math.cos(d.phi));
          pos.setZ(i, d.r * Math.sin(d.theta) * Math.cos(d.phi));
          pos.setY(i, d.r * Math.sin(d.phi) * 1.5 + Math.sin(t * d.speed + i) * 0.1);
        }
        pos.needsUpdate = true;

        // Base glow pulse
        baseGlow.intensity = (isDark ? 4.0 : 2.5) + Math.sin(t * 2.5) * 0.8;

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

  // CSS fallback
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
    <div className="relative w-full h-full">
      {/* Radial glow beneath model */}
      <div className={`absolute inset-0 pointer-events-none rounded-3xl ${
        isDark
          ? "bg-[radial-gradient(ellipse_60%_50%_at_50%_80%,rgba(16,185,129,0.18),transparent)]"
          : "bg-[radial-gradient(ellipse_60%_50%_at_50%_80%,rgba(74,222,128,0.2),transparent)]"
      }`} />
      <div ref={mountRef} className="w-full h-full" style={{minHeight: "460px"}} />
    </div>
  );
}
