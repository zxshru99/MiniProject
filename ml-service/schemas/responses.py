from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class TopClassification(BaseModel):
    label: str
    confidence: float

class SoilClassificationResult(BaseModel):
    soil_type: str = Field(..., description="Top classified soil category: Clay, Loamy, Sandy, Sandy Loam")
    confidence: float = Field(..., ge=0.0, le=1.0)
    top_predictions: List[TopClassification]
    gradcam_url: Optional[str] = None
    blur_score: float
    quality_status: str

class SoilMoistureResult(BaseModel):
    moisture_percentage: float = Field(..., ge=0.0, le=100.0, description="Volumetric water content (% VWC)")
    moisture_category: str = Field(..., description="DRY, MODERATE, WET, or SATURATED")
    irrigation_needed: bool
    irrigation_urgency: str

class YieldPredictionResult(BaseModel):
    crop_name: str
    predicted_yield_kg_ha: float
    confidence_interval_lower: float
    confidence_interval_upper: float
    shap_top_factors: List[Dict[str, Any]]

class CropRecommendationItem(BaseModel):
    crop_name: str
    suitability_score: float
    expected_yield_kg_ha: float
    water_requirement_mm: float

class FullAnalysisResponse(BaseModel):
    sample_id: str
    soil: SoilClassificationResult
    moisture: SoilMoistureResult
    yield_prediction: YieldPredictionResult
    recommended_crops: List[CropRecommendationItem]
    inference_duration_ms: int
    model_version: str

class HealthCheckResponse(BaseModel):
    status: str
    models_loaded: bool
    service: str
    version: str
