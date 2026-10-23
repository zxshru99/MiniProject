# MEMORY.md — Project Knowledge Base & Running Notes

**Project:** AgriAI Platform
**Purpose:** Living document. Updated as the project progresses. Captures things learned, gotchas, environment quirks, API behaviors, and anything that will save future-you hours of debugging.

---

## 1. Environment & Setup Notes

### PostgreSQL
- Default superuser: `postgres` / `postgres` (local Docker)
- Project DB: `agripredict`, user: `agriuser`, password: set in `.env`
- To connect manually: `psql -h localhost -U agriuser -d agripredict`
- PostGIS extension: `CREATE EXTENSION postgis;` — run once after DB creation
- UUID generation: uses `gen_random_uuid()` — available in PostgreSQL 13+

### MinIO
- Console URL: `http://localhost:9001` (admin UI)
- API URL: `http://localhost:9000`
- Default credentials: `minioadmin` / `minioadmin`
- Buckets must exist before app starts — create them in the startup script or MinIO console
- Presigned URL expiry: set to 15 minutes for upload, 1 hour for view

### Redis
- No auth in local dev (fine for local only)
- Use `redis-cli monitor` to watch what's being cached in real time
- Flush all keys: `redis-cli FLUSHALL` — use only in dev/testing

### OpenWeatherMap API
- Base URL: `https://api.openweathermap.org/data/3.0/onecall`
- Required params: `lat`, `lon`, `appid`, `units=metric`, `exclude=minutely,alerts`
- Free tier limit: 1,000 calls/day — cache aggressively (30 min per location)
- API key stored in `OPENWEATHER_API_KEY` env variable

---

## 2. ML Model Notes

### Soil Classification — EfficientNetV2-B3
- Training dataset: SoilNet — 11,000 images, 6 classes
- Input size: 224×224 RGB, normalized with ImageNet stats
- Class labels (in order): `["chalky", "clayey", "loamy", "peaty", "sandy", "silty"]`
- ONNX export command:
  ```python
  torch.onnx.export(model, dummy_input, "soil_classifier.onnx", opset_version=17)
  ```
- Grad-CAM: use `pytorch-grad-cam` library, layer = `model.features[-1]`
- Common failure: blurry images get misclassified as sandy (both lack texture detail)
- Augmentation that helped: `ColorJitter(brightness=0.3, contrast=0.3)`, random crop

### Moisture Estimation — CNN-Regression + XGBoost
- Wet soil appears darker and more homogeneous in texture
- Dry soil has lighter color and more visible texture variation
- XGBoost corrector uses: mean_R, mean_G, mean_B, contrast_GLCM, energy_GLCM, LBP histogram (64 bins)
- Biggest challenge: same soil type at different times of day looks different (lighting)
- Mitigation: CLAHE preprocessing reduces lighting sensitivity significantly

### Yield Prediction — LightGBM
- Key features by SHAP importance: soil_moisture, N_level, rainfall_30d, temperature_avg, crop_name
- Categorical features: `soil_type`, `crop_name`, `season` — passed as `category` dtype in pandas
- Model expects all weather features as 30-day averages (not raw daily values)
- GDD (Growing Degree Days): `GDD = max(0, (T_max + T_min)/2 - T_base)` where T_base = 10°C for most crops
- Prediction range: set confidence interval as ± 1.5 × RMSE from validation set

### Crop Recommendation — Random Forest
- Dataset: Kaggle "Crop Recommendation Dataset" — 22 crops, features: N, P, K, temperature, humidity, pH, rainfall
- Labels: apple, banana, blackgram, chickpea, coconut, coffee, cotton, grapes, jute, kidneybeans, lentil, maize, mango, motherbeans, mungbean, muskmelon, orange, papaya, pigeonpeas, pomegranate, rice, watermelon
- Achieved 99.1% accuracy on validation — it's an easy dataset (very clean, well-separated classes)
- For production: combine with soil type compatibility filter (e.g., rice not recommended for sandy soil regardless of NPK)

---

## 3. Known Issues & Gotchas

### Backend (Spring Boot)
- **Issue:** Flyway fails on first run if PostgreSQL is not fully ready yet in Docker.
  **Fix:** Add `depends_on` with health check in docker-compose, or add retry logic in startup.

- **Issue:** MinIO Java SDK presigned URLs use `http://minio:9000` (Docker internal hostname) but the browser needs `http://localhost:9000`.
  **Fix:** Generate the presigned URL using internal hostname, then replace host in the URL before returning to frontend.

- **Issue:** CORS errors when frontend on port 3000 calls Spring Boot on port 8080.
  **Fix:** Add `@CrossOrigin` or global CORS config in `SecurityConfig.java`:
  ```java
  config.setAllowedOrigins(List.of("http://localhost:3000"));
  ```

### ML Service (FastAPI)
- **Issue:** First request after startup is slow (model loaded but not warmed up).
  **Fix:** Run a dummy inference on a blank image during startup to warm up the ONNX runtime.

- **Issue:** `onnxruntime` and `torch` installed together cause dependency conflicts.
  **Fix:** Install `onnxruntime` (CPU) only in production. Use `torch` only for training. Export to ONNX after training, then use only `onnxruntime` for inference.

- **Issue:** OpenCV (`cv2`) cannot be imported in some Docker environments.
  **Fix:** Use `opencv-python-headless` in `requirements.txt` (not `opencv-python`).

### Frontend (Next.js)
- **Issue:** Leaflet.js throws "window is not defined" on Next.js server-side rendering.
  **Fix:** Dynamic import with `{ ssr: false }`:
  ```tsx
  const MapComponent = dynamic(() => import('@/components/Map'), { ssr: false });
  ```

- **Issue:** Large images cause slow uploads through the browser.
  **Fix:** Client-side resize to max 1920px before upload using `canvas.toBlob()`.

---

## 4. Useful Commands

### Docker
```bash
# Start all services
docker-compose up -d

# Check logs
docker-compose logs -f spring-boot
docker-compose logs -f fastapi

# Restart single service
docker-compose restart spring-boot

# Stop everything and remove volumes (DELETES ALL DATA)
docker-compose down -v
```

### Database
```bash
# Connect to PostgreSQL
docker exec -it agripredict-postgres psql -U agriuser -d agripredict

# Check Flyway migration status
SELECT * FROM flyway_schema_history ORDER BY installed_rank;

# Quick table row counts
SELECT relname, n_live_tup FROM pg_stat_user_tables ORDER BY n_live_tup DESC;
```

### ML Training
```bash
# Activate virtual environment
cd ml-service && source venv/bin/activate  # Linux/Mac
cd ml-service && venv\Scripts\activate     # Windows

# Run soil classifier training
python training/train_soil_classifier.py --epochs 50 --batch-size 32

# Export to ONNX
python training/export_onnx.py --model-path models/soil_classifier.pth

# Test inference
python -c "from services.model_loader import load_models; m = load_models(); print('Models loaded OK')"
```

### Redis
```bash
# List all keys
redis-cli KEYS "*"

# Check a specific cache entry
redis-cli GET "inference:sha256:abc123..."

# Delete a specific key
redis-cli DEL "weather:28.6_77.2_2026-10-18"
```

---

## 5. API Keys & Credentials (Dev Only)

> **NEVER commit actual values. This section lists what keys are needed and where to get them.**

| Key | Service | Where to Set | How to Get |
|---|---|---|---|
| `OPENWEATHER_API_KEY` | OpenWeatherMap | `.env` (Spring Boot) | openweathermap.org → free account |
| `MINIO_ACCESS_KEY` | MinIO | `.env` (both services) | Set during MinIO setup (default: minioadmin) |
| `JWT_SECRET` | JWT signing | `.env` (Spring Boot) | Generate: `openssl rand -hex 32` |
| `DB_PASSWORD` | PostgreSQL | `.env` (Spring Boot) | Set during Docker setup |

---

## 6. Research Paper Notes

### Metrics to Report in Paper
- Soil Classification: Accuracy, F1 (macro), Cohen's Kappa — per class and overall
- Moisture Estimation: MAE (%), RMSE (%), R²
- Yield Prediction: R², RMSE (kg/ha), MAE (kg/ha) — per crop and overall
- Crop Recommendation: Accuracy, F1 (macro)
- System Performance: inference latency P50/P95/P99

### Figures Needed for Paper
1. System architecture diagram (MSAIF-Net)
2. Image preprocessing pipeline flowchart
3. Confusion matrix — soil classification
4. Scatter plot — predicted vs actual moisture
5. Scatter plot — predicted vs actual yield (per crop)
6. SHAP summary plot (beeswarm or bar)
7. Grad-CAM sample images (3–4 examples showing model attention)
8. Ablation study table/chart
9. Comparison table (proposed vs baselines)

### Target Journal
- **Primary:** Computers and Electronics in Agriculture (Elsevier) — IF: 8.3
- **Backup:** IEEE Access — IF: 3.9
- **Template:** IEEE LaTeX template (for IEEE Access)

---

## 7. Progress Log

| Date | Update |
|---|---|
| Oct 2026 | Project started. All 8 documentation files created. |
| | ← Add entries as you make progress |
