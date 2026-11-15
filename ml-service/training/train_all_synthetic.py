import os
import sys
import json
import pickle
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, r2_score, mean_squared_error

# Fix Windows console encoding
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

DATASET_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "datasets", "synthetic")
MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")
os.makedirs(DATASET_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)

np.random.seed(42)

# =====================================================================
# 1. GENERATE DATASET & TRAIN SOIL TEXTURE CLASSIFIER
# =====================================================================
def generate_and_train_soil_classifier(n_samples=4000):
    print("\n" + "="*60)
    print("1. TRAINING SOIL TEXTURE CLASSIFICATION MODEL")
    print("="*60)

    classes = ["Clay", "Loamy", "Sandy", "Sandy Loam"]
    samples_per_class = n_samples // len(classes)
    records = []

    for c in classes:
        for _ in range(samples_per_class):
            if c == "Sandy":
                l_mean = np.random.normal(155, 12)
                a_mean = np.random.normal(128, 4)
                b_mean = np.random.normal(142, 6)
                v_mean = np.random.normal(160, 15)
                dark_channel = np.random.normal(55, 10)
                glcm_contrast = np.random.normal(18.5, 4.0)
                glcm_dissimilarity = np.random.normal(3.8, 0.8)
                glcm_homogeneity = np.random.normal(0.28, 0.05)
                glcm_energy = np.random.normal(0.12, 0.03)
                lbp_mean = np.random.normal(6.8, 0.6)
                lbp_std = np.random.normal(2.4, 0.3)
            elif c == "Clay":
                l_mean = np.random.normal(95, 10)
                a_mean = np.random.normal(139, 5)
                b_mean = np.random.normal(132, 5)
                v_mean = np.random.normal(105, 12)
                dark_channel = np.random.normal(98, 12)
                glcm_contrast = np.random.normal(7.2, 2.0)
                glcm_dissimilarity = np.random.normal(1.9, 0.4)
                glcm_homogeneity = np.random.normal(0.55, 0.06)
                glcm_energy = np.random.normal(0.24, 0.04)
                lbp_mean = np.random.normal(4.2, 0.5)
                lbp_std = np.random.normal(1.7, 0.2)
            elif c == "Loamy":
                l_mean = np.random.normal(118, 11)
                a_mean = np.random.normal(131, 4)
                b_mean = np.random.normal(136, 5)
                v_mean = np.random.normal(125, 12)
                dark_channel = np.random.normal(82, 10)
                glcm_contrast = np.random.normal(11.5, 2.5)
                glcm_dissimilarity = np.random.normal(2.7, 0.5)
                glcm_homogeneity = np.random.normal(0.44, 0.05)
                glcm_energy = np.random.normal(0.18, 0.03)
                lbp_mean = np.random.normal(5.4, 0.5)
                lbp_std = np.random.normal(2.0, 0.25)
            else: # Sandy Loam
                l_mean = np.random.normal(136, 11)
                a_mean = np.random.normal(130, 4)
                b_mean = np.random.normal(139, 5)
                v_mean = np.random.normal(142, 14)
                dark_channel = np.random.normal(68, 10)
                glcm_contrast = np.random.normal(14.8, 3.0)
                glcm_dissimilarity = np.random.normal(3.2, 0.6)
                glcm_homogeneity = np.random.normal(0.35, 0.05)
                glcm_energy = np.random.normal(0.15, 0.03)
                lbp_mean = np.random.normal(6.0, 0.5)
                lbp_std = np.random.normal(2.2, 0.25)

            records.append({
                "l_mean": round(float(l_mean), 2),
                "a_mean": round(float(a_mean), 2),
                "b_mean": round(float(b_mean), 2),
                "v_mean": round(float(v_mean), 2),
                "dark_channel": round(float(dark_channel), 2),
                "glcm_contrast": round(float(glcm_contrast), 2),
                "glcm_dissimilarity": round(float(glcm_dissimilarity), 2),
                "glcm_homogeneity": round(float(glcm_homogeneity), 3),
                "glcm_energy": round(float(glcm_energy), 3),
                "lbp_mean": round(float(lbp_mean), 2),
                "lbp_std": round(float(lbp_std), 2),
                "soil_type": c
            })

    df_soil = pd.DataFrame(records)
    csv_file = os.path.join(DATASET_DIR, "synthetic_soil_classification.csv")
    df_soil.to_csv(csv_file, index=False)
    print(f"Generated {len(df_soil)} synthetic soil descriptor records -> {csv_file}")

    feature_cols = [
        "l_mean", "a_mean", "b_mean", "v_mean", "dark_channel",
        "glcm_contrast", "glcm_dissimilarity", "glcm_homogeneity",
        "glcm_energy", "lbp_mean", "lbp_std"
    ]
    X = df_soil[feature_cols]
    y = df_soil["soil_type"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    model = RandomForestClassifier(n_estimators=100, max_depth=12, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"[SUCCESS] Soil Classifier Validation Accuracy: {acc*100:.2f}%")

    # Save classes
    classes_path = os.path.join(MODELS_DIR, "soil_classes.json")
    with open(classes_path, "w", encoding="utf-8") as f:
        json.dump(classes, f, indent=2)

    # Save model bundle
    out_path = os.path.join(MODELS_DIR, "soil_classifier.pkl")
    with open(out_path, "wb") as f:
        pickle.dump({"model": model, "classes": classes, "features": feature_cols}, f)
    print(f"Saved trained Soil Classifier bundle to {out_path}")

    return model, feature_cols


# =====================================================================
# 2. GENERATE DATASET & TRAIN SOIL MOISTURE REGRESSOR
# =====================================================================
def generate_and_train_moisture_model(n_samples=5000):
    print("\n" + "="*60)
    print("2. TRAINING SOIL MOISTURE REGRESSION MODEL (% VWC)")
    print("="*60)

    soil_types = ["Clay", "Loamy", "Sandy", "Sandy Loam"]
    soil_capacities = {"Clay": 1.25, "Loamy": 1.10, "Sandy Loam": 0.95, "Sandy": 0.75}
    records = []

    for _ in range(n_samples):
        st = np.random.choice(soil_types)
        cap = soil_capacities[st]

        rainfall = np.random.uniform(50, 1200) # mm
        temp = np.random.uniform(12, 42) # C
        humidity = np.random.uniform(20, 95) # %
        
        # Physical darkening and moisture relationship
        base_moisture = (rainfall / 32.0) * cap * (humidity / 55.0) / (1.0 + (temp - 15.0)*0.025)
        moisture_vwc = float(np.clip(base_moisture + np.random.normal(0, 1.8), 5.0, 52.0))

        # Optical manifestations
        l_mean = float(np.clip(180.0 - (moisture_vwc * 2.1) + np.random.normal(0, 5.0), 65.0, 200.0))
        dark_channel = float(np.clip((moisture_vwc * 2.2) + np.random.normal(0, 6.0), 15.0, 140.0))
        glcm_contrast = float(np.clip(22.0 - (moisture_vwc * 0.28) + np.random.normal(0, 1.5), 3.0, 30.0))
        glcm_homogeneity = float(np.clip(0.20 + (moisture_vwc * 0.008) + np.random.normal(0, 0.04), 0.15, 0.75))

        records.append({
            "l_mean": round(l_mean, 2),
            "dark_channel": round(dark_channel, 2),
            "glcm_contrast": round(glcm_contrast, 2),
            "glcm_homogeneity": round(glcm_homogeneity, 3),
            "rainfall": round(rainfall, 1),
            "temperature": round(temp, 1),
            "humidity": round(humidity, 1),
            "soil_type": st,
            "moisture_pct": round(moisture_vwc, 1)
        })

    df_moist = pd.DataFrame(records)
    csv_file = os.path.join(DATASET_DIR, "synthetic_soil_moisture.csv")
    df_moist.to_csv(csv_file, index=False)
    print(f"Generated {len(df_moist)} synthetic soil moisture records -> {csv_file}")

    le_soil = LabelEncoder()
    df_moist["soil_code"] = le_soil.fit_transform(df_moist["soil_type"])

    feature_cols = [
        "l_mean", "dark_channel", "glcm_contrast", "glcm_homogeneity",
        "rainfall", "temperature", "humidity", "soil_code"
    ]
    X = df_moist[feature_cols]
    y = df_moist["moisture_pct"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.15, random_state=42)

    model = GradientBoostingRegressor(n_estimators=120, learning_rate=0.08, max_depth=5, random_state=42)
    model.fit(X_train, y_train)

    score = model.score(X_test, y_test)
    y_pred = model.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    print(f"[SUCCESS] Soil Moisture Regressor R2 Score: {score:.4f} | RMSE: {rmse:.2f}% VWC")

    out_path = os.path.join(MODELS_DIR, "moisture_model.pkl")
    with open(out_path, "wb") as f:
        pickle.dump({"model": model, "soil_encoder": le_soil, "features": feature_cols}, f)
    print(f"Saved trained Soil Moisture model bundle to {out_path}")

    return model


# =====================================================================
# 3. GENERATE DATASET & TRAIN CROP YIELD REGRESSION ENGINE FOR ALL CROPS
# =====================================================================
def generate_and_train_yield_model(n_samples=15000):
    print("\n" + "="*60)
    print("3. TRAINING COMPREHENSIVE CROP YIELD REGRESSION ENGINE")
    print("="*60)

    # All major crops: Cereals, Pulses, Oilseeds, Commercial, and Vegetables
    crop_specs = {
        "Wheat": {"base": 4200, "opt_moist": 26, "opt_temp": 22, "opt_n": 130, "opt_p": 60, "opt_k": 50, "opt_ph": 6.8, "opt_rain": 550},
        "Rice": {"base": 4100, "opt_moist": 44, "opt_temp": 29, "opt_n": 150, "opt_p": 65, "opt_k": 60, "opt_ph": 6.2, "opt_rain": 1150},
        "Maize": {"base": 5400, "opt_moist": 30, "opt_temp": 26, "opt_n": 160, "opt_p": 70, "opt_k": 55, "opt_ph": 6.5, "opt_rain": 700},
        "Barley": {"base": 3400, "opt_moist": 22, "opt_temp": 20, "opt_n": 90, "opt_p": 45, "opt_k": 40, "opt_ph": 7.0, "opt_rain": 450},
        "Millets": {"base": 2200, "opt_moist": 16, "opt_temp": 30, "opt_n": 70, "opt_p": 35, "opt_k": 30, "opt_ph": 6.8, "opt_rain": 350},
        "Oats": {"base": 2900, "opt_moist": 24, "opt_temp": 18, "opt_n": 85, "opt_p": 40, "opt_k": 40, "opt_ph": 6.5, "opt_rain": 480},
        "Chickpea": {"base": 1550, "opt_moist": 18, "opt_temp": 20, "opt_n": 40, "opt_p": 50, "opt_k": 35, "opt_ph": 7.2, "opt_rain": 380},
        "Pigeon Pea": {"base": 1400, "opt_moist": 22, "opt_temp": 28, "opt_n": 45, "opt_p": 55, "opt_k": 40, "opt_ph": 6.8, "opt_rain": 550},
        "Lentil": {"base": 1250, "opt_moist": 19, "opt_temp": 19, "opt_n": 35, "opt_p": 45, "opt_k": 30, "opt_ph": 6.9, "opt_rain": 360},
        "Black Gram": {"base": 1100, "opt_moist": 24, "opt_temp": 29, "opt_n": 30, "opt_p": 45, "opt_k": 30, "opt_ph": 6.5, "opt_rain": 500},
        "Green Gram": {"base": 1150, "opt_moist": 22, "opt_temp": 29, "opt_n": 30, "opt_p": 45, "opt_k": 30, "opt_ph": 6.7, "opt_rain": 460},
        "Soybean": {"base": 2400, "opt_moist": 28, "opt_temp": 27, "opt_n": 50, "opt_p": 60, "opt_k": 50, "opt_ph": 6.5, "opt_rain": 680},
        "Groundnut": {"base": 2100, "opt_moist": 22, "opt_temp": 28, "opt_n": 40, "opt_p": 55, "opt_k": 45, "opt_ph": 6.3, "opt_rain": 580},
        "Mustard": {"base": 1750, "opt_moist": 20, "opt_temp": 19, "opt_n": 75, "opt_p": 45, "opt_k": 35, "opt_ph": 6.7, "opt_rain": 340},
        "Cotton": {"base": 2300, "opt_moist": 24, "opt_temp": 31, "opt_n": 120, "opt_p": 50, "opt_k": 50, "opt_ph": 7.0, "opt_rain": 620},
        "Sugarcane": {"base": 72000, "opt_moist": 38, "opt_temp": 30, "opt_n": 220, "opt_p": 80, "opt_k": 110, "opt_ph": 6.6, "opt_rain": 1400},
        "Sunflower": {"base": 1800, "opt_moist": 22, "opt_temp": 26, "opt_n": 80, "opt_p": 50, "opt_k": 40, "opt_ph": 6.8, "opt_rain": 520},
        "Potato": {"base": 24000, "opt_moist": 32, "opt_temp": 20, "opt_n": 150, "opt_p": 90, "opt_k": 120, "opt_ph": 6.0, "opt_rain": 550},
        "Tomato": {"base": 32000, "opt_moist": 30, "opt_temp": 25, "opt_n": 140, "opt_p": 80, "opt_k": 100, "opt_ph": 6.4, "opt_rain": 600},
        "Onion": {"base": 18500, "opt_moist": 25, "opt_temp": 23, "opt_n": 110, "opt_p": 60, "opt_k": 80, "opt_ph": 6.7, "opt_rain": 480}
    }

    # Universal soil texture suitability matrix
    soil_multipliers_general = {
        "Loamy": 1.10,
        "Sandy Loam": 1.05,
        "Clay": 0.98,
        "Sandy": 0.85
    }

    crops = list(crop_specs.keys())
    soils = ["Clay", "Loamy", "Sandy", "Sandy Loam"]
    records = []

    for _ in range(n_samples):
        crop = np.random.choice(crops)
        soil = np.random.choice(soils)
        spec = crop_specs[crop]

        moisture = np.random.uniform(8, 50)
        n = np.random.uniform(15, 280)
        p = np.random.uniform(10, 120)
        k = np.random.uniform(10, 150)
        ph = np.random.uniform(4.8, 8.8)
        rainfall = np.random.uniform(150, 1600)
        temp = np.random.uniform(14, 38)
        area_ha = np.random.uniform(0.5, 25.0)
        gdd = np.random.uniform(1000, 2400)

        base = spec["base"]
        # Soil specific adjustments for certain crops
        if crop in ["Rice", "Cotton", "Sugarcane"] and soil == "Clay":
            s_mult = 1.14
        elif crop in ["Chickpea", "Groundnut", "Mustard", "Barley", "Millets"] and soil in ["Sandy Loam", "Sandy"]:
            s_mult = 1.12
        else:
            s_mult = soil_multipliers_general[soil]

        moist_diff = abs(moisture - spec["opt_moist"])
        moist_factor = max(0.55, 1.0 - (moist_diff * 0.022))

        temp_diff = abs(temp - spec["opt_temp"])
        temp_factor = max(0.60, 1.0 - (temp_diff * 0.025))

        n_factor = 1.0 - np.exp(-1.8 * (n / spec["opt_n"]))
        p_factor = 1.0 - np.exp(-1.8 * (p / spec["opt_p"]))
        k_factor = 1.0 - np.exp(-1.8 * (k / spec["opt_k"]))
        npk_factor = 0.5 * n_factor + 0.25 * p_factor + 0.25 * k_factor

        ph_factor = max(0.65, 1.0 - (abs(ph - spec["opt_ph"]) * 0.12))
        rain_diff = abs(rainfall - spec["opt_rain"])
        rain_factor = max(0.70, 1.0 - (rain_diff / spec["opt_rain"] * 0.25))

        total_yield = base * s_mult * moist_factor * temp_factor * (0.4 + 0.6 * npk_factor) * ph_factor * rain_factor
        total_yield = total_yield * np.random.normal(1.0, 0.04)
        total_yield = max(100.0, total_yield)

        records.append({
            "crop": crop,
            "soil_type": soil,
            "moisture_pct": round(float(moisture), 1),
            "nitrogen": round(float(n), 1),
            "phosphorus": round(float(p), 1),
            "potassium": round(float(k), 1),
            "ph": round(float(ph), 2),
            "rainfall": round(float(rainfall), 1),
            "temperature": round(float(temp), 1),
            "field_area_ha": round(float(area_ha), 2),
            "gdd": round(float(gdd), 1),
            "yield_kg_ha": round(float(total_yield), 1)
        })

    df_yield = pd.DataFrame(records)
    csv_file = os.path.join(DATASET_DIR, "synthetic_crop_yield.csv")
    df_yield.to_csv(csv_file, index=False)
    print(f"Generated {len(df_yield)} synthetic crop yield records covering {len(crops)} crops -> {csv_file}")

    le_crop = LabelEncoder()
    le_soil = LabelEncoder()
    df_yield["crop_code"] = le_crop.fit_transform(df_yield["crop"])
    df_yield["soil_code"] = le_soil.fit_transform(df_yield["soil_type"])

    feature_cols = [
        "crop_code", "soil_code", "moisture_pct", "nitrogen",
        "phosphorus", "potassium", "ph", "rainfall", "temperature",
        "field_area_ha", "gdd"
    ]
    X = df_yield[feature_cols]
    y = df_yield["yield_kg_ha"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.15, random_state=42)

    model = RandomForestRegressor(n_estimators=50, max_depth=12, n_jobs=-1, random_state=42)
    model.fit(X_train, y_train)

    score = model.score(X_test, y_test)
    y_pred = model.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    print(f"[SUCCESS] Crop Yield Regressor R2 Score: {score:.4f} | RMSE: {rmse:.1f} kg/ha")

    out_path = os.path.join(MODELS_DIR, "yield_model.pkl")
    with open(out_path, "wb") as f:
        pickle.dump({
            "model": model,
            "crop_encoder": le_crop,
            "soil_encoder": le_soil,
            "features": feature_cols,
            "crop_specs": crop_specs
        }, f)
    print(f"Saved trained Crop Yield model bundle to {out_path}")

    # Backward compatibility
    compat_path = os.path.join(MODELS_DIR, "yield_lgbm.pkl")
    with open(compat_path, "wb") as f:
        pickle.dump({
            "model": model,
            "crop_encoder": le_crop,
            "soil_encoder": le_soil,
            "features": feature_cols,
            "crop_specs": crop_specs
        }, f)

    return model


# =====================================================================
# 4. GENERATE DATASET & TRAIN CROP RECOMMENDER AI FOR ALL CROPS
# =====================================================================
def generate_and_train_crop_recommender(n_samples=10000):
    print("\n" + "="*60)
    print("4. TRAINING CROP RECOMMENDER AI CLASSIFIER")
    print("="*60)

    rules = [
        {"crop": "Rice", "moist": (34, 52), "rain": (850, 1600), "temp": (24, 36), "n": (110, 190), "p": (45, 85), "k": (45, 85), "ph": (5.5, 7.2), "soils": ["Clay", "Loamy"]},
        {"crop": "Wheat", "moist": (18, 30), "rain": (350, 750), "temp": (15, 25), "n": (80, 160), "p": (40, 70), "k": (30, 60), "ph": (6.0, 7.5), "soils": ["Loamy", "Sandy Loam", "Clay"]},
        {"crop": "Maize", "moist": (22, 36), "rain": (500, 950), "temp": (20, 32), "n": (100, 180), "p": (50, 80), "k": (40, 70), "ph": (5.8, 7.5), "soils": ["Loamy", "Sandy Loam"]},
        {"crop": "Barley", "moist": (16, 26), "rain": (300, 600), "temp": (14, 24), "n": (60, 110), "p": (30, 55), "k": (25, 50), "ph": (6.5, 7.8), "soils": ["Loamy", "Sandy Loam", "Sandy"]},
        {"crop": "Millets", "moist": (10, 22), "rain": (200, 500), "temp": (24, 38), "n": (40, 90), "p": (25, 45), "k": (20, 45), "ph": (6.0, 8.0), "soils": ["Sandy", "Sandy Loam", "Loamy"]},
        {"crop": "Chickpea", "moist": (12, 24), "rain": (250, 500), "temp": (16, 26), "n": (20, 60), "p": (40, 70), "k": (25, 45), "ph": (6.5, 8.0), "soils": ["Sandy Loam", "Sandy", "Loamy"]},
        {"crop": "Pigeon Pea", "moist": (16, 28), "rain": (400, 750), "temp": (22, 34), "n": (25, 65), "p": (45, 75), "k": (30, 55), "ph": (6.5, 7.8), "soils": ["Loamy", "Sandy Loam"]},
        {"crop": "Lentil", "moist": (14, 24), "rain": (250, 480), "temp": (14, 23), "n": (20, 50), "p": (35, 60), "k": (20, 40), "ph": (6.5, 7.7), "soils": ["Loamy", "Sandy Loam"]},
        {"crop": "Soybean", "moist": (22, 34), "rain": (550, 900), "temp": (22, 32), "n": (30, 70), "p": (45, 80), "k": (35, 65), "ph": (6.0, 7.5), "soils": ["Loamy", "Clay"]},
        {"crop": "Groundnut", "moist": (16, 26), "rain": (400, 750), "temp": (22, 32), "n": (25, 60), "p": (40, 70), "k": (30, 55), "ph": (6.0, 7.5), "soils": ["Sandy Loam", "Sandy"]},
        {"crop": "Cotton", "moist": (18, 30), "rain": (500, 850), "temp": (25, 36), "n": (90, 150), "p": (40, 65), "k": (35, 65), "ph": (6.5, 7.8), "soils": ["Clay", "Loamy"]},
        {"crop": "Sugarcane", "moist": (30, 48), "rain": (1000, 1800), "temp": (26, 36), "n": (160, 260), "p": (60, 100), "k": (80, 140), "ph": (6.0, 7.5), "soils": ["Loamy", "Clay"]},
        {"crop": "Mustard", "moist": (14, 25), "rain": (250, 450), "temp": (14, 24), "n": (50, 100), "p": (30, 60), "k": (25, 45), "ph": (6.2, 7.6), "soils": ["Loamy", "Sandy Loam", "Sandy"]},
        {"crop": "Potato", "moist": (26, 38), "rain": (400, 700), "temp": (15, 24), "n": (110, 180), "p": (60, 110), "k": (80, 140), "ph": (5.5, 6.8), "soils": ["Sandy Loam", "Loamy"]},
        {"crop": "Tomato", "moist": (24, 36), "rain": (450, 800), "temp": (20, 30), "n": (100, 160), "p": (50, 95), "k": (65, 120), "ph": (6.0, 7.2), "soils": ["Loamy", "Sandy Loam"]},
        {"crop": "Onion", "moist": (18, 30), "rain": (350, 650), "temp": (18, 28), "n": (80, 140), "p": (40, 75), "k": (50, 95), "ph": (6.0, 7.5), "soils": ["Loamy", "Sandy Loam"]}
    ]

    records = []
    per_crop = n_samples // len(rules)

    for rule in rules:
        c = rule["crop"]
        for _ in range(per_crop):
            soil = np.random.choice(rule["soils"])
            moisture = np.random.uniform(rule["moist"][0], rule["moist"][1])
            rain = np.random.uniform(rule["rain"][0], rule["rain"][1])
            temp = np.random.uniform(rule["temp"][0], rule["temp"][1])
            n = np.random.uniform(rule["n"][0], rule["n"][1])
            p = np.random.uniform(rule["p"][0], rule["p"][1])
            k = np.random.uniform(rule["k"][0], rule["k"][1])
            ph = np.random.uniform(rule["ph"][0], rule["ph"][1])

            records.append({
                "soil_type": soil,
                "moisture_pct": round(float(moisture), 1),
                "nitrogen": round(float(n), 1),
                "phosphorus": round(float(p), 1),
                "potassium": round(float(k), 1),
                "ph": round(float(ph), 2),
                "rainfall": round(float(rain), 1),
                "temperature": round(float(temp), 1),
                "recommended_crop": c
            })

    df_rec = pd.DataFrame(records)
    csv_file = os.path.join(DATASET_DIR, "synthetic_crop_recommendation.csv")
    df_rec.to_csv(csv_file, index=False)
    print(f"Generated {len(df_rec)} synthetic crop recommendation records -> {csv_file}")

    le_soil = LabelEncoder()
    df_rec["soil_code"] = le_soil.fit_transform(df_rec["soil_type"])

    feature_cols = [
        "soil_code", "moisture_pct", "nitrogen", "phosphorus",
        "potassium", "ph", "rainfall", "temperature"
    ]
    X = df_rec[feature_cols]
    y = df_rec["recommended_crop"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.15, random_state=42, stratify=y)

    model = RandomForestClassifier(n_estimators=100, max_depth=14, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"[SUCCESS] Crop Recommender Validation Accuracy: {acc*100:.2f}% across {len(rules)} crops")

    out_path = os.path.join(MODELS_DIR, "crop_recommender.pkl")
    with open(out_path, "wb") as f:
        pickle.dump({
            "model": model,
            "soil_encoder": le_soil,
            "features": feature_cols,
            "crops": list(model.classes_)
        }, f)
    print(f"Saved trained Crop Recommender bundle to {out_path}")

    return model


if __name__ == "__main__":
    print("\n" + "#"*70)
    print("# AgriAI Multi-Crop Dataset Generator & Model Trainer")
    print("#"*70)
    
    t0 = pd.Timestamp.now()
    generate_and_train_soil_classifier()
    generate_and_train_moisture_model()
    generate_and_train_yield_model()
    generate_and_train_crop_recommender()
    print(f"\n[DONE] All models successfully trained and exported! Elapsed: {(pd.Timestamp.now() - t0).total_seconds():.1f}s")
