# DECISIONS.md — Architecture & Technical Decision Log

**Project:** AgriAI Platform
**Purpose:** Record every significant technical decision, what alternatives were considered, and why we chose what we chose. This prevents re-litigating the same debates later.

---

## Decision Template

```
## DEC-XXX: [Short Title]
Date: YYYY-MM-DD
Status: Accepted | Superseded | Rejected
Context: What situation forced this decision?
Decision: What we decided to do.
Alternatives Considered: What else was on the table?
Reason: Why we chose this over alternatives.
Consequences: What this means going forward.
```

---

## DEC-001: Database — PostgreSQL Only

**Date:** October 2026
**Status:** Accepted

**Context:** Needed a database for users, farms, predictions, and soil sample metadata. Team debated PostgreSQL vs MongoDB.

**Decision:** Use PostgreSQL as the single relational database.

**Alternatives Considered:**
- MongoDB — document store, flexible schema
- MySQL — relational, widely used

**Reason:**
- Our data IS relational. Users own farms, farms have fields, fields have soil samples, samples have predictions. This is a textbook join-heavy schema. A document store is wrong here.
- PostgreSQL has JSONB for storing flexible data (SHAP values, top-3 predictions) without needing a separate document DB.
- PostGIS extension available for future geospatial field polygon queries.
- Spring Data JPA works seamlessly with PostgreSQL.
- MySQL rejected because PostgreSQL is strictly superior: better JSON support, better standards compliance, better for research datasets.

**Consequences:** All schema changes must go through Flyway migrations.

---

## DEC-002: Redis for Inference Caching

**Date:** October 2026
**Status:** Accepted

**Context:** ML inference (soil classification + moisture) takes 2–5 seconds. If a farmer re-submits the same image, they'd wait again needlessly.

**Decision:** Cache inference results in Redis keyed by `sha256(image_bytes)` with 10-minute TTL.

**Alternatives Considered:**
- No caching (simplest)
- In-memory cache in FastAPI (dies on restart)
- Cache in PostgreSQL (too slow for cache use case)

**Reason:** Redis is the standard for this exact use case. Light, fast, supports TTL natively. Also used for weather API response caching (30-min TTL) to avoid hitting OpenWeatherMap rate limits.

**Consequences:** Need Redis in docker-compose. Cache invalidation not needed (TTL handles it). Cache hit rate expected ~20–30% during demos.

---

## DEC-003: MinIO for Image Storage (Not Local Filesystem)

**Date:** October 2026
**Status:** Accepted

**Context:** Soil images and Grad-CAM outputs need to be stored somewhere. Debated local filesystem vs object storage.

**Decision:** MinIO running in Docker for local dev. S3-compatible API means zero code change if moving to AWS S3 later.

**Alternatives Considered:**
- Local filesystem — simple but not scalable, doesn't work across services
- AWS S3 — production-ready but costs money and requires internet for local dev
- Store base64 images in PostgreSQL — terrible idea, bloats DB significantly

**Reason:** MinIO gives S3 semantics locally for free. Presigned URLs let the browser upload directly to MinIO without routing through Spring Boot, which keeps the API lightweight. The Java AWS S3 SDK works with MinIO out of the box.

**Consequences:** Need MinIO in docker-compose. Must generate presigned PUT URLs server-side. Bucket names hardcoded in config, not code.

---

## DEC-004: Two Backend Services (Spring Boot + FastAPI)

**Date:** October 2026
**Status:** Accepted

**Context:** Needed to decide whether to build one backend or two.

**Decision:** Spring Boot for business logic/auth/CRUD. FastAPI for all ML inference.

**Alternatives Considered:**
- Django (Python) for everything — eliminates Java, simpler stack
- Spring Boot only with DJL (Deep Java Library) for ML
- FastAPI for everything — no separate Java service

**Reason:**
- Python ML ecosystem (PyTorch, scikit-learn, OpenCV, SHAP, Grad-CAM) is far superior to Java's. We are NOT re-implementing model inference in Java.
- Spring Boot is better for enterprise concerns: JWT, RBAC, JPA, Flyway, Spring Security. Setting all of this up properly in FastAPI takes more time.
- Django rejected because we already know Spring Boot's maturity for auth and it has better academic familiarity in our team.
- DJL rejected because model support is limited and PyTorch models need conversion gymnastics.
- The two-service split is a clean separation: Spring Boot = business layer, FastAPI = intelligence layer.

**Consequences:** Need internal HTTP communication between Spring Boot and FastAPI. FastAPI is not exposed to the public internet — only Spring Boot is. Adds one more Docker service.

---

## DEC-005: EfficientNetV2-B3 for Soil Classification (not ResNet or ViT)

**Date:** October 2026
**Status:** Accepted

**Context:** Needed to choose a CNN backbone for soil image classification.

**Decision:** EfficientNetV2-B3 fine-tuned from ImageNet weights.

**Alternatives Considered:**
- ResNet-50: Older, heavier, slightly lower accuracy on small datasets
- ViT-B/16: Best accuracy but requires large dataset (>100k images) to generalize; our SoilNet has 11k images
- MobileNetV3: Fast but less accurate, designed for very edge-constrained devices
- Custom CNN from scratch: Would require far more data and compute

**Reason:** EfficientNetV2-B3 offers best accuracy/speed tradeoff for our dataset size. It was specifically designed to perform well with less data via compound scaling. ImageNet pre-training gives strong feature initialization for soil texture and color patterns.

**Consequences:** Model size ~50MB. Export to ONNX for inference. Fine-tuning takes ~2–4 hours on a single GPU (or Google Colab A100).

---

## DEC-006: LightGBM for Yield Prediction (not XGBoost or LSTM-only)

**Date:** October 2026
**Status:** Accepted

**Context:** Needed a model for yield prediction from tabular features (soil type, NPK, weather stats, crop name).

**Decision:** LightGBM as the primary yield prediction model.

**Alternatives Considered:**
- XGBoost: Competitive, slightly slower training
- Random Forest: Good interpretability, lower accuracy
- LSTM only: Good for temporal patterns but our training dataset is not large enough for LSTM alone to outperform GBDT
- CNN-LSTM fusion: Best accuracy potential but requires much larger labeled dataset and more compute for a mini-project

**Reason:**
- LightGBM trains faster than XGBoost (leaf-wise tree growth).
- Better handling of categorical features (soil_type, crop_name) natively.
- SHAP integration is first-class with LightGBM.
- For our dataset size (~246k USDA records), GBDT models consistently outperform deep learning in tabular regression benchmarks.
- CNN-LSTM fusion is noted in the research paper as "proposed architecture" for the theoretical contribution, but LightGBM is what we actually deploy.

**Consequences:** Model artifact is a `.pkl` file (~5MB). SHAP computation adds ~500ms to inference but is pre-computed for common scenarios.

---

## DEC-007: No Real-Time WebSockets for MVP

**Date:** October 2026
**Status:** Accepted

**Context:** ML inference takes 2–5 seconds. Frontend needs to show progress. Debated WebSocket vs polling.

**Decision:** Client-side polling every 2 seconds on `GET /api/soil/samples/{id}` until `status = DONE`.

**Alternatives Considered:**
- WebSocket connection for real-time status updates
- Server-Sent Events (SSE)

**Reason:** WebSockets add non-trivial complexity (Spring WebSocket config, frontend Socket.IO or native WS). For a 5-second max wait, polling every 2 seconds is perfectly acceptable and much simpler. Spring Boot handles it without extra dependencies. Can migrate to SSE or WebSocket in v2 if needed.

**Consequences:** Slightly more API calls during processing (max 3–4 polling requests per analysis). Acceptable for MVP scale.

---

## DEC-008: OpenWeatherMap Free Tier (Not Paid APIs)

**Date:** October 2026
**Status:** Accepted

**Context:** Need weather data. Multiple options available.

**Decision:** OpenWeatherMap One Call API 3.0 (free tier: 1000 calls/day).

**Alternatives Considered:**
- Agromonitoring API (paid)
- NASA POWER API (free, historical only)
- AccuWeather (paid, better accuracy)
- Self-hosted weather model

**Reason:** Free. Sufficient for a mini-project. 1000 calls/day is enough for demos. With Redis caching (30-min TTL per location), actual API calls will be well under 100/day in demo mode. NASA POWER API used separately for historical data in ML training — it's not suitable for real-time display.

**Consequences:** Production deployment would need to upgrade to paid tier or switch API. Rate limiting handled in Spring Boot before hitting API.

---

## DEC-009: Flyway for Database Migrations (Not Hibernate Auto-DDL)

**Date:** October 2026
**Status:** Accepted

**Context:** Need to manage database schema over time.

**Decision:** Flyway with versioned SQL migration files.

**Reason:** `spring.jpa.hibernate.ddl-auto=create` destroys all data on restart. `update` mode misses column deletions and renames. Flyway gives explicit, reviewable, version-controlled migrations. This is non-negotiable for any project that might need to publish or hand off code.

**Consequences:** Every schema change = a new Flyway file. No exceptions.
