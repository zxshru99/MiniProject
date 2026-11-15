from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from schemas.responses import HealthCheckResponse
from services.model_loader import model_manager
from routers import soil, yield_pred, weather, crop

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Load trained ML models and warm up caches
    print("[FastAPI] Starting AgriAI ML Service. Warming up models...")
    model_manager.load_all_models()
    yield
    # Shutdown
    print("[FastAPI] Shutting down AgriAI ML Service.")

app = FastAPI(
    title="AgriAI Machine Learning & Computer Vision Service",
    description="Inference API for Soil Classification, Moisture Estimation, Weather Dynamics, Crop Yield Prediction, and Recommender AI",
    version="2.0.0",
    lifespan=lifespan
)

# CORS Middleware allowing Spring Boot Gateway and Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Endpoint Routers
app.include_router(soil.router)
app.include_router(yield_pred.router)
app.include_router(weather.router)
app.include_router(crop.router)

@app.get("/health", response_model=HealthCheckResponse, tags=["Health"])
async def health_check():
    return HealthCheckResponse(
        status="HEALTHY",
        models_loaded=model_manager.initialized,
        service="fastapi-ml",
        version="2.0.0"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
