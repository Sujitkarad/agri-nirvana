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

export default function NDVITerrain3DModel({ fieldData, theme = "light" }) {
  const mountRef = useRef(null);
  const [webglSupported, setWebglSupported] = useState(true);
  const [activeSensor, setActiveSensor] = useState(null);
  const [droneFlying, setDroneFlying] = useState(true);
  const isDark = theme === "dark";

  const ndviScore = fieldData?.ndviScore || 0.76;

  useEffect(() => {
    if (!detectWebGL()) {
      setWebglSupported(false);
      return;
    }

    let THREE;
    let scene, camera, renderer, animationFrameId;
    let terrainGroup, droneGroup, laserBeam;
    let domElem;
    let onMouseDown;
    let onMouseMove;
    let onMouseUp;
    let isMouseDown = false;
    let previousMousePosition = { x: 0, y: 0 };

    import("three").then((threeModule) => {
      THREE = threeModule;
      const container = mountRef.current;
      if (!container) return;

      const width = container.clientWidth || 600;
      const height = container.clientHeight || 380;

      scene = new THREE.Scene();
      camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
      camera.position.set(0, 7.5, 9.5);
      camera.lookAt(0, 0, 0);

      renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
      renderer.setSize(width, height);
      renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

      container.innerHTML = "";
      container.appendChild(renderer.domElement);

      // Lighting
      const ambientLight = new THREE.AmbientLight(
        isDark ? 0x064e3b : 0xdcfce7,
        isDark ? 1.6 : 2.0
      );
      scene.add(ambientLight);

      const dirLight = new THREE.DirectionalLight(
        isDark ? 0xf59e0b : 0x10b981,
        isDark ? 2.2 : 2.0
      );
      dirLight.position.set(6, 10, 6);
      scene.add(dirLight);

      terrainGroup = new THREE.Group();

      // FEATURE 3: 3D Field Terrain Plane Mesh with Heightmap Curves
      const gridWidth = 10;
      const gridDepth = 10;
      const segments = 32;

      const terrainGeo = new THREE.PlaneGeometry(gridWidth, gridDepth, segments, segments);
      terrainGeo.rotateX(-Math.PI / 2);

      // Heightmap Vertex Displacement
      const posAttr = terrainGeo.attributes.position;
      for (let i = 0; i < posAttr.count; i++) {
        const x = posAttr.getX(i);
        const z = posAttr.getZ(i);
        const heightVal = Math.sin(x * 0.5) * Math.cos(z * 0.5) * 0.35 + Math.sin(x * 1.2) * 0.15;
        posAttr.setY(i, heightVal);
      }
      terrainGeo.computeVertexNormals();

      // Create Dynamic NDVI Heatmap Texture using HTML Canvas
      const canvas = document.createElement("canvas");
      canvas.width = 256;
      canvas.height = 256;
      const ctx = canvas.getContext("2d");

      // Draw NDVI Gradient (Green for high, Yellow for mid, Red for stress zones)
      const grad = ctx.createLinearGradient(0, 0, 256, 256);
      if (ndviScore >= 0.70) {
        grad.addColorStop(0, "#10b981"); // Lush emerald
        grad.addColorStop(0.5, "#84cc16"); // Healthy yellow-green
        grad.addColorStop(1, "#059669"); // Deep green
      } else if (ndviScore >= 0.50) {
        grad.addColorStop(0, "#84cc16");
        grad.addColorStop(0.5, "#f59e0b"); // Stress amber
        grad.addColorStop(1, "#10b981");
      } else {
        grad.addColorStop(0, "#ef4444"); // High stress red
        grad.addColorStop(0.6, "#f59e0b");
        grad.addColorStop(1, "#84cc16");
      }
      ctx.fillStyle = grad;
      ctx.fillRect(0, 0, 256, 256);

      // Add Grid Farm Contour Lines
      ctx.strokeStyle = "rgba(255,255,255,0.2)";
      ctx.lineWidth = 4;
      for (let x = 0; x <= 256; x += 32) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, 256);
        ctx.stroke();

        ctx.beginPath();
        ctx.moveTo(0, x);
        ctx.lineTo(256, x);
        ctx.stroke();
      }

      const canvasTexture = new THREE.CanvasTexture(canvas);

      const terrainMat = new THREE.MeshStandardMaterial({
        map: canvasTexture,
        roughness: 0.5,
        metalness: 0.1,
        flatShading: false
      });

      const terrainMesh = new THREE.Mesh(terrainGeo, terrainMat);
      terrainGroup.add(terrainMesh);

      // 3D Soil Sensor Markers (3 Sensors on field)
      const sensorPositions = [
        { id: "s1", x: -2.5, z: -2.0, label: "Sensor A (Moisture 32%)" },
        { id: "s2", x: 2.0, z: 1.5, label: "Sensor B (Soil Temp 22°C)" },
        { id: "s3", x: -1.0, z: 2.5, label: "Sensor C (Nitrogen Optimal)" }
      ];

      sensorPositions.forEach((s) => {
        const pinGroup = new THREE.Group();
        pinGroup.position.set(s.x, 0.4, s.z);

        // Sensor Pole
        const poleGeo = new THREE.CylinderGeometry(0.04, 0.04, 0.8, 8);
        const poleMat = new THREE.MeshStandardMaterial({ color: 0x94a3b8 });
        const poleMesh = new THREE.Mesh(poleGeo, poleMat);
        pinGroup.add(poleMesh);

        // Glowing Sensor Head
        const headGeo = new THREE.SphereGeometry(0.15, 12, 12);
        const headMat = new THREE.MeshStandardMaterial({
          color: 0x38bdf8,
          emissive: 0x0284c7,
          emissiveIntensity: 0.8
        });
        const headMesh = new THREE.Mesh(headGeo, headMat);
        headMesh.position.y = 0.45;
        pinGroup.add(headMesh);

        terrainGroup.add(pinGroup);
      });

      // FEATURE 4: 3D Autonomous Drone Flyover Mesh & Rotor Animation
      droneGroup = new THREE.Group();
      droneGroup.position.set(-3, 3.2, -3);

      // Drone Body Core
      const bodyGeo = new THREE.BoxGeometry(0.5, 0.12, 0.5);
      const bodyMat = new THREE.MeshStandardMaterial({ color: 0x0f172a, roughness: 0.2 });
      const bodyMesh = new THREE.Mesh(bodyGeo, bodyMat);
      droneGroup.add(bodyMesh);

      // 4 Drone Rotors
      const rotorPositions = [
        { x: 0.35, z: 0.35 },
        { x: -0.35, z: 0.35 },
        { x: 0.35, z: -0.35 },
        { x: -0.35, z: -0.35 }
      ];

      const rotorsList = [];
      rotorPositions.forEach((rp) => {
        const rotorGeo = new THREE.CylinderGeometry(0.2, 0.2, 0.02, 8);
        const rotorMat = new THREE.MeshStandardMaterial({ color: 0x38bdf8 });
        const rotorMesh = new THREE.Mesh(rotorGeo, rotorMat);
        rotorMesh.position.set(rp.x, 0.08, rp.z);
        droneGroup.add(rotorMesh);
        rotorsList.push(rotorMesh);
      });

      // Vertical Laser Scanning Cone
      const laserGeo = new THREE.ConeGeometry(1.2, 3.0, 16, 1, true);
      const laserMat = new THREE.MeshBasicMaterial({
        color: 0x10b981,
        transparent: true,
        opacity: 0.35,
        side: THREE.DoubleSide
      });
      laserBeam = new THREE.Mesh(laserGeo, laserMat);
      laserBeam.rotation.x = Math.PI;
      laserBeam.position.y = -1.5;
      droneGroup.add(laserBeam);

      scene.add(droneGroup);
      scene.add(terrainGroup);

      // Mouse Drag Controls
      domElem = renderer.domElement;
      onMouseDown = (e) => {
        isMouseDown = true;
        previousMousePosition = { x: e.clientX, y: e.clientY };
      };

      onMouseMove = (e) => {
        if (!isMouseDown || !terrainGroup) return;
        const deltaX = e.clientX - previousMousePosition.x;
        const deltaY = e.clientY - previousMousePosition.y;

        terrainGroup.rotation.y += deltaX * 0.01;
        terrainGroup.rotation.x += deltaY * 0.005;

        previousMousePosition = { x: e.clientX, y: e.clientY };
      };

      onMouseUp = () => {
        isMouseDown = false;
      };

      domElem.addEventListener("mousedown", onMouseDown);
      window.addEventListener("mousemove", onMouseMove);
      window.addEventListener("mouseup", onMouseUp);

      // Animation Loop
      let clock = new THREE.Clock();
      const animate = () => {
        animationFrameId = requestAnimationFrame(animate);
        const elapsedTime = clock.getElapsedTime();

        if (terrainGroup && !isMouseDown) {
          terrainGroup.rotation.y = Math.sin(elapsedTime * 0.2) * 0.25;
        }

        // Feature 4: Autonomous Drone Scanning Flight Loop
        if (droneGroup && droneFlying) {
          const radius = 3.2;
          droneGroup.position.x = Math.cos(elapsedTime * 0.8) * radius;
          droneGroup.position.z = Math.sin(elapsedTime * 0.8) * radius;
          droneGroup.position.y = 3.0 + Math.sin(elapsedTime * 2) * 0.15;
          droneGroup.rotation.y = -elapsedTime * 0.8;

          // Spin Rotors
          rotorsList.forEach((r) => {
            r.rotation.y += 0.4;
          });
        }

        renderer.render(scene, camera);
      };
      animate();
    }).catch(() => {
      setWebglSupported(false);
    });

    return () => {
      if (animationFrameId) cancelAnimationFrame(animationFrameId);
      if (domElem && onMouseDown) {
        domElem.removeEventListener("mousedown", onMouseDown);
      }
      if (onMouseMove) {
        window.removeEventListener("mousemove", onMouseMove);
      }
      if (onMouseUp) {
        window.removeEventListener("mouseup", onMouseUp);
      }
      if (renderer) renderer.dispose();
    };
  }, [fieldData, theme, droneFlying]);

  if (!webglSupported) {
    return (
      <div className="relative flex h-80 w-full flex-col items-center justify-center rounded-3xl border border-emerald-500/30 bg-[#04160f] p-6 text-center">
        <div className="h-28 w-28 rounded-full border border-emerald-500/40 bg-emerald-500/10 flex items-center justify-center animate-pulse">
          <span className="text-4xl">📡</span>
        </div>
        <p className="mt-3 text-xs font-mono font-bold text-emerald-400">
          Sentinel-2 NDVI Heatmap: {fieldData?.name || "North Field"} ({ndviScore})
        </p>
      </div>
    );
  }

  return (
    <div className="relative h-96 w-full flex flex-col items-center justify-center overflow-hidden rounded-3xl border border-emerald-500/30 bg-[#04160f]/80 backdrop-blur-md p-2">
      {/* Header Badge */}
      <div className="absolute top-4 left-4 z-10 flex items-center gap-2 rounded-full border border-emerald-500/40 bg-slate-950/80 px-3.5 py-1.5 text-xs font-mono text-emerald-300 shadow-md">
        <span className="h-2 w-2 rounded-full bg-emerald-400 animate-ping" />
        <span>FEATURE #3 & #4: 3D NDVI TERRAIN + AUTONOMOUS DRONE</span>
      </div>

      {/* Drone Toggle Button */}
      <button
        onClick={() => setDroneFlying((prev) => !prev)}
        className="absolute top-4 right-4 z-10 flex items-center gap-2 rounded-xl border border-cyan-500/40 bg-cyan-950/80 px-3 py-1.5 text-[11px] font-mono font-bold text-cyan-300 hover:bg-cyan-900/80"
      >
        <span>{droneFlying ? "🚁 Drone Scanning Active" : "⏸ Pause Drone"}</span>
      </button>

      {/* Glow Halo */}
      <div className="absolute h-64 w-64 rounded-full bg-emerald-500/20 blur-3xl" />

      <div ref={mountRef} className="h-full w-full cursor-grab active:cursor-grabbing" />

      {/* Bottom Telemetry Legend */}
      <div className="absolute bottom-3 left-4 right-4 z-10 flex items-center justify-between text-xs font-mono text-slate-300">
        <div className="flex items-center gap-3">
          <span className="flex items-center gap-1"><span className="h-3 w-3 rounded bg-emerald-500" /> Optimal (&gt;0.70)</span>
          <span className="flex items-center gap-1"><span className="h-3 w-3 rounded bg-lime-500" /> Moderate (0.50-0.70)</span>
          <span className="flex items-center gap-1"><span className="h-3 w-3 rounded bg-red-500" /> Stress (&lt;0.50)</span>
        </div>
        <span className="text-emerald-400 font-bold">Sentinel-2 NDVI: {ndviScore}</span>
      </div>
    </div>
  );
}
