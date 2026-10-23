# ARCHITECTURE.md — System Architecture

**Project:** AgriAI Platform
**Version:** 1.0

---

## 1. High-Level Architecture

```
Browser (Next.js)
      │
      │ HTTPS REST
      ▼
Spring Boot (Port 8080)       ← handles auth, user data, farm CRUD
      │
      ├──→ PostgreSQL          ← all structured data lives here
      ├──→ Redis               ← cache inference results (10min TTL)
      ├──→ MinIO               ← soil image file storage
      │
      │ HTTP (internal)
      ▼
FastAPI ML Service (Port 8000) ← all AI/ML inference lives here
      │
      ├──→ EfficientNetV2-B3 model  (soil classification)
      ├──→ CNN-Regression model     (moisture estimation)
      ├──→ LightGBM model          (yield prediction)
      └──→ Random Forest model      (crop recommendation)

External APIs (called by Spring Boot):
      └──→ OpenWeatherMap API       (weather data)
```

---

## 2. Service Breakdown

### 2.1 Frontend — Next.js (Port 3000)
- **Language:** TypeScript
- **Styling:** Tailwind CSS + shadcn/ui
- **State:** React Query (server state) + Zustand (UI state)
- **Maps:** Leaflet.js for field location picking
- **Charts:** Recharts for analytics
- **Calls:** Only talks to Spring Boot. Never directly to FastAPI.

### 2.2 Backend — Spring Boot (Port 8080)
- **Language:** Java 21
- **Responsibility:**
  - JWT authentication and authorization
  - User, Farm, Field, SoilSample CRUD
  - Orchestrates ML calls (calls FastAPI internally)
  - Weather API calls (OpenWeatherMap)
  - Stores prediction results in PostgreSQL
  - Serves images from MinIO via signed URLs
- **Key Libraries:** Spring Security, Spring Data JPA, Flyway, Lombok, MapStruct

### 2.3 ML Service — FastAPI (Port 8000)
- **Language:** Python 3.11
- **Responsibility:** All model inference. Stateless.
- **Endpoints:**
  - `POST /classify-soil` → runs EfficientNetV2-B3
  - `POST /estimate-moisture` → runs CNN-regression + XGBoost
  - `POST /predict-yield` → runs LightGBM
  - `POST /recommend-crop` → runs Random Forest
- **Models served:** Loaded once at startup from `/models/` directory as ONNX or `.pkl` files
- **Does NOT handle:** auth, user data, file storage — that's Spring Boot's job

### 2.4 Database — PostgreSQL (Port 5432)
- **Why PostgreSQL:** Free, reliable, handles JSON columns (for SHAP values), supports spatial queries via PostGIS extension, works great with Spring Data JPA.
- **What lives here:** users, farms, fields, soil_samples, predictions, recommendations, weather_cache, crop_catalog
- **Migrations:** Flyway (version-controlled SQL scripts in `resources/db/migration/`)

### 2.5 Cache — Redis (Port 6379)
- **Why:** ML inference takes 2–5 seconds. If the same image is submitted twice (same hash), return cached result instantly.
- **What is cached:**
  - Inference results keyed by `sha256(image_bytes)` — TTL: 10 minutes
  - Weather API responses keyed by `lat_lng_date` — TTL: 30 minutes
- **What is NOT cached:** User data, farm data (no need)

### 2.6 Object Storage — MinIO (Port 9000)
- **Why MinIO:** Free, runs locally, S3-compatible API. When you move to production you can swap to AWS S3 with zero code change.
- **Buckets:**
  - `soil-images-raw` — original uploaded images
  - `soil-images-processed` — preprocessed images (after OpenCV)
  - `gradcam-outputs` — Grad-CAM heatmap images
- **Access:** Spring Boot generates presigned URLs for frontend to upload directly. Avoids routing large files through Spring Boot.

---

## 3. Request Flow — Soil Analysis (Most Important Flow)

```
1. Farmer clicks "Upload Image" on Next.js UI
2. Next.js → POST /api/soil/upload-url to Spring Boot
3. Spring Boot → asks MinIO for a presigned upload URL → returns it to Next.js
4. Next.js uploads image DIRECTLY to MinIO (bypasses Spring Boot)
5. Next.js → POST /api/soil/analyze {sample_id} to Spring Boot
6. Spring Boot → checks Redis: is result cached? NO
7. Spring Boot → POST http://ml-service:8000/classify-soil {image_url}
8. FastAPI downloads image from MinIO, runs model, returns result JSON
9. Spring Boot → saves result to PostgreSQL predictions table
10. Spring Boot → caches result in Redis (key = image hash, TTL 10min)
11. Spring Boot → returns result to Next.js
12. Next.js renders soil type, moisture %, Grad-CAM heatmap, recommendations
```

---

## 4. Database — What Goes Where

| Data | Storage | Why |
|---|---|---|
| Users, farms, fields | PostgreSQL | Relational, needs joins |
| Soil samples metadata | PostgreSQL | Linked to fields and predictions |
| Predictions, SHAP values | PostgreSQL (JSONB column) | Structured + flexible JSON |
| Recommendations | PostgreSQL | Relational to predictions |
| Soil images (raw + processed) | MinIO | Binary files, not DB |
| Grad-CAM images | MinIO | Binary files |
| Inference results cache | Redis | Temporary, speed |
| Weather cache | Redis | Temporary, speed |
| Crop catalog (static) | PostgreSQL | Seeded once at startup |

---

## 5. Environment Setup (Local Dev)

```yaml
# docker-compose.yml structure
services:
  postgres:     # port 5432
  redis:        # port 6379
  minio:        # port 9000 (API), 9001 (console)
  spring-boot:  # port 8080
  fastapi:      # port 8000
  nextjs:       # port 3000
```

Run everything locally with one command:
```bash
docker-compose up -d
```

---

## 6. Folder Structure

```
MiniProject P-2/
├── frontend/              # Next.js app
│   ├── app/
│   ├── components/
│   ├── lib/
│   └── package.json
│
├── backend/               # Spring Boot app
│   ├── src/main/java/com/agripredict/
│   │   ├── auth/
│   │   ├── farm/
│   │   ├── soil/
│   │   ├── prediction/
│   │   └── weather/
│   └── pom.xml
│
├── ml-service/            # FastAPI app
│   ├── models/            # trained model files (.onnx, .pkl)
│   ├── routers/
│   ├── utils/
│   ├── main.py
│   └── requirements.txt
│
├── docker-compose.yml
├── PRD.md
├── ARCHITECTURE.md
├── DESIGN.md
├── RULES.md
├── TASKS.md
├── DECISIONS.md
├── MEMORY.md
└── TEST_PLAN.md
```
