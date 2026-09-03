from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from database import db
from auth import get_current_user
from models import AnimalCreate
from datetime import datetime

router = APIRouter(prefix="/api/animals", tags=["animals"])

@router.get("")
def get_animals(current_user: dict = Depends(get_current_user)):
    role = current_user.get("role", "").upper()
    
    # Farmers only see their own registered animals
    if role == "FARMER":
        return db["animals"].find({"farm_id": current_user["username"]})
    else:
        # Veterinarians, Officers, Admins see all animals
        return db["animals"].find()

@router.post("")
def create_animal(animal: AnimalCreate, current_user: dict = Depends(get_current_user)):
    # Farmers use their username as farm_id for simplicity
    farm_id = current_user["username"] if current_user.get("role") == "FARMER" else animal.farm_id
    
    animal_doc = {
        "species": animal.species,
        "breed": animal.breed,
        "age": animal.age,
        "gender": animal.gender,
        "health_history": animal.health_history,
        "farm_id": farm_id,
        "latitude": animal.latitude,
        "longitude": animal.longitude,
        "village": animal.village,
        "taluka": animal.taluka,
        "district": animal.district,
        "created_at": datetime.utcnow().isoformat()
    }
    
    res = db["animals"].insert_one(animal_doc)
    
    # Audit log
    audit_doc = {
        "action": "CREATE_ANIMAL",
        "user": current_user["username"],
        "details": f"Registered animal {res.inserted_id} ({animal.species}, {animal.breed})",
        "timestamp": datetime.utcnow().isoformat()
    }
    db["audit_logs"].insert_one(audit_doc)
    
    return {"message": "Animal registered successfully", "id": res.inserted_id}

@router.get("/{animal_id}")
def get_animal_detail(animal_id: str, current_user: dict = Depends(get_current_user)):
    animal = db["animals"].find_one({"_id": animal_id})
    if not animal:
        raise HTTPException(status_code=404, detail="Animal not found")
        
    role = current_user.get("role", "").upper()
    if role == "FARMER" and animal["farm_id"] != current_user["username"]:
        raise HTTPException(status_code=403, detail="Not authorized to view this animal")
        
    # Get associated health records and vaccinations
    health_records = db["health_records"].find({"animal_id": animal_id})
    vaccinations = db["vaccinations"].find({"animal_id": animal_id})
    cases = db["disease_cases"].find({"animal_id": animal_id})
    
    return {
        "animal": animal,
        "health_records": health_records,
        "vaccinations": vaccinations,
        "cases": cases
    }
