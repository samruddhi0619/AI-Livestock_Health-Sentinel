from fastapi import APIRouter, Depends, HTTPException
from database import db
from auth import get_current_user
from models import VaccinationCreate
from datetime import datetime

router = APIRouter(prefix="/api/vaccinations", tags=["vaccinations"])

@router.get("")
def get_vaccinations(animal_id: str = None, current_user: dict = Depends(get_current_user)):
    query = {}
    if animal_id:
        query["animal_id"] = animal_id
        
    role = current_user.get("role", "").upper()
    if role == "FARMER":
        # Farmer can see vaccinations of their animals
        if animal_id:
            animal = db["animals"].find_one({"_id": animal_id})
            if not animal or animal["farm_id"] != current_user["username"]:
                raise HTTPException(status_code=403, detail="Not authorized")
        else:
            # All animals of this farmer
            farmer_animals = db["animals"].find({"farm_id": current_user["username"]})
            ids = [a["_id"] for a in farmer_animals]
            query["animal_id"] = {"$in": ids}
            
    return db["vaccinations"].find(query)

@router.post("")
def record_vaccination(payload: VaccinationCreate, current_user: dict = Depends(get_current_user)):
    # Verify animal exists
    animal = db["animals"].find_one({"_id": payload.animal_id})
    if not animal:
        raise HTTPException(status_code=404, detail="Animal not found")
        
    # Check permission
    role = current_user.get("role", "").upper()
    if role == "FARMER" and animal["farm_id"] != current_user["username"]:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    vacc_doc = {
        "animal_id": payload.animal_id,
        "vaccine_name": payload.vaccine_name,
        "date_administered": payload.date_administered,
        "next_due_date": payload.next_due_date,
        "recorded_by": current_user["username"],
        "created_at": datetime.utcnow().isoformat()
    }
    
    db["vaccinations"].insert_one(vacc_doc)
    return {"message": "Vaccination recorded successfully"}
