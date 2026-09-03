import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from config import settings

# Route imports
from routes import auth, animals, assessment, cases, vaccinations, outbreaks, dashboard, admin

app = FastAPI(title=settings.PROJECT_NAME)

# CORS Middleware Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For hackathon demo, allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount upload directory to serve static animal symptom images
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Include Routers
app.include_router(auth.router)
app.include_router(animals.router)
app.include_router(assessment.router)
app.include_router(cases.router)
app.include_router(vaccinations.router)
app.include_router(outbreaks.router)
app.include_router(dashboard.router)
app.include_router(admin.router)

@app.get("/api/health")
def health_check():
    from database import is_mock_db
    return {
        "status": "online",
        "project": settings.PROJECT_NAME,
        "database_mode": "Local JSON Sandbox" if is_mock_db else "MongoDB Connected"
    }

@app.get("/")
def read_root():
    return {"message": f"Welcome to the {settings.PROJECT_NAME} API. Access API docs at /docs"}
