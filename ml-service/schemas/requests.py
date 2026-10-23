from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class SoilAnalysisRequest(BaseModel):
    sample_id: Optional[str] = Field(default=None, description="Unique UUID of the soil sample")
    image_url: str = Field(..., description="Accessible HTTP/S3 URL or base64 data URI of the uploaded image")
    crop_name: Optional[str] = Field("wheat", description="Target crop for yield prediction")
    latitude: Optional[float] = Field(None, description="GPS latitude of field")
    longitude: Optional[float] = Field(None, description="GPS longitude of field")
    nitrogen: Optional[float] = Field(120.0, description="Soil Nitrogen (N) content in kg/ha")
    phosphorus: Optional[float] = Field(60.0, description="Soil Phosphorus (P) content in kg/ha")
    potassium: Optional[float] = Field(40.0, description="Soil Potassium (K) content in kg/ha")
    ph: Optional[float] = Field(6.5, description="Soil pH level")

class YieldPredictionRequest(BaseModel):
    soil_type: str = Field(..., description="Soil texture type: Clay, Loamy, Sandy, Sandy Loam")
    moisture_pct: float = Field(..., ge=0.0, le=100.0, description="Estimated soil moisture percentage")
    crop_name: str = Field(..., description="Crop name: wheat, rice, maize, etc.")
    nitrogen: float = Field(120.0, ge=0.0)
    phosphorus: float = Field(60.0, ge=0.0)
    potassium: float = Field(40.0, ge=0.0)
    ph: float = Field(6.5, ge=3.0, le=10.0)
    growing_degree_days: float = Field(1450.0, description="Accumulated GDD over vegetative phase")
    rainfall_mm: float = Field(250.0, description="Seasonal total precipitation in mm")
    temperature_avg: float = Field(26.5, description="Seasonal average temperature in Celsius")

class WeatherImpactRequest(BaseModel):
    latitude: float = Field(..., description="Field latitude")
    longitude: float = Field(..., description="Field longitude")
    crop_name: str = Field("wheat", description="Current cultivated crop")
    current_soil_moisture: float = Field(25.0, description="Current soil volumetric moisture %")
