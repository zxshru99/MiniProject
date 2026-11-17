from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class SoilAnalysisRequest(BaseModel):
    sample_id: Optional[str] = Field(default=None, description="Unique UUID or identifier")
    image_url: Optional[str] = Field(default=None, description="Image URL or base64 data URI")
    leaf_image_url: Optional[str] = Field(default=None, description="Optional canopy or leaf image")
    crop_name: Optional[str] = Field(default="Wheat", description="Target crop for yield prediction")
    model_id: Optional[str] = Field(default="multimodal-ensemble", description="Selected model architecture")
    soil_type: Optional[str] = Field(default=None, description="Pre-selected or classified soil type")
    nitrogen: Optional[float] = Field(default=120.0, description="Nitrogen (N) kg/ha")
    phosphorus: Optional[float] = Field(default=45.0, description="Phosphorus (P) kg/ha")
    potassium: Optional[float] = Field(default=60.0, description="Potassium (K) kg/ha")
    ph: Optional[float] = Field(default=6.5, description="Soil pH level")
    rainfall: Optional[float] = Field(default=650.0, description="Total rainfall / precipitation in mm")
    temperature: Optional[float] = Field(default=24.5, description="Ambient temperature in °C")
    field_area_ha: Optional[float] = Field(default=2.5, description="Field surface area in hectares")
    latitude: Optional[float] = Field(default=None, description="GPS latitude")
    longitude: Optional[float] = Field(default=None, description="GPS longitude")

class SoilClassifyRequest(BaseModel):
    image_url: Optional[str] = Field(default=None)
    descriptors: Optional[Dict[str, float]] = Field(default=None)

class MoistureEstimateRequest(BaseModel):
    image_url: Optional[str] = Field(default=None)
    soil_type: Optional[str] = Field(default="Loamy")
    rainfall: Optional[float] = Field(default=650.0)
    temperature: Optional[float] = Field(default=24.5)
    humidity: Optional[float] = Field(default=60.0)
    descriptors: Optional[Dict[str, float]] = Field(default=None)

class YieldPredictionRequest(BaseModel):
    soil_type: str = Field(default="Loamy", description="Soil texture type: Clay, Loamy, Sandy, Sandy Loam")
    moisture_pct: float = Field(default=25.0, ge=0.0, le=100.0, description="Estimated soil moisture percentage")
    crop_name: str = Field(default="Wheat", description="Crop name: Wheat, Rice, Maize, Chickpea, Cotton, Sugarcane, Mustard")
    nitrogen: float = Field(default=120.0, ge=0.0)
    phosphorus: float = Field(default=45.0, ge=0.0)
    potassium: float = Field(default=60.0, ge=0.0)
    ph: float = Field(default=6.5, ge=3.0, le=10.0)
    growing_degree_days: float = Field(default=1450.0, description="Accumulated GDD")
    rainfall_mm: float = Field(default=650.0, description="Seasonal total precipitation in mm")
    temperature_avg: float = Field(default=24.5, description="Seasonal average temperature in Celsius")
    field_area_ha: float = Field(default=2.5, description="Field area in hectares")

class CropRecommendationRequest(BaseModel):
    soil_type: str = Field(default="Loamy")
    moisture_pct: float = Field(default=25.0)
    nitrogen: float = Field(default=120.0)
    phosphorus: float = Field(default=45.0)
    potassium: float = Field(default=60.0)
    ph: float = Field(default=6.5)
    rainfall: float = Field(default=650.0)
    temperature: float = Field(default=24.5)

class WeatherImpactRequest(BaseModel):
    latitude: float = Field(default=20.5937, description="Field latitude")
    longitude: float = Field(default=78.9629, description="Field longitude")
    crop_name: str = Field(default="Wheat", description="Current cultivated crop")
    current_soil_moisture: float = Field(default=25.0, description="Current soil volumetric moisture %")
    temperature: Optional[float] = Field(default=28.0)
    rainfall: Optional[float] = Field(default=10.0)
