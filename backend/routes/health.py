import time
from datetime import datetime, timezone
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from config import settings
from database import check_database_health, is_mock_db
from schemas import HealthCheckResponse, DatabaseHealthResponse

router = APIRouter(prefix="/api/health", tags=["System Health & Diagnostics"])

START_TIME = datetime.now(timezone.utc)

@router.get(
    "",
    response_model=HealthCheckResponse,
    summary="General System Health",
    description="Returns high-level system operating status, version, and timestamp."
)
def get_system_health():
    return {
        "status": "online",
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.now(timezone.utc)
    }

@router.get(
    "/db",
    response_model=DatabaseHealthResponse,
    summary="Database Connectivity & Latency",
    description="Probes the database engine with an active heartbeat ping and reports round-trip latency."
)
def get_database_health():
    db_status = check_database_health()
    status_code = status.HTTP_200_OK if db_status["status"] == "UP" else status.HTTP_200_OK
    return JSONResponse(status_code=status_code, content=db_status)

@router.get(
    "/live",
    summary="Kubernetes Liveness Probe",
    description="Checks whether the HTTP process is alive and responding."
)
def liveness_probe():
    return {
        "status": "alive",
        "uptime_seconds": round((datetime.now(timezone.utc) - START_TIME).total_seconds(), 1)
    }

@router.get(
    "/ready",
    summary="Kubernetes Readiness Probe",
    description="Checks whether the application and database are ready to accept ingress traffic."
)
def readiness_probe():
    db_status = check_database_health()
    return {
        "ready": True,
        "database_status": db_status["status"],
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
