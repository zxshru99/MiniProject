# PRD — Product Requirements Document

**Project:** AI-Based Prediction of Crop Yield, Soil Moisture & Weather Impact
**Version:** 1.0 | **Date:** October 2026 | **Status:** Active

---

## 1. What We Are Building

A web app where a farmer uploads a soil photo → gets back:
1. Soil type (Clay / Loamy / Sandy / Sandy Loam)
2. Moisture level (% and category)
3. Predicted crop yield (kg/ha)
4. Top 3 crop recommendations
5. Irrigation and fertilizer advice
6. 7-day weather impact summary

That's it. Everything else is secondary.

---

## 2. Who Uses It

| User | What They Do |
|---|---|
| Farmer | Uploads image, reads results, follows recommendations |
| Researcher | Accesses historical data, exports reports |
| Admin | Manages users, monitors model performance |

---

## 3. Core Features (Must Have for Submission)

| # | Feature | Why It Matters |
|---|---|---|
| 1 | Signup / Login with JWT | Every user needs an account |
| 2 | Farm + Field registration | Link predictions to real locations |
| 3 | Soil image upload | Core input to the system |
| 4 | Soil type classification (CNN) | Computer vision deliverable |
| 5 | Moisture estimation | ML deliverable |
| 6 | Yield prediction | Core ML deliverable |
| 7 | Crop recommendation | Practical output for farmers |
| 8 | Weather dashboard (live + 7-day) | Weather integration deliverable |
| 9 | Prediction history per field | Makes the app useful over time |
| 10 | Admin dashboard | Project completeness |

---

## 4. Features for Later (Don't Build Now)

- Mobile app
- Drone image support
- SMS notifications
- Multilingual UI
- Blockchain anything

---

## 5. Functional Requirements

### Auth
- Register: name, email, phone, password
- Login: returns JWT (1h) + refresh token (7d)
- Roles: FARMER, ADMIN, RESEARCHER
- Password reset via email

### Image Upload
- Formats: JPG, PNG, TIFF
- Max size: 10 MB
- Min resolution: 640×480
- Auto-reject blurry images (Laplacian variance < 100)
- Store in MinIO; save URL in PostgreSQL

### Soil Analysis (FastAPI → ML model)
- Input: sample_id / MinIO image URL (with client-side blur validation)
- Output: soil_type (Clay, Loamy, Sandy, Sandy Loam), confidence, moisture_pct, moisture_category (Dry, Moderate, Wet), gradcam_image_url
- Response time: ≤ 5 seconds

### Yield Prediction
- Inputs: soil_type, moisture_pct, crop_name, sowing_date, NPK values (manual input), weather (auto-fetched)
- Output: kg/ha prediction + confidence interval + top SHAP factors

### Crop Recommendation
- Input: soil_type, moisture, pH, NPK, season, location
- Output: top 3 crops with suitability score

### Weather
- Source: OpenWeatherMap One Call API 3.0
- Display: 7-day forecast, temperature, rainfall, humidity, heat stress flag

---

## 6. Non-Functional Requirements

| What | Target |
|---|---|
| API response time (non-ML) | < 300ms |
| ML inference time | < 5 seconds |
| Uptime target | 99% |
| Image storage | MinIO (local) |
| Auth security | JWT + bcrypt passwords |
| Data in transit | HTTPS only |

---

## 7. What We Are NOT Doing

- Real-time IoT sensors
- Satellite image processing
- Hyperspectal cameras
- Any paid APIs beyond OpenWeatherMap free tier
- Native mobile apps
