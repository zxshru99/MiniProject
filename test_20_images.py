import os
import sys
import json
import base64
import time
import pandas as pd
import numpy as np

# Ensure ml-service is on path
sys.path.insert(0, os.path.abspath("ml-service"))

from services.model_loader import model_manager
from services.image_processor import ImageProcessor
from schemas.requests import SoilAnalysisRequest
from routers.soil import analyze_soil_multi_modal

# Pre-load all ML models
model_manager.load_all_models()

base_dir = r"datasets\Soil types"
categories = ["Black Soil", "Cinder Soil", "Laterite Soil", "Peat Soil", "Yellow Soil"]

# Select 4 distinct images from each category = 20 images
test_files = [
    ("Black Soil", "2.jpg"),
    ("Black Soil", "10.jpg"),
    ("Black Soil", "20.jpg"),
    ("Black Soil", "30.jpg"),
    
    ("Cinder Soil", "1.jpg"),
    ("Cinder Soil", "10.jpg"),
    ("Cinder Soil", "20.jpg"),
    ("Cinder Soil", "30.jpg"),
    
    ("Laterite Soil", "1.jpg"),
    ("Laterite Soil", "10.jpg"),
    ("Laterite Soil", "20.jpg"),
    ("Laterite Soil", "30.jpg"),
    
    ("Peat Soil", "1.jpg"),
    ("Peat Soil", "10.jpg"),
    ("Peat Soil", "20.jpg"),
    ("Peat Soil", "30.jpg"),
    
    ("Yellow Soil", "2.jpg"),
    ("Yellow Soil", "10.jpg"),
    ("Yellow Soil", "20.jpg"),
    ("Yellow Soil", "30.jpg"),
]

print("="*85)
print("BENCHMARK TEST: 20 DIFFERENT SOIL IMAGES ACROSS ALL CATEGORIES")
print("="*85)

results = []
correct_count = 0

import asyncio

async def run_benchmark():
    global correct_count
    for idx, (ground_truth, fname) in enumerate(test_files, 1):
        fpath = os.path.join(base_dir, ground_truth, fname)
        if not os.path.exists(fpath):
            print(f"File not found: {fpath}")
            continue

        # Load file as base64 data URI (simulating webapp client upload)
        with open(fpath, "rb") as f:
            b64_data = base64.b64encode(f.read()).decode("utf-8")
        data_uri = f"data:image/jpeg;base64,{b64_data}"

        req = SoilAnalysisRequest(
            sample_id=f"test_{idx:02d}",
            image_url=data_uri,
            crop_name="Wheat",
            nitrogen=120.0,
            phosphorus=45.0,
            potassium=60.0,
            ph=6.5,
            rainfall=650.0,
            temperature=24.5,
            field_area_ha=2.5
        )

        resp = await analyze_soil_multi_modal(req)

        pred_soil = resp.soil.soil_type
        conf = resp.soil.confidence * 100.0
        moist_pct = resp.moisture.moisture_percentage
        moist_cat = resp.moisture.moisture_category
        yield_pred = resp.yield_prediction.predicted_yield_kg_ha
        top_rec = ", ".join([r.crop_name for r in resp.recommended_crops[:2]])

        is_match = (pred_soil.lower().strip() == ground_truth.lower().strip())
        if is_match:
            correct_count += 1

        results.append({
            "No": idx,
            "Original (Ground Truth)": ground_truth,
            "Filename": fname,
            "Predicted Soil Type": pred_soil,
            "Confidence": f"{conf:.1f}%",
            "Moisture (% VWC)": f"{moist_pct:.1f}% ({moist_cat})",
            "Predicted Yield (kg/ha)": f"{yield_pred:.0f}",
            "Top Crop Recommendations": top_rec,
            "Match": "MATCH" if is_match else "MISMATCH"
        })

asyncio.run(run_benchmark())

df_res = pd.DataFrame(results)
print("\n" + df_res[["No", "Original (Ground Truth)", "Filename", "Predicted Soil Type", "Confidence", "Moisture (% VWC)", "Match"]].to_string(index=False))

acc = (correct_count / len(test_files)) * 100.0
print("\n" + "="*85)
print(f"BENCHMARK SUMMARY: {correct_count}/{len(test_files)} Correct ({acc:.1f}% Accuracy)")
print("="*85)

# Save full results as JSON for presentation
out_json = r"datasets\benchmark_20_images_results.json"
df_res.to_json(out_json, orient="records", indent=2)
print(f"Full benchmark detailed output saved to {out_json}")
