import os
import uuid
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import JSONResponse

from config import settings
from database import db
from auth import get_current_user, RoleChecker, require_clinician, require_authenticated
from schemas import AnimalCreate, AnimalOut, AnimalHealthStatusUpdate, AnimalHealthStatus
from utils.passport_generator import (
    generate_unique_animal_id,
    generate_qr_identifier,
    generate_qr_code_assets
)

router = APIRouter(prefix="/api/animals", tags=["Animals & Digital Passport"])

# ---------------------------------------------------------------------------
# 1. Register Animal (Features 1, 2, 3: Register, Unique ID, QR Code)
# ---------------------------------------------------------------------------
@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Register Animal & Generate Digital Passport",
    description="Registers an animal, generates an official National Ear-Tag ID and cryptographic QR code."
)
def register_animal(animal: AnimalCreate, current_user: dict = Depends(get_current_user)):
    user_id = str(current_user.get("_id", current_user.get("id", "")))
    username = current_user.get("username", "")
    role = str(current_user.get("role", "FARMER")).upper()
    
    # 1. Generate or validate Unique Animal ID
    district_code = animal.district or current_user.get("district", "MH")
    tag_id = animal.animal_id.strip().upper() if animal.animal_id else generate_unique_animal_id(animal.species, district_code)
    
    # Check uniqueness of Animal Tag ID
    existing = db["animals"].find_one({"animal_id": tag_id})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Animal with tag identifier '{tag_id}' already exists."
        )
        
    # 2. Generate Cryptographic QR Code Identifier
    qr_token = animal.qr_code_identifier or generate_qr_identifier()
    
    # 3. Generate QR Code Image Assets (File on disk & Base64 Data URI)
    qr_verify_url = f"/api/animals/qr/{qr_token}"
    qr_file_url, qr_base64 = generate_qr_code_assets(qr_verify_url, tag_id)
    
    now_str = datetime.now(timezone.utc).isoformat()
    
    # 4. Construct Animal Record
    animal_doc = {
        "animal_id": tag_id,
        "qr_code_identifier": qr_token,
        "qr_code_url": qr_file_url,
        "qr_code_base64": qr_base64,
        "species": animal.species,
        "breed": animal.breed,
        "age": float(animal.age),
        "gender": animal.gender.value,
        "health_history": animal.health_history or "None",
        "owner_id": username if role == "FARMER" else user_id,
        "owner_name": current_user.get("fullname", username),
        "owner_phone": current_user.get("phone", ""),
        "health_status": "HEALTHY", # Ground truth default
        "latitude": animal.latitude or 18.5204,
        "longitude": animal.longitude or 73.8567,
        "village": animal.village or current_user.get("village", "Wagholi"),
        "taluka": animal.taluka or current_user.get("taluka", "Haveli"),
        "district": animal.district or current_user.get("district", "Pune"),
        "is_simulated_demo": False, # REAL application data
        "created_at": now_str,
        "updated_at": now_str
    }
    
    res = db["animals"].insert_one(animal_doc)
    animal_doc["id"] = res.inserted_id
    
    # Audit log
    db["audit_logs"].insert_one({
        "action": "ANIMAL_REGISTRATION",
        "animal_id": tag_id,
        "performed_by": username,
        "role": role,
        "timestamp": now_str
    })
    
    return {
        "success": True,
        "message": f"Livestock {animal.species} ({tag_id}) registered successfully.",
        "animal_id": tag_id,
        "qr_code_identifier": qr_token,
        "qr_code_url": qr_file_url,
        "qr_code_base64": qr_base64,
        "animal": animal_doc
    }

# ---------------------------------------------------------------------------
# 2. List Animals (Role-Filtered)
# ---------------------------------------------------------------------------
@router.get(
    "",
    summary="List Registered Livestock",
    description="Lists registered livestock. Farmers only see their own herd; Vets and Admins see all animals."
)
def list_animals(
    species: Optional[str] = None,
    health_status: Optional[str] = None,
    search: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    role = str(current_user.get("role", "FARMER")).upper()
    username = current_user.get("username", "")
    
    query = {}
    if role == "FARMER":
        query["owner_id"] = username
        
    if species:
        query["species"] = species
    if health_status:
        query["health_status"] = health_status.upper()
        
    animals = db["animals"].find(query)
    
    if search:
        s = search.lower().strip()
        animals = [
            a for a in animals
            if s in a.get("animal_id", "").lower()
            or s in a.get("breed", "").lower()
            or s in a.get("village", "").lower()
        ]
        
    return {
        "count": len(animals),
        "animals": animals
    }

# ---------------------------------------------------------------------------
# 3. View Basic Animal Profile (Feature 4)
# ---------------------------------------------------------------------------
@router.get(
    "/{animal_id}",
    summary="Get Animal Profile",
    description="Retrieves primary animal profile details by tag identifier or database ID."
)
def get_animal_profile(animal_id: str, current_user: dict = Depends(get_current_user)):
    animal = _find_animal(animal_id)
    if not animal:
        raise HTTPException(status_code=404, detail=f"Animal '{animal_id}' not found.")
        
    _check_animal_view_permission(animal, current_user)
    return animal

# ---------------------------------------------------------------------------
# 4. View Digital Animal Health Passport (Features 4, 5, 6, 7, 8)
# STRICT SEPARATION: Farmer Reported vs AI Generated vs Vet Reviewed
# ---------------------------------------------------------------------------
@router.get(
    "/{animal_id}/passport",
    summary="Get Complete Digital Animal Health Passport",
    description="Returns the full official Health Passport clearly separating Farmer data, AI assessments, and Vet reviews."
)
def get_digital_health_passport(animal_id: str, current_user: dict = Depends(require_authenticated)):
    animal = _find_animal(animal_id)
    if not animal:
        raise HTTPException(status_code=404, detail=f"Animal '{animal_id}' not found.")
        
    _check_animal_view_permission(animal, current_user)
    return _assemble_health_passport(animal)

# ---------------------------------------------------------------------------
# 5. Public / Paravet QR Code Scan Lookup Endpoint (Feature 3)
# ---------------------------------------------------------------------------
@router.get(
    "/qr/{qr_code_identifier}",
    summary="Scan QR Code & Lookup Digital Passport",
    description="Public or Paravet QR code scan endpoint. Resolves QR token to full digital animal health passport."
)
def scan_qr_code(qr_code_identifier: str):
    animal = db["animals"].find_one({"qr_code_identifier": qr_code_identifier})
    if not animal:
        # Fallback check on animal_id
        animal = db["animals"].find_one({"animal_id": qr_code_identifier})
        
    if not animal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No livestock record matches QR identifier '{qr_code_identifier}'."
        )
        
    return _assemble_health_passport(animal)

# ---------------------------------------------------------------------------
# 6. View QR Code Asset
# ---------------------------------------------------------------------------
@router.get(
    "/{animal_id}/qr-code",
    summary="Get Animal QR Code Asset",
    description="Returns the Base64 image and download URL for the animal's QR code."
)
def get_animal_qr_code(animal_id: str, current_user: dict = Depends(require_authenticated)):
    animal = _find_animal(animal_id)
    if not animal:
        raise HTTPException(status_code=404, detail=f"Animal '{animal_id}' not found.")
        
    return {
        "animal_id": animal.get("animal_id"),
        "qr_code_identifier": animal.get("qr_code_identifier"),
        "qr_code_url": animal.get("qr_code_url"),
        "qr_code_base64": animal.get("qr_code_base64"),
        "scan_endpoint": f"/api/animals/qr/{animal.get('qr_code_identifier')}"
    }

# ---------------------------------------------------------------------------
# 7. View Health History (Feature 5: Farmer-Reported Vitals)
# ---------------------------------------------------------------------------
@router.get(
    "/{animal_id}/health-history",
    summary="View Health History",
    description="Returns time-series physiological vitals and checkup observations."
)
def get_animal_health_history(animal_id: str, current_user: dict = Depends(require_authenticated)):
    animal = _find_animal(animal_id)
    if not animal:
        raise HTTPException(status_code=404, detail=f"Animal '{animal_id}' not found.")
        
    _check_animal_view_permission(animal, current_user)
    
    target_tag = animal.get("animal_id")
    target_uuid = str(animal.get("_id", animal.get("id", "")))
    
    records = db["health_records"].find({"$or": [{"animal_id": target_tag}, {"animal_id": target_uuid}]})
    return {
        "animal_id": target_tag,
        "total_records": len(records),
        "health_records": records
    }

# ---------------------------------------------------------------------------
# 8. View Vaccination History (Feature 6: Immunization Records)
# ---------------------------------------------------------------------------
@router.get(
    "/{animal_id}/vaccinations",
    summary="View Vaccination History",
    description="Returns complete immunization ledger and upcoming booster schedule."
)
def get_animal_vaccinations(animal_id: str, current_user: dict = Depends(require_authenticated)):
    animal = _find_animal(animal_id)
    if not animal:
        raise HTTPException(status_code=404, detail=f"Animal '{animal_id}' not found.")
        
    _check_animal_view_permission(animal, current_user)
    
    target_tag = animal.get("animal_id")
    target_uuid = str(animal.get("_id", animal.get("id", "")))
    
    vaccinations = db["vaccinations"].find({"$or": [{"animal_id": target_tag}, {"animal_id": target_uuid}]})
    return {
        "animal_id": target_tag,
        "total_vaccinations": len(vaccinations),
        "vaccination_records": vaccinations
    }

# ---------------------------------------------------------------------------
# 9. View AI Assessments (Feature 7: Autonomous Screening History)
# ---------------------------------------------------------------------------
@router.get(
    "/{animal_id}/assessments",
    summary="View AI Risk Assessments",
    description="Returns autonomous computer vision and symptom prediction results with explicit non-diagnosis disclaimers."
)
def get_animal_ai_assessments(animal_id: str, current_user: dict = Depends(require_authenticated)):
    animal = _find_animal(animal_id)
    if not animal:
        raise HTTPException(status_code=404, detail=f"Animal '{animal_id}' not found.")
        
    _check_animal_view_permission(animal, current_user)
    
    target_tag = animal.get("animal_id")
    target_uuid = str(animal.get("_id", animal.get("id", "")))
    
    assessments = db["ai_predictions"].find({"$or": [{"animal_id": target_tag}, {"animal_id": target_uuid}]})
    return {
        "animal_id": target_tag,
        "total_screenings": len(assessments),
        "ai_screenings": assessments,
        "is_veterinary_diagnosis": False,
        "disclaimer": "AI screening and risk triage tool only. Not a veterinary diagnosis. Confirmatory testing required."
    }

# ---------------------------------------------------------------------------
# 10. View Veterinarian Reviews (Feature 8: Clinical Adjudication History)
# ---------------------------------------------------------------------------
@router.get(
    "/{animal_id}/reviews",
    summary="View Veterinarian Clinical Reviews",
    description="Returns official veterinary clinical adjudications, PCR/ELISA assays, and prescribed treatments."
)
def get_animal_vet_reviews(animal_id: str, current_user: dict = Depends(require_authenticated)):
    animal = _find_animal(animal_id)
    if not animal:
        raise HTTPException(status_code=404, detail=f"Animal '{animal_id}' not found.")
        
    _check_animal_view_permission(animal, current_user)
    
    target_tag = animal.get("animal_id")
    target_uuid = str(animal.get("_id", animal.get("id", "")))
    
    reviews = db["veterinarian_reviews"].find({"$or": [{"animal_id": target_tag}, {"animal_id": target_uuid}]})
    return {
        "animal_id": target_tag,
        "total_reviews": len(reviews),
        "veterinarian_reviews": reviews
    }

# ---------------------------------------------------------------------------
# 11. Update Confirmed Health Status (Restricted to VETERINARIAN & ADMIN)
# ---------------------------------------------------------------------------
@router.patch(
    "/{animal_id}/health-status",
    summary="Update Confirmed Health Status",
    description="Authoritatively updates an animal's ground truth health status. Restricted to Veterinarians and Admins."
)
def update_animal_health_status(
    animal_id: str,
    payload: AnimalHealthStatusUpdate,
    current_user: dict = Depends(require_clinician)
):
    animal = _find_animal(animal_id)
    if not animal:
        raise HTTPException(status_code=404, detail=f"Animal '{animal_id}' not found.")
        
    new_status = payload.health_status.value
    target_id = animal.get("_id")
    
    db["animals"].update_one(
        {"_id": target_id},
        {
            "$set": {
                "health_status": new_status,
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "status_updated_by": current_user.get("fullname", current_user.get("username")),
                "status_update_reason": payload.clinical_reason or "Veterinary Clinical Adjudication"
            }
        }
    )
    
    # Audit log
    db["audit_logs"].insert_one({
        "action": "UPDATE_HEALTH_STATUS",
        "animal_id": animal.get("animal_id"),
        "old_status": animal.get("health_status"),
        "new_status": new_status,
        "clinician": current_user.get("username"),
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    
    return {
        "success": True,
        "message": f"Confirmed health status for {animal.get('animal_id')} updated to {new_status}.",
        "animal_id": animal.get("animal_id"),
        "health_status": new_status
    }

# ---------------------------------------------------------------------------
# Helper Assembly Functions
# ---------------------------------------------------------------------------
def _find_animal(identifier: str) -> Optional[dict]:
    # 1. Try match by human-readable animal_id (TAG-MH-2026-...)
    animal = db["animals"].find_one({"animal_id": identifier})
    if animal:
        return animal
    # 2. Try match by internal primary key _id
    animal = db["animals"].find_one({"_id": identifier})
    if animal:
        return animal
    # 3. Try match by QR identifier
    animal = db["animals"].find_one({"qr_code_identifier": identifier})
    return animal

def _check_animal_view_permission(animal: dict, current_user: dict):
    role = str(current_user.get("role", "")).upper()
    if role in ["VETERINARIAN", "ADMIN", "OFFICER"]:
        return # Full clearance
    username = current_user.get("username", "")
    if animal.get("owner_id") != username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. You can only view health passports for livestock in your registered herd."
        )

def _assemble_health_passport(animal: dict) -> dict:
    target_tag = animal.get("animal_id")
    target_uuid = str(animal.get("_id", animal.get("id", "")))
    
    # 1. Fetch Farmer-reported health records & checkups
    records = db["health_records"].find({"$or": [{"animal_id": target_tag}, {"animal_id": target_uuid}]})
    
    # 2. Fetch Immunization ledger
    vaccinations = db["vaccinations"].find({"$or": [{"animal_id": target_tag}, {"animal_id": target_uuid}]})
    
    # 3. Fetch Autonomous AI Risk Screenings
    ai_screenings = db["ai_predictions"].find({"$or": [{"animal_id": target_tag}, {"animal_id": target_uuid}]})
    
    # 4. Fetch Veterinarian Clinical Reviews & Laboratory Assays
    vet_reviews = db["veterinarian_reviews"].find({"$or": [{"animal_id": target_tag}, {"animal_id": target_uuid}]})
    
    is_demo = animal.get("is_simulated_demo", True if "SIM" in target_tag else False)
    
    return {
        "passport_metadata": {
            "passport_number": f"PASSPORT-{target_tag}",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "verification_endpoint": f"/api/animals/qr/{animal.get('qr_code_identifier')}",
            "data_provenance": "Simulated Demo Dataset" if is_demo else "Live Registered Application Data",
            "is_simulated_demo": is_demo
        },
        "animal_profile": {
            "id": target_uuid,
            "animal_id": target_tag,
            "qr_code_identifier": animal.get("qr_code_identifier"),
            "qr_code_url": animal.get("qr_code_url"),
            "qr_code_base64": animal.get("qr_code_base64"),
            "species": animal.get("species", "Cattle"),
            "breed": animal.get("breed"),
            "age_years": animal.get("age"),
            "gender": animal.get("gender"),
            "confirmed_health_status": animal.get("health_status", "HEALTHY"),
            "owner": {
                "owner_id": animal.get("owner_id"),
                "name": animal.get("owner_name", animal.get("owner_id")),
                "phone": animal.get("owner_phone", ""),
                "village": animal.get("village"),
                "taluka": animal.get("taluka"),
                "district": animal.get("district")
            },
            "registered_at": animal.get("created_at")
        },
        # TIER 1: Farmer-Reported Information
        "farmer_reported_information": {
            "total_checkups": len(records),
            "checkup_records": records,
            "disclaimer": "Submitted directly by livestock owner/farmer. Subject to clinical verification by a registered veterinarian."
        },
        # TIER 2: AI-Generated Risk Assessments (Probabilistic, Never Final Diagnosis)
        "ai_generated_risk_assessments": {
            "total_screenings": len(ai_screenings),
            "screening_records": ai_screenings,
            "is_veterinary_diagnosis": False,
            "disclaimer": "AI screening and risk triage tool only. Not a veterinary diagnosis. Confirmatory testing required."
        },
        # TIER 3: Veterinarian-Reviewed Information (Authoritative Clinical Adjudication)
        "veterinarian_reviewed_information": {
            "total_reviews": len(vet_reviews),
            "review_records": vet_reviews,
            "disclaimer": "Authoritative clinical adjudication and treatment orders issued by registered veterinary medical officer."
        },
        # Immunization Tracking
        "vaccination_history": {
            "total_vaccinations": len(vaccinations),
            "records": vaccinations
        }
    }
