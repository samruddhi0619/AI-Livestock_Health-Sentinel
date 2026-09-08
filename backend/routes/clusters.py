from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status

from auth import get_current_user
from config import settings
from services.cluster_service import get_cluster_service, ClusterDetectionService
from schemas import (
    ClusterDetectionRequest,
    ClusterOut,
    ClusterListResponse
)

router = APIRouter(prefix="/api/clusters", tags=["Disease Cluster Surveillance"])

DISCLAIMER_TEXT = (
    "AI-assisted spatio-temporal cluster detection (Emerging Risk Pattern) based on density "
    "of high-risk livestock reports. It does NOT constitute a confirmed epidemiological outbreak "
    "or official veterinary diagnosis. Field verification by a certified veterinary authority is required."
)

@router.post(
    "/detect",
    summary="Trigger Spatio-Temporal Cluster Detection",
    description=(
        "Executes Haversine DBSCAN clustering on high-risk livestock health reports. "
        "Configurable by geographic radius, minimum reports threshold, and time window. "
        "Outputs are strictly classified as 'Potential Disease Cluster' or 'Emerging Risk Pattern', "
        "never labeled as a confirmed outbreak."
    )
)
def trigger_cluster_detection(
    request: Optional[ClusterDetectionRequest] = None,
    current_user: dict = Depends(get_current_user),
    cluster_service: ClusterDetectionService = Depends(get_cluster_service)
):
    # Role-based access control: Only veterinarians, officers, and admins may execute trigger
    role = str(current_user.get("role", "")).upper()
    if role not in ["VETERINARIAN", "OFFICER", "ADMIN"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Surveillance cluster execution is restricted to Veterinarians and District Administrators."
        )

    req_data = request or ClusterDetectionRequest()
    geo_radius_km = req_data.geo_radius_km or settings.CLUSTER_GEO_RADIUS_KM
    min_reports = req_data.min_reports or settings.CLUSTER_MIN_REPORTS
    time_window_days = req_data.time_window_days or settings.CLUSTER_TIME_WINDOW_DAYS
    disease_filter = req_data.disease

    try:
        detected_clusters = cluster_service.run_detection(
            geo_radius_km=geo_radius_km,
            min_reports=min_reports,
            time_window_days=time_window_days,
            disease_filter=disease_filter,
            persist=True,
            emit_alerts=True
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Density clustering algorithm execution error: {str(e)}"
        )

    return {
        "status": "success",
        "pattern_type": "Emerging Risk Pattern",
        "total_clusters_detected": len(detected_clusters),
        "clusters": detected_clusters,
        "parameters_applied": {
            "geo_radius_km": geo_radius_km,
            "min_reports": min_reports,
            "time_window_days": time_window_days,
            "disease_filter": disease_filter
        },
        "is_confirmed_outbreak": False,
        "is_veterinary_diagnosis": False,
        "disclaimer": DISCLAIMER_TEXT
    }

@router.get(
    "",
    summary="List Detected Potential Disease Clusters",
    description="Retrieves active potential disease clusters / emerging risk patterns with optional disease and risk filtering."
)
def list_clusters(
    disease: Optional[str] = Query(None, description="Filter by disease name"),
    risk_level: Optional[str] = Query(None, description="Filter by risk level (Critical, High)"),
    limit: int = Query(50, ge=1, le=200, description="Max results to return"),
    current_user: dict = Depends(get_current_user),
    cluster_service: ClusterDetectionService = Depends(get_cluster_service)
):
    clusters = cluster_service.list_clusters(
        disease=disease,
        risk_level=risk_level,
        limit=limit
    )

    critical_count = sum(1 for c in clusters if c.get("risk_level") == "Critical")
    high_count = sum(1 for c in clusters if c.get("risk_level") == "High")
    
    villages = set()
    for c in clusters:
        for v in c.get("villages", []):
            villages.add(v)

    return {
        "total_clusters": len(clusters),
        "clusters": clusters,
        "summary": {
            "critical_risk_clusters": critical_count,
            "high_risk_clusters": high_count,
            "distinct_villages_affected": len(villages)
        },
        "query_parameters": {
            "disease": disease,
            "risk_level": risk_level,
            "limit": limit
        },
        "is_confirmed_outbreak": False,
        "is_veterinary_diagnosis": False,
        "disclaimer": DISCLAIMER_TEXT
    }

@router.get(
    "/{cluster_id}",
    summary="Get Potential Disease Cluster Details",
    description="Retrieves granular details, centroid coordinates, and affected reports for a detected cluster."
)
def get_cluster_details(
    cluster_id: str,
    current_user: dict = Depends(get_current_user),
    cluster_service: ClusterDetectionService = Depends(get_cluster_service)
):
    cluster = cluster_service.get_cluster(cluster_id)
    if not cluster:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Potential disease cluster '{cluster_id}' not found."
        )

    return {
        "cluster": cluster,
        "is_confirmed_outbreak": False,
        "is_veterinary_diagnosis": False,
        "disclaimer": DISCLAIMER_TEXT
    }
