import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

from config import settings
from error_handlers import register_error_handlers

# Route imports
from routes import (
    health,
    auth,
    animals,
    assessment,
    cases,
    vaccinations,
    outbreaks,
    dashboard,
    admin,
    analysis,
    reports,
    clusters,
    alerts
)

# OpenAPI Documentation Tags Metadata
OPENAPI_TAGS = [
    {
        "name": "System Health & Diagnostics",
        "description": "Liveness, readiness, and PostgreSQL connectivity heartbeat endpoints."
    },
    {
        "name": "Authentication & User Management",
        "description": "User registration, JWT authentication, role verification (FARMER, VETERINARIAN, ADMIN), and profile lookup."
    },
    {
        "name": "Animals & Digital Passport",
        "description": "Livestock registration, ear-tag and QR code identification, and ground-truth health status tracking."
    },
    {
        "name": "Clinical Assessment & Screening",
        "description": "Symptom reporting and screening triage endpoints (ML models integrated via modular pipelines)."
    },
    {
        "name": "Disease Cases & Veterinary Review",
        "description": "Case lifecycle management, isolation orders, and independent veterinarian clinical adjudication."
    },
    {
        "name": "Vaccination Tracking",
        "description": "Immunization ledger, booster reminders, and digital vaccination passports."
    },
    {
        "name": "Geospatial Surveillance & Outbreak Clusters",
        "description": "DBSCAN spatio-temporal disease clustering and early warning alert dispatching."
    },
    {
        "name": "Dashboards & Analytics",
        "description": "Aggregated statistical metrics for Farmers, Veterinarians, and District Administrators."
    },
    {
        "name": "Admin Management",
        "description": "Regional disease registry and supervisory system administration."
    },
    {
        "name": "Disease Cluster Surveillance",
        "description": "Density-based spatio-temporal cluster detection (Emerging Risk Patterns) via Haversine DBSCAN."
    },
    {
        "name": "In-App Alerts & Early Warning Notifications",
        "description": "Role-tailored alerts for Farmers, Veterinarians, and Administrators with biosecurity guidance."
    }
]

# Initialize FastAPI Application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.VERSION,
    openapi_tags=OPENAPI_TAGS,
    docs_url="/docs",
    redoc_url="/redoc"
)

# 1. Register Global CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS if settings.CORS_ORIGINS != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Register Centralized Error Handlers
register_error_handlers(app)

# 3. Mount Static Uploads Directory
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# 4. Register Modular API Routers
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(animals.router)
app.include_router(assessment.router)
app.include_router(cases.router)
app.include_router(vaccinations.router)
app.include_router(outbreaks.router)
app.include_router(dashboard.router)
app.include_router(admin.router)
app.include_router(analysis.router)
app.include_router(reports.router)
app.include_router(clusters.router)
app.include_router(alerts.router)

# 5. Root & Documentation Shortcuts
@app.get("/", include_in_schema=False)
def read_root():
    return {
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "operational",
        "documentation": "/docs",
        "health_check": "/api/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
