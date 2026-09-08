import os
import sys
import uuid
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional

from config import settings
from database import db

# Add ML directory to path for cluster_detection module
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ML_OUTBREAK_DIR = os.path.join(PROJECT_ROOT, "ml", "outbreak")
if ML_OUTBREAK_DIR not in sys.path:
    sys.path.insert(0, ML_OUTBREAK_DIR)

try:
    from cluster_detection import detect_potential_clusters, normalize_disease_name
except ImportError:
    # Local fallback import
    from ml.outbreak.cluster_detection import detect_potential_clusters, normalize_disease_name

class ClusterDetectionService:
    """
    Spatio-temporal livestock disease cluster surveillance service.
    
    Orchestrates:
      1. Aggregation of high-risk reports from health_reports and disease_reports.
      2. Geospatial Haversine DBSCAN clustering based on configurable radius, min reports, and time window.
      3. Persistence in db['disease_clusters'] and synchronized db['outbreak_clusters'].
      4. Early-warning alert generation using strict non-confirmed-outbreak terminology.
    """
    _instance: Optional["ClusterDetectionService"] = None

    def __init__(self):
        self.default_radius_km = settings.CLUSTER_GEO_RADIUS_KM
        self.default_min_reports = settings.CLUSTER_MIN_REPORTS
        self.default_time_window_days = settings.CLUSTER_TIME_WINDOW_DAYS
        self.min_risk_score = settings.CLUSTER_MIN_RISK_SCORE

    @classmethod
    def get_instance(cls) -> "ClusterDetectionService":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _collect_high_risk_candidates(self, time_window_days: int) -> List[Dict[str, Any]]:
        """
        Gathers and standardizes relevant high-risk reports within the specified time window.
        Avoids duplicates across health_reports, disease_reports, and disease_cases.
        """
        cutoff_dt = datetime.now(timezone.utc) - timedelta(days=time_window_days)
        cutoff_iso = cutoff_dt.isoformat()
        
        candidates: Dict[str, Dict[str, Any]] = {}
        
        # 1. Inspect disease_reports / disease_cases
        disease_reports = db["disease_reports"].find() or []
        for dr in disease_reports:
            r_id = str(dr.get("id") or dr.get("_id") or uuid.uuid4())
            dr_date = dr.get("reported_at") or dr.get("created_at") or ""
            
            # Extract coordinates
            lat = dr.get("exact_latitude") or dr.get("latitude")
            lng = dr.get("exact_longitude") or dr.get("longitude")
            if lat is None or lng is None:
                continue
                
            candidates[r_id] = {
                "id": r_id,
                "health_report_id": dr.get("health_report_id") or r_id,
                "animal_id": dr.get("animal_id"),
                "animal_tag": dr.get("animal_tag"),
                "farm_id": dr.get("owner_id") or dr.get("farm_id") or "unspecified_farm",
                "disease": dr.get("reported_disease") or dr.get("disease") or "Suspected Disease",
                "risk_score": dr.get("risk_score", 75.0),
                "risk_level": dr.get("risk_level", "High"),
                "latitude": float(lat),
                "longitude": float(lng),
                "village": dr.get("village", "Unknown"),
                "taluka": dr.get("taluka", "Unknown"),
                "district": dr.get("district", "Unknown"),
                "reported_at": dr_date or cutoff_iso,
                "is_quarantine_required": dr.get("is_quarantine_required", True)
            }

        # 2. Inspect health_reports for high-risk / critical entries
        health_reports = db["health_reports"].find() or []
        for hr in health_reports:
            r_id = str(hr.get("id") or hr.get("_id") or uuid.uuid4())
            
            # Check risk level
            r_level = str(hr.get("risk_level", "")).capitalize()
            r_score = hr.get("final_risk_score") or hr.get("risk_score") or 0.0
            
            if r_level not in ["High", "Critical"] and float(r_score) < self.min_risk_score:
                continue
                
            # If already added via disease_report matching, skip or enrich
            matching_key = None
            for k, val in candidates.items():
                if val.get("health_report_id") == r_id or k == r_id:
                    matching_key = k
                    break
            if matching_key:
                continue
                
            lat = hr.get("exact_latitude") or hr.get("latitude") or hr.get("approximate_latitude")
            lng = hr.get("exact_longitude") or hr.get("longitude") or hr.get("approximate_longitude")
            if lat is None or lng is None:
                continue
                
            hr_date = hr.get("reported_at") or hr.get("created_at") or ""
            
            # Find primary condition
            disease = (
                hr.get("suspected_disease") or 
                hr.get("top_condition") or 
                hr.get("disease") or 
                "Suspected Disease"
            )
            
            candidates[r_id] = {
                "id": r_id,
                "health_report_id": r_id,
                "animal_id": hr.get("animal_id"),
                "animal_tag": hr.get("animal_tag"),
                "farm_id": hr.get("owner_id") or "unspecified_farm",
                "disease": disease,
                "risk_score": float(r_score),
                "risk_level": r_level,
                "latitude": float(lat),
                "longitude": float(lng),
                "village": hr.get("village", "Unknown"),
                "taluka": hr.get("taluka", "Unknown"),
                "district": hr.get("district", "Unknown"),
                "reported_at": hr_date or cutoff_iso,
                "is_quarantine_required": False
            }
            
        return list(candidates.values())

    def run_detection(
        self,
        geo_radius_km: Optional[float] = None,
        min_reports: Optional[int] = None,
        time_window_days: Optional[int] = None,
        disease_filter: Optional[str] = None,
        persist: bool = True,
        emit_alerts: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Executes density clustering on eligible high-risk livestock records.
        """
        radius = float(geo_radius_km if geo_radius_km is not None else self.default_radius_km)
        min_reps = int(min_reports if min_reports is not None else self.default_min_reports)
        time_days = int(time_window_days if time_window_days is not None else self.default_time_window_days)
        
        candidates = self._collect_high_risk_candidates(time_days)
        
        if disease_filter:
            norm_filter = normalize_disease_name(disease_filter)
            candidates = [c for c in candidates if normalize_disease_name(c.get("disease")) == norm_filter]
            
        detected = detect_potential_clusters(
            reports_list=candidates,
            eps_km=radius,
            min_reports=min_reps,
            time_window_days=time_days,
            min_risk_score=self.min_risk_score
        )
        
        if persist:
            self._persist_clusters(detected, emit_alerts=emit_alerts)
            
        return detected

    def _persist_clusters(self, clusters: List[Dict[str, Any]], emit_alerts: bool = True) -> None:
        """
        Persists detected clusters into db['disease_clusters'] and db['outbreak_clusters'],
        and issues alerts without calling them confirmed outbreaks.
        """
        now_iso = datetime.now(timezone.utc).isoformat()
        
        # Clear legacy collections
        for col_name in ["disease_clusters", "outbreak_clusters"]:
            col = db[col_name]
            if hasattr(col, "db_path"):
                data = col._load_data()
                data[col_name] = []
                col._save_data(data)
            elif hasattr(col, "delete_many"):
                col.delete_many({})

        for cluster in clusters:
            # Clone and save into primary collection
            doc = cluster.copy()
            doc["updated_at"] = now_iso
            db["disease_clusters"].insert_one(doc)
            db["outbreak_clusters"].insert_one(doc)
            
            if emit_alerts:
                try:
                    from services.alert_service import get_alert_service
                    get_alert_service().trigger_cluster_surveillance_alerts(cluster)
                except Exception as e:
                    print(f"[ALERTS] Failed to dispatch cluster alerts via AlertService: {e}")
                    # Direct fallback
                    alert_id = str(uuid.uuid4())
                    alert_doc = {
                        "_id": alert_id,
                        "id": alert_id,
                        "alert_type": "EMERGING_RISK_PATTERN",
                        "type": "POTENTIAL_DISEASE_CLUSTER",
                        "severity": "CRITICAL" if cluster["risk_level"] == "Critical" else "MODERATE",
                        "title": f"Potential Disease Cluster: {cluster['disease']} ({cluster['report_count']} reports)",
                        "disease": cluster["disease"],
                        "risk_level": cluster["risk_level"],
                        "message": (
                            f"Emerging Risk Pattern detected: {cluster['report_count']} high-risk reports "
                            f"of {cluster['disease']} within a {cluster['radius_km']} km radius "
                            f"affecting {cluster['unique_farms_count']} farm(s) across "
                            f"{', '.join(cluster['villages']) or 'local area'}. "
                            f"AI-assisted risk cluster; field veterinary inspection recommended."
                        ),
                        "cluster_id": cluster["cluster_id"],
                        "is_confirmed_outbreak": False,
                        "is_veterinary_diagnosis": False,
                        "villages": cluster["villages"],
                        "talukas": cluster["talukas"],
                        "districts": cluster["districts"],
                        "is_read": False,
                        "created_at": now_iso
                    }
                    db["alerts"].insert_one(alert_doc)

    def list_clusters(
        self,
        disease: Optional[str] = None,
        risk_level: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Lists stored potential disease clusters with optional filters.
        """
        all_clusters = db["disease_clusters"].find() or db["outbreak_clusters"].find() or []
        filtered = []
        
        for c in all_clusters:
            if disease:
                if normalize_disease_name(c.get("disease")) != normalize_disease_name(disease):
                    continue
            if risk_level:
                if str(c.get("risk_level", "")).upper() != risk_level.upper():
                    continue
            filtered.append(c)
            
        # Limit results
        return filtered[:limit]

    def get_cluster(self, cluster_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a single cluster by ID.
        """
        cluster = db["disease_clusters"].find_one({"$or": [{"id": cluster_id}, {"cluster_id": cluster_id}, {"_id": cluster_id}]})
        if not cluster:
            cluster = db["outbreak_clusters"].find_one({"$or": [{"id": cluster_id}, {"cluster_id": cluster_id}, {"_id": cluster_id}]})
        return cluster

def get_cluster_service() -> ClusterDetectionService:
    """
    FastAPI dependency injection provider for ClusterDetectionService singleton.
    """
    return ClusterDetectionService.get_instance()
