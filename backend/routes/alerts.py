from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status

from auth import get_current_user
from services.alert_service import get_alert_service, AlertService
from schemas import (
    AlertOut,
    AlertListResponse,
    UnreadAlertCountResponse
)

router = APIRouter(prefix="/api/alerts", tags=["In-App Alerts & Early Warning Notifications"])

@router.get(
    "",
    summary="List Role-Specific Alerts",
    description=(
        "Retrieves role-scoped early-warning alerts for the authenticated user. "
        "Farmers receive high-risk animal assessments, vaccination due dates, and regional risks. "
        "Veterinarians receive clinical triage reviews and potential clusters. "
        "Administrators receive emerging clusters and critical risk patterns."
    )
)
def get_user_alerts(
    unread_only: bool = Query(False, description="Filter to only unread notifications"),
    severity: Optional[str] = Query(None, description="Filter by severity (CRITICAL, HIGH, MODERATE, INFO)"),
    alert_type: Optional[str] = Query(None, description="Filter by specific alert type"),
    limit: int = Query(50, ge=1, le=200, description="Max alerts to retrieve"),
    current_user: dict = Depends(get_current_user),
    alert_service: AlertService = Depends(get_alert_service)
):
    alerts = alert_service.get_alerts_for_user(
        current_user=current_user,
        unread_only=unread_only,
        severity=severity,
        alert_type=alert_type,
        limit=limit
    )
    unread_counts = alert_service.get_unread_counts(current_user)
    
    return {
        "total_alerts": len(alerts),
        "unread_count": unread_counts["total_unread"],
        "alerts": alerts,
        "role": current_user.get("role", "FARMER"),
        "disclaimer": (
            "Alert recommendations provide biosecurity, physical isolation, and triage guidance only. "
            "They do NOT constitute veterinary medical prescriptions or treatment orders."
        )
    }

@router.get(
    "/unread-count",
    summary="Get Unread Alert Counts",
    description="Retrieves the count of unread alerts broken down by severity for notification badge display."
)
def get_unread_alert_count(
    current_user: dict = Depends(get_current_user),
    alert_service: AlertService = Depends(get_alert_service)
):
    return alert_service.get_unread_counts(current_user)

@router.post(
    "/{alert_id}/read",
    summary="Mark Alert as Read",
    description="Marks a specific alert as read."
)
def mark_alert_read(
    alert_id: str,
    current_user: dict = Depends(get_current_user),
    alert_service: AlertService = Depends(get_alert_service)
):
    success = alert_service.mark_as_read(alert_id, current_user)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert '{alert_id}' not found."
        )
    return {"status": "success", "alert_id": alert_id, "is_read": True}

@router.post(
    "/read-all",
    summary="Mark All Alerts as Read",
    description="Marks all unread alerts for the current user as read."
)
def mark_all_alerts_read(
    current_user: dict = Depends(get_current_user),
    alert_service: AlertService = Depends(get_alert_service)
):
    marked_count = alert_service.mark_all_as_read(current_user)
    return {"status": "success", "marked_count": marked_count}

@router.post(
    "/{alert_id}/dismiss",
    summary="Dismiss Alert",
    description="Dismisses an alert from the active user notification stream."
)
def dismiss_user_alert(
    alert_id: str,
    current_user: dict = Depends(get_current_user),
    alert_service: AlertService = Depends(get_alert_service)
):
    success = alert_service.dismiss_alert(alert_id, current_user)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert '{alert_id}' not found."
        )
    return {"status": "success", "alert_id": alert_id, "is_dismissed": True}

@router.post(
    "/seed-samples",
    summary="Seed Role-Specific Sample Alerts",
    description="Populates representative demo alerts tailored for Farmer, Veterinarian, and Admin roles."
)
def seed_sample_alerts(
    current_user: dict = Depends(get_current_user),
    alert_service: AlertService = Depends(get_alert_service)
):
    role = str(current_user.get("role", "FARMER")).upper()
    username = current_user.get("username", "user")
    created = []

    if role == "FARMER":
        # 1. High-risk assessment
        a1 = alert_service.trigger_farmer_high_risk_alert(
            farmer_username=username,
            animal={"_id": "demo_cow_01", "animal_id": "MH-PUN-001", "species": "Cattle"},
            report={
                "id": "demo_rep_01",
                "top_condition": "Lumpy Skin Disease",
                "risk_level": "High",
                "final_risk_score": 74.0,
                "village": current_user.get("village", "Wagholi"),
                "taluka": current_user.get("taluka", "Haveli"),
                "district": current_user.get("district", "Pune")
            }
        )
        created.append(a1)
        
        # 2. Vaccination due
        a2 = alert_service.trigger_vaccination_due_alert(
            farmer_username=username,
            animal={"_id": "demo_cow_02", "animal_id": "MH-PUN-002", "species": "Cattle"},
            vaccine_name="Foot-and-Mouth Disease (FMD) Booster",
            due_date_str="2026-09-15",
            is_overdue=False
        )
        created.append(a2)
        
        # 3. Regional risk
        a3 = alert_service.trigger_regional_disease_risk_alert(
            disease="Lumpy Skin Disease",
            taluka=current_user.get("taluka", "Haveli"),
            district=current_user.get("district", "Pune"),
            cluster_id="cluster_demo_01"
        )
        created.append(a3)

    elif role == "VETERINARIAN":
        # 1. High-risk review required
        a1 = alert_service.trigger_vet_review_required_alert(
            animal={"_id": "demo_cow_03", "animal_id": "MH-HAV-901", "species": "Cattle"},
            report={
                "id": "demo_rep_02",
                "surveillance_case_id": "case_demo_01",
                "top_condition": "Foot-and-Mouth Disease",
                "risk_level": "Critical",
                "final_risk_score": 84.5,
                "village": "Loni Kalbhor",
                "taluka": "Haveli",
                "district": "Pune"
            }
        )
        created.append(a1)
        
        # 2. Potential disease cluster
        a2 = alert_service.trigger_vet_cluster_alert(
            cluster={
                "cluster_id": "cluster_demo_02",
                "disease": "Foot-and-Mouth Disease",
                "report_count": 4,
                "unique_farms_count": 3,
                "radius_km": 3.2,
                "talukas": ["Haveli"],
                "districts": ["Pune"],
                "risk_level": "Critical"
            }
        )
        created.append(a2)

    elif role in ["ADMIN", "OFFICER"]:
        # 1. Emerging cluster
        a1 = alert_service.trigger_admin_emerging_cluster_alert(
            cluster={
                "cluster_id": "cluster_demo_03",
                "disease": "Lumpy Skin Disease",
                "report_count": 5,
                "unique_farms_count": 4,
                "talukas": ["Baramati", "Daund"],
                "districts": ["Pune"]
            }
        )
        created.append(a1)
        
        # 2. Critical risk pattern
        a2 = alert_service.trigger_admin_critical_risk_pattern_alert(
            cluster={
                "cluster_id": "cluster_demo_04",
                "disease": "Anthrax (Suspected)",
                "report_count": 6,
                "average_risk_score": 92.0,
                "districts": ["Pune"]
            }
        )
        created.append(a2)

    return {
        "status": "success",
        "role": role,
        "seeded_count": len(created),
        "alerts": created
    }
