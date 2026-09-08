import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, List, Dict, Any
from sqlalchemy import (
    Column, String, Boolean, Float, Integer, Numeric, Text,
    DateTime, Date, ForeignKey, Enum as SQLEnum, JSON, Index, CheckConstraint
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

def get_utc_now():
    return datetime.now(timezone.utc)

# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------
class UserRole(str, Enum):
    FARMER = "FARMER"
    VETERINARIAN = "VETERINARIAN"
    ADMIN = "ADMIN"

class AnimalHealthStatus(str, Enum):
    HEALTHY = "HEALTHY"
    SUSPECTED = "SUSPECTED"
    CONFIRMED_SICK = "CONFIRMED_SICK"
    UNDER_TREATMENT = "UNDER_TREATMENT"
    RECOVERED = "RECOVERED"
    DECEASED = "DECEASED"

class AnimalGender(str, Enum):
    FEMALE = "Female"
    MALE = "Male"

class VaccinationStatus(str, Enum):
    ADMINISTERED = "ADMINISTERED"
    SCHEDULED = "SCHEDULED"
    OVERDUE = "OVERDUE"
    EXEMPTED = "EXEMPTED"

class SymptomSeverity(str, Enum):
    MILD = "MILD"
    MODERATE = "MODERATE"
    SEVERE = "SEVERE"

class PredictionType(str, Enum):
    IMAGE_VISION = "IMAGE_VISION"
    SYMPTOM_TABULAR = "SYMPTOM_TABULAR"
    ENVIRONMENTAL_RISK = "ENVIRONMENTAL_RISK"
    MULTIMODAL_FUSION = "MULTIMODAL_FUSION"

class RiskTier(str, Enum):
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"

class DiseaseReportStatus(str, Enum):
    PENDING_REVIEW = "PENDING_REVIEW"
    VERIFIED_POSITIVE = "VERIFIED_POSITIVE"
    REJECTED_FALSE_ALARM = "REJECTED_FALSE_ALARM"
    RESOLVED_RECOVERED = "RESOLVED_RECOVERED"

class ReportingSource(str, Enum):
    FARMER_SELF_REPORT = "FARMER_SELF_REPORT"
    AI_SENTINEL_SCREENING = "AI_SENTINEL_SCREENING"
    VETERINARIAN_FIELD_VISIT = "VETERINARIAN_FIELD_VISIT"
    COMMUNITY_PARAVET = "COMMUNITY_PARAVET"

class ClusterSeverity(str, Enum):
    WATCH = "WATCH"
    WARNING = "WARNING"
    EMERGENCY = "EMERGENCY"

class ClusterStatus(str, Enum):
    ACTIVE = "ACTIVE"
    CONTAINED = "CONTAINED"
    DISSOLVED = "DISSOLVED"

class AlertType(str, Enum):
    OUTBREAK_EARLY_WARNING = "OUTBREAK_EARLY_WARNING"
    CLUSTER_PROXIMITY_ALERT = "CLUSTER_PROXIMITY_ALERT"
    VACCINATION_OVERDUE = "VACCINATION_OVERDUE"
    CASE_TRIAGE_REQUIRED = "CASE_TRIAGE_REQUIRED"
    HIGH_RISK_SYMPTOM = "HIGH_RISK_SYMPTOM"

class AlertSeverity(str, Enum):
    INFO = "INFO"
    MODERATE = "MODERATE"
    CRITICAL = "CRITICAL"

class ReviewDecision(str, Enum):
    CONFIRMED_POSITIVE = "CONFIRMED_POSITIVE"
    RULED_OUT_NEGATIVE = "RULED_OUT_NEGATIVE"
    INCONCLUSIVE_RETEST = "INCONCLUSIVE_RETEST"
    DIFFERENTIAL_DIAGNOSIS = "DIFFERENTIAL_DIAGNOSIS"

# ---------------------------------------------------------------------------
# 1. Users Table
# ---------------------------------------------------------------------------
class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    fullname = Column(String(100), nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.FARMER, index=True)
    phone = Column(String(20), nullable=True)
    district = Column(String(50), nullable=True)
    taluka = Column(String(50), nullable=True)
    village = Column(String(50), nullable=True)
    license_number = Column(String(50), nullable=True) # For VETERINARIAN
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now, nullable=False)

    # Relationships
    owned_animals = relationship("Animal", back_populates="owner", cascade="all, delete-orphan")
    health_records_entered = relationship("AnimalHealthRecord", back_populates="recorded_by")
    vaccinations_administered = relationship("VaccinationRecord", back_populates="administered_by")
    veterinary_reviews = relationship("VeterinarianReview", back_populates="veterinarian")
    alerts = relationship("Alert", back_populates="recipient")

# ---------------------------------------------------------------------------
# 2. Animals Table
# ---------------------------------------------------------------------------
class Animal(Base):
    __tablename__ = "animals"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    animal_id = Column(String(50), unique=True, nullable=False, index=True) # Human readable ear-tag
    qr_code_identifier = Column(String(100), unique=True, nullable=False, index=True) # QR payload token
    species = Column(String(30), default="Cattle", nullable=False)
    breed = Column(String(50), nullable=False)
    age = Column(Numeric(4, 1), nullable=False)
    gender = Column(SQLEnum(AnimalGender), nullable=False)
    owner_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Confirmed ground-truth health status - NEVER overwritten automatically by AI
    health_status = Column(SQLEnum(AnimalHealthStatus), default=AnimalHealthStatus.HEALTHY, nullable=False, index=True)
    
    latitude = Column(Numeric(9, 6), nullable=True)
    longitude = Column(Numeric(9, 6), nullable=True)
    village = Column(String(50), nullable=True)
    taluka = Column(String(50), nullable=True)
    district = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now, nullable=False)

    # Relationships
    owner = relationship("User", back_populates="owned_animals")
    health_records = relationship("AnimalHealthRecord", back_populates="animal", cascade="all, delete-orphan")
    vaccinations = relationship("VaccinationRecord", back_populates="animal", cascade="all, delete-orphan")
    disease_reports = relationship("DiseaseReport", back_populates="animal", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="related_animal")

# ---------------------------------------------------------------------------
# 3. Animal Health Records Table
# ---------------------------------------------------------------------------
class AnimalHealthRecord(Base):
    __tablename__ = "animal_health_records"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    animal_id = Column(String(36), ForeignKey("animals.id", ondelete="CASCADE"), nullable=False, index=True)
    recorded_by_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    body_temperature_c = Column(Numeric(4, 1), nullable=False) # e.g. 38.5 C
    heart_rate_bpm = Column(Integer, nullable=True)
    respiratory_rate_bpm = Column(Integer, nullable=True)
    appetite_score = Column(Numeric(2, 1), nullable=False, default=1.0) # 0=None, 1=Normal, 2=High
    milk_yield_liters = Column(Numeric(4, 1), nullable=False, default=0.0)
    activity_score = Column(Numeric(2, 1), nullable=False, default=1.0) # 0=Low, 1=Normal, 2=High
    rumination_hours = Column(Numeric(3, 1), nullable=True)
    notes = Column(Text, nullable=True)
    recorded_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False, index=True)

    # Relationships
    animal = relationship("Animal", back_populates="health_records")
    recorded_by = relationship("User", back_populates="health_records_entered")
    symptom_report = relationship("SymptomReport", back_populates="health_record", uselist=False, cascade="all, delete-orphan")
    image_report = relationship("ImageReport", back_populates="health_record", uselist=False, cascade="all, delete-orphan")
    ai_predictions = relationship("AIPrediction", back_populates="health_record", cascade="all, delete-orphan")
    disease_reports = relationship("DiseaseReport", back_populates="health_record", cascade="all, delete-orphan")

# ---------------------------------------------------------------------------
# 4. Vaccination Records Table
# ---------------------------------------------------------------------------
class VaccinationRecord(Base):
    __tablename__ = "vaccination_records"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    animal_id = Column(String(36), ForeignKey("animals.id", ondelete="CASCADE"), nullable=False, index=True)
    vaccine_name = Column(String(100), nullable=False) # e.g. Lumpy Skin Disease Homologous Neethling
    batch_number = Column(String(50), nullable=True)
    administered_date = Column(Date, nullable=False)
    next_due_date = Column(Date, nullable=False, index=True)
    administered_by_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    status = Column(SQLEnum(VaccinationStatus), default=VaccinationStatus.ADMINISTERED, nullable=False)
    certificate_url = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)

    # Relationships
    animal = relationship("Animal", back_populates="vaccinations")
    administered_by = relationship("User", back_populates="vaccinations_administered")

# ---------------------------------------------------------------------------
# 5. Symptom Reports Table
# ---------------------------------------------------------------------------
class SymptomReport(Base):
    __tablename__ = "symptom_reports"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    health_record_id = Column(String(36), ForeignKey("animal_health_records.id", ondelete="CASCADE"), unique=True, nullable=False)
    reported_by_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    symptoms = Column(JSON, nullable=False) # List of reported symptom keys e.g. ["skin_abnormalities", "fever"]
    onset_days_ago = Column(Integer, default=1, nullable=False)
    severity_level = Column(SQLEnum(SymptomSeverity), default=SymptomSeverity.MILD, nullable=False)
    clinical_notes = Column(Text, nullable=True)
    reported_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)

    # Relationships
    health_record = relationship("AnimalHealthRecord", back_populates="symptom_report")
    ai_predictions = relationship("AIPrediction", back_populates="symptom_report")

# ---------------------------------------------------------------------------
# 6. Image Reports Table
# ---------------------------------------------------------------------------
class ImageReport(Base):
    __tablename__ = "image_reports"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    health_record_id = Column(String(36), ForeignKey("animal_health_records.id", ondelete="CASCADE"), unique=True, nullable=False)
    uploaded_by_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    image_url = Column(String(500), nullable=False)
    image_hash_sha256 = Column(String(64), nullable=True)
    body_part = Column(String(50), default="Full Body", nullable=False) # Full Body, Flank/Skin, Muzzle, Hooves
    quality_check_passed = Column(Boolean, default=True, nullable=False)
    blur_laplacian_var = Column(Numeric(8, 2), nullable=True)
    brightness_score = Column(Numeric(5, 2), nullable=True)
    uploaded_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)

    # Relationships
    health_record = relationship("AnimalHealthRecord", back_populates="image_report")
    ai_predictions = relationship("AIPrediction", back_populates="image_report")

# ---------------------------------------------------------------------------
# 7. AI Predictions Table (STRICT SEPARATION: Probabilistic, NOT Final Diagnosis)
# ---------------------------------------------------------------------------
class AIPrediction(Base):
    __tablename__ = "ai_predictions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    health_record_id = Column(String(36), ForeignKey("animal_health_records.id", ondelete="CASCADE"), nullable=False, index=True)
    symptom_report_id = Column(String(36), ForeignKey("symptom_reports.id", ondelete="SET NULL"), nullable=True)
    image_report_id = Column(String(36), ForeignKey("image_reports.id", ondelete="SET NULL"), nullable=True)
    
    prediction_type = Column(SQLEnum(PredictionType), nullable=False) # IMAGE_VISION, SYMPTOM_TABULAR, etc.
    predicted_condition = Column(String(100), nullable=False) # e.g. Possible Lumpy Skin Disease
    confidence_score = Column(Numeric(5, 4), nullable=False) # 0.0000 to 1.0000
    risk_level = Column(SQLEnum(RiskTier), nullable=False) # LOW, MODERATE, HIGH
    risk_score = Column(Numeric(5, 2), nullable=False) # 0.00 to 100.00
    all_class_probabilities = Column(JSON, nullable=False) # {"LSD": 0.88, "Healthy": 0.05, ...}
    contributing_symptoms = Column(JSON, nullable=True) # SHAP feature attributions
    model_version = Column(String(50), nullable=False) # e.g. MobileNetV3-v1.0
    
    # Permanent ethical constraint: locked to False
    is_veterinary_diagnosis = Column(Boolean, default=False, nullable=False)
    disclaimer = Column(
        Text,
        default="AI screening and risk triage tool only. Not a veterinary diagnosis. Confirmatory testing required.",
        nullable=False
    )
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)

    # Relationships
    health_record = relationship("AnimalHealthRecord", back_populates="ai_predictions")
    symptom_report = relationship("SymptomReport", back_populates="ai_predictions")
    image_report = relationship("ImageReport", back_populates="ai_predictions")
    disease_reports = relationship("DiseaseReport", back_populates="ai_prediction")

# ---------------------------------------------------------------------------
# 8. Disease Reports Table (Case Lifecycle)
# ---------------------------------------------------------------------------
class DiseaseReport(Base):
    __tablename__ = "disease_reports"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    animal_id = Column(String(36), ForeignKey("animals.id", ondelete="CASCADE"), nullable=False, index=True)
    health_record_id = Column(String(36), ForeignKey("animal_health_records.id", ondelete="CASCADE"), nullable=False)
    ai_prediction_id = Column(String(36), ForeignKey("ai_predictions.id", ondelete="SET NULL"), nullable=True)
    
    reported_disease = Column(String(100), nullable=False, index=True)
    reporting_source = Column(SQLEnum(ReportingSource), default=ReportingSource.FARMER_SELF_REPORT, nullable=False)
    latitude = Column(Numeric(9, 6), nullable=False)
    longitude = Column(Numeric(9, 6), nullable=False)
    
    # Case lifecycle state
    status = Column(SQLEnum(DiseaseReportStatus), default=DiseaseReportStatus.PENDING_REVIEW, nullable=False, index=True)
    is_quarantine_required = Column(Boolean, default=False, nullable=False)
    cluster_id = Column(String(36), ForeignKey("disease_clusters.id", ondelete="SET NULL"), nullable=True, index=True)
    
    reported_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now, nullable=False)

    # Relationships
    animal = relationship("Animal", back_populates="disease_reports")
    health_record = relationship("AnimalHealthRecord", back_populates="disease_reports")
    ai_prediction = relationship("AIPrediction", back_populates="disease_reports")
    cluster = relationship("DiseaseCluster", back_populates="cases")
    veterinarian_review = relationship("VeterinarianReview", back_populates="disease_report", uselist=False, cascade="all, delete-orphan")

# ---------------------------------------------------------------------------
# 9. Disease Clusters Table (Spatiotemporal DBSCAN)
# ---------------------------------------------------------------------------
class DiseaseCluster(Base):
    __tablename__ = "disease_clusters"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    cluster_code = Column(String(50), unique=True, nullable=False, index=True) # e.g. CLUSTER-MH-PUN-001
    disease_name = Column(String(100), nullable=False)
    center_latitude = Column(Numeric(9, 6), nullable=False)
    center_longitude = Column(Numeric(9, 6), nullable=False)
    radius_km = Column(Numeric(6, 2), nullable=False)
    case_count = Column(Integer, default=1, nullable=False)
    severity = Column(SQLEnum(ClusterSeverity), default=ClusterSeverity.WARNING, nullable=False)
    status = Column(SQLEnum(ClusterStatus), default=ClusterStatus.ACTIVE, nullable=False, index=True)
    district = Column(String(50), nullable=True)
    detected_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)
    last_case_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)

    # Relationships
    cases = relationship("DiseaseReport", back_populates="cluster")
    alerts = relationship("Alert", back_populates="related_cluster")

# ---------------------------------------------------------------------------
# 10. Alerts Table (Early Warning Notifications)
# ---------------------------------------------------------------------------
class Alert(Base):
    __tablename__ = "alerts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    recipient_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True) # Null for broadcast
    alert_type = Column(SQLEnum(AlertType), nullable=False)
    severity = Column(SQLEnum(AlertSeverity), default=AlertSeverity.INFO, nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    related_cluster_id = Column(String(36), ForeignKey("disease_clusters.id", ondelete="SET NULL"), nullable=True)
    related_animal_id = Column(String(36), ForeignKey("animals.id", ondelete="SET NULL"), nullable=True)
    is_read = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False, index=True)

    # Relationships
    recipient = relationship("User", back_populates="alerts")
    related_cluster = relationship("DiseaseCluster", back_populates="alerts")
    related_animal = relationship("Animal", back_populates="alerts")

# ---------------------------------------------------------------------------
# 11. Veterinarian Reviews Table (Independent Clinical Adjudication)
# ---------------------------------------------------------------------------
class VeterinarianReview(Base):
    __tablename__ = "veterinarian_reviews"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    disease_report_id = Column(String(36), ForeignKey("disease_reports.id", ondelete="CASCADE"), unique=True, nullable=False)
    veterinarian_id = Column(String(36), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    
    review_decision = Column(SQLEnum(ReviewDecision), nullable=False) # CONFIRMED_POSITIVE, RULED_OUT_NEGATIVE...
    clinical_diagnosis = Column(String(100), nullable=False) # Professional diagnosis text
    laboratory_test_type = Column(String(100), nullable=True) # PCR, ELISA, None
    laboratory_result = Column(String(50), nullable=True) # POSITIVE, NEGATIVE, PENDING
    treatment_plan = Column(Text, nullable=True)
    prescribed_medications = Column(Text, nullable=True)
    quarantine_order_issued = Column(Boolean, default=False, nullable=False)
    quarantine_duration_days = Column(Integer, default=0, nullable=False)
    revisit_date = Column(Date, nullable=True)
    clinical_notes = Column(Text, nullable=True)
    reviewed_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)

    # Relationships
    disease_report = relationship("DiseaseReport", back_populates="veterinarian_review")
    veterinarian = relationship("User", back_populates="veterinary_reviews")
