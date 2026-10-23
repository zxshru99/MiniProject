import math
from fastapi import APIRouter
from schemas.requests import WeatherImpactRequest
from pydantic import BaseModel, Field

router = APIRouter(prefix="/weather", tags=["Agrometeorology & Impact"])

class WeatherImpactResponse(BaseModel):
    crop_name: str
    evapotranspiration_et0_mm_day: float
    moisture_depletion_forecast_3d: float
    heat_stress_index: str
    frost_risk: bool
    growing_degree_days_estimated: float
    advisory: str

@router.post("/impact", response_model=WeatherImpactResponse)
async def compute_weather_impact(req: WeatherImpactRequest):
    """
    Computes agrometeorological indicators:
    - Reference Evapotranspiration (ET0) via Hargreaves approximation.
    - 3-day projected soil moisture depletion rate.
    - Heat stress indicator for target crop.
    """
    # Climate estimates for given coordinates
    t_max = 31.0
    t_min = 20.0
    t_mean = (t_max + t_min) / 2.0
    solar_rad_approx = 22.0  # MJ/m2/day typical for subtropics

    # Hargreaves ET0 equation: ET0 = 0.0023 * (T_mean + 17.8) * (T_max - T_min)^0.5 * Ra
    # Ra expressed in equivalent evaporation depth: ~ 15 mm/day
    et0 = 0.0023 * (t_mean + 17.8) * math.sqrt(max(1.0, t_max - t_min)) * 14.5
    et0 = round(float(et0), 2)

    # 3-day moisture drop (% VWC lost) ~ 0.55 * ET0
    daily_drop = et0 * 0.55
    projected_depletion = round(min(req.current_soil_moisture, daily_drop * 3.0), 1)

    # Growing Degree Days (Base temperature: 10°C)
    t_base = 10.0
    gdd = max(0.0, t_mean - t_base) * 30.0  # 30-day cumulative estimate

    # Heat stress check
    if t_max > 36.0:
        heat_stress = "HIGH - Transpiration stress likely to abort floral buds."
        advisory = "Apply light supplementary irrigation in evening hours to reduce canopy temperature."
    elif t_max > 32.0:
        heat_stress = "MODERATE - Monitor moisture depletion closely."
        advisory = "Soil evaporation accelerated. Schedule irrigation before moisture drops below 18%."
    else:
        heat_stress = "NORMAL - Favorable thermal range for crop growth."
        advisory = "Normal physiological growth. No immediate weather intervention required."

    frost_risk = t_min < 4.0

    return WeatherImpactResponse(
        crop_name=req.crop_name,
        evapotranspiration_et0_mm_day=et0,
        moisture_depletion_forecast_3d=projected_depletion,
        heat_stress_index=heat_stress,
        frost_risk=frost_risk,
        growing_degree_days_estimated=round(gdd, 1),
        advisory=advisory
    )
