import os
import json
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Request, UploadFile, File, Form
from fastapi.responses import JSONResponse

from config import settings
from database import db
from auth import get_current_user, require_authenticated
from schemas import HealthReportCreate, HealthReportOut
from services.reporting_service import get_reporting_service

router = APIRouter(tags=["Livestock Health Reporting & Disease Surveillance"])

# ---------------------------------------------------------------------------
# 1. Submit Health Report Endpoint
# ---------------------------------------------------------------------------
@router.post(
    "/api/reports/health",
    response_model=HealthReportOut,
    summary="Submit Livestock Health Report",
    description=(
        "Enables a farmer or clinician to submit observed symptoms, upload an image, and share location. "
        "Orchestrates image screening, symptom risk, environmental risk, and multi-modal risk scoring. "
        "Automatically creates a disease surveillance report and alert for High or Critical risk cases. "
        "Strict non-veterinary diagnosis."
    )
)
@router.post("/reports/health", response_model=HealthReportOut, include_in_schema=False)
async def submit_health_report_endpoint(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    reporting_service = get_reporting_service()
    content_type = request.headers.get("content-type", "").lower()
    
    animal_id = None
    symptoms = []
    image_bytes = None
    image_url = None
    image_base64 = None
    location_payload = None
    body_temperature_c = 38.5
    appetite_score = 1.0
    milk_yield_liters = 0.0
    activity_score = 1.0
    clinical_notes = None

    # A. Multipart Form-Data (File upload directly from form)
    if "multipart/form-data" in content_type:
        form = await request.form()
        animal_id = form.get("animal_id")
        if not animal_id:
            raise HTTPException(status_code=400, detail="Field 'animal_id' is required.")
            
        raw_symptoms = form.get("symptoms", "")
        if raw_symptoms:
            try:
                # Try parsing as JSON array
                parsed = json.loads(raw_symptoms)
                symptoms = parsed if isinstance(parsed, list) else [str(parsed)]
            except Exception:
                # Fallback to comma-separated
                symptoms = [s.strip() for s in str(raw_symptoms).split(",") if s.strip()]
                
        uploaded_file = form.get("image")
        if uploaded_file is not None and hasattr(uploaded_file, "read"):
            image_bytes = await uploaded_file.read()
            
        image_url = form.get("image_url")
        image_base64 = form.get("image_base64")
        
        # Parse Location
        loc_lat = form.get("latitude")
        loc_lng = form.get("longitude")
        if loc_lat is not None and loc_lng is not None:
            share_loc_raw = form.get("share_location")
            share_loc_bool = True if share_loc_raw is None else str(share_loc_raw).lower() in ["true", "1", "yes"]
            location_payload = {
                "latitude": float(loc_lat),
                "longitude": float(loc_lng),
                "share_location": share_loc_bool,
                "village": form.get("village"),
                "taluka": form.get("taluka"),
                "district": form.get("district")
            }
            
        if form.get("body_temperature_c"):
            body_temperature_c = float(form.get("body_temperature_c"))
        if form.get("appetite_score"):
            appetite_score = float(form.get("appetite_score"))
        if form.get("milk_yield_liters"):
            milk_yield_liters = float(form.get("milk_yield_liters"))
        if form.get("activity_score"):
            activity_score = float(form.get("activity_score"))
        clinical_notes = form.get("clinical_notes")

    # B. JSON Payload
    else:
        try:
            body = await request.json()
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid JSON body.")
            
        animal_id = body.get("animal_id")
        if not animal_id:
            raise HTTPException(status_code=400, detail="Field 'animal_id' is required.")
            
        symptoms = body.get("symptoms", [])
        image_url = body.get("image_url")
        image_base64 = body.get("image_base64")
        location_payload = body.get("location")
        body_temperature_c = float(body.get("body_temperature_c", 38.5))
        appetite_score = float(body.get("appetite_score", 1.0))
        milk_yield_liters = float(body.get("milk_yield_liters", 0.0))
        activity_score = float(body.get("activity_score", 1.0))
        clinical_notes = body.get("clinical_notes")

    if not symptoms:
        raise HTTPException(status_code=400, detail="At least one observed symptom is required in 'symptoms'.")

    try:
        result = reporting_service.submit_report(
            animal_id=animal_id,
            symptoms=symptoms,
            image_bytes=image_bytes,
            image_url=image_url,
            image_base64=image_base64,
            location=location_payload,
            body_temperature_c=body_temperature_c,
            appetite_score=appetite_score,
            milk_yield_liters=milk_yield_liters,
            activity_score=activity_score,
            clinical_notes=clinical_notes,
            current_user=current_user
        )
        return result
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))
    except PermissionError as pe:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(pe))
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Health reporting error: {str(exc)}")

# ---------------------------------------------------------------------------
# 2. List Health Reports Endpoint (Role-Filtered & Privacy-Sanitized)
# ---------------------------------------------------------------------------
@router.get(
    "/api/reports/health",
    summary="List Livestock Health Reports",
    description=(
        "Retrieves health reports. Farmers only view reports for their own herd. "
        "Veterinarians and Administrators view all reports with location privacy controls."
    )
)
@router.get("/reports/health", include_in_schema=False)
def list_health_reports(
    animal_id: Optional[str] = None,
    risk_level: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    reporting_service = get_reporting_service()
    user_role = str(current_user.get("role", "FARMER")).upper()
    username = current_user.get("username", "")
    user_id = str(current_user.get("_id", current_user.get("id", "")))

    query = {}
    if animal_id:
        query["$or"] = [{"animal_id": animal_id}, {"animal_tag": animal_id}]
    if risk_level:
        query["risk_level"] = risk_level.title()

    # Role filter: Farmers restricted to their own herd
    if user_role == "FARMER":
        query["$or"] = [
            {"owner_id": username},
            {"owner_id": user_id},
            {"recorded_by": username}
        ]

    reports = db["health_reports"].find(query)
    
    # Apply location privacy sanitization
    sanitized = []
    for r in reports:
        safe_loc = reporting_service.filter_location_for_user(r, current_user)
        r_out = dict(r)
        # Strip exact raw coordinates from dict
        r_out.pop("exact_latitude", None)
        r_out.pop("exact_longitude", None)
        r_out["location"] = safe_loc
        r_out["location_access_level"] = safe_loc["access_level"]
        r_out["report_id"] = r.get("_id", r.get("id"))
        sanitized.append(r_out)
        
    return {
        "success": True,
        "count": len(sanitized),
        "reports": sanitized
    }

# ---------------------------------------------------------------------------
# 3. Get Single Health Report Endpoint
# ---------------------------------------------------------------------------
@router.get(
    "/api/reports/health/{report_id}",
    summary="Get Health Report by ID",
    description="Retrieves a single health report with privacy-filtered coordinates."
)
@router.get("/reports/health/{report_id}", include_in_schema=False)
def get_health_report(
    report_id: str,
    current_user: dict = Depends(get_current_user)
):
    reporting_service = get_reporting_service()
    user_role = str(current_user.get("role", "FARMER")).upper()
    username = current_user.get("username", "")
    user_id = str(current_user.get("_id", current_user.get("id", "")))

    report = db["health_reports"].find_one({"$or": [{"_id": report_id}, {"id": report_id}]})
    if not report:
        raise HTTPException(status_code=404, detail=f"Health report '{report_id}' not found.")

    # Access check: Farmers can only view their own
    if user_role == "FARMER":
        is_owner = (
            report.get("owner_id") == username or 
            report.get("owner_id") == user_id or
            report.get("recorded_by") == username
        )
        if not is_owner:
            raise HTTPException(status_code=403, detail="Access denied: You do not own this health report.")

    safe_loc = reporting_service.filter_location_for_user(report, current_user)
    r_out = dict(report)
    r_out.pop("exact_latitude", None)
    r_out.pop("exact_longitude", None)
    r_out["location"] = safe_loc
    r_out["location_access_level"] = safe_loc["access_level"]
    r_out["report_id"] = report.get("_id", report.get("id"))
    
    return {
        "success": True,
        "report": r_out
    }

# ---------------------------------------------------------------------------
# 4. Disease Surveillance Map Data Endpoint (React Leaflet & OpenStreetMap)
# ---------------------------------------------------------------------------
@router.get(
    "/api/reports/surveillance-map",
    summary="Disease Surveillance Map Data",
    description=(
        "Retrieves multi-layered geospatial surveillance data for React Leaflet map. "
        "Includes individual reports (where authorized), aggregated regional risk indicators, "
        "potential hotspots, and disease clusters. "
        "Fuzzes farm locations to preserve privacy. Farmer views prioritize regional risk."
    )
)
@router.get("/reports/surveillance-map", include_in_schema=False)
def get_surveillance_map_data(
    disease: Optional[str] = None,
    risk_level: Optional[str] = None,
    region: Optional[str] = None,
    days: Optional[str] = "30",
    current_user: dict = Depends(get_current_user)
):
    reporting_service = get_reporting_service()
    user_role = str(current_user.get("role", "FARMER")).upper()
    username = current_user.get("username", "")
    user_id = str(current_user.get("_id", current_user.get("id", "")))

    # 1. Date window filtering
    cutoff_iso = None
    if days and days.lower() != "all":
        try:
            num_days = int(days)
            cutoff_iso = (datetime.now(timezone.utc) - timedelta(days=num_days)).isoformat()
        except ValueError:
            cutoff_iso = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()

    # 2. Fetch all health reports and disease cases
    raw_reports = db["health_reports"].find()
    if not raw_reports:
        # Fallback to disease_reports or disease_cases if present
        raw_reports = db["disease_reports"].find() or db["disease_cases"].find()

    # 3. Filter reports
    filtered_reports = []
    all_diseases = set()
    all_regions = set()
    all_risk_tiers = set()

    for r in raw_reports:
        r_disease = (
            r.get("reported_disease") or 
            r.get("disease") or 
            r.get("ai_analyses", {}).get("symptoms", {}).get("top_condition") or
            "Suspected Disease"
        )
        r_risk_lvl = (
            r.get("risk_level") or 
            r.get("multi_modal_risk", {}).get("risk_level") or 
            "Moderate"
        ).title()
        
        r_village = r.get("village") or "Wadgaon"
        r_taluka = r.get("taluka") or "Haveli"
        r_district = r.get("district") or "Pune"
        r_date = r.get("recorded_at") or r.get("created_at") or r.get("detected_at") or ""

        all_diseases.add(r_disease)
        all_risk_tiers.add(r_risk_lvl)
        all_regions.add(r_taluka)
        all_regions.add(r_district)

        # Apply Date Cutoff
        if cutoff_iso and r_date and r_date < cutoff_iso:
            continue

        # Apply Disease Filter
        if disease and disease.lower() not in ["all", ""]:
            if disease.lower() not in r_disease.lower():
                continue

        # Apply Risk Level Filter
        if risk_level and risk_level.lower() not in ["all", ""]:
            if risk_level.lower() != r_risk_lvl.lower():
                continue

        # Apply Region Filter
        if region and region.lower() not in ["all", ""]:
            reg_low = region.lower()
            if reg_low not in r_village.lower() and reg_low not in r_taluka.lower() and reg_low not in r_district.lower():
                continue

        # Check Farmer Privacy: Farmers only see their own reports in individual markers
        is_own_report = (
            r.get("owner_id") == username or 
            r.get("owner_id") == user_id or 
            r.get("recorded_by") == username
        )

        safe_loc = reporting_service.filter_location_for_user(r, current_user)
        
        # Build sanitized map report item
        rep_item = {
            "report_id": r.get("_id", r.get("id")),
            "animal_tag": r.get("animal_tag") or r.get("animal_id", "Unknown"),
            "disease": r_disease,
            "risk_level": r_risk_lvl,
            "risk_score": float(r.get("final_risk_score") or r.get("risk_score") or 50.0),
            "latitude": safe_loc["latitude"],
            "longitude": safe_loc["longitude"],
            "approximate_latitude": safe_loc["approximate_latitude"],
            "approximate_longitude": safe_loc["approximate_longitude"],
            "location_access_level": safe_loc["access_level"],
            "village": r_village,
            "taluka": r_taluka,
            "district": r_district,
            "status": r.get("status", "REPORTED"),
            "is_surveillance_triggered": r.get("is_surveillance_triggered", False),
            "recorded_at": r_date
        }

        # Role-appropriate report display:
        # Veterinarians and Admins see all authorized reports.
        # Farmers only see their own individual animal reports (protects neighboring farm privacy).
        if user_role in ["VETERINARIAN", "ADMIN"]:
            filtered_reports.append(rep_item)
        elif user_role == "FARMER" and is_own_report:
            filtered_reports.append(rep_item)

    # 4. Fetch and format Outbreak Clusters (DBSCAN)
    clusters = []
    raw_clusters = db["outbreak_clusters"].find() or db["disease_clusters"].find()
    for c in raw_clusters:
        c_disease = c.get("disease") or c.get("disease_name", "Lumpy Skin Disease")
        c_taluka = c.get("taluka") or "Haveli"
        c_district = c.get("district") or "Pune"

        # Apply filters to clusters
        if disease and disease.lower() not in ["all", ""] and disease.lower() not in c_disease.lower():
            continue
        if region and region.lower() not in ["all", ""]:
            reg_low = region.lower()
            if reg_low not in c_taluka.lower() and reg_low not in c_district.lower():
                continue

        center_lat = float(c.get("center_latitude") or c.get("centroid", {}).get("latitude") or c.get("center_location", {}).get("latitude", 18.525))
        center_lng = float(c.get("center_longitude") or c.get("centroid", {}).get("longitude") or c.get("center_location", {}).get("longitude", 73.860))
        rad_km = float(c.get("radius_km") or c.get("radius", 1.25))

        clusters.append({
            "cluster_code": c.get("cluster_id") or c.get("cluster_code", "CLUSTER-OUTBREAK-01"),
            "cluster_label": c.get("cluster_label", "Potential Disease Cluster"),
            "pattern_type": c.get("pattern_type", "Emerging Risk Pattern"),
            "disease": c_disease,
            "center_latitude": center_lat,
            "center_longitude": center_lng,
            "radius_km": rad_km,
            "cases_count": int(c.get("cases_count") or c.get("report_count") or 3),
            "report_count": int(c.get("report_count") or c.get("cases_count") or 3),
            "severity": c.get("risk_level") or c.get("severity", "WARNING"),
            "risk_level": c.get("risk_level", "High"),
            "status": c.get("status", "EMERGING_RISK_PATTERN"),
            "affected_farms_count": c.get("unique_farms_count") or len(c.get("affected_farms", [1])),
            "taluka": c_taluka,
            "district": c_district,
            "is_confirmed_outbreak": False,
            "is_veterinary_diagnosis": False
        })

    # 5. Compute Aggregated Regional Indicators (Taluka & District Level)
    # Group all reports by taluka
    region_groups = {}
    for r in raw_reports:
        t = r.get("taluka") or "Haveli"
        d = r.get("district") or "Pune"
        score = float(r.get("final_risk_score") or r.get("risk_score") or 50.0)
        dis = (
            r.get("reported_disease") or 
            r.get("disease") or 
            r.get("ai_analyses", {}).get("symptoms", {}).get("top_condition") or
            "Lumpy Skin Disease"
        )
        if t not in region_groups:
            region_groups[t] = {
                "region_name": t,
                "district": d,
                "scores": [],
                "diseases": [],
                "quarantine_count": 0
            }
        region_groups[t]["scores"].append(score)
        region_groups[t]["diseases"].append(dis)
        if r.get("is_surveillance_triggered") or r.get("is_quarantine_required"):
            region_groups[t]["quarantine_count"] += 1

    regional_indicators = []
    for t_name, data in region_groups.items():
        if region and region.lower() not in ["all", ""]:
            if region.lower() not in t_name.lower() and region.lower() not in data["district"].lower():
                continue
        avg_score = round(sum(data["scores"]) / len(data["scores"]), 1) if data["scores"] else 45.0
        # Determine dominant disease
        dominant_dis = max(set(data["diseases"]), key=data["diseases"].count) if data["diseases"] else "Lumpy Skin Disease"
        
        # Determine regional risk level
        if avg_score <= 30.0:
            reg_risk = "Low"
        elif avg_score <= 60.0:
            reg_risk = "Medium"
        elif avg_score <= 80.0:
            reg_risk = "High"
        else:
            reg_risk = "Critical"

        regional_indicators.append({
            "region_name": t_name,
            "district": data["district"],
            "total_cases": len(data["scores"]),
            "average_risk_score": avg_score,
            "risk_level": reg_risk,
            "predominant_disease": dominant_dis,
            "active_clusters": sum(1 for c in clusters if c["taluka"].lower() == t_name.lower()),
            "quarantine_active": data["quarantine_count"] > 0,
            "recommended_action": (
                "Heightened biosecurity, vector repellent spraying, and daily temperature logging in effect."
                if reg_risk in ["High", "Critical"] else
                "Standard preventive herd health monitoring."
            )
        })

    # 6. Compute Potential Hotspots (Fuzzed density and vector hazard centers)
    hotspots = []
    # Seed known epidemic areas from regional indicators
    for reg in regional_indicators:
        if reg["total_cases"] >= 2 or reg["risk_level"] in ["High", "Critical"]:
            # Coordinate lookup for regional centers in Maharashtra
            center_coords = {
                "haveli": (18.5204, 73.8567),
                "pune": (18.5204, 73.8567),
                "baramati": (18.1512, 74.5789),
                "shirur": (18.8256, 74.3789),
                "ambegaon": (19.0123, 73.9876)
            }
            c_lat, c_lng = center_coords.get(reg["region_name"].lower(), (18.525, 73.860))
            hotspots.append({
                "hotspot_id": f"hotspot-{reg['region_name'].lower()}",
                "name": f"{reg['region_name']} Vector-Epidemic Hotspot",
                "latitude": c_lat,
                "longitude": c_lng,
                "radius_meters": 2500,
                "intensity": min(1.0, reg["average_risk_score"] / 100.0),
                "case_count": reg["total_cases"],
                "dominant_disease": reg["predominant_disease"],
                "environmental_risk_score": reg["average_risk_score"],
                "risk_level": reg["risk_level"]
            })

    # Default fallback options if empty
    default_diseases = sorted(list(all_diseases | {"Lumpy Skin Disease", "Foot-and-Mouth Disease", "Anthrax", "Brucellosis"}))
    default_regions = sorted(list(all_regions | {"Haveli", "Baramati", "Pune", "Shirur"}))
    default_risk_tiers = ["Low", "Medium", "High", "Critical"]

    return {
        "user_role": user_role,
        "is_farmer_view": user_role == "FARMER",
        "filters_applied": {
            "disease": disease or "All",
            "risk_level": risk_level or "All",
            "region": region or "All",
            "days": days or "30"
        },
        "reports": filtered_reports,
        "clusters": clusters,
        "hotspots": hotspots,
        "regional_indicators": regional_indicators,
        "filter_options": {
            "diseases": default_diseases,
            "risk_levels": default_risk_tiers,
            "regions": default_regions,
            "date_ranges": ["7", "14", "30", "all"]
        },
        "map_center": {
            "latitude": 18.5204,
            "longitude": 73.8567,
            "zoom": 12
        },
        "is_veterinary_diagnosis": False,
        "disclaimer": (
            "Surveillance map displays epidemiological risk indicators, cluster warnings, and density hotspots. "
            "It is an AI-assisted early warning tool and NOT a veterinary diagnosis. "
            "Private farm coordinates are protected."
        )
    }

