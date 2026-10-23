-- =============================================================================
-- AgriAI Platform: V1 Database Migration
-- Generates core tables for Users, Farms, Fields, Soil Samples, and Predictions
-- =============================================================================

-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    full_name VARCHAR(150) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    role VARCHAR(50) DEFAULT 'FARMER' CHECK (role IN ('FARMER', 'RESEARCHER', 'ADMIN')),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Farms Table
CREATE TABLE IF NOT EXISTS farms (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    state VARCHAR(100) NOT NULL,
    district VARCHAR(100) NOT NULL,
    total_area_ha NUMERIC(10, 2),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Fields Table
CREATE TABLE IF NOT EXISTS fields (
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

-- 4. Soil Samples Table
CREATE TABLE IF NOT EXISTS soil_samples (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    field_id UUID NOT NULL REFERENCES fields(id) ON DELETE CASCADE,
    image_raw_url TEXT NOT NULL,
    image_processed_url TEXT,
    image_hash_sha256 VARCHAR(64) NOT NULL,
    blur_score NUMERIC(8, 2) DEFAULT 0.0,
    quality_status VARCHAR(20) DEFAULT 'VALID',
    captured_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. Predictions Table
CREATE TABLE IF NOT EXISTS predictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    soil_sample_id UUID NOT NULL REFERENCES soil_samples(id) ON DELETE CASCADE,
    field_id UUID NOT NULL REFERENCES fields(id) ON DELETE CASCADE,
    
    -- Soil Texture & Moisture
    soil_type VARCHAR(50) NOT NULL,
    soil_confidence NUMERIC(5, 4) NOT NULL,
    moisture_percentage NUMERIC(5, 2) NOT NULL,
    moisture_category VARCHAR(20) NOT NULL,
    
    -- Yield Prediction
    predicted_yield_kg_ha NUMERIC(10, 2) NOT NULL,
    yield_confidence_lower NUMERIC(10, 2) NOT NULL,
    yield_confidence_upper NUMERIC(10, 2) NOT NULL,
    
    -- Context
    crop_name VARCHAR(100) NOT NULL,
    temperature_c NUMERIC(5, 2),
    precipitation_mm NUMERIC(7, 2),
    
    -- Explainability
    gradcam_url TEXT,
    shap_top_factors JSONB,
    
    model_version VARCHAR(50) NOT NULL,
    inference_duration_ms INT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 6. Crop Catalog Seed Table
CREATE TABLE IF NOT EXISTS crop_catalog (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL UNIQUE,
    scientific_name VARCHAR(150),
    optimal_moisture_pct NUMERIC(5, 2) NOT NULL,
    water_requirement_mm NUMERIC(7, 2) NOT NULL,
    base_yield_kg_ha NUMERIC(10, 2) NOT NULL,
    growth_duration_days INT NOT NULL,
    suitable_soils TEXT[] NOT NULL
);

-- Insert Seed Crop Catalog
INSERT INTO crop_catalog (name, scientific_name, optimal_moisture_pct, water_requirement_mm, base_yield_kg_ha, growth_duration_days, suitable_soils)
VALUES 
('Wheat', 'Triticum aestivum', 26.0, 450.0, 4200.0, 120, ARRAY['Loamy', 'Clay', 'Sandy Loam']),
('Rice', 'Oryza sativa', 44.0, 1200.0, 3900.0, 135, ARRAY['Clay', 'Loamy']),
('Maize', 'Zea mays', 30.0, 500.0, 5300.0, 105, ARRAY['Loamy', 'Sandy Loam']),
('Chickpea', 'Cicer arietinum', 18.0, 300.0, 1500.0, 95, ARRAY['Sandy Loam', 'Sandy', 'Loamy']),
('Cotton', 'Gossypium hirsutum', 24.0, 650.0, 2200.0, 160, ARRAY['Clay', 'Loamy']),
('Mustard', 'Brassica juncea', 20.0, 280.0, 1700.0, 110, ARRAY['Loamy', 'Sandy'])
ON CONFLICT (name) DO NOTHING;

-- Optimization Indexes
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_fields_farm ON fields(farm_id);
CREATE INDEX IF NOT EXISTS idx_soil_samples_field ON soil_samples(field_id);
CREATE INDEX IF NOT EXISTS idx_predictions_field ON predictions(field_id);
CREATE INDEX IF NOT EXISTS idx_predictions_created ON predictions(created_at DESC);
