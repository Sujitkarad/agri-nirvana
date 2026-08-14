import React, { useEffect, useRef } from "react";
import { Radar, Wind, Navigation, AlertTriangle, ShieldAlert } from "lucide-react";

export default function AirborneSporeRadar({ isDark = false }) {
  const canvasRef = useRef(null);

  useEffect(() => {
    if (!canvasRef.current) return;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");

    canvas.width = 600;
    canvas.height = 360;

    let particles = [];
    const particleCount = 45;

    for (let i = 0; i < particleCount; i++) {
      particles.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        speed: 1 + Math.random() * 2,
        size: 1.5 + Math.random() * 2.5,
        opacity: 0.3 + Math.random() * 0.7,
      });
    }

    let animId;
    let angle = 0;

    const render = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // Radar background rings
      const centerX = canvas.width / 2;
      const centerY = canvas.height / 2;

      ctx.strokeStyle = "rgba(16, 185, 129, 0.25)";
      ctx.lineWidth = 1;
      [50, 100, 150].forEach((r) => {
        ctx.beginPath();
        ctx.arc(centerX, centerY, r, 0, Math.PI * 2);
        ctx.stroke();
      });

      // Radar Sweep Line
      angle += 0.02;
      ctx.strokeStyle = "rgba(16, 185, 129, 0.6)";
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(centerX, centerY);
      ctx.lineTo(centerX + Math.cos(angle) * 160, centerY + Math.sin(angle) * 160);
      ctx.stroke();

      // Spore Particles Moving NW along Wind Vector
      ctx.fillStyle = "#f59e0b"; // Spore amber color
      particles.forEach((p) => {
        p.x += p.speed * 0.8;
        p.y -= p.speed * 0.5;

        if (p.x > canvas.width) p.x = 0;
        if (p.y < 0) p.y = canvas.height;

        ctx.globalAlpha = p.opacity;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
        ctx.fill();
      });
      ctx.globalAlpha = 1.0;

      animId = requestAnimationFrame(render);
    };

    render();

    return () => cancelAnimationFrame(animId);
  }, []);

  return (
    <div className={`rounded-2xl p-4 border transition-all ${isDark ? "border-emerald-800/40 bg-[#04160f]" : "border-slate-200 bg-slate-50"}`}>
      <div className="flex items-center justify-between mb-3 pb-2 border-b border-slate-200/50">
        <div className="flex items-center gap-2">
          <Radar size={18} className="text-emerald-500 animate-spin" />
          <h4 className={`text-xs font-black uppercase tracking-wider ${isDark ? "text-emerald-300" : "text-slate-800"}`}>
            Airborne Spore Wind Dispersal Vector Radar (15km Radius)
          </h4>
        </div>
        <span className="text-[10px] font-mono font-bold text-amber-400 bg-amber-500/10 px-2.5 py-1 rounded border border-amber-500/30 flex items-center gap-1">
          <Wind size={12} /> Wind NW 14 km/h
        </span>
      </div>

      <div className="relative aspect-[16/10] overflow-hidden rounded-xl bg-slate-950 shadow-inner flex items-center justify-center">
        <canvas ref={canvasRef} className="h-full w-full object-cover" />
        <div className="absolute top-3 left-3 bg-black/70 backdrop-blur px-3 py-1 rounded-full border border-amber-500/30 text-[10px] font-mono font-bold text-amber-300 flex items-center gap-1.5">
          <Navigation size={12} className="text-amber-400 rotate-45" />
          Spore Dispersal Vector: NW 312° • Flight Velocity: 4.2 km/h
        </div>
      </div>

      <div className="mt-3 flex items-center gap-2 text-[11px] font-bold text-amber-800 dark:text-amber-300 bg-amber-500/10 p-2.5 rounded-xl border border-amber-500/30">
        <ShieldAlert size={15} className="shrink-0" />
        <span>Spore Flight Warning: Fungal spores projected to reach East Orchard (Block C) in 2 hours 15 mins.</span>
      </div>
    </div>
  );
}
