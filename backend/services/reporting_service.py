import os
import io
import uuid
import base64
import time
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, Union

from config import settings
from database import db
from services.image_service import get_image_service
from services.symptom_service import get_symptom_service
from services.environmental_service import get_environmental_service
from services.multi_modal_engine import get_multi_modal_engine

class HealthReportingService:
    """
    Orchestrates end-to-end livestock health reporting:
      1. Validates animal and farmer authorization
      2. Ingests and sanitizes approximate vs. authorized location
      3. Executes available autonomous AI models (Image, Symptom, Environmental)
      4. Synthesizes multi-modal risk via MultiModalRiskEngine
      5. Persists the health record
      6. Automatically triggers disease surveillance reports & alerts for High/Critical risk
      7. Enforces privacy-aware location filtering based on caller role
    """
    _instance: Optional["HealthReportingService"] = None

    def __init__(self):
        self.image_service = get_image_service()
        self.symptom_service = get_symptom_service()
        self.env_service = get_environmental_service()
        self.multi_modal_engine = get_multi_modal_engine()

    @classmethod
    def get_instance(cls) -> "HealthReportingService":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def process_location(
        self,
        location_data: Optional[Dict[str, Any]],
        animal: Dict[str, Any],
        user: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Extracts, fuzzed-masks, and categorizes location coordinates to preserve farm privacy.
        """
        # Priority: explicit location payload -> animal registered location -> user profile defaults
        loc = location_data or {}
        raw_lat = loc.get("latitude")
        raw_lng = loc.get("longitude")
        
        if raw_lat is None:
            raw_lat = animal.get("latitude") or 18.5204
        if raw_lng is None:
            raw_lng = animal.get("longitude") or 73.8567
            
        exact_lat = float(raw_lat)
        exact_lng = float(raw_lng)
        
        # Privacy Fuzzing: Truncate to 2 decimal places (~1.1 km grid resolution)
        approx_lat = round(exact_lat, 2)
        approx_lng = round(exact_lng, 2)
        
        village = loc.get("village") or animal.get("village") or user.get("village", "Wagholi")
        taluka = loc.get("taluka") or animal.get("taluka") or user.get("taluka", "Haveli")
        district = loc.get("district") or animal.get("district") or user.get("district", "Pune")
        share_location = loc.get("share_location", True)
        
        return {
            "exact_latitude": exact_lat,
            "exact_longitude": exact_lng,
            "approximate_latitude": approx_lat,
            "approximate_longitude": approx_lng,
            "village": village,
            "taluka": taluka,
            "district": district,
            "share_location": share_location
        }

    def filter_location_for_user(
        self,
        report: Dict[str, Any],
        current_user: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Enforces privacy guardrails:
        - Owning Farmer or Admin: Receives full authorized coordinates.
        - Treating Veterinarian on active surveillance case: Receives authorized coordinates.
        - Other Veterinarians, Paravets, and Public: Receives fuzzed ~1.1km coordinates only.
        """
        user_role = str(current_user.get("role", "FARMER")).upper()
        username = current_user.get("username", "")
        user_id = str(current_user.get("_id", current_user.get("id", "")))
        
        is_owner = (
            report.get("owner_id") == username or 
            report.get("owner_id") == user_id or
            report.get("recorded_by") == username
        )
        is_admin = user_role == "ADMIN"
        is_emergency_clinician = (
            user_role == "VETERINARIAN" and 
            report.get("is_surveillance_triggered", False)
        )
        
        if is_owner or is_admin or is_emergency_clinician:
            access_level = "authorized_exact"
            lat = report.get("exact_latitude")
            lng = report.get("exact_longitude")
        else:
            access_level = "approximate_public"
            lat = report.get("approximate_latitude")
            lng = report.get("approximate_longitude")
            
        return {
            "latitude": lat,
            "longitude": lng,
            "approximate_latitude": report.get("approximate_latitude"),
            "approximate_longitude": report.get("approximate_longitude"),
            "village": report.get("village"),
            "taluka": report.get("taluka"),
            "district": report.get("district"),
            "access_level": access_level
        }

    def submit_report(
        self,
        animal_id: str,
        symptoms: List[str],
        image_bytes: Optional[bytes] = None,
        image_url: Optional[str] = None,
        image_base64: Optional[str] = None,
        location: Optional[Dict[str, Any]] = None,
        body_temperature_c: float = 38.5,
        appetite_score: float = 1.0,
        milk_yield_liters: float = 0.0,
        activity_score: float = 1.0,
        clinical_notes: Optional[str] = None,
        current_user: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Coordinates full multi-modal health reporting workflow.
        """
        now_utc = datetime.now(timezone.utc)
        now_iso = now_utc.isoformat()
        current_user = current_user or {}
        username = current_user.get("username", "anonymous_farmer")
        role = str(current_user.get("role", "FARMER")).upper()
        
        # 1. Look up Animal in Database
        animal = db["animals"].find_one({"$or": [{"animal_id": animal_id}, {"_id": animal_id}]})
        if not animal:
            raise ValueError(f"Animal with identifier '{animal_id}' was not found.")
            
        # Ownership check: Farmers can only submit for their own herd
        if role == "FARMER":
            owner_id = animal.get("owner_id")
            if owner_id and owner_id != username and owner_id != current_user.get("_id"):
                raise PermissionError("Access denied: You can only submit health reports for animals in your registered herd.")

        # 2. Process Location with Privacy Guardrails
        loc_info = self.process_location(location, animal, current_user)
        
        # 3. Handle Image Ingestion & Analysis
        image_score = None
        image_result = None
        saved_image_url = image_url
        
        # Process image bytes or base64
        if image_base64:
            try:
                b64_str = image_base64.split(",")[1] if "," in image_base64 else image_base64
                image_bytes = base64.b64decode(b64_str)
            except Exception:
                pass
                
        if image_bytes:
            # Save file to disk
            upload_dir = settings.UPLOAD_DIR
            os.makedirs(upload_dir, exist_ok=True)
            unique_filename = f"health_{uuid.uuid4().hex[:12]}.jpg"
            file_path = os.path.join(upload_dir, unique_filename)
            with open(file_path, "wb") as f:
                f.write(image_bytes)
            saved_image_url = f"/uploads/{unique_filename}"
            
            # Run Image Risk Analysis
            try:
                image_result = self.image_service.analyze_image(image_bytes, filename=unique_filename)
                image_score = image_result.get("risk_score")
            except Exception as e:
                image_result = {"error": str(e), "quality_check_passed": False}
        elif saved_image_url and os.path.exists(os.path.join(settings.BASE_DIR, "..", saved_image_url.lstrip("/"))):
            local_p = os.path.join(settings.BASE_DIR, "..", saved_image_url.lstrip("/"))
            with open(local_p, "rb") as f:
                b = f.read()
            image_result = self.image_service.analyze_image(b)
            image_score = image_result.get("risk_score")

        # 4. Run Symptom-Based Risk Analysis
        symptom_result = None
        symptom_score = None
        if symptoms:
            symptom_result = self.symptom_service.analyze_symptoms(
                symptoms=symptoms,
                age=float(animal.get("age", 4.0)),
                breed=str(animal.get("breed", "gir")).lower(),
                gender=str(animal.get("gender", "female")).lower(),
                history=str(animal.get("health_history", "none")),
                vaccination=str(animal.get("vaccination_status", "not_vaccinated"))
            )
            symptom_score = symptom_result.get("risk_score")

        # 5. Run Environmental Risk Analysis using approximate location
        env_result = None
        env_score = None
        if loc_info["share_location"]:
            env_result = self.env_service.analyze_environment(
                latitude=loc_info["approximate_latitude"],
                longitude=loc_info["approximate_longitude"]
            )
            env_score = env_result.get("environmental_risk_score")

        # 6. Synthesize Multi-Modal Risk
        multi_modal_eval = self.multi_modal_engine.evaluate(
            image_risk_score=image_score,
            symptom_risk_score=symptom_score,
            environmental_risk_score=env_score,
            vaccination_status=animal.get("vaccination_status", "not_vaccinated"),
            health_history=animal.get("health_history", "none")
        )
        
        final_risk_score = multi_modal_eval["final_risk_score"]
        risk_level = multi_modal_eval["risk_level"]
        top_condition = "Suspected Disease"
        if symptom_result and symptom_result.get("top_condition"):
            top_condition = symptom_result["top_condition"]
        elif image_result and image_result.get("predicted_class"):
            top_condition = image_result["predicted_class"]

        # 7. Determine Automated Disease Surveillance Escalation
        # High-risk (61-80) or Critical (81-100) automatically triggers surveillance case
        is_high_risk = risk_level in ["High", "Critical"] or final_risk_score >= 61.0
        surveillance_case_id = None
        
        report_id = str(uuid.uuid4())
        
        if is_high_risk:
            surveillance_case_id = str(uuid.uuid4())
            
            # Create Case in disease_reports & disease_cases
            case_doc = {
                "_id": surveillance_case_id,
                "id": surveillance_case_id,
                "animal_id": animal["_id"],
                "animal_tag": animal.get("animal_id", animal_id),
                "health_report_id": report_id,
                "reported_disease": top_condition,
                "disease": top_condition,
                "reporting_source": "FARMER_SELF_REPORT",
                "exact_latitude": loc_info["exact_latitude"],
                "exact_longitude": loc_info["exact_longitude"],
                "approximate_latitude": loc_info["approximate_latitude"],
                "approximate_longitude": loc_info["approximate_longitude"],
                "latitude": loc_info["exact_latitude"],
                "longitude": loc_info["exact_longitude"],
                "village": loc_info["village"],
                "taluka": loc_info["taluka"],
                "district": loc_info["district"],
                "status": "PENDING_REVIEW",
                "is_quarantine_required": True,
                "risk_score": final_risk_score,
                "risk_level": risk_level,
                "reported_at": now_iso,
                "created_at": now_iso,
                "updated_at": now_iso
            }
            db["disease_reports"].insert_one(case_doc)
            db["disease_cases"].insert_one(case_doc)
            
            # Update Animal Ground-Truth Health Status to SUSPECTED
            db["animals"].update_one(
                {"_id": animal["_id"]},
                {"$set": {"health_status": "SUSPECTED", "updated_at": now_iso}}
            )
            
            # 1. Standardized Early Warning Alert for Surveillance Triage
            alert_doc = {
                "_id": str(uuid.uuid4()),
                "id": str(uuid.uuid4()),
                "alert_type": "OUTBREAK_EARLY_WARNING",
                "severity": "CRITICAL" if risk_level == "Critical" else "MODERATE",
                "title": f"High Risk Alert: Suspected {top_condition} in {animal.get('animal_id', animal_id)}",
                "message": (
                    f"Multi-modal AI risk reached {final_risk_score}/100 ({risk_level}) for {animal.get('species', 'Cattle')} "
                    f"({animal.get('animal_id', animal_id)}) in {loc_info['village']}, {loc_info['taluka']}. "
                    f"Clinical review and quarantine triage required."
                ),
                "related_animal_id": animal["_id"],
                "related_case_id": surveillance_case_id,
                "related_report_id": report_id,
                "district": loc_info["district"],
                "is_read": False,
                "created_at": now_iso
            }
            db["alerts"].insert_one(alert_doc)

            # 2. Dispatch Role-Specific Alerts via AlertService
            try:
                from services.alert_service import get_alert_service
                alert_svc = get_alert_service()
                
                # Farmer Alert (High-risk animal assessment)
                farmer_owner = animal.get("owner_id") or username
                alert_svc.trigger_farmer_high_risk_alert(
                    farmer_username=farmer_owner,
                    animal=animal,
                    report={
                        "id": report_id,
                        "top_condition": top_condition,
                        "risk_level": risk_level,
                        "final_risk_score": final_risk_score,
                        "village": loc_info["village"],
                        "taluka": loc_info["taluka"],
                        "district": loc_info["district"]
                    }
                )
                
                # Veterinarian Alert (High-risk report requiring clinical review)
                alert_svc.trigger_vet_review_required_alert(
                    animal=animal,
                    report={
                        "id": report_id,
                        "surveillance_case_id": surveillance_case_id,
                        "top_condition": top_condition,
                        "risk_level": risk_level,
                        "final_risk_score": final_risk_score,
                        "village": loc_info["village"],
                        "taluka": loc_info["taluka"],
                        "district": loc_info["district"]
                    }
                )
            except Exception as e:
                print(f"[ALERTS] Failed to dispatch via AlertService: {e}")

        # 8. Save Health Report Document
        report_doc = {
            "_id": report_id,
            "id": report_id,
            "animal_id": animal["_id"],
            "animal_tag": animal.get("animal_id", animal_id),
            "species": animal.get("species", "Cattle"),
            "breed": animal.get("breed", "Unknown"),
            "owner_id": animal.get("owner_id", username),
            "owner_name": animal.get("owner_name", username),
            "recorded_by": username,
            "recorded_by_role": role,
            "symptoms": symptoms,
            "image_url": saved_image_url,
            "body_temperature_c": body_temperature_c,
            "appetite_score": appetite_score,
            "milk_yield_liters": milk_yield_liters,
            "activity_score": activity_score,
            "clinical_notes": clinical_notes,
            # Protected Location Fields
            "exact_latitude": loc_info["exact_latitude"],
            "exact_longitude": loc_info["exact_longitude"],
            "approximate_latitude": loc_info["approximate_latitude"],
            "approximate_longitude": loc_info["approximate_longitude"],
            "village": loc_info["village"],
            "taluka": loc_info["taluka"],
            "district": loc_info["district"],
            "share_location": loc_info["share_location"],
            # AI Model Outputs
            "ai_analyses": {
                "image": image_result,
                "symptoms": symptom_result,
                "environment": env_result
            },
            "multi_modal_risk": multi_modal_eval,
            "final_risk_score": final_risk_score,
            "risk_level": risk_level,
            "is_surveillance_triggered": is_high_risk,
            "surveillance_report_id": surveillance_case_id,
            "animal_health_status": "SUSPECTED" if is_high_risk else animal.get("health_status", "HEALTHY"),
            "recorded_at": now_iso,
            "created_at": now_iso,
            # Permanent Non-Diagnosis Marker
            "is_veterinary_diagnosis": False,
            "disclaimer": (
                "AI-assisted risk report only. Not a veterinary diagnosis. "
                "Confirmatory testing and prescription must be performed by a registered veterinarian."
            )
        }
        db["health_reports"].insert_one(report_doc)
        db["animal_health_records"].insert_one(report_doc)

        # 9. Format Response with Privacy Filtered Location
        safe_location = self.filter_location_for_user(report_doc, current_user)
        
        return {
            "report_id": report_id,
            "animal_id": animal["_id"],
            "animal_tag": animal.get("animal_id", animal_id),
            "species": animal.get("species", "Cattle"),
            "breed": animal.get("breed", "Unknown"),
            "owner_id": animal.get("owner_id", username),
            "owner_name": animal.get("owner_name", username),
            "recorded_by": username,
            "symptoms": symptoms,
            "image_url": saved_image_url,
            "location": safe_location,
            "location_access_level": safe_location["access_level"],
            "ai_analyses": {
                "image": image_result,
                "symptoms": symptom_result,
                "environment": env_result
            },
            "multi_modal_risk": multi_modal_eval,
            "final_risk_score": final_risk_score,
            "risk_score": final_risk_score,
            "risk_level": risk_level,
            "is_surveillance_triggered": is_high_risk,
            "surveillance_report_id": surveillance_case_id,
            "animal_health_status": report_doc["animal_health_status"],
            "recorded_at": now_iso,
            "is_veterinary_diagnosis": False,
            "disclaimer": report_doc["disclaimer"]
        }

def get_reporting_service() -> HealthReportingService:
    return HealthReportingService.get_instance()
