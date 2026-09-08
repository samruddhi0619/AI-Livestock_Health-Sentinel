from fastapi import APIRouter, Depends, HTTPException, status
from auth import get_current_user
from services.cluster_service import get_cluster_service, ClusterDetectionService

router = APIRouter(prefix="/api/outbreaks", tags=["outbreaks"])

@router.get("")
def get_outbreaks(
    cluster_service: ClusterDetectionService = Depends(get_cluster_service)
):
    """
    Returns all detected potential disease clusters.
    """
    return cluster_service.list_clusters(limit=100)

@router.post("/detect")
def trigger_outbreak_detection(
    current_user: dict = Depends(get_current_user),
    cluster_service: ClusterDetectionService = Depends(get_cluster_service)
):
    """
    Triggers spatio-temporal cluster detection on high-risk reports.
    Uses 'Potential Disease Cluster' and 'Emerging Risk Pattern' terminology.
    """
    role = str(current_user.get("role", "")).upper()
    if role not in ["VETERINARIAN", "OFFICER", "ADMIN"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden. Cluster detection execution requires Veterinarian, Officer, or Admin credentials."
        )

    try:
        new_clusters = cluster_service.run_detection(persist=True, emit_alerts=True)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Clustering error: {str(e)}"
        )

    return {
        "status": "success",
        "message": f"Cluster detection complete. Identified {len(new_clusters)} potential disease cluster(s).",
        "pattern_type": "Emerging Risk Pattern",
        "clusters": new_clusters,
        "is_confirmed_outbreak": False,
        "is_veterinary_diagnosis": False,
        "disclaimer": (
            "This is an AI-assisted spatio-temporal cluster detection (Emerging Risk Pattern). "
            "It does NOT constitute a confirmed epidemiological outbreak or official veterinary diagnosis."
        )
    }
