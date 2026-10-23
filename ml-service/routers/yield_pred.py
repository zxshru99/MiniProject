from fastapi import APIRouter
from schemas.requests import YieldPredictionRequest
from schemas.responses import YieldPredictionResult
from services.model_loader import model_manager
from services.explainability import ExplainabilityService

router = APIRouter(prefix="/yield", tags=["Crop Yield Prediction"])

@router.post("/predict", response_model=YieldPredictionResult)
async def predict_crop_yield(req: YieldPredictionRequest):
    """
    Direct yield prediction endpoint combining soil properties,
    accumulated weather thermal indices (GDD), and nutrient inputs.
    """
    predicted_yield, lower_bound, upper_bound = model_manager.predict_yield(
        soil_type=req.soil_type,
        moisture_pct=req.moisture_pct,
        crop_name=req.crop_name,
        gdd=req.growing_degree_days,
        rainfall_mm=req.rainfall_mm,
        nitrogen=req.nitrogen,
        phosphorus=req.phosphorus,
        potassium=req.potassium,
        ph=req.ph
    )

    shap_factors = ExplainabilityService.compute_yield_shap_factors(
        soil_type=req.soil_type,
        moisture_pct=req.moisture_pct,
        crop_name=req.crop_name,
        gdd=req.growing_degree_days,
        rainfall_mm=req.rainfall_mm,
        nitrogen=req.nitrogen,
        phosphorus=req.phosphorus,
        potassium=req.potassium,
        ph=req.ph
    )

    return YieldPredictionResult(
        crop_name=req.crop_name,
        predicted_yield_kg_ha=predicted_yield,
        confidence_interval_lower=lower_bound,
        confidence_interval_upper=upper_bound,
        shap_top_factors=shap_factors
    )
