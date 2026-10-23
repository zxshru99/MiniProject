# RULES.md — Project Rules & Coding Standards

**Project:** AgriAI Platform
**Apply to:** All team members. No exceptions.

---

## 1. General Rules

- **No gold-plating.** Build what's in PRD.md. If it's not in the PRD, don't build it.
- **No skeleton code.** Don't commit placeholder functions that do nothing.
- **No `// TODO` in production code.** Either do it now or create a task in TASKS.md.
- **Every feature must be testable.** If you can't write a test for it, redesign it.
- **Commit often.** Minimum one commit per meaningful change. Never commit broken code to `main`.

---

## 2. Git Rules

```
Branch naming:
  feature/soil-classification-api
  fix/image-upload-validation
  chore/update-dependencies
  docs/update-architecture

Commit message format (Conventional Commits):
  feat: add soil classification endpoint
  fix: correct moisture percentage calculation
  chore: add docker-compose for local dev
  docs: update API examples in ARCHITECTURE.md
  test: add unit tests for yield prediction service

Branch protection:
  - Never push directly to main
  - All code goes via a branch + PR
  - At least 1 review before merge (even if it's just yourself reviewing)
```

---

## 3. Backend Rules (Spring Boot — Java)

### 3.1 Project Structure
```
com.agripredict/
├── auth/
│   ├── AuthController.java
│   ├── AuthService.java
│   ├── JwtUtil.java
│   └── dto/
├── farm/
│   ├── FarmController.java
│   ├── FarmService.java
│   ├── FarmRepository.java
│   ├── Farm.java          ← Entity
│   └── dto/
├── soil/
│   ├── SoilController.java
│   ├── SoilService.java
│   └── ...
├── prediction/
├── weather/
└── common/
    ├── exception/
    ├── response/
    └── config/
```

### 3.2 Coding Standards
- Use `@RestController` + `@RequestMapping` for all controllers
- Return `ResponseEntity<ApiResponse<T>>` from every endpoint (standard wrapper)
- Always validate request bodies with `@Valid` + Bean Validation annotations
- Use Lombok: `@Data`, `@Builder`, `@RequiredArgsConstructor` — no boilerplate getters/setters
- Use MapStruct for all Entity ↔ DTO conversions. Never map manually.
- Database access only through JPA Repositories. No raw SQL in business logic. Use `@Query` for complex queries.
- All DB migrations via Flyway SQL files in `resources/db/migration/`. Never let Hibernate auto-create tables in production.
- Use `@Transactional` on service methods that write to DB
- Log with SLF4J. No `System.out.println()`.

### 3.3 Error Handling
- One `@ControllerAdvice` class handles ALL exceptions globally
- Never let a raw exception stack trace reach the client
- HTTP status codes must be correct: 400 (bad input), 401 (unauthenticated), 403 (unauthorized), 404 (not found), 500 (server error)

### 3.4 API Response Format
```json
{
  "success": true,
  "data": { ... },
  "message": "Soil analysis completed",
  "timestamp": "2026-10-18T22:00:00Z"
}
```
Error format:
```json
{
  "success": false,
  "error": "IMAGE_TOO_BLURRY",
  "message": "Image quality too low. Please retake in good lighting.",
  "timestamp": "2026-10-18T22:00:00Z"
}
```

---

## 4. ML Service Rules (FastAPI — Python)

### 4.1 Project Structure
```
ml-service/
├── main.py              ← FastAPI app init + startup model loading
├── routers/
│   ├── soil.py          ← /classify-soil, /estimate-moisture
│   ├── yield.py         ← /predict-yield
│   └── crop.py          ← /recommend-crop
├── models/              ← trained model files (ONNX / .pkl)
│   ├── soil_classifier.onnx
│   ├── moisture_regressor.pkl
│   ├── yield_lgbm.pkl
│   └── crop_rf.pkl
├── services/
│   ├── image_processor.py    ← all OpenCV preprocessing
│   ├── model_loader.py       ← loads models once at startup
│   └── explainability.py     ← Grad-CAM and SHAP
├── schemas/             ← Pydantic request/response models
└── requirements.txt
```

### 4.2 Coding Standards
- All models loaded ONCE at startup using `@app.on_event("startup")`. Never load a model inside a request handler.
- All inputs validated with Pydantic schemas. No raw dicts.
- All image processing in `image_processor.py`. Keep routes thin.
- Use `async def` for route handlers. Use `run_in_executor` for CPU-heavy model inference.
- Never hardcode paths. Use environment variables via `python-dotenv`.
- Type hints on every function signature.

### 4.3 Model Files
- Store model files in `ml-service/models/` — NOT in source control (add to `.gitignore`)
- Use DVC or provide a download script to get model files
- Model version stored in a `model_metadata.json` file alongside each model

---

## 5. Frontend Rules (Next.js — TypeScript)

### 5.1 Folder Structure
```
frontend/
├── app/
│   ├── (auth)/
│   │   ├── login/page.tsx
│   │   └── register/page.tsx
│   ├── dashboard/page.tsx
│   ├── analyze/page.tsx
│   ├── fields/page.tsx
│   ├── weather/page.tsx
│   └── admin/page.tsx
├── components/
│   ├── ui/              ← shadcn/ui components (don't modify these)
│   ├── charts/          ← chart components
│   ├── soil/            ← soil-specific components
│   └── layout/          ← Sidebar, Navbar, etc.
├── lib/
│   ├── api.ts           ← all API calls (axios/fetch wrappers)
│   ├── auth.ts          ← JWT handling
│   └── utils.ts
├── stores/              ← Zustand stores
└── types/               ← TypeScript interfaces
```

### 5.2 Coding Standards
- **TypeScript strict mode ON.** No `any` types. If you're using `any`, you're doing it wrong.
- All API calls centralized in `lib/api.ts`. No fetch() calls scattered in components.
- Use React Query for all server state. No useState for data that comes from the server.
- Component files: PascalCase (`SoilResultCard.tsx`). Non-components: camelCase (`imageUtils.ts`)
- No inline styles. All styling via Tailwind classes.
- No CSS files per component unless absolutely necessary.
- Every page-level component wrapped in `<Suspense>` with a loading skeleton.
- Images served from MinIO via Next.js `<Image>` component for optimization.

---

## 6. Database Rules (PostgreSQL)

- All schema changes via Flyway migration files. File naming: `V1__create_users.sql`, `V2__create_farms.sql`
- Never use `Hibernate.hbm2ddl.auto=create` in any environment except local dev sandbox.
- All tables have `id UUID PRIMARY KEY DEFAULT gen_random_uuid()`, `created_at TIMESTAMPTZ`, `updated_at TIMESTAMPTZ`
- Soft delete only (add `deleted_at TIMESTAMPTZ` column). Never hard delete user data.
- Index every foreign key column. Index columns used in WHERE clauses.
- JSONB columns for flexible/schema-less data (SHAP values, weather snapshots, top-3 predictions)

---

## 7. Security Rules

- Passwords stored with bcrypt (cost factor 12). Never MD5, SHA1.
- JWT secret from environment variable. Never hardcoded.
- All file uploads scanned for MIME type server-side. Don't trust the Content-Type header.
- No sensitive data in logs (email, passwords, tokens).
- CORS configured explicitly for known origins only.
- Rate limiting on: login (5 req/min), image upload (10 req/min), ML inference (20 req/min)

---

## 8. Environment Variables

Each service has its own `.env` file. Template in `.env.example`. Actual `.env` in `.gitignore`.

```bash
# Spring Boot
DB_URL=jdbc:postgresql://localhost:5432/agripredict
DB_USERNAME=agriuser
DB_PASSWORD=secret
JWT_SECRET=your-256-bit-secret
MINIO_ENDPOINT=http://localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
OPENWEATHER_API_KEY=your-key
ML_SERVICE_URL=http://localhost:8000

# FastAPI
MODEL_DIR=./models
MINIO_ENDPOINT=http://localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin

# Next.js
NEXT_PUBLIC_API_URL=http://localhost:8080/api
```

---

## 9. What Will Get Your PR Rejected

- Missing input validation
- Commented-out code blocks
- Unused imports
- Magic numbers with no explanation (use named constants)
- Hardcoded credentials in code
- Catching exceptions and doing nothing with them
- Frontend calling FastAPI directly (must go through Spring Boot)
- Any model file committed to git
