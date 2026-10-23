"use client";

import React, { useState, useRef, useEffect } from "react";
import { ChevronDown, Check, Sprout } from "lucide-react";

export interface CropOption {
  id: string;
  name: string;
  season: string;
  baseYield: number; // kg/ha
  waterReq: number; // mm
}

export const CROPS: CropOption[] = [
  { id: "wheat", name: "Wheat", season: "Rabi", baseYield: 4200, waterReq: 450 },
  { id: "maize", name: "Maize", season: "Kharif", baseYield: 5300, waterReq: 500 },
  { id: "rice", name: "Rice (Paddy)", season: "Kharif", baseYield: 3800, waterReq: 1100 },
  { id: "chickpea", name: "Chickpea", season: "Rabi", baseYield: 1500, waterReq: 300 },
  { id: "soybean", name: "Soybean", season: "Kharif", baseYield: 2400, waterReq: 600 },
  { id: "cotton", name: "Cotton", season: "Kharif", baseYield: 2100, waterReq: 700 },
];

interface CropSelectorProps {
  selectedCrop: CropOption;
  onSelectCrop: (crop: CropOption) => void;
}

export function CropSelector({ selectedCrop, onSelectCrop }: CropSelectorProps) {
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

  return (
    <div className="relative inline-block text-left" ref={dropdownRef}>
      <button
        type="button"
        role="combobox"
        aria-label="Select target crop"
        aria-expanded={isOpen}
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center justify-between gap-1.5 w-[85px] md:w-[125px] !h-7 md:!h-10 px-2 md:px-3 !py-0 bg-black/50 border border-gray-600 text-white text-xs md:text-sm hover:border-gray-500 focus:outline-none focus:border-white transition-all select-none"
      >
        <span className="font-mono text-xs md:text-sm truncate">{selectedCrop.name}</span>
        <ChevronDown className={`w-3.5 h-3.5 text-gray-400 transition-transform ${isOpen ? "rotate-180" : ""}`} />
      </button>

      {isOpen && (
        <div className="absolute left-0 mt-1 w-52 bg-black/95 border border-gray-700 shadow-2xl backdrop-blur-xl z-50 p-1 animate-in fade-in-0 zoom-in-95 duration-150">
          <div className="px-2 py-1 text-[10px] text-gray-400 font-mono uppercase tracking-wider flex items-center justify-between">
            <span>Target Crop</span>
            <span>Season</span>
          </div>
          <div className="py-0.5 max-h-60 overflow-y-auto">
            {CROPS.map((crop) => {
              const isSelected = crop.id === selectedCrop.id;
              return (
                <button
                  key={crop.id}
                  type="button"
                  onClick={() => {
                    onSelectCrop(crop);
                    setIsOpen(false);
                  }}
                  className={`w-full flex items-center justify-between px-2.5 py-1.5 text-left text-xs font-mono transition-colors hover:bg-white/10 ${
                    isSelected ? "bg-white/10 text-white font-semibold" : "text-gray-300"
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <Sprout className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0" />
                    <span className="text-white truncate">{crop.name}</span>
                  </div>
                  <div className="flex items-center gap-1.5 flex-shrink-0">
                    <span className="text-[10px] text-gray-400">{crop.season}</span>
                    {isSelected && <Check className="w-3.5 h-3.5 text-emerald-400" />}
                  </div>
                </button>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
