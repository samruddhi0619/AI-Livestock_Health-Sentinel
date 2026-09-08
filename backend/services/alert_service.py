import re
import uuid
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional

from database import db
from schemas import AlertSeverityEnum, AlertTypeEnum

# Standard statutory non-prescription safety disclaimer
SAFETY_DISCLAIMER_TEXT = (
    "Notice: Recommended actions provide biosecurity, physical isolation, and triage guidance only. "
    "They do NOT constitute veterinary medical prescriptions or therapeutic drug regimens. "
    "Never administer unverified pharmaceuticals without direct clinical examination and prescription by a licensed veterinarian."
)

# Regex pattern detecting unverified pharmaceutical / medication instructions
FORBIDDEN_MEDICATION_PATTERN = re.compile(
    r"\b(mg|ml|tablets|capsules|dosage|inject|injection|prescribe|administer\s+\d+|penicillin|"
    r"oxytetracycline|ivermectin|enrofloxacin|amoxicillin|paracetamol|dexamethasone|meloxicam|"
    r"sulphonamide|antibiotic|antipyretic|anti-inflammatory)\b",
    re.IGNORECASE
)

class AlertService:
    """
    Role-specific early-warning in-app alert service.
    
    Roles supported:
      - Farmer: High-risk animal assessments, herd vaccination due/overdue, regional disease risks.
      - Veterinarian: High-risk reports requiring clinical review, potential disease clusters.
      - Admin: Emerging clusters, critical risk patterns.
      
    Guarantees:
      - Strictly avoids unverified medication instructions.
      - Enforces structured alert metadata on every dispatch.
      - Provides role-tailored retrieval, unread tracking, and dismissal lifecycle.
    """
    _instance: Optional["AlertService"] = None

    @classmethod
    def get_instance(cls) -> "AlertService":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def sanitize_recommended_action(self, action_text: str, fallback_action: str) -> str:
        """
        Enforces medical safety guardrail: Strips out unauthorized drug dosages or medication
        instructions, replacing them with compliant biosecurity and veterinary consultation guidance.
        """
        if not action_text:
            return fallback_action
            
        if FORBIDDEN_MEDICATION_PATTERN.search(action_text):
            # Replace with safe triage instruction
            return (
                "Isolate the affected animal in a dry, well-ventilated stall. Provide clean water and maintain strict shed hygiene. "
                "Do NOT administer unverified medications or antibiotics without an authorized clinical prescription. "
                "Request immediate on-farm clinical inspection by a licensed veterinarian."
            )
        return action_text.strip()

    def create_alert(
        self,
        recipient_role: str,
        alert_type: str,
        severity: str,
        title: str,
        message: str,
        recommended_action: str,
        recipient_id: Optional[str] = None,
        related_entity: Optional[Dict[str, Any]] = None,
        fallback_action: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Validates, structures, and persists an in-app alert record.
        """
        now_utc = datetime.now(timezone.utc)
        now_iso = now_utc.isoformat()
        alert_id = str(uuid.uuid4())
        
        # Safe recommended action check
        safe_action = self.sanitize_recommended_action(
            recommended_action,
            fallback_action or "Observe biosecurity protocols and consult your local veterinary officer."
        )
        
        related = related_entity or {}
        alert_doc = {
            "_id": alert_id,
            "id": alert_id,
            "recipient_role": recipient_role.upper(),
            "recipient_id": recipient_id,
            "alert_type": alert_type,
            "severity": severity.upper(),
            "title": title.strip(),
            "message": message.strip(),
            "timestamp": now_iso,
            "created_at": now_iso,
            "related_entity": {
                "animal_id": str(related.get("animal_id") or "") or None,
                "animal_tag": str(related.get("animal_tag") or "") or None,
                "health_report_id": str(related.get("health_report_id") or "") or None,
                "disease_report_id": str(related.get("disease_report_id") or "") or None,
                "cluster_id": str(related.get("cluster_id") or "") or None,
                "disease": str(related.get("disease") or "") or None,
                "vaccination_id": str(related.get("vaccination_id") or "") or None,
                "village": str(related.get("village") or "") or None,
                "taluka": str(related.get("taluka") or "") or None,
                "district": str(related.get("district") or "") or None,
            },
            # Top-level backward compatibility references
            "related_animal_id": str(related.get("animal_id") or "") or None,
            "related_report_id": str(related.get("health_report_id") or "") or None,
            "related_case_id": str(related.get("disease_report_id") or "") or None,
            "district": str(related.get("district") or "") or None,
            "recommended_action": safe_action,
            "is_read": False,
            "is_dismissed": False,
            "is_veterinary_prescription": False,
            "safety_disclaimer": SAFETY_DISCLAIMER_TEXT
        }
        
        db["alerts"].insert_one(alert_doc)
        return alert_doc

    # -----------------------------------------------------------------------
    # Trigger Helpers: Farmer Specific Alerts
    # -----------------------------------------------------------------------
    def trigger_farmer_high_risk_alert(
        self,
        farmer_username: str,
        animal: Dict[str, Any],
        report: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Farmer Alert: High-risk animal assessment detected.
        """
        animal_tag = animal.get("animal_id") or animal.get("animal_tag") or "Livestock"
        disease = report.get("top_condition") or report.get("disease") or "Suspected Disease"
        risk_level = report.get("risk_level", "High")
        score = report.get("final_risk_score") or report.get("risk_score") or 70.0
        
        severity = AlertSeverityEnum.CRITICAL.value if str(risk_level).upper() == "CRITICAL" or float(score) >= 81.0 else AlertSeverityEnum.HIGH.value
        
        title = f"Urgent: High-Risk Health Assessment for {animal_tag}"
        message = (
            f"Multi-modal assessment for {animal.get('species', 'Animal')} ({animal_tag}) "
            f"computed a risk score of {score}/100 ({risk_level}) for suspected {disease}. "
            f"Immediate physical isolation required to safeguard the herd."
        )
        action = (
            f"1. Isolate {animal_tag} immediately in a shaded, well-ventilated isolation stall away from other animals. "
            f"2. Provide a dedicated clean water bucket and feed bin (do not share with healthy livestock). "
            f"3. Disinfect boots and wash hands before and after tending to the animal. "
            f"4. Do NOT administer unverified medications or anti-inflammatory drugs without prescription. "
            f"5. Request urgent veterinary clinical examination via the Sentinel portal."
        )
        
        return self.create_alert(
            recipient_role="FARMER",
            recipient_id=farmer_username,
            alert_type=AlertTypeEnum.HIGH_RISK_ASSESSMENT.value,
            severity=severity,
            title=title,
            message=message,
            recommended_action=action,
            related_entity={
                "animal_id": animal.get("_id") or animal.get("id"),
                "animal_tag": animal_tag,
                "health_report_id": report.get("id") or report.get("_id"),
                "disease": disease,
                "village": report.get("village"),
                "taluka": report.get("taluka"),
                "district": report.get("district")
            }
        )

    def trigger_vaccination_due_alert(
        self,
        farmer_username: str,
        animal: Dict[str, Any],
        vaccine_name: str,
        due_date_str: str,
        is_overdue: bool = False,
        vaccination_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Farmer Alert: Herd vaccination due or overdue.
        """
        animal_tag = animal.get("animal_id") or animal.get("animal_tag") or "Animal"
        severity = AlertSeverityEnum.HIGH.value if is_overdue else AlertSeverityEnum.MODERATE.value
        status_text = "OVERDUE" if is_overdue else "Due Soon"
        
        title = f"Vaccination {status_text}: {vaccine_name} for {animal_tag}"
        message = (
            f"{vaccine_name} vaccination for {animal.get('species', 'Cattle')} ({animal_tag}) "
            f"is {status_text.lower()} (Scheduled date: {due_date_str}). "
            f"Maintaining up-to-date immunizations protects herd immunity against epizootic outbreaks."
        )
        action = (
            f"1. Contact your assigned paravet or local government veterinary dispensary to schedule vaccination. "
            f"2. Ensure {animal_tag} is healthy, well-fed, and hydrated prior to the injection. "
            f"3. Update the Digital Animal Health Passport immediately after the booster is administered."
        )
        
        return self.create_alert(
            recipient_role="FARMER",
            recipient_id=farmer_username,
            alert_type=AlertTypeEnum.VACCINATION_DUE.value,
            severity=severity,
            title=title,
            message=message,
            recommended_action=action,
            related_entity={
                "animal_id": animal.get("_id") or animal.get("id"),
                "animal_tag": animal_tag,
                "vaccination_id": vaccination_id,
                "disease": vaccine_name
            }
        )

    def trigger_regional_disease_risk_alert(
        self,
        disease: str,
        taluka: str,
        district: str,
        cluster_id: Optional[str] = None,
        severity: str = "HIGH"
    ) -> Dict[str, Any]:
        """
        Farmer Alert: Regional disease risk / emerging pattern notification for local livestock owners.
        """
        title = f"Biosecurity Alert: Elevated {disease} Risk in {taluka}, {district}"
        message = (
            f"Epidemiological surveillance has identified elevated {disease} activity in the {taluka} sub-district. "
            f"Local livestock keepers are advised to enforce preventative farm biosecurity protocols."
        )
        action = (
            f"1. Inspect all livestock twice daily for skin nodules, oral/foot blisters, fever, or sudden milk drops. "
            f"2. Install fine insect mesh and apply approved botanical fly/tick repellents around animal shelters. "
            f"3. Disinfect animal sheds, stalls, and watering troughs with lime powder or approved farm virucides. "
            f"4. Restrict herd mixing at public grazing lands or livestock markets until regional transmission subsides. "
            f"5. Report any suspicious symptoms immediately through the Sentinel health reporting tool."
        )
        
        return self.create_alert(
            recipient_role="FARMER",
            recipient_id=None,  # Broadcast to farmers in the jurisdiction
            alert_type=AlertTypeEnum.REGIONAL_DISEASE_RISK.value,
            severity=severity,
            title=title,
            message=message,
            recommended_action=action,
            related_entity={
                "cluster_id": cluster_id,
                "disease": disease,
                "taluka": taluka,
                "district": district
            }
        )

    # -----------------------------------------------------------------------
    # Trigger Helpers: Veterinarian Specific Alerts
    # -----------------------------------------------------------------------
    def trigger_vet_review_required_alert(
        self,
        animal: Dict[str, Any],
        report: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Veterinarian Alert: High-risk report requiring clinical review.
        """
        animal_tag = animal.get("animal_id") or animal.get("animal_tag") or "Livestock"
        disease = report.get("top_condition") or report.get("disease") or "Suspected Condition"
        risk_level = report.get("risk_level", "High")
        score = report.get("final_risk_score") or report.get("risk_score") or 75.0
        village = report.get("village", "Unknown")
        taluka = report.get("taluka", "Unknown")
        
        severity = AlertSeverityEnum.CRITICAL.value if str(risk_level).upper() == "CRITICAL" else AlertSeverityEnum.HIGH.value
        
        title = f"Clinical Triage Required: Suspected {disease} in {village}, {taluka}"
        message = (
            f"Autonomous AI surveillance escalated an urgent case: Animal {animal_tag} "
            f"evaluated at risk score {score}/100 ({risk_level}) for suspected {disease}. "
            f"Clinical adjudication and quarantine verification required."
        )
        action = (
            f"1. Review uploaded photographic lesions and symptom severity in the Sentinel triage console. "
            f"2. Contact the herd keeper to confirm physical isolation status. "
            f"3. Schedule an on-site clinical visit to perform physical examination and collect confirmatory lab samples (PCR/ELISA). "
            f"4. Submit independent veterinary clinical adjudication and formalize statutory movement restrictions if necessary."
        )
        
        return self.create_alert(
            recipient_role="VETERINARIAN",
            recipient_id=None,
            alert_type=AlertTypeEnum.HIGH_RISK_REPORT_REVIEW.value,
            severity=severity,
            title=title,
            message=message,
            recommended_action=action,
            related_entity={
                "animal_id": animal.get("_id") or animal.get("id"),
                "animal_tag": animal_tag,
                "health_report_id": report.get("id") or report.get("_id"),
                "disease_report_id": report.get("surveillance_case_id") or report.get("surveillance_report_id"),
                "disease": disease,
                "village": village,
                "taluka": taluka,
                "district": report.get("district")
            }
        )

    def trigger_vet_cluster_alert(
        self,
        cluster: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Veterinarian Alert: Potential disease cluster detected via Haversine DBSCAN.
        """
        disease = cluster.get("disease") or cluster.get("disease_name") or "Suspected Disease"
        report_count = cluster.get("report_count") or cluster.get("cases_count") or 3
        farms_count = cluster.get("unique_farms_count") or len(cluster.get("affected_farms", [])) or 1
        radius_km = cluster.get("radius_km") or cluster.get("radius") or 5.0
        talukas = ", ".join(cluster.get("talukas", [])) or "Local Jurisdiction"
        risk_level = cluster.get("risk_level", "High")
        
        severity = AlertSeverityEnum.CRITICAL.value if str(risk_level).upper() == "CRITICAL" else AlertSeverityEnum.HIGH.value
        
        title = f"Surveillance Alert: Potential {disease} Cluster ({report_count} Reports)"
        message = (
            f"Density surveillance detected an Emerging Risk Pattern: {report_count} high-risk reports "
            f"of {disease} across {farms_count} farm(s) within a {radius_km} km radius in {talukas}. "
            f"Not a confirmed outbreak; field verification required."
        )
        action = (
            f"1. Inspect cluster centroid coordinates and spatial perimeter in the Disease Surveillance Map. "
            f"2. Coordinate with mobile veterinary units to establish an active 5km ring surveillance buffer. "
            f"3. Prioritize diagnostic specimen collection from symptomatic animals across the affected holdings. "
            f"4. Advise village panchayat and paravets regarding vector management and early case reporting."
        )
        
        return self.create_alert(
            recipient_role="VETERINARIAN",
            recipient_id=None,
            alert_type=AlertTypeEnum.POTENTIAL_DISEASE_CLUSTER.value,
            severity=severity,
            title=title,
            message=message,
            recommended_action=action,
            related_entity={
                "cluster_id": cluster.get("cluster_id") or cluster.get("id"),
                "disease": disease,
                "taluka": talukas,
                "district": ", ".join(cluster.get("districts", [])) or "Pune"
            }
        )

    # -----------------------------------------------------------------------
    # Trigger Helpers: Admin Specific Alerts
    # -----------------------------------------------------------------------
    def trigger_admin_emerging_cluster_alert(
        self,
        cluster: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Admin Alert: Emerging disease cluster requiring administrative awareness.
        """
        disease = cluster.get("disease") or cluster.get("disease_name") or "Suspected Disease"
        report_count = cluster.get("report_count") or cluster.get("cases_count") or 3
        farms_count = cluster.get("unique_farms_count") or len(cluster.get("affected_farms", [])) or 1
        districts = ", ".join(cluster.get("districts", [])) or "District"
        talukas = ", ".join(cluster.get("talukas", [])) or "Sub-District"
        
        title = f"Emerging Cluster: {disease} Detected in {talukas}, {districts}"
        message = (
            f"Spatio-temporal intelligence indicates an Emerging Risk Pattern with {report_count} "
            f"high-risk cases across {farms_count} farm(s) in {talukas}. Preliminary surveillance signal."
        )
        action = (
            f"1. Review district-wide veterinary staff coverage and mobile dispensary deployment schedules. "
            f"2. Verify sufficient regional buffer inventory for ring vaccination and personal protective kits. "
            f"3. Coordinate with district animal husbandry officers for inter-taluka livestock movement advisories."
        )
        
        return self.create_alert(
            recipient_role="ADMIN",
            recipient_id=None,
            alert_type=AlertTypeEnum.EMERGING_CLUSTERS.value,
            severity=AlertSeverityEnum.HIGH.value,
            title=title,
            message=message,
            recommended_action=action,
            related_entity={
                "cluster_id": cluster.get("cluster_id") or cluster.get("id"),
                "disease": disease,
                "taluka": talukas,
                "district": districts
            }
        )

    def trigger_admin_critical_risk_pattern_alert(
        self,
        cluster: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Admin Alert: Critical risk pattern requiring high-level emergency intervention.
        """
        disease = cluster.get("disease") or cluster.get("disease_name") or "Severe Disease"
        report_count = cluster.get("report_count") or cluster.get("cases_count") or 5
        avg_score = cluster.get("average_risk_score", 85.0)
        districts = ", ".join(cluster.get("districts", [])) or "Jurisdiction"
        
        title = f"Critical Risk Pattern: Severe {disease} Pattern in {districts}"
        message = (
            f"CRITICAL RISK PATTERN: Cluster severity has escalated to Critical tier (Mean Score: {avg_score}/100, "
            f"{report_count} clustered high-risk cases). Urgent multi-departmental containment response needed."
        )
        action = (
            f"1. Convene the District Livestock Disease Emergency Oversight Committee. "
            f"2. Authorize rapid deployment of state epidemiological investigation teams and emergency diagnostics. "
            f"3. Establish regional quarantine coordination and enforce sanitization barriers around livestock transit points. "
            f"4. Release official public health and farmer awareness bulletins through certified agricultural channels."
        )
        
        return self.create_alert(
            recipient_role="ADMIN",
            recipient_id=None,
            alert_type=AlertTypeEnum.CRITICAL_RISK_PATTERNS.value,
            severity=AlertSeverityEnum.CRITICAL.value,
            title=title,
            message=message,
            recommended_action=action,
            related_entity={
                "cluster_id": cluster.get("cluster_id") or cluster.get("id"),
                "disease": disease,
                "district": districts
            }
        )

    # -----------------------------------------------------------------------
    # Multi-Trigger Integrations
    # -----------------------------------------------------------------------
    def trigger_cluster_surveillance_alerts(self, cluster: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Dispatches all role-appropriate alerts when a cluster is detected:
          1. Veterinarian: Potential Disease Cluster Alert.
          2. Admin: Emerging Cluster Alert (and Critical Risk Pattern if Critical).
          3. Farmer: Regional Disease Risk Broadcast.
        """
        dispatched = []
        # 1. Vet alert
        vet_alert = self.trigger_vet_cluster_alert(cluster)
        dispatched.append(vet_alert)
        
        # 2. Admin alert
        admin_alert = self.trigger_admin_emerging_cluster_alert(cluster)
        dispatched.append(admin_alert)
        
        # If Critical risk, also trigger Admin Critical Pattern Alert
        is_critical = cluster.get("risk_level") == "Critical" or float(cluster.get("average_risk_score", 0)) >= 81.0
        if is_critical:
            crit_alert = self.trigger_admin_critical_risk_pattern_alert(cluster)
            dispatched.append(crit_alert)
            
        # 3. Farmer regional alert
        talukas = cluster.get("talukas", [])
        primary_taluka = talukas[0] if talukas else "Local Sub-District"
        districts = cluster.get("districts", [])
        primary_district = districts[0] if districts else "District"
        disease = cluster.get("disease") or "Suspected Disease"
        
        farmer_alert = self.trigger_regional_disease_risk_alert(
            disease=disease,
            taluka=primary_taluka,
            district=primary_district,
            cluster_id=cluster.get("cluster_id") or cluster.get("id"),
            severity="CRITICAL" if is_critical else "HIGH"
        )
        dispatched.append(farmer_alert)
        
        return dispatched

    def generate_vaccination_due_alerts(self, days_ahead: int = 14) -> List[Dict[str, Any]]:
        """
        Scans db["vaccinations"] and issues due/overdue alerts for upcoming or lapsed boosters.
        """
        now = datetime.now(timezone.utc)
        future = now + timedelta(days=days_ahead)
        now_iso = now.date().isoformat()
        future_iso = future.date().isoformat()
        
        vaccinations = db["vaccinations"].find() or []
        created_alerts = []
        
        for v in vaccinations:
            due_date_str = str(v.get("next_due_date") or v.get("due_date") or "")
            if not due_date_str:
                continue
                
            is_due_soon = now_iso <= due_date_str <= future_iso
            is_overdue = due_date_str < now_iso and v.get("status") != "COMPLETED"
            
            if is_due_soon or is_overdue:
                animal_id = v.get("animal_id")
                animal = db["animals"].find_one({"$or": [{"_id": animal_id}, {"animal_id": animal_id}]}) or {}
                farmer_id = animal.get("owner_id") or animal.get("farm_id")
                if not farmer_id:
                    continue
                    
                vaccine_name = v.get("vaccine_name") or v.get("disease") or "Livestock Booster"
                alert = self.trigger_vaccination_due_alert(
                    farmer_username=farmer_id,
                    animal=animal,
                    vaccine_name=vaccine_name,
                    due_date_str=due_date_str,
                    is_overdue=is_overdue,
                    vaccination_id=str(v.get("_id") or v.get("id"))
                )
                created_alerts.append(alert)
                
        return created_alerts

    # -----------------------------------------------------------------------
    # Querying & Lifecycle
    # -----------------------------------------------------------------------
    def get_alerts_for_user(
        self,
        current_user: Dict[str, Any],
        unread_only: bool = False,
        severity: Optional[str] = None,
        alert_type: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Retrieves strictly scoped, role-tailored alerts for the requesting user.
        """
        role = str(current_user.get("role", "FARMER")).upper()
        username = current_user.get("username", "")
        user_id = str(current_user.get("_id", current_user.get("id", "")))
        user_taluka = current_user.get("taluka", "")
        user_district = current_user.get("district", "")
        
        all_alerts = db["alerts"].find() or []
        user_alerts = []
        
        for a in all_alerts:
            if a.get("is_dismissed", False):
                continue
                
            recip_role = str(a.get("recipient_role", "")).upper()
            recip_id = a.get("recipient_id")
            
            # Role Scoping
            if role == "FARMER":
                # Farmer sees:
                # 1. Direct alerts addressed to their username or user_id
                # 2. Broadcast alerts addressed to FARMER role (e.g. regional alerts for their area or general broadcast)
                is_direct = recip_id in [username, user_id]
                is_broadcast = (recip_role in ["FARMER", "ALL"]) and (recip_id is None)
                if not (is_direct or is_broadcast):
                    continue
            elif role == "VETERINARIAN":
                # Veterinarian sees alerts intended for VETERINARIAN or ALL
                if recip_role not in ["VETERINARIAN", "ALL"]:
                    continue
            elif role in ["ADMIN", "OFFICER"]:
                # Admin sees alerts intended for ADMIN, OFFICER, or ALL
                if recip_role not in ["ADMIN", "OFFICER", "ALL"]:
                    continue
            else:
                continue
                
            # Filter unread
            if unread_only and a.get("is_read", False):
                continue
                
            # Filter severity
            if severity and str(a.get("severity", "")).upper() != severity.upper():
                continue
                
            # Normalize legacy alert record fields
            normalized_alert = a.copy()
            if "timestamp" not in normalized_alert:
                normalized_alert["timestamp"] = normalized_alert.get("created_at") or datetime.now(timezone.utc).isoformat()
            if "related_entity" not in normalized_alert or not isinstance(normalized_alert["related_entity"], dict):
                normalized_alert["related_entity"] = {
                    "animal_id": normalized_alert.get("related_animal_id"),
                    "health_report_id": normalized_alert.get("related_report_id"),
                    "disease_report_id": normalized_alert.get("related_case_id"),
                    "cluster_id": normalized_alert.get("cluster_id"),
                    "disease": normalized_alert.get("disease"),
                    "district": normalized_alert.get("district")
                }
            if "recommended_action" not in normalized_alert or not normalized_alert["recommended_action"]:
                normalized_alert["recommended_action"] = (
                    "Observe biosecurity protocols, isolate symptomatic animals, and request certified veterinary consultation."
                )
            if "safety_disclaimer" not in normalized_alert:
                normalized_alert["safety_disclaimer"] = SAFETY_DISCLAIMER_TEXT
            if "is_veterinary_prescription" not in normalized_alert:
                normalized_alert["is_veterinary_prescription"] = False

            user_alerts.append(normalized_alert)
            
        # Sort newest first
        user_alerts.sort(key=lambda x: x.get("timestamp", x.get("created_at", "")), reverse=True)
        return user_alerts[:limit]

    def get_unread_counts(self, current_user: Dict[str, Any]) -> Dict[str, int]:
        """
        Calculates unread counts grouped by severity for badges and notifications.
        """
        alerts = self.get_alerts_for_user(current_user, unread_only=True, limit=500)
        
        critical_count = sum(1 for a in alerts if str(a.get("severity")).upper() == "CRITICAL")
        high_count = sum(1 for a in alerts if str(a.get("severity")).upper() == "HIGH")
        mod_count = sum(1 for a in alerts if str(a.get("severity")).upper() == "MODERATE")
        info_count = sum(1 for a in alerts if str(a.get("severity")).upper() == "INFO")
        
        return {
            "total_unread": len(alerts),
            "critical_unread": critical_count,
            "high_unread": high_count,
            "moderate_unread": mod_count,
            "info_unread": info_count
        }

    def mark_as_read(self, alert_id: str, current_user: Dict[str, Any]) -> bool:
        """
        Marks an individual alert as read.
        """
        return db["alerts"].update_one(
            {"$or": [{"_id": alert_id}, {"id": alert_id}]},
            {"$set": {"is_read": True}}
        )

    def mark_all_as_read(self, current_user: Dict[str, Any]) -> int:
        """
        Marks all active unread alerts for the current user as read.
        """
        alerts = self.get_alerts_for_user(current_user, unread_only=True, limit=500)
        count = 0
        for a in alerts:
            aid = a.get("id") or a.get("_id")
            db["alerts"].update_one(
                {"$or": [{"_id": aid}, {"id": aid}]},
                {"$set": {"is_read": True}}
            )
            count += 1
        return count

    def dismiss_alert(self, alert_id: str, current_user: Dict[str, Any]) -> bool:
        """
        Soft-dismisses an alert from view.
        """
        return db["alerts"].update_one(
            {"$or": [{"_id": alert_id}, {"id": alert_id}]},
            {"$set": {"is_dismissed": True, "is_read": True}}
        )

def get_alert_service() -> AlertService:
    """
    FastAPI dependency injection provider for AlertService singleton.
    """
    return AlertService.get_instance()
