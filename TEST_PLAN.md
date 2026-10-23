# TEST_PLAN.md — Testing Strategy

**Project:** AgriAI Platform
**Version:** 1.0

---

## 1. What We Test and Why

We test the things that will break silently and cost us during a demo or viva:
1. Auth — wrong tokens should never get through
2. Image upload — corrupt or invalid files should be rejected cleanly
3. ML inference — results should be consistent and in valid ranges
4. API contracts — Spring Boot and FastAPI must agree on request/response shapes
5. Database — data must be saved correctly and retrievable

We do NOT write tests for:
- Boilerplate CRUD that Spring Data JPA already handles
- Third-party libraries (trust them)
- UI pixel perfection

---

## 2. Test Layers

```
Unit Tests          → Fast, isolated, no DB/network
Integration Tests   → Test with real DB / Redis / MinIO (Docker)
API Tests           → HTTP-level tests (Postman / RestAssured)
E2E Tests           → Browser automation (Playwright)
ML Evaluation       → Model accuracy on held-out test set (not a test suite — a notebook)
```

---

## 3. Backend — Spring Boot (JUnit 5 + Mockito)

### 3.1 Unit Tests

**`AuthServiceTest.java`**
```
✅ registerUser_success: valid input → user saved, password hashed
✅ registerUser_duplicateEmail: existing email → throws UserAlreadyExistsException
✅ login_success: correct credentials → returns JWT tokens
✅ login_wrongPassword: incorrect password → throws InvalidCredentialsException
✅ login_inactiveUser: disabled account → throws AccountDisabledException
✅ generateToken: token contains correct user ID and role
✅ validateToken_expired: expired token → returns false
✅ validateToken_tampered: modified token → returns false
```

**`SoilServiceTest.java`**
```
✅ analyzeImage_success: valid sample_id → calls MlServiceClient, saves prediction, returns result
✅ analyzeImage_imageNotFound: unknown sample_id → throws SoilSampleNotFoundException
✅ analyzeImage_mlServiceDown: FastAPI unreachable → throws MlServiceUnavailableException with correct HTTP 503
✅ getPresignedUploadUrl: returns valid MinIO URL structure
✅ validateImageMetadata_tooBlurry: blur score < 0.5 → throws ImageQualityException
```

**`YieldPredictionServiceTest.java`**
```
✅ predictYield_validInputs: returns prediction with non-null yield, confidence interval
✅ predictYield_missingCropName: null crop → throws ValidationException
✅ predictYield_resultCached: second call with same params → no ML call made (Redis hit)
```

**`WeatherServiceTest.java`**
```
✅ fetchWeather_success: valid lat/lng → returns 7-day forecast
✅ fetchWeather_cached: same location within 30 min → uses Redis, no API call
✅ fetchWeather_apiError: OpenWeatherMap returns 401 → throws WeatherFetchException
```

---

### 3.2 Integration Tests (with Testcontainers)

Use **Testcontainers** to spin up real PostgreSQL and Redis instances during tests:

```java
@SpringBootTest
@Testcontainers
class AuthIntegrationTest {
    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:16");
    
    @Container
    static GenericContainer<?> redis = new GenericContainer<>("redis:7").withExposedPorts(6379);
    ...
}
```

**Tests to write:**
```
✅ Full register → login → get /me flow using real DB
✅ Create farm → create field → link correctly in DB
✅ Upload soil sample → save to DB → trigger analysis → prediction saved in DB
✅ Prediction result cached in Redis → subsequent request hits cache (verify no DB call)
✅ JWT refresh flow: use refresh token to get new access token
✅ Role access: farmer cannot call /api/admin/* endpoints → 403
✅ Flyway migrations run cleanly and all tables exist
```

---

### 3.3 API Contract Tests (Postman Collection)

**Auth endpoints:**
```
POST /api/auth/register     → 201, returns user object (no password field in response)
POST /api/auth/login        → 200, returns {access_token, refresh_token, user}
POST /api/auth/login        → 401 with wrong password
POST /api/auth/refresh      → 200 with valid refresh token
GET  /api/auth/me           → 200 with valid JWT
GET  /api/auth/me           → 401 without JWT
GET  /api/auth/me           → 401 with expired JWT
```

**Soil endpoints:**
```
GET  /api/soil/upload-url   → 200, returns presigned_url (string, starts with http)
POST /api/soil/analyze      → 202 accepted (async) with sample_id
GET  /api/soil/samples/{id} → 200, status: PROCESSING or DONE
GET  /api/soil/samples/{id} → 200 with full prediction when status=DONE
GET  /api/soil/samples/bad-id → 404
```

**Weather:**
```
GET /api/weather?lat=28.6&lng=77.2 → 200, 7-element forecast array
GET /api/weather (no params)        → 400, validation error
```

---

## 4. ML Service — FastAPI (pytest)

### 4.1 Unit Tests (`tests/`)

**`test_image_processor.py`**
```python
✅ test_resize_224: output shape == (224, 224, 3)
✅ test_clahe_normalization: pixel values in [0, 1] after normalization
✅ test_blur_detection_blurry: blurry image returns score < 0.5
✅ test_blur_detection_sharp: sharp image returns score > 0.7
✅ test_grabcut_segment: output is binary mask same shape as input
```

**`test_soil_classifier.py`**
```python
✅ test_classify_returns_valid_label: output in expected 6 class labels
✅ test_confidence_sum_to_one: top-3 confidence scores sum ≤ 1.0
✅ test_classify_loamy_image: known loamy test image → "loamy" predicted
✅ test_gradcam_output_shape: Grad-CAM output is same H×W as input image
```

**`test_moisture_estimator.py`**
```python
✅ test_moisture_in_valid_range: output value between 0.0 and 60.0
✅ test_dry_soil_lower_than_wet: dry image VWC < wet image VWC
✅ test_category_mapping: moisture_pct → correct category (DRY/MODERATE/WET/SATURATED)
```

**`test_yield_predictor.py`**
```python
✅ test_predict_returns_positive_value: yield > 0 for valid inputs
✅ test_confidence_interval_valid: lower < predicted < upper
✅ test_shap_values_count: returns at least 5 SHAP factors
```

**`test_crop_recommender.py`**
```python
✅ test_returns_three_recommendations: exactly 3 crops returned
✅ test_scores_descending: first crop has highest score
✅ test_score_range: all scores between 0.0 and 1.0
✅ test_rice_not_recommended_for_sandy: soil_type=sandy → rice not in top-3
```

---

### 4.2 FastAPI Endpoint Tests

```python
✅ POST /classify-soil with valid image_url → 200 with soil_type, confidence, gradcam_url
✅ POST /classify-soil with invalid URL → 422 validation error
✅ POST /classify-soil with unreachable image URL → 400 with error message
✅ POST /predict-yield with all valid fields → 200 with yield value
✅ POST /predict-yield with missing crop_name → 422
✅ GET /health → 200 {"status": "ok", "models_loaded": true}
```

---

## 5. Model Accuracy Evaluation (Research Notebook)

This is NOT a test suite. This is a Jupyter notebook (`evaluation/model_eval.ipynb`) run once after training.

### 5.1 Soil Classification Evaluation
- Dataset split: 80% train / 10% val / 10% test (held-out, never seen during training)
- Metrics to compute and report:
  - Overall accuracy
  - Per-class F1 score
  - Cohen's Kappa
  - Confusion matrix (save as image for paper)

**Pass threshold:** Overall accuracy ≥ 90%

### 5.2 Moisture Estimation Evaluation
- Metrics: MAE, RMSE, R² on test split

**Pass threshold:** MAE < 4% VWC

### 5.3 Yield Prediction Evaluation
- Cross-validation: TimeSeriesSplit(n_splits=5) — respect temporal order of data
- Metrics: R², RMSE, MAE — both overall and per crop type

**Pass threshold:** R² ≥ 0.85 on test split

### 5.4 Crop Recommendation Evaluation
- Standard train/test split (80/20)
- Metrics: Accuracy, macro F1

**Pass threshold:** Accuracy ≥ 95%

---

## 6. Frontend — Playwright E2E Tests

**Setup:**
```bash
cd frontend
npx playwright install chromium
```

**Test file: `tests/e2e/farmer-flow.spec.ts`**

```typescript
✅ test('register new farmer account')
   → fills form, submits, redirected to dashboard

✅ test('login with valid credentials')
   → fills form, submits, sees dashboard

✅ test('login with wrong password shows error')
   → error message visible, no redirect

✅ test('upload soil image and see results')
   → uploads test JPG, waits for processing, results visible on page

✅ test('blurry image rejected with helpful message')
   → uploads blur-test.jpg, sees quality error message

✅ test('add new field to farm')
   → fills field form, field appears in fields list

✅ test('weather page shows forecast')
   → navigates to /weather, 7 forecast cards visible

✅ test('farmer cannot access /admin')
   → logs in as farmer, navigates to /admin, redirected away
```

---

## 7. Load Testing (Locust)

**File: `tests/load/locustfile.py`**

Simulate 50 concurrent farmers uploading images:

```python
# Target endpoints for load test
- POST /api/auth/login       (warm-up)
- GET  /api/soil/upload-url  (presigned URL)
- POST /api/soil/analyze     (trigger ML)
- GET  /api/soil/samples/{id} (polling — 3 polls avg)
```

**Targets:**
- 50 concurrent users, 5 min sustained
- `POST /api/soil/analyze` P95 < 8 seconds
- Error rate < 1%
- Spring Boot memory stable (no leak)

Run:
```bash
cd tests/load
locust -f locustfile.py --host=http://localhost:8080 --users=50 --spawn-rate=5
```

---

## 8. Security Tests (Manual Checklist)

- [ ] SQL injection: send `'; DROP TABLE users; --` as email in login → must be rejected
- [ ] JWT with wrong signature → must return 401
- [ ] Farmer A trying to access Farmer B's data → must return 403 or 404
- [ ] Upload a `.php` or `.exe` file as "image" → must be rejected at MIME type check
- [ ] Call ML endpoints directly (bypassing Spring Boot) → FastAPI should only accept calls from internal network (not exposed publicly)
- [ ] Brute force login: 20 attempts in 1 minute → rate limiter must kick in

---

## 9. Test Data

### Test Images
| File | Description | Expected Soil Type |
|---|---|---|
| `tests/fixtures/loamy_good.jpg` | Clear loamy soil | loamy |
| `tests/fixtures/sandy_dry.jpg` | Dry sandy soil | sandy |
| `tests/fixtures/clayey_wet.jpg` | Wet clay soil | clayey |
| `tests/fixtures/blurry_test.jpg` | Intentionally blurred | REJECTED |
| `tests/fixtures/non_soil.jpg` | Photo of a wall | Classification uncertain — system should still not crash |

### Test User Credentials (Dev Only)
```
farmer@test.com / Test@1234 (role: FARMER)
admin@test.com  / Admin@1234 (role: ADMIN)
```

---

## 10. Test Execution Checklist Before Any Demo

- [ ] `docker-compose up -d` — all services healthy
- [ ] Run Spring Boot unit tests: `mvn test` — all pass
- [ ] Run FastAPI unit tests: `pytest ml-service/tests/ -v` — all pass
- [ ] Manual E2E: register → upload image → view result
- [ ] Check Redis caching: upload same image twice, second should be faster
- [ ] Check weather widget shows real data
- [ ] Admin dashboard loads for admin user
- [ ] Farmer cannot access admin page
