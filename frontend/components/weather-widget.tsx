"use client";

import React, { useState, useEffect } from "react";
import { 
  CloudRain, 
  Thermometer, 
  Droplets, 
  Wind, 
  Sun, 
  MapPin, 
  RefreshCw, 
  AlertTriangle, 
  CheckCircle2, 
  Compass, 
  Layers, 
  ArrowRight
} from "lucide-react";
import { fetchLiveWeather, LiveWeatherData } from "@/lib/weather";

interface WeatherWidgetProps {
  onSyncWithSettings?: (weatherData: { temperature: number; rainfall: number }) => void;
}

export const PRESET_LOCATIONS = [
  { name: "Punjab (Ludhiana) - Wheat/Rice Hub", lat: 30.90, lon: 75.85 },
  { name: "Maharashtra (Nagpur) - Cotton/Soybean", lat: 21.14, lon: 79.08 },
  { name: "Uttar Pradesh (Kanpur) - Fertile Alluvial", lat: 26.44, lon: 80.33 },
  { name: "Iowa Corn Belt, USA - Grain Heartland", lat: 41.87, lon: -93.09 },
  { name: "California Central Valley - High-Yield", lat: 36.77, lon: -119.41 },
];

export function WeatherWidget({ onSyncWithSettings }: WeatherWidgetProps) {
  const [selectedLoc, setSelectedLoc] = useState(PRESET_LOCATIONS[0]);
  const [weather, setWeather] = useState<LiveWeatherData | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [isGpsLoading, setIsGpsLoading] = useState<boolean>(false);
  const [synced, setSynced] = useState<boolean>(false);

  const loadWeather = async (lat: number, lon: number, name: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await fetchLiveWeather(lat, lon, name);
      setWeather(data);
    } catch (err: any) {
      setError(err?.message || "Failed to fetch weather data");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadWeather(selectedLoc.lat, selectedLoc.lon, selectedLoc.name);
  }, [selectedLoc]);

  const [gpsError, setGpsError] = useState<string | null>(null);

  const handleGpsDetect = () => {
    if (!navigator.geolocation) {
      setGpsError("Geolocation is not supported by your browser");
      setTimeout(() => setGpsError(null), 4000);
      return;
    }
    setIsGpsLoading(true);
    setGpsError(null);
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setIsGpsLoading(false);
        const lat = Number(pos.coords.latitude.toFixed(4));
        const lon = Number(pos.coords.longitude.toFixed(4));
        const gpsLoc = { name: `GPS Field (${lat}, ${lon})`, lat, lon };
        setSelectedLoc(gpsLoc);
      },
      (err) => {
        setIsGpsLoading(false);
        setGpsError(`GPS lookup failed: ${err.message}.`);
        setTimeout(() => setGpsError(null), 5000);
      },
      { timeout: 8000 }
    );
  };

  const handleSync = () => {
    if (!weather || !onSyncWithSettings) return;
    const estAnnualRain = Math.max(300, Math.round(weather.current.precipitation * 30 + 550));
    onSyncWithSettings({
      temperature: weather.current.temperature,
      rainfall: estAnnualRain,
    });
    setSynced(true);
    setTimeout(() => setSynced(false), 2500);
  };

  return (
    <div className="flex flex-col gap-3 font-mono text-white">
      {gpsError && (
        <div className="p-2 border border-amber-500/30 bg-amber-500/10 text-amber-300 text-xs flex items-center justify-between">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 flex-shrink-0" />
            <span>{gpsError}</span>
          </div>
          <button
            type="button"
            onClick={() => setGpsError(null)}
            className="text-amber-400 hover:text-white text-xs px-1"
          >
            ✕
          </button>
        </div>
      )}

      {/* Location Selector Bar */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-2 p-2.5 bg-black/70 border border-white/10">
        <div className="flex items-center gap-2 flex-1 min-w-0">
          <MapPin className="w-4 h-4 text-emerald-400 flex-shrink-0" />
          <select
            value={selectedLoc.name}
            onChange={(e) => {
              if (selectedLoc.name === e.target.value) return;
              const loc = PRESET_LOCATIONS.find((l) => l.name === e.target.value);
              if (loc) {
                setSelectedLoc(loc);
              }
            }}
            className="bg-black/80 border border-gray-700 text-xs text-white p-1.5 focus:outline-none focus:border-white w-full sm:max-w-xs font-mono truncate"
          >
            {!PRESET_LOCATIONS.some((l) => l.name === selectedLoc.name) && (
              <option value={selectedLoc.name}>{selectedLoc.name}</option>
            )}
            {PRESET_LOCATIONS.map((loc) => (
              <option key={loc.name} value={loc.name}>
                {loc.name}
              </option>
            ))}
          </select>
        </div>

        <div className="flex items-center gap-1.5 flex-shrink-0">
          <button
            type="button"
            onClick={handleGpsDetect}
            disabled={isGpsLoading}
            className="px-2.5 py-1.5 text-xs bg-black/60 border border-gray-600 hover:border-white text-gray-300 hover:text-white transition-all flex items-center gap-1.5"
            title="Auto-detect current field GPS coordinates"
          >
            <Compass className={`w-3.5 h-3.5 text-emerald-400 ${isGpsLoading ? "animate-spin" : ""}`} />
            <span className="hidden sm:inline">Use Field GPS</span>
          </button>

          <button
            type="button"
            onClick={() => loadWeather(selectedLoc.lat, selectedLoc.lon, selectedLoc.name)}
            disabled={isLoading}
            className="p-1.5 text-gray-300 hover:text-white border border-gray-600 hover:border-white transition-all"
            title="Refresh Live Weather"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? "animate-spin" : ""}`} />
          </button>
        </div>
      </div>

      {isLoading && (
        <div className="p-8 text-center border border-gray-800 bg-black/40 text-gray-400 text-xs flex flex-col items-center gap-2">
          <RefreshCw className="w-5 h-5 animate-spin text-emerald-400" />
          <span>Polling Live Open-Meteo Agrometeorology Satellite Feeds...</span>
        </div>
      )}

      {error && (
        <div className="p-3 border border-red-500/30 bg-red-500/10 text-red-300 text-xs flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {weather && !isLoading && (
        <div className="flex flex-col gap-3">
          {/* Main Telemetry Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
            
            {/* Temp */}
            <div className="p-2.5 border border-white/10 bg-black/60 flex flex-col gap-1">
              <span className="text-[10px] text-gray-400 flex items-center gap-1">
                <Thermometer className="w-3.5 h-3.5 text-amber-400" />
                Air Temperature
              </span>
              <span className="text-xl md:text-2xl font-bold text-white">
                {weather.current.temperature}°C
              </span>
              <span className="text-[10px] text-gray-500">
                {weather.current.weatherDescription}
              </span>
            </div>

            {/* Humidity */}
            <div className="p-2.5 border border-white/10 bg-black/60 flex flex-col gap-1">
              <span className="text-[10px] text-gray-400 flex items-center gap-1">
                <Droplets className="w-3.5 h-3.5 text-blue-400" />
                Relative Humidity
              </span>
              <span className="text-xl md:text-2xl font-bold text-white">
                {weather.current.relativeHumidity}%
              </span>
              <span className="text-[10px] text-gray-500">
                Dew point buffer
              </span>
            </div>

            {/* Precipitation */}
            <div className="p-2.5 border border-white/10 bg-black/60 flex flex-col gap-1">
              <span className="text-[10px] text-gray-400 flex items-center gap-1">
                <CloudRain className="w-3.5 h-3.5 text-cyan-400" />
                Current Precip
              </span>
              <span className="text-xl md:text-2xl font-bold text-white">
                {weather.current.precipitation} mm
              </span>
              <span className="text-[10px] text-gray-500">
                Surface accumulation
              </span>
            </div>

            {/* FAO-56 ET0 */}
            <div className="p-2.5 border border-white/10 bg-black/60 flex flex-col gap-1">
              <span className="text-[10px] text-gray-400 flex items-center gap-1">
                <Sun className="w-3.5 h-3.5 text-yellow-400" />
                FAO-56 ET0 Rate
              </span>
              <span className="text-xl md:text-2xl font-bold text-emerald-400">
                {weather.agriImpact.et0MmDay} <span className="text-xs text-gray-400 font-normal">mm/d</span>
              </span>
              <span className="text-[10px] text-gray-500">
                Daily evapotranspiration
              </span>
            </div>

          </div>

          {/* Agrometeorological Impact Advisory */}
          <div className="border border-emerald-500/30 bg-emerald-950/20 p-3 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
            <div className="flex flex-col gap-1">
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold text-emerald-400">
                  Agrometeorological Impact Analysis
                </span>
                <span className="text-[9px] px-1.5 py-0.2 bg-emerald-500/10 border border-emerald-500/30 text-emerald-300">
                  Heat Stress: {weather.agriImpact.heatStressIndex}
                </span>
                <span className="text-[9px] px-1.5 py-0.2 bg-blue-500/10 border border-blue-500/30 text-blue-300">
                  3-Day Moisture Loss: ~{weather.agriImpact.threeDayMoistureDropPct}% VWC
                </span>
              </div>
              <p className="text-xs text-gray-300 leading-snug">
                {weather.agriImpact.advisory}
              </p>
            </div>

            {onSyncWithSettings && (
              <button
                type="button"
                onClick={handleSync}
                className="px-3 py-1.5 text-xs font-semibold bg-white text-black hover:bg-gray-200 transition-all flex items-center gap-1.5 whitespace-nowrap"
              >
                {synced ? <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" /> : <ArrowRight className="w-3.5 h-3.5" />}
                <span>{synced ? "Synced with Model!" : "Sync Live Weather"}</span>
              </button>
            )}
          </div>

          {/* 7-Day Forecast Strip */}
          <div className="border border-white/10 bg-black/60 p-3 flex flex-col gap-2">
            <span className="text-xs font-semibold text-gray-300 flex items-center gap-1.5">
              <Compass className="w-3.5 h-3.5 text-emerald-400" />
              7-Day Agricultural Outlook (Precipitation & Thermal Range)
            </span>

            <div className="grid grid-cols-7 gap-1 overflow-x-auto text-center text-xs">
              {weather.daily.time.slice(0, 7).map((day, idx) => {
                const dateObj = new Date(day);
                const dayName = dateObj.toLocaleDateString("en-US", { weekday: "short" });
                const maxT = weather.daily.temperatureMax[idx];
                const minT = weather.daily.temperatureMin[idx];
                const rain = weather.daily.precipitationSum[idx];

                return (
                  <div key={day} className="p-2 border border-white/5 bg-white/5 flex flex-col gap-1 items-center">
                    <span className="text-[10px] text-gray-400 font-bold">{dayName}</span>
                    <span className="text-xs font-bold text-white">{Math.round(maxT)}°</span>
                    <span className="text-[10px] text-gray-500">{Math.round(minT)}°</span>
                    <div className="mt-1 flex items-center gap-0.5 text-[9px] text-cyan-400">
                      <CloudRain className="w-2.5 h-2.5" />
                      <span>{rain}mm</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
