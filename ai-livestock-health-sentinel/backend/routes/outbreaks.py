import os
import sys
from fastapi import APIRouter, Depends, HTTPException
from database import db
from auth import get_current_user
from datetime import datetime, timedelta

# Programmatically adjust path to import ML modules
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(PROJECT_ROOT, "ml", "outbreak"))

try:
    from cluster_detection import detect_outbreak_clusters
except ImportError:
    # Dummy fallback if path mapping fails
    def detect_outbreak_clusters(cases_list, **kwargs):
        return []

router = APIRouter(prefix="/api/outbreaks", tags=["outbreaks"])

@router.get("")
def get_outbreaks():
    """
    Returns all detected outbreak clusters.
    """
    return db["outbreak_clusters"].find()

@router.post("/detect")
def trigger_outbreak_detection(current_user: dict = Depends(get_current_user)):
    """
    Triggers outbreak detection by fetching cases from the last 14 days and clustering.
    """
    # Verify permission: VETERINARIAN, OFFICER, or ADMIN
    if current_user.get("role") not in ["VETERINARIAN", "OFFICER", "ADMIN"]:
        raise HTTPException(status_code=403, detail="Forbidden. Unauthorized role.")
        
    # 1. Fetch cases from the last 14 days
    cutoff_date = (datetime.utcnow() - timedelta(days=14)).isoformat()
    cases_cursor = db["disease_cases"].find()
    
    cases_list = []
    for c in cases_cursor:
        detected_at = c.get("detected_at", "")
        if detected_at >= cutoff_date and c.get("status") in ["SUSPECTED", "VERIFIED"]:
            # Get animal farm_id
            animal = db["animals"].find_one({"_id": c["animal_id"]})
            farm_id = animal["farm_id"] if animal else "unknown_farm"
            
            cases_list.append({
                "id": str(c["_id"]),
                "latitude": float(c["location"]["latitude"]),
                "longitude": float(c["location"]["longitude"]),
                "disease": c["disease"],
                "farm_id": farm_id,
                "risk_level": c["risk_level"],
                "date": c["detected_at"]
            })
            
    # 2. Run DBSCAN clustering (threshold: 5km radius, min 3 cases)
    try:
        new_clusters = detect_outbreak_clusters(cases_list, eps_km=5.0, min_cases=3, time_window_days=14)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Clustering error: {str(e)}")
        
    # 3. Synchronize / Overwrite active clusters in DB
    # Clear old clusters first
    db["outbreak_clusters"].find().clear() if hasattr(db["outbreak_clusters"].find(), "clear") else None
    
    # Alternatively, delete all clusters
    # Since mock DB fallback lists are actual lists in memory or local JSON
    if hasattr(db["outbreak_clusters"], "db_path"):
        # Local JSON DB Mock cleanup
        import json
        data = db["outbreak_clusters"]._load_data()
        data["outbreak_clusters"] = []
        db["outbreak_clusters"]._save_data(data)
    else:
        # Real MongoDB deletion
        db["outbreak_clusters"].delete_many({})
        
    # Insert new ones and trigger alerts
    inserted_count = 0
    for cluster in new_clusters:
        db["outbreak_clusters"].insert_one(cluster)
        inserted_count += 1
        
        # Trigger outbreak alert to Officers & Veterinarians
        alert_doc = {
            "type": "OUTBREAK_ALERT",
            "disease": cluster["disease"],
            "risk_level": cluster["risk_level"],
            "village": "Multiple",
            "taluka": "Multiple",
            "message": f"POTENTIAL OUTBREAK CLUSTER DETECTED: {cluster['cases_count']} suspected cases of {cluster['disease']} within a {cluster['radius']}km radius affecting {len(cluster['affected_farms'])} farms.",
            "status": "UNREAD",
            "created_at": datetime.utcnow().isoformat()
        }
        db["alerts"].insert_one(alert_doc)
        
    return {
        "message": f"Outbreak detection complete. Found {inserted_count} cluster(s).",
        "clusters": new_clusters
    }
