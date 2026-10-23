"use client";

import React, { useState, useEffect } from "react";
import { TrendingUp, Sliders, Sprout, BarChart3, RefreshCw, Check, ArrowRight } from "lucide-react";
import { CROPS } from "@/components/crop-selector";

interface YieldAnalyticsChartProps {
  baseYield: number;
  initialMoisture: number;
  initialNitrogen: number;
  initialRainfall: number;
  cropName: string;
  onApplySimulatedSettings?: (settings: { nitrogen: number; rainfall: number }) => void;
}

export function YieldAnalyticsChart({
  baseYield,
  initialMoisture,
  initialNitrogen,
  initialRainfall,
  cropName,
  onApplySimulatedSettings,
}: YieldAnalyticsChartProps) {
  // What-If Simulator Sliders
  const [simMoisture, setSimMoisture] = useState<number>(initialMoisture);
  const [simNitrogen, setSimNitrogen] = useState<number>(initialNitrogen);
  const [simRainfall, setSimRainfall] = useState<number>(initialRainfall);
  const [applied, setApplied] = useState<boolean>(false);

  // Sync simulator sliders whenever external baseline changes
  useEffect(() => {
    setSimMoisture(initialMoisture);
    setSimNitrogen(initialNitrogen);
    setSimRainfall(initialRainfall);
  }, [initialMoisture, initialNitrogen, initialRainfall]);

  // Dynamic what-if yield calculation
  const yieldRatio =
    (simMoisture / Math.max(1, initialMoisture)) * 0.4 +
    (simNitrogen / Math.max(1, initialNitrogen)) * 0.35 +
    (simRainfall / Math.max(1, initialRainfall)) * 0.25;

  const simulatedYield = Math.round(baseYield * Math.min(1.4, Math.max(0.65, yieldRatio)));
  const yieldDelta = simulatedYield - baseYield;

  // Comparison across all crops under simulated conditions
  const cropComparisons = CROPS.map((c) => {
    const moistureFit = Math.max(0.6, 1 - Math.abs(simMoisture - 28) * 0.02);
    const nitrogenFit = Math.min(1.2, simNitrogen / 110);
    const estimated = Math.round(c.baseYield * moistureFit * nitrogenFit);
    return {
      name: c.name,
      yield: estimated,
      isCurrent: c.name.toLowerCase().includes(cropName.toLowerCase()),
    };
  });

  const maxComparisonYield = Math.max(...cropComparisons.map((c) => c.yield), 1);

  // 7-day moisture projection points
  const dailyMoisturePoints = Array.from({ length: 7 }, (_, i) => {
    const projected = Math.max(10, simMoisture - i * 2.3 + (i === 3 ? 4 : 0));
    return {
      day: `Day ${i + 1}`,
      vwc: Number(projected.toFixed(1)),
    };
  });

  return (
    <div className="flex flex-col gap-4 font-mono text-white">
      {/* What-If Simulator Header Card */}
      <div className="border border-emerald-500/30 bg-black/70 p-3.5 flex flex-col gap-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-1.5 text-xs font-bold text-emerald-400">
            <Sliders className="w-4 h-4" />
            <span>Interactive "What-If" Yield Simulator</span>
          </div>

          <button
            type="button"
            onClick={() => {
              setSimMoisture(initialMoisture);
              setSimNitrogen(initialNitrogen);
              setSimRainfall(initialRainfall);
            }}
            className="text-[10px] text-gray-400 hover:text-white flex items-center gap-1 transition-colors"
          >
            <RefreshCw className="w-3 h-3" />
            <span>Reset Baseline</span>
          </button>
        </div>

        {/* Sliders Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
          {/* Moisture */}
          <div className="flex flex-col gap-1 p-2 bg-white/5 border border-white/5">
            <div className="flex justify-between text-[11px] text-gray-400">
              <span>Soil Moisture</span>
              <span className="text-white font-bold">{simMoisture.toFixed(1)}% VWC</span>
            </div>
            <input
              type="range"
              min="10"
              max="45"
              step="0.5"
              value={simMoisture}
              onChange={(e) => setSimMoisture(parseFloat(e.target.value))}
              className="w-full accent-blue-400 h-1.5 cursor-pointer bg-gray-700"
            />
          </div>

          {/* Nitrogen */}
          <div className="flex flex-col gap-1 p-2 bg-white/5 border border-white/5">
            <div className="flex justify-between text-[11px] text-gray-400">
              <span>Nitrogen (N)</span>
              <span className="text-white font-bold">{simNitrogen} kg/ha</span>
            </div>
            <input
              type="range"
              min="40"
              max="200"
              step="5"
              value={simNitrogen}
              onChange={(e) => setSimNitrogen(parseInt(e.target.value, 10))}
              className="w-full accent-emerald-400 h-1.5 cursor-pointer bg-gray-700"
            />
          </div>

          {/* Rainfall */}
          <div className="flex flex-col gap-1 p-2 bg-white/5 border border-white/5">
            <div className="flex justify-between text-[11px] text-gray-400">
              <span>Precipitation</span>
              <span className="text-white font-bold">{simRainfall} mm</span>
            </div>
            <input
              type="range"
              min="200"
              max="1200"
              step="25"
              value={simRainfall}
              onChange={(e) => setSimRainfall(parseInt(e.target.value, 10))}
              className="w-full accent-cyan-400 h-1.5 cursor-pointer bg-gray-700"
            />
          </div>
        </div>

        {/* Simulated Output Indicator */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 p-2.5 bg-black border border-white/10">
          <div className="flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-emerald-400" />
            <span className="text-xs text-gray-300">Simulated Yield Impact:</span>
            <span className="text-base font-extrabold text-white">
              {simulatedYield.toLocaleString()} kg/ha
            </span>
          </div>

          <div className="flex items-center gap-2">
            <span
              className={`text-xs font-bold px-2 py-0.5 border ${
                yieldDelta >= 0
                  ? "text-emerald-400 border-emerald-500/30 bg-emerald-500/10"
                  : "text-red-400 border-red-500/30 bg-red-500/10"
              }`}
            >
              {yieldDelta >= 0 ? `+${yieldDelta.toLocaleString()}` : yieldDelta.toLocaleString()} kg/ha ({((yieldDelta / baseYield) * 100).toFixed(1)}%)
            </span>

            {onApplySimulatedSettings && (
              <button
                type="button"
                onClick={() => {
                  onApplySimulatedSettings({
                    nitrogen: simNitrogen,
                    rainfall: simRainfall,
                  });
                  setApplied(true);
                  setTimeout(() => setApplied(false), 2000);
                }}
                className="px-2.5 py-1 text-xs bg-white text-black hover:bg-gray-200 transition-all font-semibold flex items-center gap-1"
                title="Adopt these simulated nutrients and precipitation into Playground settings"
              >
                {applied ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <ArrowRight className="w-3.5 h-3.5" />}
                <span>{applied ? "Applied!" : "Apply to Model"}</span>
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Cross-Crop Comparative Yield Chart */}
      <div className="border border-white/10 bg-black/60 p-3.5 flex flex-col gap-2">
        <span className="text-xs font-semibold text-gray-300 flex items-center gap-1.5">
          <BarChart3 className="w-3.5 h-3.5 text-emerald-400" />
          Comparative Yield Matrix (All Crops under Current Field Conditions)
        </span>

        <div className="flex flex-col gap-2 mt-2">
          {cropComparisons.map((c) => (
            <div key={c.name} className="flex flex-col gap-1">
              <div className="flex items-center justify-between text-xs">
                <span className={`font-semibold ${c.isCurrent ? "text-emerald-400" : "text-gray-300"}`}>
                  {c.name} {c.isCurrent && "★ (Selected)"}
                </span>
                <span className="font-mono text-white text-xs">{c.yield.toLocaleString()} kg/ha</span>
              </div>
              <div className="w-full bg-gray-800 h-2 overflow-hidden">
                <div
                  className={`h-full transition-all duration-300 ${
                    c.isCurrent ? "bg-emerald-400" : "bg-gray-400 hover:bg-gray-300"
                  }`}
                  style={{ width: `${(c.yield / maxComparisonYield) * 100}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 7-Day Moisture Depletion Curve */}
      <div className="border border-white/10 bg-black/60 p-3.5 flex flex-col gap-2">
        <span className="text-xs font-semibold text-gray-300 flex items-center gap-1.5">
          <TrendingUp className="w-3.5 h-3.5 text-blue-400" />
          7-Day Volumetric Water Content Depletion Trajectory
        </span>

        <div className="grid grid-cols-7 gap-1 mt-2 text-center text-xs">
          {dailyMoisturePoints.map((pt) => {
            const isCritical = pt.vwc < 18;
            return (
              <div
                key={pt.day}
                className={`p-2 border flex flex-col gap-1 items-center ${
                  isCritical ? "border-amber-500/30 bg-amber-950/20" : "border-white/5 bg-white/5"
                }`}
              >
                <span className="text-[10px] text-gray-400">{pt.day}</span>
                <span className={`text-xs font-bold ${isCritical ? "text-amber-400" : "text-blue-300"}`}>
                  {pt.vwc}%
                </span>
                <span className="text-[9px] text-gray-500">{isCritical ? "Irrigate!" : "Adequate"}</span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
