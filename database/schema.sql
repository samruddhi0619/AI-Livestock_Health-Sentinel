-- ==============================================================================
-- AI-LIVESTOCK HEALTH SENTINEL: PRODUCTION POSTGRESQL SCHEMA (WITH POSTGIS)
-- Smart India Hackathon 2026 (SIH26128)
-- Spatial Reference Identifier: EPSG:4326 (WGS 84)
-- ==============================================================================

-- 1. Enable Core PostgreSQL Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "postgis";

-- ------------------------------------------------------------------------------
-- 2. Enumerated Data Types
-- ------------------------------------------------------------------------------
DO $$ BEGIN
    CREATE TYPE user_role_enum AS ENUM ('FARMER', 'VETERINARIAN', 'ADMIN');
EXCEPTION WHEN duplicate_object THEN null; END $$;

DO $$ BEGIN
    CREATE TYPE animal_health_status_enum AS ENUM (
        'HEALTHY', 'SUSPECTED', 'CONFIRMED_SICK', 'UNDER_TREATMENT', 'RECOVERED', 'DECEASED'
    );
EXCEPTION WHEN duplicate_object THEN null; END $$;

DO $$ BEGIN
    CREATE TYPE animal_gender_enum AS ENUM ('Female', 'Male');
EXCEPTION WHEN duplicate_object THEN null; END $$;

DO $$ BEGIN
    CREATE TYPE vaccination_status_enum AS ENUM ('ADMINISTERED', 'SCHEDULED', 'OVERDUE', 'EXEMPTED');
EXCEPTION WHEN duplicate_object THEN null; END $$;

DO $$ BEGIN
    CREATE TYPE symptom_severity_enum AS ENUM ('MILD', 'MODERATE', 'SEVERE');
EXCEPTION WHEN duplicate_object THEN null; END $$;

DO $$ BEGIN
    CREATE TYPE prediction_type_enum AS ENUM (
        'IMAGE_VISION', 'SYMPTOM_TABULAR', 'ENVIRONMENTAL_RISK', 'MULTIMODAL_FUSION'
    );
EXCEPTION WHEN duplicate_object THEN null; END $$;

DO $$ BEGIN
    CREATE TYPE risk_tier_enum AS ENUM ('LOW', 'MODERATE', 'HIGH');
EXCEPTION WHEN duplicate_object THEN null; END $$;

DO $$ BEGIN
    CREATE TYPE disease_report_status_enum AS ENUM (
        'PENDING_REVIEW', 'VERIFIED_POSITIVE', 'REJECTED_FALSE_ALARM', 'RESOLVED_RECOVERED'
    );
EXCEPTION WHEN duplicate_object THEN null; END $$;

DO $$ BEGIN
    CREATE TYPE reporting_source_enum AS ENUM (
        'FARMER_SELF_REPORT', 'AI_SENTINEL_SCREENING', 'VETERINARIAN_FIELD_VISIT', 'COMMUNITY_PARAVET'
    );
EXCEPTION WHEN duplicate_object THEN null; END $$;

DO $$ BEGIN
    CREATE TYPE cluster_severity_enum AS ENUM ('WATCH', 'WARNING', 'EMERGENCY');
EXCEPTION WHEN duplicate_object THEN null; END $$;

DO $$ BEGIN
    CREATE TYPE cluster_status_enum AS ENUM ('ACTIVE', 'CONTAINED', 'DISSOLVED');
EXCEPTION WHEN duplicate_object THEN null; END $$;

DO $$ BEGIN
    CREATE TYPE alert_type_enum AS ENUM (
        'OUTBREAK_EARLY_WARNING', 'CLUSTER_PROXIMITY_ALERT', 'VACCINATION_OVERDUE',
        'CASE_TRIAGE_REQUIRED', 'HIGH_RISK_SYMPTOM'
    );
EXCEPTION WHEN duplicate_object THEN null; END $$;

DO $$ BEGIN
    CREATE TYPE alert_severity_enum AS ENUM ('INFO', 'MODERATE', 'CRITICAL');
EXCEPTION WHEN duplicate_object THEN null; END $$;

DO $$ BEGIN
    CREATE TYPE review_decision_enum AS ENUM (
        'CONFIRMED_POSITIVE', 'RULED_OUT_NEGATIVE', 'INCONCLUSIVE_RETEST', 'DIFFERENTIAL_DIAGNOSIS'
    );
EXCEPTION WHEN duplicate_object THEN null; END $$;

-- ------------------------------------------------------------------------------
-- 3. Table Definitions
-- ------------------------------------------------------------------------------

-- 3.1. Users Table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    fullname VARCHAR(100) NOT NULL,
    role user_role_enum NOT NULL DEFAULT 'FARMER',
    phone VARCHAR(20),
    district VARCHAR(50),
    taluka VARCHAR(50),
    village VARCHAR(50),
    license_number VARCHAR(50), -- Only for VETERINARIAN
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_users_district ON users(district);

-- 3.2. Animals Table (Supports ear-tag, QR token, demographics, owner, confirmed health status)
CREATE TABLE IF NOT EXISTS animals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    animal_id VARCHAR(50) UNIQUE NOT NULL, -- Human-readable ear tag (e.g. TAG-MH-2026-0042)
    qr_code_identifier VARCHAR(100) UNIQUE NOT NULL, -- Cryptographic QR payload token
    species VARCHAR(30) NOT NULL DEFAULT 'Cattle',
    breed VARCHAR(50) NOT NULL,
    age NUMERIC(4, 1) NOT NULL CHECK (age >= 0.0 AND age <= 35.0),
    gender animal_gender_enum NOT NULL,
    owner_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Ground truth health status - strictly separate from AI predictions
    health_status animal_health_status_enum NOT NULL DEFAULT 'HEALTHY',
    
    latitude NUMERIC(9, 6),
    longitude NUMERIC(9, 6),
    village VARCHAR(50),
    taluka VARCHAR(50),
    district VARCHAR(50),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_animals_tag_id ON animals(animal_id);
CREATE INDEX IF NOT EXISTS idx_animals_qr_code ON animals(qr_code_identifier);
CREATE INDEX IF NOT EXISTS idx_animals_owner ON animals(owner_id);
CREATE INDEX IF NOT EXISTS idx_animals_health_status ON animals(health_status);
CREATE INDEX IF NOT EXISTS idx_animals_district ON animals(district);

-- 3.3. Animal Health Records Table (Vitals and clinical checkups)
CREATE TABLE IF NOT EXISTS animal_health_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    animal_id UUID NOT NULL REFERENCES animals(id) ON DELETE CASCADE,
    recorded_by_id UUID REFERENCES users(id) ON DELETE SET NULL,
    body_temperature_c NUMERIC(4, 1) NOT NULL CHECK (body_temperature_c >= 34.0 AND body_temperature_c <= 44.0),
    heart_rate_bpm INTEGER CHECK (heart_rate_bpm IS NULL OR (heart_rate_bpm >= 30 AND heart_rate_bpm <= 200)),
    respiratory_rate_bpm INTEGER CHECK (respiratory_rate_bpm IS NULL OR (respiratory_rate_bpm >= 8 AND respiratory_rate_bpm <= 100)),
    appetite_score NUMERIC(2, 1) NOT NULL DEFAULT 1.0 CHECK (appetite_score >= 0.0 AND appetite_score <= 2.0),
    milk_yield_liters NUMERIC(4, 1) NOT NULL DEFAULT 0.0 CHECK (milk_yield_liters >= 0.0),
    activity_score NUMERIC(2, 1) NOT NULL DEFAULT 1.0 CHECK (activity_score >= 0.0 AND activity_score <= 2.0),
    rumination_hours NUMERIC(3, 1) CHECK (rumination_hours IS NULL OR (rumination_hours >= 0.0 AND rumination_hours <= 24.0)),
    notes TEXT,
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_health_records_animal ON animal_health_records(animal_id);
CREATE INDEX IF NOT EXISTS idx_health_records_recorded_at ON animal_health_records(recorded_at DESC);

-- 3.4. Vaccination Records Table
CREATE TABLE IF NOT EXISTS vaccination_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    animal_id UUID NOT NULL REFERENCES animals(id) ON DELETE CASCADE,
    vaccine_name VARCHAR(100) NOT NULL,
    batch_number VARCHAR(50),
    administered_date DATE NOT NULL,
    next_due_date DATE NOT NULL,
    administered_by_id UUID REFERENCES users(id) ON DELETE SET NULL,
    status vaccination_status_enum NOT NULL DEFAULT 'ADMINISTERED',
    certificate_url VARCHAR(255),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_vaccinations_animal ON vaccination_records(animal_id);
CREATE INDEX IF NOT EXISTS idx_vaccinations_due_date ON vaccination_records(next_due_date);
CREATE INDEX IF NOT EXISTS idx_vaccinations_status ON vaccination_records(status);

-- 3.5. Symptom Reports Table
CREATE TABLE IF NOT EXISTS symptom_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    health_record_id UUID UNIQUE NOT NULL REFERENCES animal_health_records(id) ON DELETE CASCADE,
    reported_by_id UUID REFERENCES users(id) ON DELETE SET NULL,
    symptoms JSONB NOT NULL, -- Array of reported symptoms e.g. ["skin_abnormalities", "fever"]
    onset_days_ago INTEGER NOT NULL DEFAULT 1 CHECK (onset_days_ago >= 0),
    severity_level symptom_severity_enum NOT NULL DEFAULT 'MILD',
    clinical_notes TEXT,
    reported_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_symptom_reports_record ON symptom_reports(health_record_id);

-- 3.6. Image Reports Table
CREATE TABLE IF NOT EXISTS image_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    health_record_id UUID UNIQUE NOT NULL REFERENCES animal_health_records(id) ON DELETE CASCADE,
    uploaded_by_id UUID REFERENCES users(id) ON DELETE SET NULL,
    image_url VARCHAR(500) NOT NULL,
    image_hash_sha256 VARCHAR(64),
    body_part VARCHAR(50) NOT NULL DEFAULT 'Full Body',
    quality_check_passed BOOLEAN NOT NULL DEFAULT TRUE,
    blur_laplacian_var NUMERIC(8, 2),
    brightness_score NUMERIC(5, 2),
    uploaded_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_image_reports_record ON image_reports(health_record_id);

-- 3.7. AI Predictions Table (STRICT SEPARATION: Probabilistic Inference, Never Confirmed Medical Truth)
CREATE TABLE IF NOT EXISTS ai_predictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    health_record_id UUID NOT NULL REFERENCES animal_health_records(id) ON DELETE CASCADE,
    symptom_report_id UUID REFERENCES symptom_reports(id) ON DELETE SET NULL,
    image_report_id UUID REFERENCES image_reports(id) ON DELETE SET NULL,
    prediction_type prediction_type_enum NOT NULL,
    predicted_condition VARCHAR(100) NOT NULL,
    confidence_score NUMERIC(5, 4) NOT NULL CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0),
    risk_level risk_tier_enum NOT NULL,
    risk_score NUMERIC(5, 2) NOT NULL CHECK (risk_score >= 0.0 AND risk_score <= 100.0),
    all_class_probabilities JSONB NOT NULL,
    contributing_symptoms JSONB, -- SHAP feature attributions
    model_version VARCHAR(50) NOT NULL,
    
    -- Permanent ethical constraint: strictly false
    is_veterinary_diagnosis BOOLEAN NOT NULL DEFAULT FALSE,
    disclaimer TEXT NOT NULL DEFAULT 'AI screening and risk triage tool only. Not a veterinary diagnosis. Confirmatory testing required.',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_ai_predictions_record ON ai_predictions(health_record_id);
CREATE INDEX IF NOT EXISTS idx_ai_predictions_risk ON ai_predictions(risk_level, risk_score DESC);

-- 3.8. Disease Clusters Table (Spatiotemporal Outbreak Surveillance)
CREATE TABLE IF NOT EXISTS disease_clusters (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cluster_code VARCHAR(50) UNIQUE NOT NULL, -- e.g. CLUSTER-MH-PUN-001
    disease_name VARCHAR(100) NOT NULL,
    center_latitude NUMERIC(9, 6) NOT NULL,
    center_longitude NUMERIC(9, 6) NOT NULL,
    radius_km NUMERIC(6, 2) NOT NULL CHECK (radius_km >= 0.0),
    case_count INTEGER NOT NULL DEFAULT 1 CHECK (case_count >= 1),
    severity cluster_severity_enum NOT NULL DEFAULT 'WARNING',
    status cluster_status_enum NOT NULL DEFAULT 'ACTIVE',
    district VARCHAR(50),
    detected_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_case_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_clusters_code ON disease_clusters(cluster_code);
CREATE INDEX IF NOT EXISTS idx_clusters_status ON disease_clusters(status);
CREATE INDEX IF NOT EXISTS idx_clusters_district ON disease_clusters(district);

-- 3.9. Disease Reports Table (Case Lifecycle Management)
CREATE TABLE IF NOT EXISTS disease_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    animal_id UUID NOT NULL REFERENCES animals(id) ON DELETE CASCADE,
    health_record_id UUID NOT NULL REFERENCES animal_health_records(id) ON DELETE CASCADE,
    ai_prediction_id UUID REFERENCES ai_predictions(id) ON DELETE SET NULL,
    reported_disease VARCHAR(100) NOT NULL,
    reporting_source reporting_source_enum NOT NULL DEFAULT 'FARMER_SELF_REPORT',
    latitude NUMERIC(9, 6) NOT NULL,
    longitude NUMERIC(9, 6) NOT NULL,
    status disease_report_status_enum NOT NULL DEFAULT 'PENDING_REVIEW',
    is_quarantine_required BOOLEAN NOT NULL DEFAULT FALSE,
    cluster_id UUID REFERENCES disease_clusters(id) ON DELETE SET NULL,
    reported_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_disease_reports_animal ON disease_reports(animal_id);
CREATE INDEX IF NOT EXISTS idx_disease_reports_status ON disease_reports(status);
CREATE INDEX IF NOT EXISTS idx_disease_reports_disease ON disease_reports(reported_disease);
CREATE INDEX IF NOT EXISTS idx_disease_reports_cluster ON disease_reports(cluster_id);
CREATE INDEX IF NOT EXISTS idx_disease_reports_date ON disease_reports(reported_at DESC);

-- 3.10. Alerts Table (Early Warning Notifications)
CREATE TABLE IF NOT EXISTS alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    recipient_id UUID REFERENCES users(id) ON DELETE CASCADE, -- NULL indicates broadcast to all district users
    alert_type alert_type_enum NOT NULL,
    severity alert_severity_enum NOT NULL DEFAULT 'INFO',
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    related_cluster_id UUID REFERENCES disease_clusters(id) ON DELETE SET NULL,
    related_animal_id UUID REFERENCES animals(id) ON DELETE SET NULL,
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_alerts_recipient ON alerts(recipient_id);
CREATE INDEX IF NOT EXISTS idx_alerts_is_read ON alerts(is_read);
CREATE INDEX IF NOT EXISTS idx_alerts_created_at ON alerts(created_at DESC);

-- 3.11. Veterinarian Reviews Table (Independent Clinical Adjudication)
CREATE TABLE IF NOT EXISTS veterinarian_reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    disease_report_id UUID UNIQUE NOT NULL REFERENCES disease_reports(id) ON DELETE CASCADE,
    veterinarian_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    review_decision review_decision_enum NOT NULL,
    clinical_diagnosis VARCHAR(100) NOT NULL,
    laboratory_test_type VARCHAR(100), -- PCR, ELISA, Bacterial Culture, None / Clinical Only
    laboratory_result VARCHAR(50),     -- POSITIVE, NEGATIVE, INCONCLUSIVE, PENDING
    treatment_plan TEXT,
    prescribed_medications TEXT,
    quarantine_order_issued BOOLEAN NOT NULL DEFAULT FALSE,
    quarantine_duration_days INTEGER NOT NULL DEFAULT 0 CHECK (quarantine_duration_days >= 0),
    revisit_date DATE,
    clinical_notes TEXT,
    reviewed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_vet_reviews_report ON veterinarian_reviews(disease_report_id);
CREATE INDEX IF NOT EXISTS idx_vet_reviews_vet ON veterinarian_reviews(veterinarian_id);
CREATE INDEX IF NOT EXISTS idx_vet_reviews_decision ON veterinarian_reviews(review_decision);
