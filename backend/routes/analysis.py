import os
import io
import base64
import urllib.request
from typing import Optional
from fastapi import APIRouter, Request, UploadFile, File, Form, HTTPException, status, Body
from fastapi.responses import JSONResponse

from config import settings
from schemas import (
    ImageAnalysisUrlRequest,
    SymptomAnalysisRequest,
    EnvironmentalAnalysisRequest,
    MultiModalRiskRequest,
    MultiModalRiskResponse
)
from services import (
    get_image_service,
    get_symptom_service,
    get_environmental_service,
    get_multi_modal_engine
)

# Support both /analysis and /api/analysis router prefixes
router = APIRouter(tags=["Machine Learning Risk Analysis Services"])

# ---------------------------------------------------------------------------
# 1. Image Risk Analysis Service
# ---------------------------------------------------------------------------
@router.post(
    "/analysis/image",
    summary="Independent Image Risk Screening",
    description=(
        "Performs autonomous computer vision visual screening for Lumpy Skin Disease (LSD) "
        "on an uploaded cattle photograph using a cached PyTorch MobileNetV3 model."
    )
)
@router.post("/api/analysis/image", include_in_schema=False)
async def analyze_image_endpoint(request: Request):
    content_type = request.headers.get("content-type", "").lower()
    image_bytes = None
    filename = "uploaded_image.jpg"
    low_threshold = 0.30
    high_threshold = 0.70
    
    # 1. Handle multipart form-data file upload
    if "multipart/form-data" in content_type:
        form = await request.form()
        uploaded_file = form.get("file")
        if uploaded_file is not None and hasattr(uploaded_file, "read"):
            filename = getattr(uploaded_file, "filename", "uploaded_image.jpg") or "uploaded_image.jpg"
            image_bytes = await uploaded_file.read()
        try:
            if "low_threshold" in form:
                low_threshold = float(form["low_threshold"])
            if "high_threshold" in form:
                high_threshold = float(form["high_threshold"])
        except (ValueError, TypeError):
            pass
    # 2. Handle JSON payload (base64 or URL)
    else:
        try:
            payload = await request.json()
        except Exception:
            payload = {}
            
        if isinstance(payload, dict):
            b64_str = payload.get("image_base64")
            image_url = payload.get("image_url")
            if b64_str:
                try:
                    if "," in b64_str:
                        b64_str = b64_str.split(",")[1]
                    image_bytes = base64.b64decode(b64_str)
                    filename = "base64_image.png"
                except Exception as e:
                    raise HTTPException(status_code=400, detail=f"Invalid Base64 image payload: {e}")
            elif image_url:
                if image_url.startswith("/uploads/"):
                    local_path = os.path.join(settings.BASE_DIR, "..", image_url.lstrip("/"))
                    if os.path.exists(local_path):
                        with open(local_path, "rb") as f:
                            image_bytes = f.read()
                        filename = os.path.basename(local_path)
                elif image_url.startswith("http://") or image_url.startswith("https://"):
                    try:
                        with urllib.request.urlopen(image_url, timeout=5) as resp:
                            image_bytes = resp.read()
                        filename = os.path.basename(image_url)
                    except Exception as e:
                        raise HTTPException(status_code=400, detail=f"Failed to fetch image from URL: {e}")
            try:
                if "low_threshold" in payload and payload["low_threshold"] is not None:
                    low_threshold = float(payload["low_threshold"])
                if "high_threshold" in payload and payload["high_threshold"] is not None:
                    high_threshold = float(payload["high_threshold"])
            except (ValueError, TypeError):
                pass
        
    if not image_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No image provided. Upload an image file or provide a valid image_url / image_base64."
        )
        
    try:
        service = get_image_service()
        result = service.analyze_image(
            image_bytes=image_bytes,
            filename=filename,
            low_threshold=low_threshold,
            high_threshold=high_threshold
        )
        return result
    except ValueError as val_err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(val_err))
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Image analysis error: {str(exc)}")

# ---------------------------------------------------------------------------
# 2. Symptom-Based Disease Risk Assessment Service
# ---------------------------------------------------------------------------
@router.post(
    "/analysis/symptoms",
    summary="Independent Symptom-Based Disease Risk Assessment",
    description=(
        "Evaluates reported clinical signs and host demographics against the trained multi-disease "
        "XGBoost classifier. Returns ranked disease probabilities, risk score, and real-time SHAP explainability."
    )
)
@router.post("/api/analysis/symptoms", include_in_schema=False)
def analyze_symptoms_endpoint(payload: SymptomAnalysisRequest):
    try:
        service = get_symptom_service()
        result = service.analyze_symptoms(
            symptoms=payload.symptoms,
            age=payload.age or 4.0,
            breed=payload.breed or "gir",
            gender=payload.gender or "female",
            history=payload.history or "none",
            vaccination=payload.vaccination or "not_vaccinated",
            low_threshold=payload.low_threshold or 35.0,
            high_threshold=payload.high_threshold or 65.0
        )
        return result
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Symptom risk assessment error: {str(exc)}"
        )

# ---------------------------------------------------------------------------
# 3. Environmental Risk Assessment Service
# ---------------------------------------------------------------------------
@router.post(
    "/analysis/environment",
    summary="Independent Environmental & Geospatial Risk Assessment",
    description=(
        "Computes regional vector-breeding and outbreak transmission vulnerability for a geographical area "
        "using the trained geospatial XGBoost model. Does not diagnose an individual animal."
    )
)
@router.post("/api/analysis/environment", include_in_schema=False)
def analyze_environment_endpoint(payload: EnvironmentalAnalysisRequest):
    try:
        service = get_environmental_service()
        result = service.analyze_environment(
            latitude=payload.latitude,
            longitude=payload.longitude,
            temperature_c=payload.temperature_c,
            humidity_percent=payload.humidity_percent,
            rainfall_mm=payload.rainfall_mm,
            elevation_m=payload.elevation_m or 180.0,
            cattle_density=payload.cattle_density or 15000.0,
            buffalo_density=payload.buffalo_density or 3000.0,
            dominant_land_cover=payload.dominant_land_cover or 4
        )
        return result
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Environmental risk assessment error: {str(exc)}"
        )

# ---------------------------------------------------------------------------
# 4. Transparent Multi-Modal Livestock Health Risk Engine
# ---------------------------------------------------------------------------
@router.post(
    "/analysis/multi-modal",
    response_model=MultiModalRiskResponse,
    summary="Transparent Multi-Modal Health Risk Assessment",
    description=(
        "Synthesizes Image AI, Symptom AI, Environmental risk, and Health/Vaccination context "
        "using configurable weights. Returns final risk score, risk level (Low, Medium, High, Critical), "
        "individual model scores, and transparent contributing factor breakdown. "
        "Not a veterinary diagnosis."
    )
)
@router.post("/api/analysis/multi-modal", response_model=MultiModalRiskResponse, include_in_schema=False)
def analyze_multi_modal_endpoint(payload: MultiModalRiskRequest):
    try:
        engine = get_multi_modal_engine()
        custom_weights_dict = None
        if payload.custom_weights:
            custom_weights_dict = payload.custom_weights.model_dump(exclude_none=True)
            
        result = engine.evaluate(
            image_risk_score=payload.image_risk_score,
            symptom_risk_score=payload.symptom_risk_score,
            environmental_risk_score=payload.environmental_risk_score,
            vaccination_status=payload.vaccination_status or "not_vaccinated",
            health_history=payload.health_history or "none",
            custom_weights=custom_weights_dict
        )
        return result
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Multi-modal risk engine assessment error: {str(exc)}"
        )

