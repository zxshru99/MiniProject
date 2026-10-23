"use client";

import React, { useState, useRef, useEffect } from "react";
import { ChevronDown, Check } from "lucide-react";

export interface AspectRatioOption {
  id: string;
  label: string;
  desc: string;
  width: number;
  height: number;
  cssAspect: string;
}

export const ASPECT_RATIOS: AspectRatioOption[] = [
  { id: "1:1", label: "1:1", desc: "Square (1024×1024)", width: 1024, height: 1024, cssAspect: "1 / 1" },
  { id: "16:9", label: "16:9", desc: "Landscape (1344×768)", width: 1344, height: 768, cssAspect: "16 / 9" },
  { id: "9:16", label: "9:16", desc: "Portrait / Story (768×1344)", width: 768, height: 1344, cssAspect: "9 / 16" },
  { id: "4:3", label: "4:3", desc: "Standard (1152×864)", width: 1152, height: 864, cssAspect: "4 / 3" },
  { id: "3:4", label: "3:4", desc: "Portrait (864×1152)", width: 864, height: 1152, cssAspect: "3 / 4" },
];

interface AspectRatioSelectorProps {
  selectedRatio: AspectRatioOption;
  onSelectRatio: (ratio: AspectRatioOption) => void;
}

export function AspectRatioSelector({ selectedRatio, onSelectRatio }: AspectRatioSelectorProps) {
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
        aria-label="Select aspect ratio"
        aria-expanded={isOpen}
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center justify-between gap-1.5 w-[72px] md:w-[115px] !h-7 md:!h-10 px-2 md:px-3 !py-0 bg-black/50 border border-gray-600 text-white text-xs md:text-sm hover:border-gray-500 focus:outline-none focus:border-white transition-all select-none"
      >
        <span className="font-mono text-xs md:text-sm">{selectedRatio.label}</span>
        <ChevronDown className={`w-3.5 h-3.5 text-gray-400 transition-transform ${isOpen ? "rotate-180" : ""}`} />
      </button>

      {isOpen && (
        <div className="absolute left-0 mt-1 w-48 bg-black/95 border border-gray-700 shadow-2xl backdrop-blur-xl z-50 p-1 animate-in fade-in-0 zoom-in-95 duration-150">
          <div className="px-2 py-1 text-[10px] text-gray-400 font-mono uppercase tracking-wider">
            Aspect Ratio
          </div>
          <div className="py-0.5">
            {ASPECT_RATIOS.map((ratio) => {
              const isSelected = ratio.id === selectedRatio.id;
              return (
                <button
                  key={ratio.id}
                  type="button"
                  onClick={() => {
                    onSelectRatio(ratio);
                    setIsOpen(false);
                  }}
                  className={`w-full flex items-center justify-between px-2.5 py-1.5 text-left text-xs font-mono transition-colors hover:bg-white/10 ${
                    isSelected ? "bg-white/10 text-white font-semibold" : "text-gray-300"
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <span className="w-8 text-white font-bold">{ratio.label}</span>
                    <span className="text-[10px] text-gray-400">{ratio.desc.split(" ")[0]}</span>
                  </div>
                  {isSelected && <Check className="w-3.5 h-3.5 text-white" />}
                </button>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
