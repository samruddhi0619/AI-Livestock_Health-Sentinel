import os
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI-Livestock Health Sentinel"
    PROJECT_DESCRIPTION: str = (
        "Early warning livestock disease surveillance, multi-modal risk scoring, "
        "and veterinary outbreak intelligence platform."
    )
    VERSION: str = "2.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Server configuration
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    
    # JWT & Security Configuration
    SECRET_KEY: str = "metaminds_sih2026_sentinel_secret_key_secure_9a8b7c6d5e4f3a2b1"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    
    # PostgreSQL Database Configuration
    DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/livestock_sentinel"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "livestock_sentinel"
    
    # Connection Pool settings
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 1800
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*"
    ]
    
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        return v

    # Storage Paths
    BASE_DIR: str = os.path.dirname(os.path.abspath(__file__))
    UPLOAD_DIR: str = os.path.join(os.path.dirname(BASE_DIR), "uploads")
    DATA_DIR: str = os.path.join(BASE_DIR, "data")
    
    # Multi-Modal Health Risk Engine Configurable Weights (Must sum to ~1.0)
    RISK_WEIGHT_IMAGE: float = 0.40
    RISK_WEIGHT_SYMPTOM: float = 0.35
    RISK_WEIGHT_ENVIRONMENT: float = 0.15
    RISK_WEIGHT_CONTEXT: float = 0.10
    
    # Risk Level Boundaries
    RISK_THRESHOLD_LOW_MAX: float = 30.0
    RISK_THRESHOLD_MEDIUM_MAX: float = 60.0
    RISK_THRESHOLD_HIGH_MAX: float = 80.0
    # 81-100 is Critical

    # Spatio-Temporal Disease Cluster Detection Configuration
    CLUSTER_GEO_RADIUS_KM: float = 5.0
    CLUSTER_MIN_REPORTS: int = 3
    CLUSTER_TIME_WINDOW_DAYS: int = 14
    CLUSTER_MIN_RISK_SCORE: float = 60.0  # Only high-risk and critical reports evaluated
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

# Ensure runtime directories exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.DATA_DIR, exist_ok=True)
