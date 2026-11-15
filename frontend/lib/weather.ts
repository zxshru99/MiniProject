export interface LiveWeatherData {
  locationName: string;
  latitude: number;
  longitude: number;
  current: {
    temperature: number; // °C
    relativeHumidity: number; // %
    precipitation: number; // mm
    weatherCode: number;
    weatherDescription: string;
    windSpeed: number; // km/h
    isDay: boolean;
  };
  daily: {
    time: string[];
    temperatureMax: number[];
    temperatureMin: number[];
    precipitationSum: number[];
    et0Evapotranspiration: number[];
  };
  agriImpact: {
    et0MmDay: number;
    threeDayMoistureDropPct: number;
    heatStressIndex: "LOW" | "MODERATE" | "HIGH" | "CRITICAL";
    frostRisk: boolean;
    growingDegreeDays: number;
    advisory: string;
  };
}

export function mapWeatherCodeToDescription(code: number): string {
  if (code === 0) return "Clear Sky";
  if (code === 1 || code === 2) return "Partly Cloudy";
  if (code === 3) return "Overcast";
  if (code >= 45 && code <= 48) return "Fog / High Humidity";
  if (code >= 51 && code <= 55) return "Light Drizzle";
  if (code >= 61 && code <= 65) return "Rain Showers";
  if (code >= 71 && code <= 77) return "Snow Flurries";
  if (code >= 80 && code <= 82) return "Heavy Rain";
  if (code >= 95) return "Thunderstorm";
  return "Cloudy";
}

/**
 * Fetches real-time agrometeorological data from Open-Meteo.
 * Free, no API key required, with FAO-56 Penman-Monteith Evapotranspiration (ET0).
 */
export async function fetchLiveWeather(
  lat: number,
  lon: number,
  locationName = "Detected Farm Coordinates"
): Promise<LiveWeatherData> {
  const url = `https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}&current=temperature_2m,relative_humidity_2m,precipitation,weather_code,wind_speed_10m,is_day&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,et0_fao_evapotranspiration&timezone=auto`;

  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(`Open-Meteo API returned status ${res.status}`);
  }

  const data = await res.json();
  const current = data.current;
  const daily = data.daily;

  const temp = current.temperature_2m;
  const precip = current.precipitation;
  const et0 = daily.et0_fao_evapotranspiration?.[0] || 4.2;

  // Compute 3-day projected soil moisture loss
  const dailyDrop = et0 * 0.55;
  const threeDayLoss = Number((dailyDrop * 3).toFixed(1));

  // Heat stress calculation
  let heatStress: "LOW" | "MODERATE" | "HIGH" | "CRITICAL" = "LOW";
  let advisory = "Optimal weather window for active crop transpiration.";

  if (temp > 38) {
    heatStress = "CRITICAL";
    advisory = "Severe heat stress detected! Floral abortion risk high. Apply light evening misting or sprinkler irrigation.";
  } else if (temp > 33) {
    heatStress = "HIGH";
    advisory = "High ambient heat accelerating soil evaporation. Monitor topsoil moisture closely.";
  } else if (temp > 28) {
    heatStress = "MODERATE";
    advisory = "Moderate evaporation rate. Standard scheduled irrigation recommended.";
  }

  const frostRisk = current.temperature_2m <= 3.5;
  if (frostRisk) {
    advisory = "Frost advisory: Night temperatures approaching freezing. Protect sensitive seedling foliage.";
  }

  // Growing Degree Days (Base temp 10°C)
  const gdd = Math.max(0, temp - 10) * 1.2;

  return {
    locationName,
    latitude: lat,
    longitude: lon,
    current: {
      temperature: temp,
      relativeHumidity: current.relative_humidity_2m,
      precipitation: precip,
      weatherCode: current.weather_code,
      weatherDescription: mapWeatherCodeToDescription(current.weather_code),
      windSpeed: current.wind_speed_10m,
      isDay: current.is_day === 1,
    },
    daily: {
      time: daily.time || [],
      temperatureMax: daily.temperature_2m_max || [],
      temperatureMin: daily.temperature_2m_min || [],
      precipitationSum: daily.precipitation_sum || [],
      et0Evapotranspiration: daily.et0_fao_evapotranspiration || [],
    },
    agriImpact: {
      et0MmDay: Number(et0.toFixed(2)),
      threeDayMoistureDropPct: threeDayLoss,
      heatStressIndex: heatStress,
      frostRisk,
      growingDegreeDays: Number(gdd.toFixed(1)),
      advisory,
    },
  };
}
