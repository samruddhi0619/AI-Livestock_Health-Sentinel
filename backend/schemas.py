import uuid
from datetime import datetime, date
from enum import Enum
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field, ConfigDict, field_validator

# ---------------------------------------------------------------------------
# Enums
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

class ReviewDecision(str, Enum):
    CONFIRMED_POSITIVE = "CONFIRMED_POSITIVE"
    RULED_OUT_NEGATIVE = "RULED_OUT_NEGATIVE"
    INCONCLUSIVE_RETEST = "INCONCLUSIVE_RETEST"
    DIFFERENTIAL_DIAGNOSIS = "DIFFERENTIAL_DIAGNOSIS"

# ---------------------------------------------------------------------------
# User Schemas
# ---------------------------------------------------------------------------
class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Unique login handle")
    password: str = Field(..., min_length=6, description="Password with minimum 6 characters")
    fullname: str = Field(..., min_length=2, max_length=100)
    role: UserRole = Field(default=UserRole.FARMER, description="FARMER, VETERINARIAN, or ADMIN")
    phone: Optional[str] = Field(None, max_length=20)
    district: Optional[str] = Field(None, max_length=50)
    taluka: Optional[str] = Field(None, max_length=50)
    village: Optional[str] = Field(None, max_length=50)
    license_number: Optional[str] = Field(None, description="Required for VETERINARIAN")

    @field_validator("role", mode="before")
    @classmethod
    def normalize_role(cls, v):
        if isinstance(v, str):
            v_clean = v.strip().upper()
            if v_clean in ["FARMER", "VETERINARIAN", "ADMIN"]:
                return UserRole(v_clean)
            if v_clean == "OFFICER": # Map legacy role to ADMIN
                return UserRole.ADMIN
        return v

class UserLogin(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    id: str
    username: str
    fullname: str
    role: UserRole
    phone: Optional[str] = None
    district: Optional[str] = None
    taluka: Optional[str] = None
    village: Optional[str] = None
    license_number: Optional[str] = None
    is_active: bool
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut

# ---------------------------------------------------------------------------
# Animal Schemas
# ---------------------------------------------------------------------------
class AnimalCreate(BaseModel):
    animal_id: Optional[str] = Field(None, description="Ear tag identifier (auto-generated if omitted)")
    qr_code_identifier: Optional[str] = Field(None, description="QR code payload identifier")
    species: str = Field(default="Cattle", max_length=30)
    breed: str = Field(..., max_length=50)
    age: float = Field(..., ge=0.0, le=35.0, description="Age in years")
    gender: AnimalGender
    health_history: Optional[str] = "None"
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)
    village: Optional[str] = None
    taluka: Optional[str] = None
    district: Optional[str] = None

class AnimalOut(BaseModel):
    id: str
    animal_id: str
    qr_code_identifier: str
    species: str
    breed: str
    age: float
    gender: AnimalGender
    owner_id: str
    health_status: AnimalHealthStatus
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    village: Optional[str] = None
    taluka: Optional[str] = None
    district: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class AnimalHealthStatusUpdate(BaseModel):
    health_status: AnimalHealthStatus
    clinical_reason: Optional[str] = Field(None, description="Reason for status change")

# ---------------------------------------------------------------------------
# Health Record Schemas
# ---------------------------------------------------------------------------
class HealthRecordCreate(BaseModel):
    animal_id: str
    body_temperature_c: float = Field(..., ge=34.0, le=44.0, description="Rectal temperature in Celsius")
    heart_rate_bpm: Optional[int] = Field(None, ge=30, le=200)
    respiratory_rate_bpm: Optional[int] = Field(None, ge=8, le=100)
    appetite_score: float = Field(1.0, ge=0.0, le=2.0, description="0=None, 1=Normal, 2=High")
    milk_yield_liters: float = Field(0.0, ge=0.0)
    activity_score: float = Field(1.0, ge=0.0, le=2.0, description="0=Lethargic, 1=Normal, 2=High")
    rumination_hours: Optional[float] = Field(None, ge=0.0, le=24.0)
    notes: Optional[str] = None

class HealthRecordOut(BaseModel):
    id: str
    animal_id: str
    recorded_by_id: Optional[str] = None
    body_temperature_c: float
    heart_rate_bpm: Optional[int] = None
    respiratory_rate_bpm: Optional[int] = None
    appetite_score: float
    milk_yield_liters: float
    activity_score: float
    rumination_hours: Optional[float] = None
    notes: Optional[str] = None
    recorded_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

# ---------------------------------------------------------------------------
# Vaccination Schemas
# ---------------------------------------------------------------------------
class VaccinationCreate(BaseModel):
    animal_id: str
    vaccine_name: str = Field(..., max_length=100)
    batch_number: Optional[str] = None
    administered_date: date
    next_due_date: date
    status: VaccinationStatus = Field(default=VaccinationStatus.ADMINISTERED)
    certificate_url: Optional[str] = None

class VaccinationOut(BaseModel):
    id: str
    animal_id: str
    vaccine_name: str
    batch_number: Optional[str] = None
    administered_date: date
    next_due_date: date
    administered_by_id: Optional[str] = None
    status: VaccinationStatus
    certificate_url: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

# ---------------------------------------------------------------------------
# Symptom Report Schemas
# ---------------------------------------------------------------------------
class SymptomReportCreate(BaseModel):
    health_record_id: str
    symptoms: List[str] = Field(..., min_length=1, description="List of observed symptoms")
    onset_days_ago: int = Field(1, ge=0)
    severity_level: SymptomSeverity = Field(default=SymptomSeverity.MILD)
    clinical_notes: Optional[str] = None

# ---------------------------------------------------------------------------
# Disease Report & Veterinarian Review Schemas
# ---------------------------------------------------------------------------
class DiseaseReportCreate(BaseModel):
    animal_id: str
    health_record_id: str
    reported_disease: str
    reporting_source: ReportingSource = Field(default=ReportingSource.FARMER_SELF_REPORT)
    latitude: float
    longitude: float

class VeterinarianReviewCreate(BaseModel):
    disease_report_id: str
    review_decision: ReviewDecision
    clinical_diagnosis: str = Field(..., min_length=3, max_length=100)
    laboratory_test_type: Optional[str] = None
    laboratory_result: Optional[str] = None
    treatment_plan: Optional[str] = None
    prescribed_medications: Optional[str] = None
    quarantine_order_issued: bool = False
    quarantine_duration_days: int = Field(0, ge=0)
    revisit_date: Optional[date] = None
    clinical_notes: Optional[str] = None

# ---------------------------------------------------------------------------
# Health-Check Schemas
# ---------------------------------------------------------------------------
class HealthCheckResponse(BaseModel):
    status: str
    project: str
    version: str
    environment: str
    timestamp: datetime

class DatabaseHealthResponse(BaseModel):
    status: str
    database_connected: bool
    database_mode: str
    engine_dialect: str
    latency_ms: Optional[float] = None
    message: str

# ---------------------------------------------------------------------------
# Independent Machine Learning Analysis Request Schemas
# ---------------------------------------------------------------------------
class ImageAnalysisUrlRequest(BaseModel):
    image_url: Optional[str] = Field(None, description="Public HTTP URL or local static path of cattle image")
    image_base64: Optional[str] = Field(None, description="Base64 data URI of the image")
    low_threshold: Optional[float] = Field(0.30, ge=0.0, le=1.0)
    high_threshold: Optional[float] = Field(0.70, ge=0.0, le=1.0)

class SymptomAnalysisRequest(BaseModel):
    symptoms: List[str] = Field(..., min_length=1, description="List of observed symptoms, e.g. ['skin_abnormalities', 'fever']")
    age: Optional[float] = Field(4.0, ge=0.0, le=35.0, description="Age of animal in years")
    breed: Optional[str] = Field("gir", description="Breed name (gir, sahiwal, holstein_friesian, jersey, etc.)")
    gender: Optional[str] = Field("female", description="female or male")
    history: Optional[str] = Field("none", description="none, previous_illness, or chronic")
    vaccination: Optional[str] = Field("not_vaccinated", description="vaccinated or not_vaccinated")
    low_threshold: Optional[float] = Field(35.0, ge=0.0, le=100.0)
    high_threshold: Optional[float] = Field(65.0, ge=0.0, le=100.0)

class EnvironmentalAnalysisRequest(BaseModel):
    latitude: float = Field(20.59, ge=-90.0, le=90.0, description="Latitude coordinate")
    longitude: float = Field(78.96, ge=-180.0, le=180.0, description="Longitude coordinate")
    temperature_c: float = Field(28.0, ge=-20.0, le=60.0, description="Ambient temperature in Celsius")
    humidity_percent: float = Field(65.0, ge=0.0, le=100.0, description="Relative humidity %")
    rainfall_mm: float = Field(20.0, ge=0.0, le=500.0, description="Recent precipitation in mm")
    elevation_m: Optional[float] = Field(180.0, ge=-100.0, le=6000.0, description="Elevation above sea level in meters")
    cattle_density: Optional[float] = Field(15000.0, ge=0.0, description="Local cattle population density per sq km")
    buffalo_density: Optional[float] = Field(3000.0, ge=0.0, description="Local buffalo population density per sq km")
    dominant_land_cover: Optional[int] = Field(4, ge=1, le=12, description="Categorical land cover index (1 to 12)")

# ---------------------------------------------------------------------------
# Multi-Modal Livestock Health Risk Engine Schemas
# ---------------------------------------------------------------------------
class CustomWeightsSchema(BaseModel):
    image: Optional[float] = Field(None, ge=0.0, le=1.0, description="Weight for Image AI risk (0.0 to 1.0)")
    symptoms: Optional[float] = Field(None, ge=0.0, le=1.0, description="Weight for Symptom AI risk (0.0 to 1.0)")
    environment: Optional[float] = Field(None, ge=0.0, le=1.0, description="Weight for Environmental risk (0.0 to 1.0)")
    context: Optional[float] = Field(None, ge=0.0, le=1.0, description="Weight for Health/Vaccination context (0.0 to 1.0)")

class MultiModalRiskRequest(BaseModel):
    image_risk_score: Optional[float] = Field(None, ge=0.0, le=100.0, description="0-100 Image AI risk score from visual screening")
    symptom_risk_score: Optional[float] = Field(None, ge=0.0, le=100.0, description="0-100 Symptom AI risk score from clinical signs")
    environmental_risk_score: Optional[float] = Field(None, ge=0.0, le=100.0, description="0-100 Geospatial / bioclimatic risk score")
    vaccination_status: Optional[str] = Field("not_vaccinated", description="vaccinated, partially_vaccinated, overdue, or not_vaccinated")
    health_history: Optional[Union[str, List[str]]] = Field("none", description="Previous medical history or known prior conditions")
    custom_weights: Optional[CustomWeightsSchema] = Field(None, description="Optional per-request override weights")

class ContributingFactorDetail(BaseModel):
    factor: str
    modality_key: str
    raw_score: float
    weight: float
    weighted_contribution: float
    percentage_of_total_risk: float
    description: str

class IndividualModelScores(BaseModel):
    image_risk: Optional[float] = None
    symptom_risk: Optional[float] = None
    environmental_risk: Optional[float] = None
    context_risk: Optional[float] = None

class MultiModalRiskResponse(BaseModel):
    final_risk_score: float
    risk_level: str
    contributing_factors: List[ContributingFactorDetail]
    individual_model_scores: IndividualModelScores
    risk_thresholds: Dict[str, str]
    calculation_details: Dict[str, Any]
    is_veterinary_diagnosis: bool = False
    disclaimer: str

# ---------------------------------------------------------------------------
# Livestock Health Reporting & Disease Surveillance Schemas
# ---------------------------------------------------------------------------
class LocationPayload(BaseModel):
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0, description="Device GPS latitude")
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0, description="Device GPS longitude")
    share_location: bool = Field(True, description="Whether farmer authorizes location sharing")
    location_precision: str = Field("approximate", description="'approximate' or 'authorized_exact'")
    village: Optional[str] = Field(None, description="Village name")
    taluka: Optional[str] = Field(None, description="Taluka / sub-district name")
    district: Optional[str] = Field(None, description="District name")

class HealthReportCreate(BaseModel):
    animal_id: str = Field(..., description="Unique ear-tag identifier or animal database ID")
    symptoms: List[str] = Field(..., min_length=1, description="List of observed symptoms, e.g. ['skin_abnormalities', 'fever']")
    image_url: Optional[str] = Field(None, description="Public URL or static path of uploaded animal photo")
    image_base64: Optional[str] = Field(None, description="Base64 data URI of animal photo")
    location: Optional[LocationPayload] = Field(None, description="Location data and sharing authorization")
    body_temperature_c: Optional[float] = Field(38.5, ge=30.0, le=45.0, description="Measured body temperature in Celsius")
    appetite_score: Optional[float] = Field(1.0, ge=0.0, le=2.0, description="0=None, 1=Normal, 2=High")
    milk_yield_liters: Optional[float] = Field(0.0, ge=0.0, le=100.0, description="Daily milk yield in liters")
    activity_score: Optional[float] = Field(1.0, ge=0.0, le=2.0, description="0=Lethargic/Low, 1=Normal, 2=Restless/High")
    clinical_notes: Optional[str] = Field(None, description="Optional observations by the farmer or clinician")

class HealthReportOut(BaseModel):
    report_id: str
    animal_id: str
    animal_tag: str
    species: str
    breed: str
    owner_id: str
    owner_name: str
    recorded_by: str
    symptoms: List[str]
    image_url: Optional[str] = None
    location: Dict[str, Any]
    location_access_level: str
    ai_analyses: Dict[str, Any]
    multi_modal_risk: Dict[str, Any]
    is_surveillance_triggered: bool
    surveillance_report_id: Optional[str] = None
    animal_health_status: str
    recorded_at: str
    is_veterinary_diagnosis: bool = False
    disclaimer: str

# ---------------------------------------------------------------------------
# Spatio-Temporal Potential Disease Cluster Schemas
# ---------------------------------------------------------------------------
class ClusterCentroid(BaseModel):
    latitude: float
    longitude: float

class ClusterDetectionRequest(BaseModel):
    geo_radius_km: Optional[float] = Field(None, gt=0, le=100.0, description="DBSCAN spatial radius in km")
    min_reports: Optional[int] = Field(None, ge=2, le=50, description="Minimum high-risk reports required to form cluster")
    time_window_days: Optional[int] = Field(None, ge=1, le=90, description="Temporal window in days (default: 14 days)")
    disease: Optional[str] = Field(None, description="Optional disease filter, e.g. 'Foot-and-Mouth Disease'")

class ClusterOut(BaseModel):
    id: str
    cluster_id: str
    cluster_label: str = Field("Potential Disease Cluster", description="Designation: never labeled as confirmed outbreak")
    pattern_type: str = Field("Emerging Risk Pattern", description="Epidemiological pattern category")
    disease: str
    disease_name: str
    risk_level: str
    average_risk_score: float
    report_count: int
    cases_count: int
    unique_farms_count: int
    affected_farms: List[str] = []
    affected_cases: List[str] = []
    affected_reports: List[str] = []
    affected_animal_ids: List[str] = []
    centroid: ClusterCentroid
    radius_km: float
    eps_threshold_km: float
    min_reports_threshold: int
    time_window_days: int
    temporal_span_days: int
    earliest_report_at: str
    latest_report_at: str
    villages: List[str] = []
    talukas: List[str] = []
    districts: List[str] = []
    status: str
    is_confirmed_outbreak: bool = False
    is_veterinary_diagnosis: bool = False
    disclaimer: str
    detected_at: str

class ClusterListResponse(BaseModel):
    total_clusters: int
    clusters: List[ClusterOut]
    summary: Dict[str, Any]
    query_parameters: Dict[str, Any]
    disclaimer: str

# ---------------------------------------------------------------------------
# In-App Role-Specific Alert Schemas
# ---------------------------------------------------------------------------
class AlertSeverityEnum(str, Enum):
    INFO = "INFO"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class AlertTypeEnum(str, Enum):
    # Farmer Alerts
    HIGH_RISK_ASSESSMENT = "HIGH_RISK_ASSESSMENT"
    VACCINATION_DUE = "VACCINATION_DUE"
    REGIONAL_DISEASE_RISK = "REGIONAL_DISEASE_RISK"
    
    # Veterinarian Alerts
    HIGH_RISK_REPORT_REVIEW = "HIGH_RISK_REPORT_REVIEW"
    POTENTIAL_DISEASE_CLUSTER = "POTENTIAL_DISEASE_CLUSTER"
    
    # Admin Alerts
    EMERGING_CLUSTERS = "EMERGING_CLUSTERS"
    CRITICAL_RISK_PATTERNS = "CRITICAL_RISK_PATTERNS"

class RelatedEntityPayload(BaseModel):
    animal_id: Optional[str] = None
    animal_tag: Optional[str] = None
    health_report_id: Optional[str] = None
    disease_report_id: Optional[str] = None
    cluster_id: Optional[str] = None
    disease: Optional[str] = None
    vaccination_id: Optional[str] = None
    village: Optional[str] = None
    taluka: Optional[str] = None
    district: Optional[str] = None

class AlertOut(BaseModel):
    id: str
    recipient_role: str
    recipient_id: Optional[str] = None
    alert_type: str
    severity: str
    title: str
    message: str
    timestamp: str
    created_at: Optional[str] = None
    related_entity: RelatedEntityPayload
    recommended_action: str
    is_read: bool = False
    is_dismissed: bool = False
    is_veterinary_prescription: bool = False
    safety_disclaimer: str

class AlertListResponse(BaseModel):
    total_alerts: int
    unread_count: int
    alerts: List[AlertOut]
    role: str
    disclaimer: str

class UnreadAlertCountResponse(BaseModel):
    total_unread: int
    critical_unread: int
    high_unread: int
    moderate_unread: int
    info_unread: int

