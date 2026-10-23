# TASKS.md — Implementation Task List

**Project:** AgriAI Platform
**Format:** Phase → Task → Status

Status legend: `[ ]` = Not started | `[~]` = In progress | `[x]` = Done | `[!]` = Blocked

---

## PHASE 1 — Project Setup & Infrastructure

### 1.1 Repository & Tooling
- [x] Create GitHub repo / workspace layout
- [x] Set up `.gitignore` for Java, Python, Node, `.env` files
- [x] Create folder structure: `frontend/`, `backend/`, `ml-service/`
- [x] Write `docker-compose.yml` with PostgreSQL, Redis, MinIO services
- [x] Create `.env.example` files for all three services

### 1.2 Database Setup
- [x] Define PostgreSQL schema and migrations with Flyway
- [x] Write `V1__init_schema.sql` (users, farms, fields, soil_samples, predictions, crop_catalog)
- [x] Seed crop catalog with common crops (Wheat, Rice, Maize, Chickpea, Cotton, Mustard)

### 1.3 MinIO Setup
- [x] Configured MinIO with auto-provisioning container (`minio-init`)
- [x] Buckets provisioned: `soil-images-raw`, `soil-images-processed`, `gradcam-outputs`

### 1.4 Redis Setup
- [x] Redis service configured with healthchecks in docker-compose.yml
- [x] Added Spring Cache and Redis config template in backend application.yml

---

## PHASE 2 — Backend (Spring Boot)

### 2.1 Auth Module
- [ ] Add dependencies: spring-security, jjwt, spring-data-jpa, lombok, validation
- [ ] Create `User` entity with fields: id, full_name, email, password_hash, phone, role, is_active
- [ ] Create `UserRepository` (JPA)
- [ ] Implement `JwtUtil` class: generate, validate, extract claims
- [ ] Implement `POST /api/auth/register` endpoint
- [ ] Implement `POST /api/auth/login` endpoint (returns access + refresh tokens)
- [ ] Implement `POST /api/auth/refresh` endpoint
- [ ] Implement `POST /api/auth/logout` (invalidate refresh token)
- [ ] Implement `GET /api/auth/me` endpoint (requires auth)
- [ ] Add global `@ControllerAdvice` for exception handling
- [ ] Add request logging filter (method, path, response time, status)

### 2.2 Farm Module
- [ ] Create `Farm` entity: id, user_id, name, total_area_ha, state, district, created_at
- [ ] Create `FarmRepository`, `FarmService`, `FarmController`
- [ ] `POST /api/farms` — create farm
- [ ] `GET /api/farms` — list farms for current user
- [ ] `GET /api/farms/{id}` — get single farm
- [ ] `PUT /api/farms/{id}` — update farm
- [ ] `DELETE /api/farms/{id}` — soft delete

### 2.3 Field Module
- [ ] Create `Field` entity: id, farm_id, name, area_ha, current_crop, sowing_date
- [ ] CRUD: `POST/GET/PUT/DELETE /api/farms/{farmId}/fields`
- [ ] `GET /api/fields/{id}` — includes latest prediction summary

### 2.4 Soil Sample Module
- [ ] Create `SoilSample` entity
- [ ] `GET /api/soil/upload-url` — returns MinIO presigned URL
- [ ] `POST /api/soil/analyze` — triggers ML pipeline, returns prediction
- [ ] `GET /api/soil/samples/{id}` — get sample details + prediction
- [ ] MinIO integration: Java SDK to generate presigned PUT URLs

### 2.5 ML Orchestration (calls FastAPI)
- [ ] Add `RestTemplate` / `WebClient` bean for internal HTTP calls
- [ ] `MlServiceClient.java` — typed HTTP client for FastAPI endpoints
- [ ] Call `/classify-soil` from FastAPI, handle response
- [ ] Call `/estimate-moisture` from FastAPI, handle response
- [ ] Call `/predict-yield` from FastAPI, handle response
- [ ] Call `/recommend-crop` from FastAPI, handle response
- [ ] Save all results to `predictions` table
- [ ] Generate recommendations records from ML results

### 2.6 Weather Module
- [ ] Add `OpenWeatherMapClient.java` using RestTemplate
- [ ] Fetch current + 7-day forecast for a given lat/lng
- [ ] Cache weather responses in Redis for 30 minutes
- [ ] `GET /api/weather?lat={lat}&lng={lng}` endpoint
- [ ] Store daily weather snapshot in `weather_data` table per field

### 2.7 Dashboard / Analytics APIs
- [ ] `GET /api/dashboard/summary` — farmer's KPI summary
- [ ] `GET /api/dashboard/predictions/history?fieldId={id}` — prediction timeline
- [ ] `GET /api/admin/stats` — system-wide stats (admin role only)

---

## PHASE 3 — ML Service (FastAPI + Python)

### 3.1 Dataset Collection & Preparation
- [ ] Download SoilNet dataset from Kaggle (~11,000 images, 6 classes)
- [ ] Download Crop Recommendation dataset from Kaggle
- [ ] Download ERA5 weather data for 5 years, 2 Indian regions
- [ ] Download USDA NASS yield data (or Indian crop production dataset)
- [ ] Run EDA notebook: class distribution, missing values, image quality check

### 3.2 Image Preprocessing Pipeline
- [ ] `image_processor.py`: resize to 224×224, CLAHE, normalize (ImageNet stats)
- [ ] Blur detection function (Laplacian variance)
- [ ] Segmentation: GrabCut to isolate soil region from background
- [ ] Data augmentation script: random flip, rotation, color jitter, cutout
- [ ] Save preprocessed dataset to disk

### 3.3 Soil Classification Model
- [ ] Set up training script: fine-tune EfficientNetV2-B3 on SoilNet
- [ ] Train for 50 epochs, Adam optimizer, lr=1e-4, cosine annealing
- [ ] Evaluate: confusion matrix, per-class F1, overall accuracy
- [ ] Target: ≥ 90% validation accuracy
- [ ] Export trained model to ONNX format
- [ ] Implement Grad-CAM for inference: save heatmap overlay to MinIO

### 3.4 Moisture Estimation Model
- [ ] Feature engineering: extract color stats + GLCM texture from images
- [ ] Build training dataset: pair soil images with SMAP moisture ground truth (or proxy labels)
- [ ] Train CNN-Regression model (EfficientNet backbone + regression head)
- [ ] Train XGBoost on extracted features as ensemble corrector
- [ ] Evaluate: MAE, RMSE on held-out validation set
- [ ] Target: MAE < 4% VWC
- [ ] Export to ONNX + pickle

### 3.5 Yield Prediction Model
- [ ] Feature engineering: NPK interaction terms, GDD (Growing Degree Days) from weather
- [ ] Train LightGBM on: soil_type, moisture, NPK, pH, temp, rainfall, crop_name
- [ ] Hyperparameter tuning: Optuna (50 trials)
- [ ] Evaluate: R², RMSE per crop type
- [ ] Target: R² ≥ 0.87
- [ ] Compute SHAP values for top features
- [ ] Save model as `.pkl`

### 3.6 Crop Recommendation Model
- [ ] Train Random Forest on crop recommendation dataset (N, P, K, temp, humidity, pH, rainfall → crop)
- [ ] Evaluate: accuracy, per-class F1
- [ ] Target: ≥ 95% accuracy
- [ ] Save model as `.pkl`

### 3.7 FastAPI Service Setup
- [ ] FastAPI app initialization with CORS, startup model loading
- [ ] `POST /classify-soil` — accepts image URL, returns classification + Grad-CAM URL
- [ ] `POST /estimate-moisture` — returns moisture %, category
- [ ] `POST /predict-yield` — accepts soil+weather+NPK data, returns yield + SHAP
- [ ] `POST /recommend-crop` — returns top 3 crops with scores
- [ ] Health check: `GET /health`
- [ ] Pydantic schemas for all request/response models
- [ ] Error handling: return structured errors, not raw Python tracebacks
- [ ] Dockerize FastAPI service

---

## PHASE 4 — Frontend (Next.js)

### 4.1 Project Setup
- [ ] `npx create-next-app@latest frontend --typescript --tailwind --app`
- [ ] Install shadcn/ui: `npx shadcn-ui@latest init`
- [ ] Add required shadcn components: button, card, badge, input, label, toast, table, tabs, dialog, progress, select
- [ ] Install: `axios`, `@tanstack/react-query`, `zustand`, `recharts`, `leaflet`, `react-leaflet`
- [ ] Add Google Fonts: Inter + Outfit in `layout.tsx`
- [ ] Set up global CSS variables from DESIGN.md color system
- [ ] Create `lib/api.ts` with axios instance + interceptors (JWT attach, 401 redirect)
- [ ] Create auth Zustand store

### 4.2 Auth Pages
- [ ] `/login` page with form validation
- [ ] `/register` page with form validation
- [ ] JWT storage in `httpOnly` cookie (or localStorage for simplicity)
- [ ] Protected route wrapper: redirect to `/login` if no valid token
- [ ] Logout clears token and redirects

### 4.3 Layout & Navigation
- [ ] App shell: Sidebar (desktop) + Bottom Nav (mobile)
- [ ] Sidebar items: Dashboard, Analyze, Fields, Weather, Admin (role-gated)
- [ ] Responsive breakpoints as defined in DESIGN.md

### 4.4 Dashboard Page (`/dashboard`)
- [ ] Fetch farmer summary from `GET /api/dashboard/summary`
- [ ] Last analysis card
- [ ] Weather today card (mini widget)
- [ ] Active fields count card
- [ ] Last crop recommendation card
- [ ] Moisture status per field (mini gauge per field)
- [ ] Skeleton loaders for all cards

### 4.5 Soil Analysis Page (`/analyze`)
- [ ] File upload zone (drag & drop + click to select)
- [ ] Client-side validation: format check, size check, basic blur check
- [ ] Image preview after selection
- [ ] Upload flow: get presigned URL → upload to MinIO → trigger analysis
- [ ] Processing steps indicator (animated)
- [ ] Results display: soil type badge, moisture gauge, yield card, recommendations list
- [ ] Grad-CAM viewer with toggle between original and heatmap
- [ ] SHAP horizontal bar chart

### 4.6 Field Management (`/fields`)
- [ ] List view of all fields
- [ ] Add field modal with name, area, crop, sowing date, location
- [ ] Click field → prediction history table (paginated)
- [ ] Leaflet map showing field location pin

### 4.7 Weather Page (`/weather`)
- [ ] 7-day forecast cards
- [ ] 30-day temperature + rainfall line chart (Recharts)
- [ ] Agricultural advisory banners

### 4.8 Admin Dashboard (`/admin`)
- [ ] User list table with search + role filter
- [ ] System stats: total users, total predictions, predictions today
- [ ] Model accuracy table (manually updated)
- [ ] Admin-only route guard

---

## PHASE 5 — Integration & Testing

- [ ] End-to-end test: register → upload image → get prediction → view on dashboard
- [ ] Load test FastAPI inference endpoint: 20 concurrent requests
- [ ] Test Redis caching: same image twice should return cached result
- [ ] Test MinIO presigned URL upload from browser
- [ ] Test JWT expiry + refresh flow
- [ ] Test role-based access: farmer cannot access `/admin`
- [ ] Cross-browser test: Chrome, Firefox, Safari

---

## PHASE 6 — Deployment

- [ ] Write `Dockerfile` for Spring Boot (multi-stage build)
- [ ] Write `Dockerfile` for FastAPI
- [ ] Write `Dockerfile` for Next.js
- [ ] Full `docker-compose.yml` for all 6 services
- [ ] Write startup script: check MinIO buckets exist, run Flyway migrations
- [ ] Document deployment steps in README.md
- [ ] Deploy to any VPS or local server and verify all features work

---

## PHASE 7 — Research Paper

- [ ] Write methodology section (architecture + model details)
- [ ] Generate all evaluation tables (accuracy, R², MAE, RMSE)
- [ ] Create Grad-CAM figure samples for paper
- [ ] Create SHAP figure for paper
- [ ] Write ablation study section
- [ ] Draft full paper using IEEE LaTeX template
- [ ] Internal review and revision
- [ ] Submit to target journal
