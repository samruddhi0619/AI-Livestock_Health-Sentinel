from fastapi import APIRouter, Depends, HTTPException, status
from database import db
from auth import get_current_user, RoleChecker
from models import CaseVerifyRequest
from datetime import datetime

router = APIRouter(prefix="/api/cases", tags=["cases"])

@router.get("")
def get_cases(
    status_filter: str = None,
    disease_filter: str = None,
    district_filter: str = None,
    current_user: dict = Depends(get_current_user)
):
    query = {}
    if status_filter:
        query["status"] = status_filter.upper()
    if disease_filter:
        query["disease"] = disease_filter
    if district_filter:
        query["district"] = district_filter
        
    cases = db["disease_cases"].find(query)
    
    # Hydrate cases with animal details (breed, age, species)
    hydrated_cases = []
    for c in cases:
        animal = db["animals"].find_one({"$or": [{"_id": c.get("animal_id")}, {"animal_id": c.get("animal_id")}]})
        if animal:
            c["animal_details"] = {
                "species": animal.get("species", "Cattle"),
                "breed": animal.get("breed", "Unknown"),
                "age": animal.get("age", 4.0),
                "gender": animal.get("gender", "Female")
            }
        hydrated_cases.append(c)
        
    return hydrated_cases

@router.put("/{case_id}/verify")
def verify_case(
    case_id: str,
    payload: CaseVerifyRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Veterinary officer verification of a suspected disease case.
    """
    # Verify current user is Vet or Admin
    if current_user.get("role") not in ["VETERINARIAN", "ADMIN"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only veterinarians can verify disease cases"
        )
        
    case = db["disease_cases"].find_one({"$or": [{"_id": case_id}, {"id": case_id}]})
    if not case:
        raise HTTPException(status_code=404, detail="Disease case not found")
        
    # Update Case Status
    db["disease_cases"].update_one(
        {"$or": [{"_id": case_id}, {"id": case_id}]},
        {
            "$set": {
                "status": payload.status.upper(),
                "verified_by": current_user["username"],
                "verification_date": datetime.utcnow().isoformat()
            }
        }
    )
    
    # Store Treatment plan
    treatment_doc = {
        "case_id": case_id,
        "animal_id": case.get("animal_id"),
        "diagnosis": payload.diagnosis,
        "treatment_plan": payload.treatment,
        "follow_up": payload.follow_up,
        "prescribed_by": current_user["username"],
        "created_at": datetime.utcnow().isoformat()
    }
    db["treatments"].insert_one(treatment_doc)
    
    # If VERIFIED, check if it triggers an outbreak alert or update clusters
    # Insert notification for the Farmer
    animal = db["animals"].find_one({"$or": [{"_id": case.get("animal_id")}, {"animal_id": case.get("animal_id")}]})
    if animal:
        farmer_alert = {
            "type": "TREATMENT_PLAN",
            "animal_id": case.get("animal_id"),
            "farm_id": animal.get("farm_id") or animal.get("owner_id") or "unspecified_farm",
            "disease": case.get("disease", "Suspected Condition"),
            "risk_level": case.get("risk_level", "High"),
            "village": case.get("village", "Unknown"),
            "taluka": case.get("taluka", "Unknown"),
            "message": f"Veterinarian verified {case.get('disease')} for animal {case.get('animal_id')}. Treatment plan details: {payload.treatment[:100]}...",
            "status": "UNREAD",
            "created_at": datetime.utcnow().isoformat()
        }
        db["alerts"].insert_one(farmer_alert)
        
    # Audit log
    audit_doc = {
        "action": f"VERIFY_CASE_{payload.status.upper()}",
        "user": current_user["username"],
        "details": f"Case {case_id} status updated to {payload.status.upper()} by {current_user['username']}",
        "timestamp": datetime.utcnow().isoformat()
    }
    db["audit_logs"].insert_one(audit_doc)
    
    return {"message": "Case updated successfully"}
