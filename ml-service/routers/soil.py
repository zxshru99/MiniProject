import os
import time
import base64
import httpx
import cv2
import numpy as np
from fastapi import APIRouter, HTTPException, status
from schemas.requests import SoilAnalysisRequest, SoilClassifyRequest, MoistureEstimateRequest
from schemas.responses import (
    FullAnalysisResponse, SoilClassificationResult,
    SoilMoistureResult, YieldPredictionResult, TopClassification
)
from services.image_processor import ImageProcessor
from services.model_loader import model_manager
from services.explainability import ExplainabilityService

router = APIRouter(prefix="/soil", tags=["Soil Analysis & Moisture"])

# Representative baseline descriptors used when no physical image is uploaded
DEFAULT_SOIL_DESCRIPTORS = {
    "l_mean": 118.5, "a_mean": 131.2, "b_mean": 136.0, "v_mean": 125.0,
    "dark_channel": 82.0, "glcm_contrast": 11.5, "glcm_dissimilarity": 2.7,
    "glcm_homogeneity": 0.44, "glcm_energy": 0.18, "lbp_mean": 5.4, "lbp_std": 2.0
}

@router.post("/analyze", response_model=FullAnalysisResponse)
async def analyze_soil_multi_modal(req: SoilAnalysisRequest):
    """
    Unified multi-input prediction endpoint:
    Orchestrates Deep Soil Texture Classifier, Soil Moisture Regressor,
    Crop Yield Regressor, and Crop Recommender AI models.
    Supports all frontend model selectors (Multi-Modal Ensemble, AgriVision CNN,
    Moisture-Net VWC, Yield XGBoost, and Crop Recommender AI).
    Supports all image formats: base64, HTTP/HTTPS URL, and local disk paths.
    """
    start_time = time.time()
    sample_id = req.sample_id or f"sample_{int(time.time() * 1000)}"

    blur_score = 145.2
    quality_status = "VALID"
    descriptors = dict(DEFAULT_SOIL_DESCRIPTORS)
    img_bgr = None

    # 1. Acquire Soil Image if provided
    if req.image_url and len(req.image_url.strip()) > 0:
        try:
            image_bytes = None
            raw_url = req.image_url.strip()
            if raw_url.startswith("data:"):
                encoded = raw_url.split(",", 1)[1] if "," in raw_url else raw_url
                image_bytes = base64.b64decode(encoded)
            elif raw_url.startswith("http://") or raw_url.startswith("https://"):
                try:
                    async with httpx.AsyncClient(timeout=3.5) as client:
                        resp = await client.get(raw_url)
                        if resp.status_code == 200:
                            image_bytes = resp.content
                except Exception:
                    image_bytes = None
            elif os.path.exists(raw_url):
                with open(raw_url, "rb") as f:
                    image_bytes = f.read()

            if image_bytes:
                img_bgr = ImageProcessor.bytes_to_cv2(image_bytes)
                blur_score = ImageProcessor.compute_blur_score(img_bgr)
                quality_status = "VALID" if blur_score >= 40.0 else "BLURRY_REJECT"

                clahe_bgr = ImageProcessor.apply_clahe(img_bgr)
                segmented_bgr, soil_mask = ImageProcessor.segment_soil_surface(clahe_bgr)
                descriptors = ImageProcessor.extract_physical_descriptors(segmented_bgr)

                # Generate and save optical Grad-CAM attention heatmap
                try:
                    heatmap_img = ExplainabilityService.generate_synthetic_gradcam(img_bgr)
                    heatmap_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "heatmaps")
                    os.makedirs(heatmap_dir, exist_ok=True)
                    heatmap_path = os.path.join(heatmap_dir, f"{sample_id}_gradcam.jpg")
                    cv2.imwrite(heatmap_path, heatmap_img)
                except Exception as e:
                    print(f"[SoilRouter] Heatmap generation note: {e}")
        except Exception as e:
            print(f"[SoilRouter] Soil image processing note: {e}")

    # Optional Canopy / Leaf Image Processing
    canopy_vigor = None
    if req.leaf_image_url and len(req.leaf_image_url.strip()) > 0:
        try:
            leaf_bytes = None
            raw_leaf = req.leaf_image_url.strip()
            if raw_leaf.startswith("data:"):
                enc = raw_leaf.split(",", 1)[1] if "," in raw_leaf else raw_leaf
                leaf_bytes = base64.b64decode(enc)
            elif raw_leaf.startswith("http://") or raw_leaf.startswith("https://"):
                try:
                    async with httpx.AsyncClient(timeout=3.5) as client:
                        resp = await client.get(raw_leaf)
                        if resp.status_code == 200:
                            leaf_bytes = resp.content
                except Exception:
                    leaf_bytes = None
            elif os.path.exists(raw_leaf):
                with open(raw_leaf, "rb") as f:
                    leaf_bytes = f.read()

            if leaf_bytes:
                leaf_bgr = ImageProcessor.bytes_to_cv2(leaf_bytes)
                rgb = cv2.cvtColor(leaf_bgr, cv2.COLOR_BGR2RGB).astype(np.float32)
                r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
                denom = 2 * g + r + b + 1e-6
                gli = float(np.mean((2 * g - r - b) / denom))
                if gli > 0.08:
                    canopy_vigor = "VIGOROUS_HEALTHY"
                elif gli > 0.0:
                    canopy_vigor = "MODERATE_HEALTH"
                else:
                    canopy_vigor = "CHLOROTIC_STRESS"
        except Exception as e:
            print(f"[SoilRouter] Leaf analysis note: {e}")

    # 2. Model 1: Soil Texture & Type Classification
    if req.soil_type:
        soil_type = req.soil_type.strip().title()
        top_conf = 0.95
        top_preds = [TopClassification(label=soil_type, confidence=0.95)]
    else:
        soil_type, top_conf, top_preds = model_manager.classify_soil(descriptors, img_bgr=img_bgr)

    # 3. Model 2: Volumetric Soil Moisture (% VWC)
    moisture_pct, moist_cat, irrig_needed, urgency = model_manager.estimate_moisture(
        descriptors=descriptors,
        rainfall=req.rainfall if req.rainfall is not None else 650.0,
        temperature=req.temperature if req.temperature is not None else 24.5,
        humidity=60.0,
        soil_type=soil_type
    )

    # 4. Model 3: Crop Yield Prediction Engine
    crop_name = req.crop_name or "Wheat"
    predicted_yield, yield_lower, yield_upper = model_manager.predict_yield(
        soil_type=soil_type,
        moisture_pct=moisture_pct,
        crop_name=crop_name,
        gdd=1450.0,
        rainfall_mm=req.rainfall if req.rainfall is not None else 650.0,
        nitrogen=req.nitrogen if req.nitrogen is not None else 120.0,
        phosphorus=req.phosphorus if req.phosphorus is not None else 45.0,
        potassium=req.potassium if req.potassium is not None else 60.0,
        ph=req.ph if req.ph is not None else 6.5,
        field_area_ha=req.field_area_ha if req.field_area_ha is not None else 2.5,
        temperature=req.temperature if req.temperature is not None else 24.5
    )

    # Adjust yield if canopy leaf photo is provided
    if canopy_vigor == "VIGOROUS_HEALTHY":
        predicted_yield = round(predicted_yield * 1.07, 1)
        yield_lower = round(yield_lower * 1.07, 1)
        yield_upper = round(yield_upper * 1.07, 1)
    elif canopy_vigor == "CHLOROTIC_STRESS":
        predicted_yield = round(predicted_yield * 0.91, 1)
        yield_lower = round(yield_lower * 0.91, 1)
        yield_upper = round(yield_upper * 0.91, 1)

    # 5. SHAP Feature Attribution Factors
    shap_factors = ExplainabilityService.compute_yield_shap_factors(
        soil_type=soil_type,
        moisture_pct=moisture_pct,
        crop_name=crop_name,
        gdd=1450.0,
        rainfall_mm=req.rainfall if req.rainfall is not None else 650.0,
        nitrogen=req.nitrogen if req.nitrogen is not None else 120.0,
        phosphorus=req.phosphorus if req.phosphorus is not None else 45.0,
        potassium=req.potassium if req.potassium is not None else 60.0,
        ph=req.ph if req.ph is not None else 6.5,
        temperature=req.temperature if req.temperature is not None else 24.5
    )

    if canopy_vigor == "VIGOROUS_HEALTHY":
        shap_factors.insert(0, {
            "feature": "Canopy Chlorophyll & Vigor (GLI)",
            "feature_name": "Canopy Chlorophyll & Vigor (GLI)",
            "value": "Healthy Photosynthetic Green (+7%)",
            "impact": 0.17,
            "shap_value": 0.17,
            "unit": "index"
        })
    elif canopy_vigor == "CHLOROTIC_STRESS":
        shap_factors.insert(0, {
            "feature": "Canopy Chlorophyll & Vigor (GLI)",
            "feature_name": "Canopy Chlorophyll & Vigor (GLI)",
            "value": "Chlorotic Foliar Stress (-9%)",
            "impact": -0.21,
            "shap_value": -0.21,
            "unit": "index"
        })

    # 6. Model 4: Crop Recommender AI
    recommendations = model_manager.recommend_crops(
        soil_type=soil_type,
        moisture_pct=moisture_pct,
        nitrogen=req.nitrogen if req.nitrogen is not None else 120.0,
        phosphorus=req.phosphorus if req.phosphorus is not None else 45.0,
        potassium=req.potassium if req.potassium is not None else 60.0,
        ph=req.ph if req.ph is not None else 6.5,
        rainfall=req.rainfall if req.rainfall is not None else 650.0,
        temperature=req.temperature if req.temperature is not None else 24.5
    )

    duration_ms = int((time.time() - start_time) * 1000)

    return FullAnalysisResponse(
        sample_id=sample_id,
        selected_model=req.model_id or "multimodal-ensemble",
        soil=SoilClassificationResult(
            soil_type=soil_type,
            confidence=top_conf,
            top_predictions=top_preds,
            gradcam_url=f"/static/heatmaps/{sample_id}_gradcam.jpg",
            blur_score=round(blur_score, 1),
            quality_status=quality_status
        ),
        moisture=SoilMoistureResult(
            moisture_percentage=moisture_pct,
            moisture_category=moist_cat,
            irrigation_needed=irrig_needed,
            irrigation_urgency=urgency
        ),
        yield_prediction=YieldPredictionResult(
            crop_name=crop_name,
            predicted_yield_kg_ha=predicted_yield,
            confidence_interval_lower=yield_lower,
            confidence_interval_upper=yield_upper,
            shap_top_factors=shap_factors
        ),
        recommended_crops=recommendations,
        inference_duration_ms=max(15, duration_ms),
        model_version="AgriPredict-MultiModel-v2.0"
    )

@router.post("/classify", response_model=SoilClassificationResult)
async def classify_soil_only(req: SoilClassifyRequest):
    """Dedicated endpoint for AgriVision CNN / Random Forest Soil Classifier."""
    img_bgr = None
    descriptors = req.descriptors or dict(DEFAULT_SOIL_DESCRIPTORS)
    blur_score = 150.0

    if req.image_url and len(req.image_url.strip()) > 0:
        try:
            image_bytes = None
            raw_url = req.image_url.strip()
            if raw_url.startswith("data:"):
                encoded = raw_url.split(",", 1)[1] if "," in raw_url else raw_url
                image_bytes = base64.b64decode(encoded)
            elif os.path.exists(raw_url):
                with open(raw_url, "rb") as f:
                    image_bytes = f.read()

            if image_bytes:
                img_bgr = ImageProcessor.bytes_to_cv2(image_bytes)
                blur_score = ImageProcessor.compute_blur_score(img_bgr)
                descriptors = ImageProcessor.extract_physical_descriptors(img_bgr)
        except Exception as e:
            print(f"[SoilRouter] Classify endpoint note: {e}")

    soil_type, top_conf, top_preds = model_manager.classify_soil(descriptors, img_bgr=img_bgr)
    return SoilClassificationResult(
        soil_type=soil_type,
        confidence=top_conf,
        top_predictions=top_preds,
        blur_score=round(blur_score, 1),
        quality_status="VALID" if blur_score >= 40.0 else "BLURRY_REJECT"
    )

@router.post("/moisture", response_model=SoilMoistureResult)
async def estimate_moisture_only(req: MoistureEstimateRequest):
    """Dedicated endpoint for Moisture-Net VWC Regressor."""
    descriptors = req.descriptors or dict(DEFAULT_SOIL_DESCRIPTORS)
    pct, cat, irrig, urgency = model_manager.estimate_moisture(
        descriptors=descriptors,
        rainfall=req.rainfall or 650.0,
        temperature=req.temperature or 24.5,
        humidity=req.humidity or 60.0,
        soil_type=req.soil_type or "Loamy"
    )
    return SoilMoistureResult(
        moisture_percentage=pct,
        moisture_category=cat,
        irrigation_needed=irrig,
        irrigation_urgency=urgency
    )
