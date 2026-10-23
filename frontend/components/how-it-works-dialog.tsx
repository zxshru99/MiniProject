"use client";

import React, { useState, useEffect } from "react";
import { X, Sprout, Layers, Sliders, Activity, ShieldCheck, Cpu } from "lucide-react";

export function HowItWorksDialog() {
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    if (!isOpen) return;
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") setIsOpen(false);
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen]);

  return (
    <>
      <button
        type="button"
        onClick={() => setIsOpen(true)}
        className="hover:text-white/80 transition-colors cursor-pointer text-[10px] sm:text-xs"
      >
        How it works
      </button>

      {isOpen && (
        <div 
          className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4 bg-black/85 backdrop-blur-md animate-in fade-in-0 duration-200"
          onClick={(e) => {
            if (e.target === e.currentTarget) setIsOpen(false);
          }}
        >
          <div 
            className="w-full max-w-lg bg-black/95 border border-gray-700 shadow-2xl p-5 sm:p-6 text-white font-mono flex flex-col gap-4 relative animate-in zoom-in-95 duration-150 max-h-[90vh] overflow-y-auto"
            role="dialog"
            aria-modal="true"
          >
            {/* Header */}
            <div className="flex items-center justify-between pb-3 border-b border-white/10">
              <div className="flex items-center gap-2">
                <Sprout className="w-4 h-4 text-emerald-400" />
                <h2 className="text-sm md:text-base font-bold text-white tracking-wide">
                  How AgriAI Intelligence Works
                </h2>
              </div>
              <button
                type="button"
                onClick={() => setIsOpen(false)}
                className="text-gray-400 hover:text-white transition-colors p-1"
                aria-label="Close dialog"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Content sections */}
            <div className="flex flex-col gap-4 text-xs text-gray-300 leading-relaxed">
              <section className="bg-white/5 p-3 border border-white/10">
                <h3 className="text-white font-semibold flex items-center gap-1.5 mb-1 text-xs">
                  <Cpu className="w-3.5 h-3.5 text-cyan-400" />
                  1. Optical Clarity Check & CLAHE Normalization
                </h3>
                <p className="text-gray-400 text-[11px]">
                  Uploaded soil field photos pass through a Laplacian variance optical filter to reject blurry images (blur score &lt; 40.0). Validated images undergo CLAHE lighting compensation to segment pure topsoil earth from background foliage.
                </p>
              </section>

              <section className="bg-white/5 p-3 border border-white/10">
                <h3 className="text-white font-semibold flex items-center gap-1.5 mb-1 text-xs">
                  <Layers className="w-3.5 h-3.5 text-emerald-400" />
                  2. CNN Soil Texture Classification (4 Classes)
                </h3>
                <p className="text-gray-400 text-[11px]">
                  A deep convolutional network analyzes colorimetry, Gray-Level Co-occurrence Matrix (GLCM), and Local Binary Patterns (LBP) to classify soil into Clay, Loamy, Sandy, or Sandy Loam with probabilistic confidence.
                </p>
              </section>

              <section className="bg-white/5 p-3 border border-white/10">
                <h3 className="text-white font-semibold flex items-center gap-1.5 mb-1 text-xs">
                  <Activity className="w-3.5 h-3.5 text-blue-400" />
                  3. Moisture Estimation (% VWC) & Irrigation Urgency
                </h3>
                <p className="text-gray-400 text-[11px]">
                  Computes volumetric water content (% VWC) from soil reflectance spectra and classifies moisture into DRY, MODERATE, WET, or SATURATED, advising immediate irrigation actions.
                </p>
              </section>

              <section className="bg-white/5 p-3 border border-white/10">
                <h3 className="text-white font-semibold flex items-center gap-1.5 mb-1 text-xs">
                  <Sliders className="w-3.5 h-3.5 text-amber-400" />
                  4. XGBoost Yield Forecasting & SHAP Attribution
                </h3>
                <p className="text-gray-400 text-[11px]">
                  Combines soil features with N-P-K nutrient parameters, GDD, and rainfall to forecast yield (kg/ha) with lower and upper confidence bounds, accompanied by SHAP explainability factors.
                </p>
              </section>
            </div>

            {/* Footer */}
            <div className="flex items-center justify-end pt-3 border-t border-white/10">
              <button
                type="button"
                onClick={() => setIsOpen(false)}
                className="px-4 py-1.5 text-xs font-semibold bg-white text-black hover:bg-gray-200 transition-all"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
