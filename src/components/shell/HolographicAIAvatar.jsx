import React, { useEffect, useRef } from "react";
import * as THREE from "three";

export default function HolographicAIAvatar({
  state = "idle", // 'idle' | 'thinking' | 'processing' | 'speaking' | 'success' | 'error'
  selectedModel = "Mistral-7B",
  isDark = true,
  className = ""
}) {
  const mountRef = useRef(null);
  const stateRef = useRef(state);
  stateRef.current = state;

  useEffect(() => {
    const container = mountRef.current;
    if (!container) return;

    const width = container.clientWidth || 240;
    const height = container.clientHeight || 240;

    // Scene & Camera
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
    camera.position.z = 7;

    // WebGL Renderer
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: "high-performance" });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    container.appendChild(renderer.domElement);

    // 1. Central Core Sphere (Icosahedron with wireframe + glowing points)
    const coreGeo = new THREE.IcosahedronGeometry(1.2, 2);
    const coreMat = new THREE.MeshBasicMaterial({
      color: 0x10b981,
      wireframe: true,
      transparent: true,
      opacity: 0.8
    });
    const coreMesh = new THREE.Mesh(coreGeo, coreMat);
    scene.add(coreMesh);

    // 2. Inner Glowing Core Points
    const innerGeo = new THREE.SphereGeometry(0.75, 16, 16);
    const innerMat = new THREE.MeshBasicMaterial({
      color: 0x06b6d4,
      wireframe: false,
      transparent: true,
      opacity: 0.6
    });
    const innerMesh = new THREE.Mesh(innerGeo, innerMat);
    scene.add(innerMesh);

    // 3. Orbital Particle Rings (Particle System)
    const particleCount = 180;
    const particleGeo = new THREE.BufferGeometry();
    const particlePositions = new Float32Array(particleCount * 3);
    const particleColors = new Float32Array(particleCount * 3);

    const cEmerald = new THREE.Color(0x10b981);
    const cCyan = new THREE.Color(0x06b6d4);
    const cAmber = new THREE.Color(0xf59e0b);

    for (let i = 0; i < particleCount; i++) {
      const radius = 2.0 + Math.random() * 0.8;
      const theta = Math.random() * Math.PI * 2;
      const phi = (Math.random() - 0.5) * 0.8;

      particlePositions[i * 3] = radius * Math.cos(theta) * Math.cos(phi);
      particlePositions[i * 3 + 1] = radius * Math.sin(phi);
      particlePositions[i * 3 + 2] = radius * Math.sin(theta) * Math.cos(phi);

      const mixed = Math.random() > 0.5 ? cEmerald : cCyan;
      particleColors[i * 3] = mixed.r;
      particleColors[i * 3 + 1] = mixed.g;
      particleColors[i * 3 + 2] = mixed.b;
    }

    particleGeo.setAttribute("position", new THREE.BufferAttribute(particlePositions, 3));
    particleGeo.setAttribute("color", new THREE.BufferAttribute(particleColors, 3));

    const particleMat = new THREE.PointsMaterial({
      size: 0.07,
      vertexColors: true,
      transparent: true,
      opacity: 0.9,
      blending: THREE.AdditiveBlending
    });

    const particleSystem = new THREE.Points(particleGeo, particleMat);
    scene.add(particleSystem);

    // 4. Outer Ring Torus
    const torusGeo = new THREE.TorusGeometry(2.4, 0.02, 16, 100);
    const torusMat = new THREE.MeshBasicMaterial({
      color: 0x10b981,
      transparent: true,
      opacity: 0.4
    });
    const torusMesh = new THREE.Mesh(torusGeo, torusMat);
    torusMesh.rotation.x = Math.PI / 3;
    scene.add(torusMesh);

    // Animation loop with state reactive physics
    let animationFrameId;
    let clock = new THREE.Clock();

    const animate = () => {
      animationFrameId = requestAnimationFrame(animate);
      const elapsed = clock.getElapsedTime();
      const currentState = stateRef.current;

      let speedMultiplier = 1.0;
      let targetColor = cEmerald;
      let scaleTarget = 1.0;

      if (currentState === "thinking") {
        speedMultiplier = 3.2;
        targetColor = cAmber;
        scaleTarget = 1.15 + Math.sin(elapsed * 8) * 0.05;
        coreMat.color.setHex(0xf59e0b);
        innerMat.color.setHex(0xfbbf24);
      } else if (currentState === "processing") {
        speedMultiplier = 2.4;
        targetColor = cCyan;
        scaleTarget = 1.08;
        coreMat.color.setHex(0x06b6d4);
        innerMat.color.setHex(0x22d3ee);
      } else if (currentState === "speaking") {
        speedMultiplier = 1.6;
        // Simulated audio amplitude pulse
        const audioAmp = Math.sin(elapsed * 12) * 0.5 + 0.5;
        scaleTarget = 1.05 + audioAmp * 0.22;
        coreMat.color.setHex(0x34d399);
        innerMat.color.setHex(0x6ee7b7);
      } else if (currentState === "success") {
        speedMultiplier = 1.2;
        scaleTarget = 1.2;
        coreMat.color.setHex(0x10b981);
        innerMat.color.setHex(0x34d399);
      } else if (currentState === "error") {
        speedMultiplier = 0.8;
        scaleTarget = 0.95;
        coreMat.color.setHex(0xf43f5e);
        innerMat.color.setHex(0xfb7185);
      } else {
        // IDLE
        speedMultiplier = 1.0;
        scaleTarget = 1.0 + Math.sin(elapsed * 1.5) * 0.03;
        coreMat.color.setHex(0x10b981);
        innerMat.color.setHex(0x06b6d4);
      }

      // Rotations
      coreMesh.rotation.x = elapsed * 0.3 * speedMultiplier;
      coreMesh.rotation.y = elapsed * 0.5 * speedMultiplier;
      coreMesh.scale.set(scaleTarget, scaleTarget, scaleTarget);

      innerMesh.rotation.y = -elapsed * 0.4 * speedMultiplier;
      innerMesh.rotation.z = elapsed * 0.2 * speedMultiplier;

      particleSystem.rotation.y = elapsed * 0.25 * speedMultiplier;
      particleSystem.rotation.x = Math.sin(elapsed * 0.5) * 0.2;

      torusMesh.rotation.z = elapsed * 0.4 * speedMultiplier;
      torusMesh.rotation.y = Math.cos(elapsed * 0.3) * 0.3;

      renderer.render(scene, camera);
    };

    animate();

    const handleResize = () => {
      if (!container) return;
      const w = container.clientWidth;
      const h = container.clientHeight;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    };

    window.addEventListener("resize", handleResize);

    return () => {
      cancelAnimationFrame(animationFrameId);
      window.removeEventListener("resize", handleResize);
      if (container && renderer.domElement) {
        container.removeChild(renderer.domElement);
      }
      scene.clear();
      renderer.dispose();
    };
  }, []);

  return (
    <div className={`relative flex flex-col items-center justify-center select-none ${className}`}>
      {/* Background Ambient Radial Glow */}
      <div
        className={`absolute h-48 w-48 rounded-full blur-3xl transition-colors duration-700 pointer-events-none ${
          state === "thinking"
            ? "bg-amber-500/25"
            : state === "processing"
            ? "bg-cyan-500/25"
            : state === "speaking"
            ? "bg-emerald-400/30"
            : state === "error"
            ? "bg-rose-500/20"
            : "bg-emerald-500/20"
        }`}
      />

      {/* 3D WebGL Canvas Viewport */}
      <div ref={mountRef} className="relative h-48 w-48 sm:h-56 sm:w-56 cursor-pointer" />
    </div>
  );
}
