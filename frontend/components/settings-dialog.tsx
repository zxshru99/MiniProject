"use client";

import React, { useState, useEffect } from "react";
import { Settings2, X, Sliders, Dices, Sprout, Check, Thermometer, CloudRain } from "lucide-react";

export interface AgriSettings {
  nitrogen: number; // kg/ha
  phosphorus: number; // kg/ha
  potassium: number; // kg/ha
  rainfall: number; // mm
  temperature: number; // °C
  fieldAreaHa: number;
  blurThreshold: number;
}

export const DEFAULT_AGRI_SETTINGS: AgriSettings = {
  nitrogen: 120,
  phosphorus: 45,
  potassium: 60,
  rainfall: 650,
  temperature: 24.5,
  fieldAreaHa: 2.5,
  blurThreshold: 40.0,
};

interface SettingsDialogProps {
  settings: AgriSettings;
  onSaveSettings: (settings: AgriSettings) => void;
}

export function SettingsDialog({ settings, onSaveSettings }: SettingsDialogProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [tempSettings, setTempSettings] = useState<AgriSettings>(settings);

  useEffect(() => {
    if (!isOpen) return;
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") setIsOpen(false);
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen]);

  const handleOpen = () => {
    setTempSettings(settings);
    setIsOpen(true);
  };

  const handleSave = () => {
    onSaveSettings(tempSettings);
    setIsOpen(false);
  };

  const randomizeConditions = () => {
    setTempSettings({
      nitrogen: Math.floor(Math.random() * 120) + 60,
      phosphorus: Math.floor(Math.random() * 60) + 20,
      potassium: Math.floor(Math.random() * 80) + 30,
      rainfall: Math.floor(Math.random() * 800) + 300,
      temperature: Number((Math.random() * 18 + 16).toFixed(1)),
      fieldAreaHa: Number((Math.random() * 8 + 1).toFixed(1)),
      blurThreshold: 40.0,
    });
  };

  return (
    <>
      <button
        type="button"
        aria-label="Field parameters"
        onClick={handleOpen}
        className="h-7 md:h-10 px-2 bg-black/50 border border-gray-600 text-gray-300 hover:text-white hover:border-gray-500 transition-all focus:outline-none focus:border-white flex items-center justify-center"
      >
        <Settings2 className="w-3.5 h-3.5 md:w-4 md:h-4" />
      </button>

      {isOpen && (
        <div 
          className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4 bg-black/80 backdrop-blur-sm animate-in fade-in-0 duration-200"
          onClick={(e) => {
            if (e.target === e.currentTarget) setIsOpen(false);
          }}
        >
          <div 
            className="w-full max-w-md bg-black/95 border border-gray-700 shadow-2xl p-4 sm:p-6 text-white font-mono flex flex-col gap-4 relative animate-in zoom-in-95 duration-150 max-h-[90vh] overflow-y-auto"
            role="dialog"
            aria-modal="true"
          >
            {/* Header */}
            <div className="flex items-center justify-between pb-3 border-b border-white/10">
              <div className="flex items-center gap-2">
                <Sliders className="w-4 h-4 text-emerald-400" />
                <h2 className="text-sm md:text-base font-bold text-white tracking-wide">
                  Field & Weather Environment
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

            {/* Quick Randomize */}
            <div className="flex items-center justify-between bg-white/5 p-2 border border-white/10">
              <span className="text-[11px] text-gray-400">Preset Environmental Dynamics</span>
              <button
                type="button"
                onClick={randomizeConditions}
                className="flex items-center gap-1.5 px-2 py-1 bg-white/10 text-white hover:bg-white/20 text-[10px] transition-colors"
              >
                <Dices className="w-3.5 h-3.5" />
                <span>Simulate Weather</span>
              </button>
            </div>

            {/* Form inputs */}
            <div className="flex flex-col gap-3 text-xs">
              {/* N-P-K Nutrients */}
              <div className="flex flex-col gap-1.5">
                <label className="text-gray-300 font-medium">Soil Nutrients (N-P-K in kg/ha)</label>
                <div className="grid grid-cols-3 gap-2">
                  <div>
                    <span className="text-[10px] text-gray-500">Nitrogen (N)</span>
                    <input
                      type="number"
                      value={tempSettings.nitrogen}
                      onChange={(e) =>
                        setTempSettings({ ...tempSettings, nitrogen: Number(e.target.value) })
                      }
                      className="w-full p-2 bg-black/60 border border-gray-600 text-white text-xs focus:outline-none focus:border-white"
                    />
                  </div>
                  <div>
                    <span className="text-[10px] text-gray-500">Phosphorus (P)</span>
                    <input
                      type="number"
                      value={tempSettings.phosphorus}
                      onChange={(e) =>
                        setTempSettings({ ...tempSettings, phosphorus: Number(e.target.value) })
                      }
                      className="w-full p-2 bg-black/60 border border-gray-600 text-white text-xs focus:outline-none focus:border-white"
                    />
                  </div>
                  <div>
                    <span className="text-[10px] text-gray-500">Potassium (K)</span>
                    <input
                      type="number"
                      value={tempSettings.potassium}
                      onChange={(e) =>
                        setTempSettings({ ...tempSettings, potassium: Number(e.target.value) })
                      }
                      className="w-full p-2 bg-black/60 border border-gray-600 text-white text-xs focus:outline-none focus:border-white"
                    />
                  </div>
                </div>
              </div>

              {/* Climate: Rainfall & Temperature */}
              <div className="grid grid-cols-2 gap-2">
                <div className="flex flex-col gap-1">
                  <span className="text-gray-400 text-[11px] flex items-center gap-1">
                    <CloudRain className="w-3 h-3 text-blue-400" /> Rainfall (mm)
                  </span>
                  <input
                    type="number"
                    value={tempSettings.rainfall}
                    onChange={(e) =>
                      setTempSettings({ ...tempSettings, rainfall: Number(e.target.value) })
                    }
                    className="w-full p-2 bg-black/60 border border-gray-600 text-white text-xs focus:outline-none focus:border-white"
                  />
                </div>
                <div className="flex flex-col gap-1">
                  <span className="text-gray-400 text-[11px] flex items-center gap-1">
                    <Thermometer className="w-3 h-3 text-amber-400" /> Temperature (°C)
                  </span>
                  <input
                    type="number"
                    step="0.1"
                    value={tempSettings.temperature}
                    onChange={(e) =>
                      setTempSettings({ ...tempSettings, temperature: Number(e.target.value) })
                    }
                    className="w-full p-2 bg-black/60 border border-gray-600 text-white text-xs focus:outline-none focus:border-white"
                  />
                </div>
              </div>

              {/* Field Area & Blur Gating */}
              <div className="grid grid-cols-2 gap-2">
                <div className="flex flex-col gap-1">
                  <span className="text-gray-400 text-[11px]">Field Area (Hectares)</span>
                  <input
                    type="number"
                    step="0.5"
                    value={tempSettings.fieldAreaHa}
                    onChange={(e) =>
                      setTempSettings({ ...tempSettings, fieldAreaHa: Number(e.target.value) })
                    }
                    className="w-full p-2 bg-black/60 border border-gray-600 text-white text-xs focus:outline-none focus:border-white"
                  />
                </div>
                <div className="flex flex-col gap-1">
                  <span className="text-gray-400 text-[11px]">Blur Rejection Score</span>
                  <input
                    type="number"
                    step="5"
                    value={tempSettings.blurThreshold}
                    onChange={(e) =>
                      setTempSettings({ ...tempSettings, blurThreshold: Number(e.target.value) })
                    }
                    className="w-full p-2 bg-black/60 border border-gray-600 text-white text-xs focus:outline-none focus:border-white"
                  />
                </div>
              </div>
            </div>

            {/* Footer Buttons */}
            <div className="flex items-center justify-end gap-2 pt-3 border-t border-white/10 mt-2">
              <button
                type="button"
                onClick={() => setTempSettings(DEFAULT_AGRI_SETTINGS)}
                className="px-3 py-1.5 text-xs text-gray-400 hover:text-white border border-transparent hover:border-gray-700 transition-colors"
              >
                Reset Defaults
              </button>
              <button
                type="button"
                onClick={handleSave}
                className="px-4 py-1.5 text-xs font-semibold bg-white text-black hover:bg-gray-200 transition-all rounded-none"
              >
                Apply Parameters
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
