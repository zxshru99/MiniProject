"use client";

import React, { useState, useRef, useEffect } from "react";
import { Sparkles, Check, Cpu, Layers, Activity, Leaf, ShieldCheck } from "lucide-react";

export interface ModelOption {
  id: string;
  name: string;
  category: string;
  badge?: string;
  description: string;
  iconType: "ensemble" | "cnn" | "moisture" | "xgboost" | "recommender";
}

export const AGRI_MODELS: ModelOption[] = [
  {
    id: "multimodal-ensemble",
    name: "Multi-Modal Ensemble",
    category: "Full Pipeline",
    badge: "Recommended",
    description: "Deep CNN Vision + XGBoost Regressor + SHAP Attribution",
    iconType: "ensemble",
  },
  {
    id: "agrivision-cnn",
    name: "AgriVision CNN v2",
    category: "Computer Vision",
    badge: "Vision AI",
    description: "Deep CNN soil classifier (Black, Cinder, Laterite, Peat, Yellow Soil)",
    iconType: "cnn",
  },
  {
    id: "moisture-net",
    name: "Moisture-Net VWC",
    category: "Moisture Regressor",
    badge: "% VWC",
    description: "Optical colorimetry & CLAHE surface moisture estimation",
    iconType: "moisture",
  },
  {
    id: "yield-xgboost",
    name: "Yield XGBoost v2.1",
    category: "Yield Engine",
    badge: "Explainable",
    description: "Gradient boosted trees predicting kg/ha with confidence intervals",
    iconType: "xgboost",
  },
  {
    id: "crop-recommender",
    name: "Crop Recommender AI",
    category: "Advisory",
    badge: "Agronomy",
    description: "Cross-references soil texture, moisture, and seasonal weather",
    iconType: "recommender",
  },
];

interface ModelSelectorProps {
  selectedModel: ModelOption;
  onSelectModel: (model: ModelOption) => void;
}

export function ModelSelector({ selectedModel, onSelectModel }: ModelSelectorProps) {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const renderIcon = (type: string, className = "w-4 h-4") => {
    switch (type) {
      case "ensemble":
        return <Layers className={`${className} text-emerald-400`} />;
      case "cnn":
        return <Cpu className={`${className} text-cyan-400`} />;
      case "moisture":
        return <Activity className={`${className} text-blue-400`} />;
      case "xgboost":
        return <Sparkles className={`${className} text-amber-400`} />;
      case "recommender":
        return <Leaf className={`${className} text-green-400`} />;
      default:
        return <Layers className={className} />;
    }
  };

  return (
    <div className="relative inline-block text-left" ref={dropdownRef}>
      <button
        type="button"
        aria-label="Select model"
        aria-expanded={isOpen}
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-1.5 h-7 md:h-10 px-2 md:px-3 bg-black/50 border border-gray-600 text-gray-300 hover:text-white hover:border-gray-500 transition-all max-w-[150px] md:max-w-[230px] rounded-none focus:outline-none focus:border-white"
      >
        <span className="flex-shrink-0">
          {renderIcon(selectedModel.iconType, "w-3.5 h-3.5 md:w-4 md:h-4")}
        </span>
        <span className="text-xs font-medium truncate">{selectedModel.name}</span>
        <svg
          className={`w-3 h-3 flex-shrink-0 ml-auto transition-transform ${isOpen ? "rotate-180" : ""}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {isOpen && (
        <div className="absolute left-0 mt-1 w-72 md:w-80 bg-black/95 border border-gray-700 shadow-2xl backdrop-blur-xl z-50 p-1 divide-y divide-white/10 animate-in fade-in-0 zoom-in-95 duration-150">
          <div className="px-2 py-1.5 text-[10px] text-gray-400 font-mono uppercase tracking-wider flex items-center justify-between">
            <span>Inference Pipeline</span>
            <span className="text-emerald-400 text-[9px]">AgriAI Models</span>
          </div>
          <div className="py-1 max-h-72 overflow-y-auto">
            {AGRI_MODELS.map((model) => {
              const isSelected = model.id === selectedModel.id;
              return (
                <button
                  key={model.id}
                  type="button"
                  onClick={() => {
                    onSelectModel(model);
                    setIsOpen(false);
                  }}
                  className={`w-full flex items-start gap-2.5 px-2.5 py-2 text-left transition-colors hover:bg-white/10 ${
                    isSelected ? "bg-white/5 text-white" : "text-gray-300"
                  }`}
                >
                  <span className="mt-0.5 flex-shrink-0">
                    {renderIcon(model.iconType, "w-4 h-4")}
                  </span>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between gap-1">
                      <span className="text-xs font-semibold text-white truncate">
                        {model.name}
                      </span>
                      {model.badge && (
                        <span className="text-[9px] px-1.5 py-0.2 bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 rounded font-mono">
                          {model.badge}
                        </span>
                      )}
                    </div>
                    <p className="text-[10px] text-gray-400 leading-tight mt-0.5 line-clamp-1">
                      {model.description}
                    </p>
                  </div>
                  {isSelected && (
                    <Check className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0 mt-0.5" />
                  )}
                </button>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
