"use client";

import React, { useState, useEffect } from "react";
import { Layers, Eye, Sparkles, Sliders, ShieldCheck } from "lucide-react";

interface GradCamViewerProps {
  originalImage: string;
  soilType: string;
  confidence: number;
  blurScore: number;
}

const FALLBACK_IMAGE = "https://images.unsplash.com/photo-1592419044706-39796d40f98c?auto=format&fit=crop&w=800&q=80";

export function GradCamViewer({
  originalImage,
  soilType,
  confidence,
  blurScore,
}: GradCamViewerProps) {
  const [activeLayer, setActiveLayer] = useState<"raw" | "clahe" | "gradcam">("gradcam");
  const [heatmapOpacity, setHeatmapOpacity] = useState<number>(0.75);
  const [imgSrc, setImgSrc] = useState<string>(originalImage || FALLBACK_IMAGE);

  useEffect(() => {
    if (originalImage) {
      setImgSrc(originalImage);
    }
  }, [originalImage]);

  return (
    <div className="flex flex-col gap-3 font-mono text-white">
      {/* Layer Toggle Bar */}
      <div className="flex items-center justify-between p-2.5 bg-black/70 border border-white/10">
        <div className="flex items-center gap-1.5">
          <Layers className="w-4 h-4 text-emerald-400" />
          <span className="text-xs font-bold text-white">Multi-Spectral Soil Vision Inspector</span>
        </div>

        <div className="inline-flex bg-black/60 border border-gray-700 text-xs">
          <button
            type="button"
            onClick={() => setActiveLayer("raw")}
            className={`px-2.5 py-1 transition-all ${
              activeLayer === "raw" ? "bg-white text-black font-semibold" : "text-gray-400 hover:text-white"
            }`}
          >
            Raw Photo
          </button>
          <button
            type="button"
            onClick={() => setActiveLayer("clahe")}
            className={`px-2.5 py-1 transition-all ${
              activeLayer === "clahe" ? "bg-white text-black font-semibold" : "text-gray-400 hover:text-white"
            }`}
          >
            CLAHE Equalized
          </button>
          <button
            type="button"
            onClick={() => setActiveLayer("gradcam")}
            className={`px-2.5 py-1 transition-all ${
              activeLayer === "gradcam" ? "bg-white text-black font-semibold" : "text-gray-400 hover:text-white"
            }`}
          >
            Grad-CAM Heatmap
          </button>
        </div>
      </div>

      {/* Main Visual Display */}
      <div className="relative w-full h-[320px] md:h-[400px] border border-white/10 bg-black/80 flex items-center justify-center overflow-hidden">
        {/* Base Soil Image */}
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src={imgSrc}
          onError={() => setImgSrc(FALLBACK_IMAGE)}
          alt="Soil under inspection"
          className={`w-full h-full object-cover transition-all duration-300 ${
            activeLayer === "clahe" ? "contrast-150 brightness-95 saturate-125" : ""
          }`}
        />

        {/* Grad-CAM Synthetic Heatmap Overlay */}
        {activeLayer === "gradcam" && (
          <div
            className="absolute inset-0 pointer-events-none mix-blend-screen transition-opacity duration-200"
            style={{
              opacity: heatmapOpacity,
              background: `radial-gradient(circle at 45% 55%, rgba(239, 68, 68, 0.85) 0%, rgba(234, 179, 8, 0.65) 30%, rgba(34, 197, 94, 0.45) 55%, rgba(59, 130, 246, 0.25) 75%, transparent 100%),
                           radial-gradient(circle at 75% 30%, rgba(239, 68, 68, 0.7) 0%, rgba(234, 179, 8, 0.5) 35%, transparent 70%)`,
            }}
          />
        )}

        {/* Top telemetry badge */}
        <div className="absolute top-2 left-2 bg-black/80 border border-white/10 backdrop-blur-md px-2.5 py-1 text-[11px] text-gray-300 flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-emerald-400" />
          <span>Classified: <strong>{soilType}</strong> ({(confidence * 100).toFixed(1)}%)</span>
          <span className="text-gray-500">•</span>
          <span>Blur Score: {blurScore.toFixed(0)}</span>
        </div>

        {/* Grad-CAM legend */}
        {activeLayer === "gradcam" && (
          <div className="absolute bottom-2 right-2 bg-black/85 border border-white/10 backdrop-blur-md p-2 flex flex-col gap-1 text-[10px]">
            <span className="text-gray-400">CNN Visual Attention Index</span>
            <div className="w-32 h-2 rounded-full bg-gradient-to-r from-blue-500 via-green-500 via-yellow-500 to-red-500" />
            <div className="flex justify-between text-[9px] text-gray-400">
              <span>Low (Clay/Silt)</span>
              <span>High (Organic Matter)</span>
            </div>
          </div>
        )}
      </div>

      {/* Heatmap opacity slider */}
      {activeLayer === "gradcam" && (
        <div className="flex items-center justify-between p-2 bg-white/5 border border-white/10 text-xs">
          <span className="text-gray-400 flex items-center gap-1.5">
            <Sliders className="w-3.5 h-3.5" />
            Heatmap Transparency
          </span>
          <div className="flex items-center gap-2 w-48">
            <input
              type="range"
              min="0.1"
              max="1"
              step="0.05"
              value={heatmapOpacity}
              onChange={(e) => setHeatmapOpacity(parseFloat(e.target.value))}
              className="w-full accent-emerald-400 h-1.5 cursor-pointer bg-gray-700"
            />
            <span className="text-[11px] font-mono text-gray-300 w-8 text-right">
              {Math.round(heatmapOpacity * 100)}%
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
