import time
from fastapi import APIRouter
from schemas.requests import CropRecommendationRequest
from schemas.responses import CropRecommendationResponse
from services.model_loader import model_manager

router = APIRouter(prefix="/crop", tags=["Crop Recommendation AI"])

@router.get("/list")
async def list_available_crops():
    """Lists all supported crops with baseline water requirements and yields."""
    return {
        "total_crops": len(model_manager.CROP_METADATA),
        "crops": model_manager.CROP_METADATA
    }

@router.post("/recommend", response_model=CropRecommendationResponse)
async def recommend_crops(req: CropRecommendationRequest):
    """
    Direct Crop Recommender AI endpoint:
    Predicts the top suitable crops given soil texture, moisture % VWC,
    nitrogen, phosphorus, potassium, pH, rainfall, and temperature.
    """
    t0 = time.time()
    recs = model_manager.recommend_crops(
        soil_type=req.soil_type,
        moisture_pct=req.moisture_pct,
        nitrogen=req.nitrogen,
        phosphorus=req.phosphorus,
        potassium=req.potassium,
        ph=req.ph,
        rainfall=req.rainfall,
        temperature=req.temperature
    )
    duration_ms = int((time.time() - t0) * 1000)

    return CropRecommendationResponse(
        top_recommendations=recs,
        analysis_duration_ms=max(10, duration_ms)
    )

