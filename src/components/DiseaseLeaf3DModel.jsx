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

export default function DiseaseLeaf3DModel({ disease, theme = "light" }) {
  const mountRef = useRef(null);
  const [webglSupported, setWebglSupported] = useState(true);
  const [isDragging, setIsDragging] = useState(false);
  const isDark = theme === "cyber" || theme === "dark" || theme === "monochrome";

  const rawSev = typeof disease?.severity === "object" ? disease?.severity?.tier : disease?.severity;
  const isHealthy = String(rawSev || "").toLowerCase() === "healthy";
  const confidence = disease?.confidence || 95;
  const diseaseName = typeof disease?.condition === "object"
    ? (disease.condition?.name || "Leaf Lesion Spot")
    : (disease?.diseaseName || disease?.condition || disease?.diagnosis || "Leaf Lesion Spot");

  useEffect(() => {
    if (!detectWebGL()) {
      setWebglSupported(false);
      return;
    }

    let isMounted = true;
    let THREE;
    let scene, camera, renderer, animationFrameId;
    let leafMesh, lesionMesh, mainGroup;

    let isMouseDown = false;
    let previousMousePosition = { x: 0, y: 0 };

    import("three").then((threeModule) => {
      if (!isMounted) return;
      THREE = threeModule;
      const container = mountRef.current;
      if (!container) return;

      const width = container.clientWidth || 340;
      const height = container.clientHeight || 320;

      scene = new THREE.Scene();
      camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
      camera.position.set(0, 0, 5);

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
        isDark ? 0x10b981 : 0x059669,
        isDark ? 2.2 : 2.0
      );
      dirLight.position.set(4, 5, 4);
      scene.add(dirLight);

      const spotLight = new THREE.SpotLight(
        isHealthy ? 0x10b981 : 0xef4444,
        isDark ? 3.0 : 2.5
      );
      spotLight.position.set(-3, 3, 5);
      scene.add(spotLight);

      mainGroup = new THREE.Group();

      // 1. Create Curved Organic Leaf Mesh Shape
      const leafShape = new THREE.Shape();
      leafShape.moveTo(0, -1.8);
      leafShape.bezierCurveTo(0.9, -1.0, 1.2, 0.2, 0, 1.8);
      leafShape.bezierCurveTo(-1.2, 0.2, -0.9, -1.0, 0, -1.8);

      const extrudeSettings = {
        depth: 0.08,
        bevelEnabled: true,
        bevelSegments: 3,
        steps: 1,
        bevelSize: 0.04,
        bevelThickness: 0.04
      };

      const leafGeo = new THREE.ExtrudeGeometry(leafShape, extrudeSettings);

      // Add gentle parabolic curvature along Z axis for realism
      const posAttr = leafGeo.attributes.position;
      for (let i = 0; i < posAttr.count; i++) {
        const y = posAttr.getY(i);
        const z = posAttr.getZ(i);
        // Curve leaf along Y axis
        posAttr.setZ(i, z - Math.sin((y + 1.8) * 0.8) * 0.25);
      }
      leafGeo.computeVertexNormals();

      const leafMat = new THREE.MeshStandardMaterial({
        color: isDark ? 0x059669 : 0x16a34a,
        roughness: 0.35,
        metalness: 0.1,
        side: THREE.DoubleSide,
        flatShading: false
      });

      leafMesh = new THREE.Mesh(leafGeo, leafMat);
      mainGroup.add(leafMesh);

      // Midrib Stem Line
      const stemGeo = new THREE.CylinderGeometry(0.04, 0.02, 3.8, 8);
      const stemMat = new THREE.MeshStandardMaterial({
        color: isDark ? 0x047857 : 0x15803d,
        roughness: 0.5
      });
      const stemMesh = new THREE.Mesh(stemGeo, stemMat);
      stemMesh.position.set(0, 0, 0.04);
      mainGroup.add(stemMesh);

      // 2. Infection Lesion Highlight Zone (Glowing Red/Orange for Disease)
      if (!isHealthy) {
        const lesionGeo = new THREE.SphereGeometry(0.45, 16, 16);
        lesionGeo.scale(1.2, 0.8, 0.2); // Flattened oval lesion

        const lesionMat = new THREE.MeshStandardMaterial({
          color: 0xef4444,
          emissive: 0xd97706,
          emissiveIntensity: 0.8,
          roughness: 0.2,
          transparent: true,
          opacity: 0.9
        });

        lesionMesh = new THREE.Mesh(lesionGeo, lesionMat);
        lesionMesh.position.set(0.25, 0.4, 0.12);
        mainGroup.add(lesionMesh);

        // Secondary small satellite lesion
        const subLesionGeo = new THREE.SphereGeometry(0.25, 12, 12);
        subLesionGeo.scale(1.0, 0.7, 0.15);
        const subLesionMesh = new THREE.Mesh(subLesionGeo, lesionMat);
        subLesionMesh.position.set(-0.35, -0.3, 0.1);
        mainGroup.add(subLesionMesh);
      } else {
        // Healthy Glow Aura Ring
        const healthyGeo = new THREE.RingGeometry(1.4, 1.5, 32);
        const healthyMat = new THREE.MeshBasicMaterial({
          color: 0x10b981,
          side: THREE.DoubleSide,
          transparent: true,
          opacity: 0.5
        });
        const healthyMesh = new THREE.Mesh(healthyGeo, healthyMat);
        healthyMesh.position.set(0, 0, 0.05);
        mainGroup.add(healthyMesh);
      }

      scene.add(mainGroup);

      // Interactive Rotation Drag Listeners
      const domElem = renderer.domElement;
      
      const onMouseDown = (e) => {
        isMouseDown = true;
        setIsDragging(true);
        previousMousePosition = { x: e.clientX, y: e.clientY };
      };

      const onMouseMove = (e) => {
        if (!isMouseDown || !mainGroup) return;
        const deltaX = e.clientX - previousMousePosition.x;
        const deltaY = e.clientY - previousMousePosition.y;

        mainGroup.rotation.y += deltaX * 0.015;
        mainGroup.rotation.x += deltaY * 0.015;

        previousMousePosition = { x: e.clientX, y: e.clientY };
      };

      const onMouseUp = () => {
        isMouseDown = false;
        setIsDragging(false);
      };

      domElem.addEventListener("mousedown", onMouseDown);
      window.addEventListener("mousemove", onMouseMove);
      window.addEventListener("mouseup", onMouseUp);

      // Render Loop
      let clock = new THREE.Clock();
      const animate = () => {
        animationFrameId = requestAnimationFrame(animate);
        const elapsedTime = clock.getElapsedTime();

        if (mainGroup && !isMouseDown) {
          mainGroup.rotation.y += 0.006;
          mainGroup.position.y = Math.sin(elapsedTime * 1.5) * 0.08;
        }

        if (lesionMesh) {
          // Pulsate disease lesion glow intensity
          lesionMesh.material.emissiveIntensity = 0.6 + Math.sin(elapsedTime * 4) * 0.35;
        }

        renderer.render(scene, camera);
      };
      animate();

      return () => {
        domElem.removeEventListener("mousedown", onMouseDown);
        window.removeEventListener("mousemove", onMouseMove);
        window.removeEventListener("mouseup", onMouseUp);
      };
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
  }, [disease, theme]);

  if (!webglSupported) {
    return (
      <div className="relative flex h-72 w-full flex-col items-center justify-center rounded-2xl border border-emerald-500/30 bg-[#04160f] p-4 text-center">
        <div className="h-24 w-24 rounded-full border border-red-500/40 bg-red-500/10 flex items-center justify-center animate-pulse">
          <span className="text-3xl">🍃</span>
        </div>
        <p className="mt-2 text-xs font-mono font-bold text-amber-400">
          Lesion Zone: {diseaseName}
        </p>
      </div>
    );
  }

  return (
    <div className="relative h-72 w-full flex flex-col items-center justify-center overflow-hidden rounded-2xl border border-emerald-500/30 bg-[#04160f]/60 backdrop-blur-md p-2">
      {/* Dynamic Header Badge */}
      <div className="absolute top-3 left-3 z-10 flex items-center gap-2 rounded-full border border-emerald-500/40 bg-slate-950/80 px-3 py-1 text-[10px] font-mono text-emerald-300">
        <span className={`h-2 w-2 rounded-full ${isHealthy ? "bg-emerald-400 animate-pulse" : "bg-red-500 animate-ping"}`} />
        <span>
          {isHealthy ? "3D HEALTHY CELLULAR MATRIX" : `3D LESION HIGHLIGHT: ${diseaseName}`}
        </span>
      </div>

      <div className="absolute top-3 right-3 z-10 text-[10px] font-mono text-slate-400">
        {isDragging ? "Rotating..." : "Drag to 3D Rotate"}
      </div>

      {/* Glow Halo */}
      <div
        className={`absolute h-48 w-48 rounded-full blur-3xl transition-colors duration-500 ${
          isHealthy ? "bg-emerald-500/20" : "bg-red-500/25"
        }`}
      />

      <div ref={mountRef} className="h-full w-full cursor-grab active:cursor-grabbing" />

      <div className="absolute bottom-2 left-3 right-3 z-10 flex items-center justify-between text-[10px] font-mono text-slate-300">
        <span>AI Match: {confidence}%</span>
        <span className={isHealthy ? "text-emerald-400 font-bold" : "text-red-400 font-bold"}>
          {isHealthy ? "Zero Infection" : "Lesion Zone Highlighted in Glowing Red"}
        </span>
      </div>
    </div>
  );
}
