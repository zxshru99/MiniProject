# IMPLEMENTATION_PLAN.md — Strict Implementation Blueprint

**Project Topic:** "Predicting Yield, Soil Moisture, and Weather Using Image Processing"  
**Scope:** Strictly Soil Moisture, Crop Yield, and Weather Analysis/Prediction driven by Image Processing & Multimodal ML  
**Version:** 1.0  
**Date:** October 2026  

---

## 1. REQUIREMENT SUMMARY

### 1.1 Key Objectives
1. **Soil Moisture Estimation via Image Processing:** Extract spectral, textural, and chromatic features from surface soil imagery to quantify volumetric soil moisture (% VWC) and classify moisture state (Dry, Moderate, Wet, Saturated).
2. **Crop Yield Prediction:** Predict expected crop yield (kg/ha) using fused inputs: soil characteristics derived from image processing + historical/forecasted meteorological variables + agronomic parameters.
3. **Weather Impact & Prediction:** Ingest historical meteorological time-series and real-time atmospheric data to forecast local micro-weather trends (precipitation, temperature, evapotranspiration) and evaluate their quantified impact on moisture depletion and yield.

### 1.2 Core Functionality
- **Image Processing Engine:** Ingests field soil images, executes quality validation (blur/exposure gating), segments soil boundaries, extracts color/texture descriptors (LAB/HSV color moments, GLCM, LBP), and generates deep spatial feature embeddings.
- **Multimodal Soil Moisture Estimator:** Infers volumetric water content (% VWC) using a dual-branch architecture combining deep convolutional visual features with empirical textural indicators.
- **Weather Analysis & Time-Series Forecaster:** Processes sequential meteorological data (ERA5 / OpenWeatherMap) via Bi-LSTM to produce multi-day weather outlooks and calculate agrometeorological indices: Growing Degree Days (GDD), Reference Evapotranspiration ($ET_0$), and Standardized Precipitation Evapotranspiration Index (SPEI).
- **Multimodal Yield Prediction Engine:** Merges image-derived soil features + weather sequential embeddings + crop parameters into a gradient-boosted regression pipeline (LightGBM/XGBoost) to output predicted yield with confidence intervals.
- **Explainability Layer:** Employs Grad-CAM on convolutional feature maps to localize moisture and soil indicators, and TreeSHAP on yield models to rank feature contributions.

### 1.3 Technical Constraints
- **Zero Sensor Dependency:** All soil physical properties must be inferred from standard RGB/NIR photography without requiring in-situ capacitance probes or laboratory spectrophotometry.
- **Inference Latency:** Total end-to-end model execution pipeline (Image Processing + Weather Inference + Yield Prediction) must complete in $\le 4.5\text{ seconds}$ on CPU-only edge/server instances.
- **Storage & Bandwidth Optimization:** High-resolution field photos must undergo client-side image compression and spatial downsampling to $\le 1024\times1024$ before transit to preserve bandwidth in low-connectivity rural zones.
- **Data Integrity & Consistency:** Temporal alignment between the date of soil capture, 30-day antecedent meteorological history, and harvest dates must be synchronized to prevent temporal look-ahead leakage.

---

## 2. DATASET ANALYSIS

### 2.1 Publicly Available Datasets Strictly Aligned with Scope

| Domain | Dataset Name | Source & Public Access Link | Access Type | Exact Contents & Features | Why It Fits |
|---|---|---|---|---|---|
| **Image Processing & Soil Classification** | **Soil Types Dataset** | [Kaggle - prasanshasatpathy/soil-types](https://www.kaggle.com/datasets/prasanshasatpathy/soil-types) | **100% Public (1-click Kaggle)** | ~1,600 ground-level RGB images in 4 folders (`Clay`, `Loamy`, `Sandy`, `Sandy Loam`) | Perfect for training the CNN/EfficientNet backbone without any data cleaning needed. Folders are already organized for `ImageFolder`. |
| **Soil Moisture Estimation (Images)** | **Soil Moisture Dataset** | [Mendeley Data - Soil Moisture](https://data.mendeley.com/datasets/kghv73t7pd/1) | **100% Open Access (Direct Download)** | RGB soil surface photos categorized by moisture stage (`Dry`, `Moderate`, `Wet`) based on drying intervals | Solves the visual moisture estimation problem directly from optical images without hardware sensors. |
| **Crop Yield Prediction** | **Crop Production in India (APY)** | [Kaggle - abhinand05/crop-production-in-india](https://www.kaggle.com/datasets/abhinand05/crop-production-in-india) | **100% Public (1-click Kaggle CSV)** | 246,000+ tabular records: State, District, Crop, Season, Area, Production, Yield (kg/ha) | Complete historical ground truth for training the LightGBM yield prediction model. |
| **Real-Time & Forecast Weather** | **OpenWeatherMap One Call 3.0** | [OpenWeatherMap API](https://openweathermap.org/api/one-call-3) | **Free Public API (1,000 calls/day)** | Current weather, 48-hour hourly forecast, 8-day daily forecast (Temp, Rain, Humidity, Wind) | Live weather for field locations; cached in Redis so you never hit the rate limit. |
| **Historical Weather (Optional Deep Baseline)** | **NASA POWER Agroclimatology** | [NASA POWER Data Access](https://power.larc.nasa.gov/data-access-viewer/) | **100% Free Public API (No key required)** | Daily Solar Radiation, Min/Max Temp, Precipitation, RH by Lat/Long from 1981–present | Ideal for calculating historical Growing Degree Days ($GDD$) and $ET_0$ for any farm coordinates. |

### 2.2 Recommended Dataset Combination & Justification

**Primary Production Pipeline Stack:**
$$\mathbf{\text{Soil Types (Kaggle)}} + \mathbf{\text{Soil Moisture Images (Mendeley)}} + \mathbf{\text{OpenWeatherMap / NASA POWER}} + \mathbf{\text{Crop Production APY (Kaggle)}}$$

**Justification:**
1. **Soil Types Dataset (Kaggle):** Pre-organized into 4 clean texture folders (`Clay`, `Loamy`, `Sandy`, `Sandy Loam`) enabling immediate PyTorch `ImageFolder` training for EfficientNetV2 without messy scraping or unzipping issues.
2. **Soil Moisture Dataset (Mendeley):** Provides direct optical image pairs categorized into `Dry`, `Moderate`, and `Wet` soil surface states, avoiding satellite calibration complexities while directly supporting image-based moisture inference.
3. **OpenWeatherMap One Call 3.0 & NASA POWER:** Supplies real-time micro-weather (current + 7-day forecast) with 1,000 free API calls/day, alongside zero-friction historical agrometeorological indicators ($GDD, ET_0$).
4. **Crop Production APY (Kaggle):** Supplies 246,000+ localized district-level yield records to train the LightGBM yield regression model across seasons and crops.

---

## 3. TECHNOLOGY STACK

```
┌────────────────────────────────────────────────────────────────────────┐
│                          PRESENTATION LAYER                            │
│  Next.js 14 (App Router) + TypeScript + Tailwind CSS + shadcn/ui       │
│  State: TanStack Query v5 + Zustand │ Charts: Recharts + D3.js         │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ HTTPS / REST (JSON)
┌───────────────────────────────────▼────────────────────────────────────┐
│                       ENTERPRISE GATEWAY & BACKEND                     │
│  Spring Boot 3.3 (Java 21)                                             │
│  - Security: Spring Security 6 + Stateless JWT (RS256)                 │
│  - Data Access: Spring Data JPA + Hibernate + PostGIS                   │
│  - Storage Orchestration: AWS S3 SDK (targeting MinIO)                 │
│  - External Weather Proxy: OpenWeatherMap One Call 3.0 via WebClient   │
└───────────────────┬───────────────────────────────┬────────────────────┘
                    │                               │ Internal REST
┌───────────────────▼──────────────┐   ┌────────────▼────────────────────┐
│        DATA PERSISTENCE          │   │         AI / ML SERVICE         │
│  - PostgreSQL 16 (Relational/GIS)│   │  FastAPI (Python 3.11)          │
│  - Redis 7 (Inference/Weather)   │   │  - Computer Vision: OpenCV 4.9  │
│  - MinIO (Object Storage)        │   │  - Deep Learning: PyTorch 2.3   │
│                                  │   │  - Tabular ML: LightGBM / Scikit│
│                                  │   │  - Serving: ONNX Runtime 1.18   │
│                                  │   │  - Explainability: SHAP + GradCAM│
└──────────────────────────────────┘   └─────────────────────────────────┘
```

### 3.1 Frontend
- **Framework:** Next.js 14 (React 18, App Router) with strict TypeScript 5.x.
- **UI & Component System:** Tailwind CSS for atomic utility styles + shadcn/ui (Radix UI primitives) for accessible UI elements.
- **State Management:** TanStack React Query v5 for asynchronous server-state synchronization, request deduplication, and cache invalidation; Zustand for client-side form and session state.
- **Visualization Tools:** Recharts for meteorological trends, yield probability densities, and SHAP feature importance; Leaflet.js with OpenStreetMap tiles for field spatial coordinates.

### 3.2 Backend
- **Framework:** Spring Boot 3.3.x on Java 21 LTS (utilizing Virtual Threads for high concurrency).
- **Database:** PostgreSQL 16 with PostGIS extension for spatial field boundaries; Redis 7 for high-speed caching of weather payloads and image hash inference lookups.
- **Authentication:** Spring Security with stateless asymmetric JWTs (RS256); RBAC controlling `FARMER`, `RESEARCHER`, and `ADMIN` privileges.
- **API Architecture:** RESTful microservices architecture; Spring Boot acts as the public-facing API Gateway, orchestrator, and data store, proxying inference tasks to internal FastAPI nodes via non-blocking Spring `WebClient`.

### 3.3 AI / Machine Learning
- **Image Processing Libraries:** OpenCV 4.9 (headless) for CLAHE, morphological filtering, and spatial transformations; scikit-image for Haralick Gray-Level Co-occurrence Matrices (GLCM) and Local Binary Patterns (LBP).
- **ML/DL Frameworks:** PyTorch 2.3 for CNN feature extraction (EfficientNetV2) and Bi-LSTM temporal weather modeling; LightGBM 4.3 and XGBoost 2.0 for tabular yield and moisture regression; ONNX Runtime 1.18 for optimized cross-platform production inference.
- **Model Serving Strategy:** Decoupled FastAPI microservice executing containerized ONNX Runtime engines with pre-allocated thread pools; models loaded into system memory once during application startup event lifecycle.

---

## 4. IMAGE PROCESSING PIPELINE

```
Input: Raw Field Soil Photo (Smartphone/UAV)
                      │
                      ▼
┌──────────────────────────────────────────────────────────┐
│ STAGE 1: INGESTION & QUALITY GATING                      │
│ - EXIF orientation normalization & GPS metadata extraction│
│ - Laplacian Variance Blur Detection: Var(∇²I) ≥ 100     │
│ - Luminance Gating: 40 ≤ Mean(V) ≤ 215 (HSV domain)      │
└─────────────────────┬────────────────────────────────────┘
                      │ Pass
                      ▼
┌──────────────────────────────────────────────────────────┐
│ STAGE 2: PREPROCESSING & NORMALIZATION                   │
│ - Bicubic downsampling to 224×224 resolution             │
│ - Non-local Means (NLM) denoising (h=3, template=7)      │
│ - Contrast-Limited Adaptive Histogram Equalization (CLAHE)│
│   (Clip Limit = 2.0, Tile Grid = 8×8) applied to L-channel│
│ - Zero-mean unit-variance ImageNet tensor standardization│
└─────────────────────┬────────────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────────────────┐
│ STAGE 3: SEGMENTATION & REGION OF INTEREST (ROI)         │
│ - Color-threshold masking in HSV space to strip foliage  │
│   (Hue: 35°–85° removed)                                 │
│ - Otsu thresholding + Morphological Opening (kernel 5×5) │
│ - Output: Binary soil-surface mask isolating pure earth  │
└─────────────────────┬────────────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────────────────┐
│ STAGE 4: HYBRID DUAL-STREAM FEATURE EXTRACTION           │
│                                                          │
│  [Stream A: Handcrafted Physical Descriptors]            │
│  ├── Color Statistics: Mean & Std of L*, a*, b* channels │
│  ├── Dark Channel Prior: J^dark(x) = min_{y}(min_c I^c(y))│
│  └── Texture Descriptors:                                │
│      - GLCM (Contrast, Dissimilarity, Homogeneity, ASM)  │
│      - LBP Histogram (Uniform, P=8, R=1, 59 bins)        │
│                                                          │
│  [Stream B: Deep Spatial Embeddings]                     │
│  └── EfficientNetV2-B3 Backbone (truncated at conv_head) │
│      - Output: 1536-dimensional latent representation   │
└─────────────────────┬────────────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────────────────┐
│ STAGE 5: INTEGRATION WITH PREDICTION HEADS               │
│ - Concat: [1536-dim Deep] + [68-dim Handcrafted]         │
│ - Branch 1: Soil Classification Head → Softmax (6 Types)  │
│ - Branch 2: Moisture Regression Head → VWC % + Category   │
│ - Branch 3: Soil Feature Vector → Fused into Yield Model │
│ - Visualization: Grad-CAM heatmap generated from Layer 6 │
└──────────────────────────────────────────────────────────┘
```

### Detailed Mathematical Pipeline

1. **Blur Detection Metric:**
   $$\text{Score} = \text{Var}\left( \nabla^2 I \right) = \frac{1}{N}\sum_{x,y} \left( \nabla^2 I(x,y) - \mu_{\nabla^2 I} \right)^2$$
   Images with $\text{Score} < 100$ are rejected with an explicit client response.

2. **Dark Channel Prior Formulation for Surface Moisture:**
   $$I^{\text{dark}}(x) = \min_{c \in \{R,G,B\}} \left( \min_{y \in \Omega(x)} I^c(y) \right)$$
   Moist soil exhibits strong light absorption and specular refraction, directly correlating $I^{\text{dark}}$ decay with increasing volumetric moisture content.

3. **Gray-Level Co-occurrence Matrix (GLCM) Texture Descriptors:**
   $$\text{Contrast} = \sum_{i,j} |i - j|^2 P(i,j), \quad \text{Homogeneity} = \sum_{i,j} \frac{P(i,j)}{1 + |i - j|}, \quad \text{Energy} = \sum_{i,j} P(i,j)^2$$
   Fine-grained dry soil shows high local contrast and low homogeneity; moisture saturation causes clumping, significantly altering the spatial grey-level transition matrix $P(i,j)$.

---

## 5. PHASE-WISE IMPLEMENTATION PLAN

```
Month 1: Infrastructure & Data Setup
├── Phase 1: Literature Review & Mathematical Formulation
├── Phase 2: Dataset Collection, Verification & Ingestion
└── Phase 3: Data Cleaning, Alignment & Feature Engineering

Month 2: Model Development & Evaluation
├── Phase 4: Image Processing & Soil Classification Module
├── Phase 5: Soil Moisture Prediction Model
├── Phase 6: Weather Modeling & Time-Series Forecasting
└── Phase 7: Multimodal Crop Yield Prediction Model

Month 3: Engineering, Integration & Production Deployment
├── Phase 8: Backend Architecture & Gateway Development
├── Phase 9: Frontend Portal & Visualization Development
├── Phase 10: End-to-End System API Integration
├── Phase 11: Comprehensive Verification, Security & Load Testing
└── Phase 12: Production Orchestration & Documentation
```

### Phase 1: Literature Review & Research
- **Tasks:**
  - Synthesize empirical methods mapping optical reflectance to volumetric soil moisture.
  - Review deep convolutional architectures (ResNet, EfficientNet, ConvNeXt) versus vision transformers for agricultural soil texture domains.
  - Establish mathematical formulation for multi-task loss function balancing classification and continuous regression.
- **Deliverables:** Mathematical specification document; model loss formulations; annotated bibliography of 35 peer-reviewed sources.
- **Technologies Used:** LaTeX, Mendeley, Google Scholar, ArXiv.

### Phase 2: Dataset Collection & Validation
- **Tasks:**
  - Pull and extract the Kaggle Soil Types dataset (~1,600 images across 4 classes: Clay, Loamy, Sandy, Sandy Loam).
  - Ingest the Mendeley Soil Moisture image dataset (RGB soil photos categorized by Dry, Moderate, Wet desiccation intervals).
  - Download and validate the Indian Crop Production (APY) tabular dataset (246,000+ entries) from Kaggle.
  - Query NASA POWER API to retrieve historical agrometeorological indicators for target districts.
  - Implement DVC (Data Version Control) tracking backed by MinIO object storage.
- **Deliverables:** Version-controlled raw data buckets; verified data checksums; data integrity and class balance report.
- **Technologies Used:** Python 3.11, DVC, MinIO Client, Pandas, Requests.

### Phase 3: Data Cleaning & Preprocessing
- **Tasks:**
  - Build automated OpenCV image cleaning pipeline: EXIF auto-rotation, color space conversion, CLAHE application.
  - Handle tabular missing data via iterative multivariate imputation (MICE); clip extreme yield outliers via Interquartile Range (IQR).
  - Align timestamps between historical weather records, sowing periods, and harvest yields.
  - Perform time-series normalization (StandardScaler) on meteorological continuous variables.
- **Deliverables:** Cleaned, split dataset artifacts (`train`, `val`, `test` partitions under 80/10/10 split); transformation pipeline scripts.
- **Technologies Used:** OpenCV, Scikit-learn, NumPy, Pandas, Scipy.

### Phase 4: Image Processing Module
- **Tasks:**
  - Train EfficientNetV2-B3 on the 4-class Soil Types dataset using transfer learning (ImageNet initialization).
  - Implement Haralick GLCM and LBP feature extractors to output a 68-dimensional handcrafted descriptor.
  - Construct concatenated dual-stream embedding generator ($1536\text{ deep} + 68\text{ handcrafted}$).
  - Implement Grad-CAM hook on the final convolutional layer to generate explainability heatmaps.
  - Convert trained PyTorch weights to ONNX format with dynamic batching.
- **Deliverables:** `soil_classifier.onnx`; Grad-CAM visual generation utility; confusion matrix report demonstrating $\ge 90\%$ test accuracy.
- **Technologies Used:** PyTorch 2.3, Torchvision, PyTorch-Grad-CAM, ONNX, OpenCV.

### Phase 5: Soil Moisture Prediction Model
- **Tasks:**
  - Train an EfficientNet-based regression head on the Mendeley soil moisture dataset.
  - Extract physical image features (Dark Channel Prior, mean L* luminance in LAB space, GLCM texture energy).
  - Train a gradient-boosted secondary estimator (XGBoost) over physical image features to correct non-linear ambient lighting variations.
  - Ensemble CNN and XGBoost predictions through variance-weighted blending to predict volumetric moisture (% VWC) and classify into `Dry`, `Moderate`, `Wet`.
- **Deliverables:** `moisture_estimator.onnx`; validation report showing $\text{MAE} \le 3.5\%\text{ VWC}$; categorical mapping utility.
- **Technologies Used:** PyTorch, XGBoost, Scikit-learn, Optuna.

### Phase 6: Weather Prediction Model
- **Tasks:**
  - Pre-train a 2-layer Bidirectional LSTM (hidden size = 128) on NASA POWER historical sequences.
  - Formulate multi-step forecasting: input 30 days of antecedent meteorology $\to$ predict 7-day temperature and rainfall tendencies.
  - Calculate dynamic agrometeorological indicators:
    $$\text{GDD} = \max\left(0, \frac{T_{\max} + T_{\min}}{2} - T_{\text{base}}\right), \quad ET_0 \text{ via Hargreaves equation}$$
  - Integrate OpenWeatherMap One Call API 3.0 client for real-time live weather feeds with 30-minute Redis caching.
- **Deliverables:** `weather_lstm.onnx`; Hargreaves $ET_0$ calculation engine; OpenWeatherMap caching proxy service.
- **Technologies Used:** PyTorch, Redis, OpenWeatherMap API, Pandas.

### Phase 7: Yield Prediction Model
- **Tasks:**
  - Construct unified feature vectors combining:
    - Soil categorical class + moisture % (from Image Processing)
    - 30-day aggregated weather features ($GDD, ET_0$, total precipitation)
    - Agronomic inputs (Crop type, sowing week, optional NPK ratios)
  - Train LightGBM regressor with 5-fold cross-validation; tune hyperparameters using Optuna (100 trials).
  - Implement TreeSHAP to compute local and global feature attribution vectors.
  - Calculate prediction confidence bounds using quantile loss estimation ($\alpha = 0.05, 0.5, 0.95$).
- **Deliverables:** `yield_lgbm.pkl`; SHAP interpreter script; validation report achieving $R^2 \ge 0.87$.
- **Technologies Used:** LightGBM, SHAP, Optuna, Scikit-learn.

### Phase 8: Backend Development
- **Tasks:**
  - Initialize Spring Boot 3.3 project with Java 21, JPA, Security, Actuator, and Flyway.
  - Implement Flyway database migrations (`V1` through `V8`) for all PostgreSQL schemas.
  - Build JWT authentication, authorization filter chain, and user lifecycle endpoints.
  - Integrate AWS Java SDK for S3/MinIO to generate presigned upload URLs.
  - Build non-blocking internal HTTP proxy service using `WebClient` to query FastAPI inference nodes.
- **Deliverables:** Spring Boot application executable; complete REST API documentation (Swagger/OpenAPI 3.0); Flyway migration suite.
- **Technologies Used:** Java 21, Spring Boot 3.3, Spring Data JPA, Spring Security, Flyway, PostgreSQL, MinIO SDK.

### Phase 9: Frontend Development
- **Tasks:**
  - Initialize Next.js 14 project with TypeScript, Tailwind CSS, and shadcn/ui.
  - Build responsive dark-mode UI shells: Farmer Dashboard, Analysis Center, Weather Station, and Admin Monitoring.
  - Build Drag-and-Drop Image Uploader with client-side canvas image compression and blur pre-check.
  - Implement interactive result views: Grad-CAM heatmap overlay toggle, moisture gauge, yield range distribution, and SHAP horizontal bar charts.
  - Implement Leaflet.js field coordinate picker.
- **Deliverables:** Production Next.js web application bundle; fully styled responsive client interfaces.
- **Technologies Used:** Next.js 14, TypeScript, Tailwind CSS, shadcn/ui, Recharts, Leaflet.js, Lucide Icons.

### Phase 10: API Integration
- **Tasks:**
  - Connect Next.js data fetching layers to Spring Boot API using TanStack Query.
  - Implement presigned upload flow: Client requests URL $\to$ Spring Boot issues presigned MinIO token $\to$ Client streams binary directly to MinIO.
  - Connect Spring Boot async analysis trigger to FastAPI inference routes.
  - Configure Redis caching policies: 10-minute TTL on image SHA-256 hashes, 30-minute TTL on weather lat/lng queries.
- **Deliverables:** Fully operational end-to-end communication loop between Client, Spring Boot, MinIO, FastAPI, Redis, and PostgreSQL.
- **Technologies Used:** TanStack Query, Axios, Spring WebClient, Redis.

### Phase 11: Testing & Validation
- **Tasks:**
  - Execute JUnit 5 + Mockito test suites across all Spring Boot controllers and business services.
  - Execute PyTest suites on FastAPI data schemas, image transformation shapes, and model outputs.
  - Execute Playwright end-to-end tests covering: Registration $\to$ Login $\to$ Image Upload $\to$ Result Display.
  - Perform stress/load testing using Locust (50 concurrent users streaming analyses) to benchmark latency and memory stability.
- **Deliverables:** Test execution reports ($\ge 85\%$ backend line coverage); Locust load test metrics (P95 latency under 5 seconds).
- **Technologies Used:** JUnit 5, Mockito, PyTest, Playwright, Locust.

### Phase 12: Deployment
- **Tasks:**
  - Write multi-stage Dockerfiles for Next.js, Spring Boot, and FastAPI.
  - Construct root `docker-compose.yml` orchestrating PostgreSQL, Redis, MinIO, Spring Boot, FastAPI, and Next.js.
  - Implement database auto-initialization, health checks, and MinIO default bucket creation scripts.
  - Set up Nginx reverse proxy with SSL termination and Gzip/Brotli compression.
- **Deliverables:** Production-grade `docker-compose.yml`; system operational runbook; containerized multi-service deployment.
- **Technologies Used:** Docker, Docker Compose, Nginx, Linux.

---

## 6. SYSTEM ARCHITECTURE

### 6.1 End-to-End Component Flow

```
┌────────────────────────────────────────────────────────────────────────┐
│                              CLIENT (Next.js)                          │
└───────────────┬────────────────────────────────────────▲───────────────┘
                │ 1. Request Upload URL (Auth Token)     │ 13. Render Visuals
                │ 2. Binary Image Upload (Direct)        │     & Predictions
                ▼                                        │
┌───────────────────────────────┐        ┌───────────────┴───────────────┐
│     OBJECT STORE (MinIO)      │        │      API GATEWAY / BACKEND    │
│  - Stores raw soil JPG/PNG    │        │         (Spring Boot)         │
│  - Stores Grad-CAM heatmaps   │        │  - Validates JWT & User State │
└───────────────▲───────────────┘        │  - Coordinates Workflow       │
                │                        │  - Persists Records to DB     │
                │ 3. Fetch Raw Image     └───────┬───────────────▲───────┘
                │ 8. Save GradCAM Output         │               │
                │                                │ 4. Forward    │ 9. Return
                ▼                                │    Request    │    Prediction
┌────────────────────────────────────────┐       │    Payload    │    JSON
│            AI / ML SERVICE             │◄──────┘               │
│               (FastAPI)                │                       │
│  ├── Quality Validation & Preprocessing│───────────────────────┘
│  ├── Dual-Stream Feature Extraction    │
│  ├── Soil Classification (ONNX)        │
│  ├── Moisture Estimation Head          │
│  ├── Bi-LSTM Weather Encoder           │
│  ├── LightGBM Yield Regressor          │
│  └── Grad-CAM & SHAP Interpreters      │
└────────────────────────────────────────┘
```

### 6.2 Database Design (PostgreSQL Schema)

```sql
-- Core User Schema
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    full_name VARCHAR(150) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'FARMER' CHECK (role IN ('FARMER', 'RESEARCHER', 'ADMIN')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Farm & Spatial Field Boundaries
CREATE TABLE farms (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    state VARCHAR(100) NOT NULL,
    district VARCHAR(100) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE fields (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    farm_id UUID NOT NULL REFERENCES farms(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    area_hectares NUMERIC(10, 2) NOT NULL,
    latitude NUMERIC(10, 7) NOT NULL,
    longitude NUMERIC(10, 7) NOT NULL,
    current_crop VARCHAR(100),
    sowing_date DATE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Soil Sample & Image Processing Records
CREATE TABLE soil_samples (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    field_id UUID NOT NULL REFERENCES fields(id) ON DELETE CASCADE,
    image_raw_url TEXT NOT NULL,
    image_processed_url TEXT,
    image_hash_sha256 VARCHAR(64) NOT NULL,
    blur_score NUMERIC(8, 2) NOT NULL,
    quality_status VARCHAR(20) DEFAULT 'VALID' CHECK (quality_status IN ('VALID', 'BLURRY', 'POOR_LIGHTING')),
    captured_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Core Multimodal Predictions Output Table
CREATE TABLE predictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    soil_sample_id UUID NOT NULL REFERENCES soil_samples(id) ON DELETE CASCADE,
    field_id UUID NOT NULL REFERENCES fields(id) ON DELETE CASCADE,
    
    -- Objective 1: Soil Classification & Moisture
    soil_type VARCHAR(50) NOT NULL,
    soil_confidence NUMERIC(5, 4) NOT NULL,
    moisture_percentage NUMERIC(5, 2) NOT NULL,
    moisture_category VARCHAR(20) NOT NULL CHECK (moisture_category IN ('DRY', 'MODERATE', 'WET', 'SATURATED')),
    
    -- Objective 2: Crop Yield Prediction
    predicted_yield_kg_ha NUMERIC(10, 2) NOT NULL,
    yield_confidence_lower NUMERIC(10, 2) NOT NULL,
    yield_confidence_upper NUMERIC(10, 2) NOT NULL,
    
    -- Objective 3: Weather Context at Prediction Time
    temperature_c NUMERIC(5, 2) NOT NULL,
    humidity_percentage NUMERIC(5, 2) NOT NULL,
    precipitation_mm NUMERIC(7, 2) NOT NULL,
    growing_degree_days NUMERIC(8, 2) NOT NULL,
    evapotranspiration_mm NUMERIC(6, 2) NOT NULL,
    
    -- Explainability Artifacts
    gradcam_image_url TEXT,
    shap_top_features JSONB NOT NULL,
    
    model_version VARCHAR(50) NOT NULL,
    inference_duration_ms INT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Weather Temporal History & Forecast Cache
CREATE TABLE weather_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    field_id UUID NOT NULL REFERENCES fields(id) ON DELETE CASCADE,
    recorded_date DATE NOT NULL,
    temp_max_c NUMERIC(5, 2) NOT NULL,
    temp_min_c NUMERIC(5, 2) NOT NULL,
    rainfall_mm NUMERIC(7, 2) NOT NULL,
    solar_radiation_mj_m2 NUMERIC(8, 2),
    humidity_avg_pct NUMERIC(5, 2),
    is_forecast BOOLEAN DEFAULT FALSE,
    source VARCHAR(50) DEFAULT 'OPENWEATHERMAP',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(field_id, recorded_date, is_forecast)
);

-- Indices for Fast Geospatial & Time Queries
CREATE INDEX idx_fields_farm ON fields(farm_id);
CREATE INDEX idx_soil_samples_field ON soil_samples(field_id);
CREATE INDEX idx_predictions_field ON predictions(field_id);
CREATE INDEX idx_predictions_created_at ON predictions(created_at DESC);
CREATE INDEX idx_weather_lookup ON weather_records(field_id, recorded_date);
```

### 6.3 Request / Response Flow (Inference Lifecycle)

```
[User Browser]           [Spring Boot: 8080]        [MinIO: 9000]          [FastAPI: 8000]
      │                           │                       │                      │
      │── 1. GET /soil/upload-url ─►                      │                      │
      │◄── 2. Presigned PUT URL ──│                       │                      │
      │                                                   │                      │
      │────── 3. PUT binary image stream ────────────────►│                      │
      │◄───── 4. 200 OK (Upload Complete) ────────────────│                      │
      │                                                   │                      │
      │── 5. POST /soil/analyze {sample_id, field_id} ───►│                      │
      │    (Spring Boot checks Redis for cached hash)     │                      │
      │                           │                                              │
      │                           │── 6. POST /internal/v1/predict-pipeline ────►│
      │                           │      {image_url, lat, lon, crop_name}        │
      │                           │                       │                      │
      │                           │                       │── 7. Fetch Image ───►│
      │                           │                       │◄─ 8. Image Bytes ────│
      │                           │                       │                      │
      │                           │                       │── [Preprocess & CV] ─│
      │                           │                       │── [Fetch Weather] ───│
      │                           │                       │── [Execute ONNX] ────│
      │                           │                       │── [Generate GradCAM]─│
      │                           │                       │── 9. Save Heatmap ──►│
      │                           │                       │                      │
      │                           │◄─ 10. Return Complete Analysis JSON ─────────│
      │                           │                                              │
      │                           │── [Store into PostgreSQL `predictions`]      │
      │                           │── [Cache Analysis in Redis (TTL=10min)]      │
      │◄── 11. 200 OK Response ───│                                              │
      │    (Full UI Payload)      │                                              │
```

---

## 7. FINAL RECOMMENDATIONS

### 7.1 Best Dataset Combination
**Soil Types (Kaggle) + Soil Moisture (Mendeley) + OpenWeatherMap/NASA POWER + India APY (Kaggle)**
- **Why:** 100% free and open-access, zero account or approval roadblocks, immediate 1-click download, and cleanly separated modalities eliminating data leakage.

### 7.2 Best Model Stack

| Component | Selected Architecture | Justification |
|---|---|---|
| **Image Feature Extractor** | **EfficientNetV2-B3** | Superior parameter efficiency (14M parameters vs 25M for ResNet-50); faster convergence via progressive learning; small footprint when compiled to ONNX. |
| **Moisture Estimator** | **CNN-Regression + XGBoost Ensemble** | CNN extracts deep spatial texture; XGBoost handles explicit lighting shifts (DCP & CLAHE stats), preventing over-fitting to ambient sunlight. |
| **Weather Encoder** | **2-Layer Bi-LSTM (Hidden=128)** | Captures forward and backward meteorological dynamics (dry spells, sudden heavy downpours) over a rolling 30-day window. |
| **Crop Yield Predictor** | **LightGBM Regressor** | Consistently outperforms deep learning architectures on tabular multi-feature regression; native handling of categorical soil classes; native TreeSHAP support. |
| **Model Serving Engine** | **ONNX Runtime (CPU, Multi-threaded)** | Zero PyTorch runtime overhead in production; sub-100ms inference execution on commodity server CPUs. |

### 7.3 Expected Performance Benchmarks

| Metric | Minimum Target | Realistic Target | Stretch Goal |
|---|---|---|---|
| **Soil Classification Accuracy** | 88.0% | **91.5%** | 93.8% |
| **Moisture Content Estimation MAE** | $\le 4.0\%\text{ VWC}$ | **$\le 3.2\%\text{ VWC}$** | $\le 2.5\%\text{ VWC}$ |
| **Yield Prediction $R^2$ Score** | 0.82 | **0.88** | 0.91 |
| **Yield Prediction RMSE** | $\le 250\text{ kg/ha}$ | **$\le 180\text{ kg/ha}$** | $\le 140\text{ kg/ha}$ |
| **End-to-End System Latency (P95)** | $\le 5.0\text{ s}$ | **$\le 3.2\text{ s}$** | $\le 1.8\text{ s}$ |

### 7.4 Major Technical Risks & Mitigation Strategies

1. **Ambient Lighting Variance in Field Photos:**
   - *Risk:* Direct midday sun vs. overcast dusk alters perceived soil color, creating false moisture readings.
   - *Mitigation:* Convert images to LAB color space; normalize luminance using CLAHE ($L^*$-channel only); incorporate Dark Channel Prior ($I^{\text{dark}}$) which is robust to surface intensity fluctuations.
2. **Extreme Class Imbalance in Soil Types:**
   - *Risk:* Loamy/Clayey soils heavily outnumber Chalky/Peaty samples in public datasets.
   - *Mitigation:* Apply targeted data augmentations: RandAugment, CutMix, and Focal Loss ($\gamma=2.0$) on underrepresented classes.
3. **Temporal Misalignment of Historical Data:**
   - *Risk:* Associating post-harvest satellite or weather data with pre-harvest crop stages leads to look-ahead data leakage.
   - *Mitigation:* Rigid temporal masking enforcing strict cutoff at the stated harvest date in training data preparation scripts.
4. **Third-Party API Rate Limits (Weather):**
   - *Risk:* OpenWeatherMap free tier exhausts during live demonstration or multiple users.
   - *Mitigation:* Redis geospatial caching ($0.05^\circ \times 0.05^\circ$ grid key) with 30-minute TTL, ensuring repeated queries within $\approx 5\text{ km}$ hit memory directly.

### 7.5 Research & Publication Opportunities
- **Primary Target:** *Elsevier — Computers and Electronics in Agriculture* (Impact Factor: 8.3)
- **Secondary Target:** *IEEE Access* (Impact Factor: 3.9) / *Springer — Precision Agriculture* (Impact Factor: 5.4)
- **Distinct Research Contribution (Novelty Hook):**
  > *"MSAIF: A Sensorless Multimodal Agricultural Intelligence Framework Fusing Surface Soil Imagery with Recurrent Meteorological Encodings for Simultaneous Moisture and Yield Estimation."*
- **Key Paper Contributions:**
  1. Elimination of in-situ physical soil probes by replacing them with optical dark-channel and GLCM texture image analysis.
  2. Late-fusion mechanism combining computer vision spatial embeddings with Bi-LSTM temporal weather representations.
  3. Real-world validation with explainability: Grad-CAM verification of soil image saliency coupled with SHAP-driven agrometeorological impact transparency.
