import React, { useEffect, useRef } from "react";
import * as THREE from "three";

export default function HolographicAIAvatar({
  state = "idle",
  selectedModel = "",
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
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
    camera.position.z = 7;
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: "high-performance" });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    container.appendChild(renderer.domElement);

    const coreGeo = new THREE.IcosahedronGeometry(1.2, 2);
    const coreMat = new THREE.MeshBasicMaterial({ color: 0x10b981, wireframe: true, transparent: true, opacity: 0.8 });
    const coreMesh = new THREE.Mesh(coreGeo, coreMat);
    scene.add(coreMesh);
    const innerGeo = new THREE.SphereGeometry(0.75, 16, 16);
    const innerMat = new THREE.MeshBasicMaterial({ color: 0x06b6d4, transparent: true, opacity: 0.6 });
    const innerMesh = new THREE.Mesh(innerGeo, innerMat);
    scene.add(innerMesh);

    const particleCount = 120;
    const particleGeo = new THREE.BufferGeometry();
    const positions = new Float32Array(particleCount * 3);
    for (let i = 0; i < particleCount; i++) {
      const radius = 2.0 + Math.random() * 0.8;
      const theta = Math.random() * Math.PI * 2;
      const phi = (Math.random() - 0.5) * 0.8;
      positions[i * 3] = radius * Math.cos(theta) * Math.cos(phi);
      positions[i * 3 + 1] = radius * Math.sin(phi);
      positions[i * 3 + 2] = radius * Math.sin(theta) * Math.cos(phi);
    }
    particleGeo.setAttribute("position", new THREE.BufferAttribute(positions, 3));
    const particleMat = new THREE.PointsMaterial({ size: 0.06, color: 0x10b981, transparent: true, opacity: 0.75, blending: THREE.AdditiveBlending });
    const particleSystem = new THREE.Points(particleGeo, particleMat);
    scene.add(particleSystem);

    const torusGeo = new THREE.TorusGeometry(2.4, 0.02, 16, 100);
    const torusMat = new THREE.MeshBasicMaterial({ color: 0x10b981, transparent: true, opacity: 0.35 });
    const torusMesh = new THREE.Mesh(torusGeo, torusMat);
    torusMesh.rotation.x = Math.PI / 3;
    scene.add(torusMesh);

    let animationFrameId;
    const clock = new THREE.Clock();
    const animate = () => {
      animationFrameId = requestAnimationFrame(animate);
      const elapsed = clock.getElapsedTime();
      const currentState = stateRef.current;
      let speed = 0.8;
      let scale = 1 + Math.sin(elapsed * 1.5) * 0.025;
      if (currentState === "thinking") { speed = 2.0; scale = 1.08 + Math.sin(elapsed * 6) * 0.025; coreMat.color.setHex(0xf59e0b); innerMat.color.setHex(0xfbbf24); }
      else if (currentState === "processing") { speed = 1.7; scale = 1.05; coreMat.color.setHex(0x06b6d4); innerMat.color.setHex(0x22d3ee); }
      else if (currentState === "speaking") { speed = 1.1; scale = 1.04 + (Math.sin(elapsed * 8) * 0.5 + 0.5) * 0.08; coreMat.color.setHex(0x34d399); innerMat.color.setHex(0x6ee7b7); }
      else if (currentState === "error") { speed = 0.5; scale = 0.98; coreMat.color.setHex(0xf43f5e); innerMat.color.setHex(0xfb7185); }
      else { coreMat.color.setHex(0x10b981); innerMat.color.setHex(0x06b6d4); }
      coreMesh.rotation.x = elapsed * 0.3 * speed;
      coreMesh.rotation.y = elapsed * 0.5 * speed;
      coreMesh.scale.setScalar(scale);
      innerMesh.rotation.y = -elapsed * 0.4 * speed;
      particleSystem.rotation.y = elapsed * 0.2 * speed;
      torusMesh.rotation.z = elapsed * 0.3 * speed;
      renderer.render(scene, camera);
    };
    animate();
    const handleResize = () => {
      const w = container.clientWidth;
      const h = container.clientHeight;
      if (!w || !h) return;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    };
    window.addEventListener("resize", handleResize);
    return () => {
      cancelAnimationFrame(animationFrameId);
      window.removeEventListener("resize", handleResize);
      renderer.dispose();
      scene.traverse((obj) => {
        if (obj.geometry) obj.geometry.dispose();
        if (obj.material) obj.material.dispose();
      });
      if (renderer.domElement.parentNode === container) container.removeChild(renderer.domElement);
    };
  }, []);

  const status = {
    thinking: ["Analyzing", "bg-amber-400 animate-pulse"],
    processing: ["Processing", "bg-cyan-400 animate-pulse"],
    speaking: ["Responding", "bg-emerald-400 animate-pulse"],
    success: ["Ready", "bg-emerald-400"],
    error: ["Needs attention", "bg-rose-500"],
    idle: ["AI Ready", "bg-emerald-400"]
  }[state] || ["AI Ready", "bg-emerald-400"];

  return (
    <div className={`relative flex flex-col items-center justify-center select-none ${className}`}>
      <div className={`absolute h-48 w-48 rounded-full blur-3xl pointer-events-none ${state === "error" ? "bg-rose-500/15" : "bg-emerald-500/15"}`} />
      <div ref={mountRef} className="relative h-48 w-48 sm:h-56 sm:w-56" aria-hidden="true" />
      <div className={`-mt-2 flex items-center gap-2 rounded-full border px-3.5 py-1 text-[10px] font-semibold shadow-lg backdrop-blur-md ${isDark ? "border-emerald-500/30 bg-[#061910]/90 text-emerald-300" : "border-slate-300 bg-white/90 text-slate-800"}`}>
        <span className={`h-2 w-2 rounded-full ${status[1]}`} />
        <span>{status[0]}</span>
      </div>
      <span className="mt-1 text-[10px] font-medium text-emerald-400/75">Agricultural AI assistant</span>
    </div>
  );
}
