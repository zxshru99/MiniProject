"use client";

import React, { useState, useRef, useEffect } from "react";
import { ChevronDown, Check, Sprout, Search } from "lucide-react";

export interface CropOption {
  id: string;
  name: string;
  season: string;
  baseYield: number; // kg/ha
  waterReq: number; // mm
}

export const CROPS: CropOption[] = [
  // Cereals
  { id: "wheat", name: "Wheat", season: "Rabi", baseYield: 4200, waterReq: 450 },
  { id: "rice", name: "Rice (Paddy)", season: "Kharif", baseYield: 4100, waterReq: 1200 },
  { id: "maize", name: "Maize (Corn)", season: "Kharif/Rabi", baseYield: 5400, waterReq: 550 },
  { id: "barley", name: "Barley", season: "Rabi", baseYield: 3400, waterReq: 380 },
  { id: "millets", name: "Millets (Bajra/Jowar)", season: "Kharif", baseYield: 2200, waterReq: 320 },
  { id: "oats", name: "Oats", season: "Rabi", baseYield: 2900, waterReq: 400 },
  // Pulses
  { id: "chickpea", name: "Chickpea (Gram)", season: "Rabi", baseYield: 1550, waterReq: 300 },
  { id: "pigeonpea", name: "Pigeon Pea (Tur)", season: "Kharif", baseYield: 1400, waterReq: 450 },
  { id: "lentil", name: "Lentil (Masoor)", season: "Rabi", baseYield: 1250, waterReq: 280 },
  { id: "blackgram", name: "Black Gram (Urad)", season: "Kharif", baseYield: 1100, waterReq: 350 },
  { id: "greengram", name: "Green Gram (Moong)", season: "Kharif/Zaid", baseYield: 1150, waterReq: 340 },
  // Oilseeds & Commercial Crops
  { id: "soybean", name: "Soybean", season: "Kharif", baseYield: 2400, waterReq: 600 },
  { id: "groundnut", name: "Groundnut (Peanut)", season: "Kharif", baseYield: 2100, waterReq: 550 },
  { id: "mustard", name: "Mustard / Rapeseed", season: "Rabi", baseYield: 1750, waterReq: 290 },
  { id: "cotton", name: "Cotton", season: "Kharif", baseYield: 2300, waterReq: 680 },
  { id: "sugarcane", name: "Sugarcane", season: "Annual", baseYield: 72000, waterReq: 1500 },
  { id: "sunflower", name: "Sunflower", season: "Rabi/Kharif", baseYield: 1800, waterReq: 480 },
  // Vegetables & Roots
  { id: "potato", name: "Potato", season: "Rabi", baseYield: 24000, waterReq: 500 },
  { id: "tomato", name: "Tomato", season: "Annual", baseYield: 32000, waterReq: 600 },
  { id: "onion", name: "Onion", season: "Rabi/Kharif", baseYield: 18500, waterReq: 450 },
];

interface CropSelectorProps {
  selectedCrop: CropOption;
  onSelectCrop: (crop: CropOption) => void;
}

export function CropSelector({ selectedCrop, onSelectCrop }: CropSelectorProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [search, setSearch] = useState("");
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

  const filteredCrops = CROPS.filter((c) =>
    c.name.toLowerCase().includes(search.toLowerCase()) ||
    c.season.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="relative inline-block text-left" ref={dropdownRef}>
      <button
        type="button"
        role="combobox"
        aria-label="Select target crop"
        aria-expanded={isOpen}
        onClick={() => {
          setIsOpen(!isOpen);
          setSearch("");
        }}
        className="flex items-center justify-between gap-1.5 w-[95px] md:w-[135px] !h-7 md:!h-10 px-2 md:px-3 !py-0 bg-black/50 border border-gray-600 text-white text-xs md:text-sm hover:border-gray-500 focus:outline-none focus:border-white transition-all select-none"
      >
        <span className="font-mono text-xs md:text-sm truncate">{selectedCrop.name}</span>
        <ChevronDown className={`w-3.5 h-3.5 text-gray-400 transition-transform ${isOpen ? "rotate-180" : ""}`} />
      </button>

      {isOpen && (
        <div className="absolute left-0 mt-1 w-64 bg-black/95 border border-gray-700 shadow-2xl backdrop-blur-xl z-50 p-2 animate-in fade-in-0 zoom-in-95 duration-150">
          {/* Quick Search */}
          <div className="relative mb-2">
            <Search className="w-3.5 h-3.5 text-gray-400 absolute left-2 top-2.5" />
            <input
              type="text"
              placeholder="Search crop or season..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full bg-white/5 border border-gray-700 text-white text-xs pl-7 pr-2 py-1.5 focus:outline-none focus:border-emerald-400 font-mono"
              autoFocus
            />
          </div>

          <div className="px-1 py-1 text-[10px] text-gray-400 font-mono uppercase tracking-wider flex items-center justify-between border-b border-white/10 pb-1 mb-1">
            <span>Crop Name ({filteredCrops.length})</span>
            <span>Season</span>
          </div>

          <div className="py-0.5 max-h-64 overflow-y-auto scrollbar-thin scrollbar-thumb-gray-700">
            {filteredCrops.length === 0 ? (
              <div className="p-3 text-center text-xs text-gray-500 font-mono">
                No matching crop found
              </div>
            ) : (
              filteredCrops.map((crop) => {
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
                      isSelected ? "bg-white/10 text-emerald-400 font-semibold" : "text-gray-300"
                    }`}
                  >
                    <div className="flex items-center gap-2">
                      <Sprout className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0" />
                      <span className="truncate">{crop.name}</span>
                    </div>
                    <div className="flex items-center gap-1.5 flex-shrink-0">
                      <span className="text-[10px] text-gray-400">{crop.season}</span>
                      {isSelected && <Check className="w-3.5 h-3.5 text-emerald-400" />}
                    </div>
                  </button>
                );
              })
            )}
          </div>
        </div>
      )}
    </div>
  );
}
