from fastapi import APIRouter, Depends, HTTPException
from database import db
from auth import get_current_user
from pydantic import BaseModel

router = APIRouter(prefix="/api/admin", tags=["admin"])

class ConfigUpdateRequest(BaseModel):
    low_risk_threshold: int
    high_risk_threshold: int
    dbscan_eps_km: float
    dbscan_min_cases: int

@router.get("/users")
def get_users(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin authorization required.")
    
    users = db["users"].find()
    # Strip passwords for security
    for u in users:
        u.pop("password", None)
    return users

@router.get("/config")
def get_system_config():
    """
    Returns configurable risk thresholds and ML configurations.
    """
    config = db["system_config"].find_one({"type": "main"})
    if not config:
        # Default configuration
        config = {
            "type": "main",
            "low_risk_threshold": 40,
            "high_risk_threshold": 70,
            "dbscan_eps_km": 5.0,
            "dbscan_min_cases": 3
        }
        db["system_config"].insert_one(config)
    return config

@router.put("/config")
def update_system_config(payload: ConfigUpdateRequest, current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin authorization required.")
        
    db["system_config"].update_one(
        {"type": "main"},
        {
            "$set": {
                "low_risk_threshold": payload.low_risk_threshold,
                "high_risk_threshold": payload.high_risk_threshold,
                "dbscan_eps_km": payload.dbscan_eps_km,
                "dbscan_min_cases": payload.dbscan_min_cases
            }
        }
    )
    
    # Audit log
    import datetime
    audit_doc = {
        "action": "UPDATE_SYSTEM_CONFIG",
        "user": current_user["username"],
        "details": f"Updated thresholds: Low={payload.low_risk_threshold}, High={payload.high_risk_threshold}",
        "timestamp": datetime.datetime.utcnow().isoformat()
    }
    db["audit_logs"].insert_one(audit_doc)
    
    return {"message": "Configuration updated successfully"}

@router.post(
    "/seed-demo-data",
    summary="Seed Controlled SIH Demonstration Dataset",
    description=(
        "Populates clean demo records for Farmers, Veterinarians, Animals, Health Records, "
        "Vaccinations, and Disease Reports, triggering the intentional spatial cluster scenario. "
        "All records are explicitly tagged as simulated prototype data."
    )
)
def seed_demo_dataset(current_user: dict = Depends(get_current_user)):
    role = str(current_user.get("role", "")).upper()
    if role not in ["ADMIN", "VETERINARIAN"]:
        raise HTTPException(status_code=403, detail="Demo dataset seeding is restricted to Administrators and Veterinarians.")
    
    from generate_demo_data import seed_demo_data
    try:
        seed_demo_data()
        return {
            "status": "success",
            "message": "Controlled SIH demonstration dataset seeded successfully.",
            "data_provenance": "Simulated Prototype SIH Dataset",
            "dataset_label": "SIMULATED_DEMO_SIH_2026",
            "is_simulated_demo": True,
            "ml_training_eligible": False
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to seed demo dataset: {str(e)}")

