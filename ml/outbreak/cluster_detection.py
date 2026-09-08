import math
import uuid
import numpy as np
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
from sklearn.cluster import DBSCAN

EARTH_RADIUS_KM = 6371.0088

def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Computes great-circle distance between two points on Earth in kilometers.
    """
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return EARTH_RADIUS_KM * c

def normalize_disease_name(disease: Optional[str]) -> str:
    """
    Normalizes disease names for biological grouping.
    """
    if not disease:
        return "Unspecified Condition"
    d = disease.strip().lower()
    if "foot" in d or "fmd" in d:
        return "Foot-and-Mouth Disease (FMD)"
    if "lumpy" in d or "lsd" in d:
        return "Lumpy Skin Disease (LSD)"
    if "mastitis" in d:
        return "Bovine Mastitis"
    if "anthrax" in d:
        return "Anthrax"
    if "brucell" in d:
        return "Brucellosis"
    if "blackleg" in d:
        return "Blackleg (BQ)"
    if "respiratory" in d or "pneumonia" in d:
        return "Bovine Respiratory Disease (BRD)"
    # Return Title Cased clean string
    return disease.strip().title()

def parse_iso_datetime(dt_val: Any) -> datetime:
    """
    Helper to parse datetime or ISO strings safely into timezone-naive UTC datetime.
    """
    if isinstance(dt_val, datetime):
        return dt_val.replace(tzinfo=None) if dt_val.tzinfo else dt_val
    if isinstance(dt_val, str):
        try:
            cleaned = dt_val.replace("Z", "+00:00")
            parsed = datetime.fromisoformat(cleaned)
            return parsed.replace(tzinfo=None) if parsed.tzinfo else parsed
        except Exception:
            pass
    return datetime.now(timezone.utc).replace(tzinfo=None)

def is_high_risk_report(report: Dict[str, Any], min_risk_score: float = 60.0) -> bool:
    """
    Strict filter: Clusters are formed ONLY from relevant high-risk or critical reports.
    Excludes baseline healthy, mild, or low-risk events.
    """
    risk_level = str(report.get("risk_level", "")).upper()
    if risk_level in ["HIGH", "CRITICAL"]:
        return True
    
    score = report.get("risk_score") or report.get("final_risk_score")
    if score is not None:
        try:
            if float(score) >= min_risk_score:
                return True
        except (ValueError, TypeError):
            pass
            
    # Also check if quarantined or emergency surveillance case
    if report.get("is_quarantine_required", False):
        return True
        
    return False

def detect_potential_clusters(
    reports_list: List[Dict[str, Any]],
    eps_km: float = 5.0,
    min_reports: int = 3,
    time_window_days: int = 14,
    min_risk_score: float = 60.0,
    reference_time: Optional[datetime] = None
) -> List[Dict[str, Any]]:
    """
    Detects Potential Disease Clusters / Emerging Risk Patterns using Haversine DBSCAN.
    
    Features considered:
      - Spatial Coordinates: Latitude and Longitude (geodesic distance in kilometers)
      - Disease Similarity: High-risk reports grouped by normalized disease label
      - Risk Level: Strictly considers only relevant High & Critical risk reports
      - Timestamp: Filtered within sliding time window (time_window_days)

    Adheres strictly to epidemiological communication standards:
      - Never labeled as 'Confirmed Outbreak'.
      - Designated as 'Potential Disease Cluster' or 'Emerging Risk Pattern'.
      - Includes clear AI-assisted surveillance disclaimers.
    """
    now = reference_time.replace(tzinfo=None) if reference_time else datetime.now(timezone.utc).replace(tzinfo=None)
    cutoff_date = now - timedelta(days=time_window_days)
    
    # 1. Filter: Time window + High-Risk validation + Coordinate availability
    valid_candidates = []
    for r in reports_list:
        dt = parse_iso_datetime(r.get("reported_at") or r.get("created_at") or r.get("date"))
        if dt < cutoff_date:
            continue
            
        if not is_high_risk_report(r, min_risk_score=min_risk_score):
            continue
            
        # Support both flat and nested location structures
        lat = r.get("latitude")
        lng = r.get("longitude")
        if lat is None or lng is None:
            loc = r.get("location") or {}
            lat = loc.get("latitude")
            lng = loc.get("longitude")
            
        if lat is None or lng is None:
            continue
            
        try:
            lat_f = float(lat)
            lng_f = float(lng)
        except (ValueError, TypeError):
            continue
            
        disease_raw = (
            r.get("disease") or 
            r.get("reported_disease") or 
            r.get("top_condition") or 
            r.get("suspected_disease") or 
            "Unspecified Condition"
        )
        
        # Risk score extraction
        r_score = r.get("risk_score") or r.get("final_risk_score")
        try:
            r_score_f = float(r_score) if r_score is not None else 70.0
        except (ValueError, TypeError):
            r_score_f = 70.0
            
        valid_candidates.append({
            "id": str(r.get("id") or r.get("_id") or uuid.uuid4()),
            "report_id": str(r.get("health_report_id") or r.get("id") or r.get("_id")),
            "animal_id": str(r.get("animal_id", "")),
            "animal_tag": str(r.get("animal_tag") or r.get("animal_id", "Unknown")),
            "farm_id": str(r.get("farm_id") or r.get("owner_id") or "unspecified_farm"),
            "owner_name": r.get("owner_name") or r.get("owner_id") or "Farmer",
            "latitude": lat_f,
            "longitude": lng_f,
            "disease_raw": disease_raw,
            "disease_normalized": normalize_disease_name(disease_raw),
            "risk_score": r_score_f,
            "risk_level": str(r.get("risk_level", "High")).capitalize(),
            "village": r.get("village", "Unknown"),
            "taluka": r.get("taluka", "Unknown"),
            "district": r.get("district", "Unknown"),
            "reported_at": dt
        })
        
    if len(valid_candidates) < min_reports:
        return []
        
    # 2. Group candidates by Disease Similarity
    by_disease: Dict[str, List[Dict[str, Any]]] = {}
    for cand in valid_candidates:
        d_key = cand["disease_normalized"]
        if d_key not in by_disease:
            by_disease[d_key] = []
        by_disease[d_key].append(cand)
        
    detected_clusters: List[Dict[str, Any]] = []
    
    # Epsilon in radians for Haversine DBSCAN
    eps_rad = eps_km / EARTH_RADIUS_KM
    
    # 3. Execute Haversine DBSCAN per disease group
    for disease_name, group_reports in by_disease.items():
        if len(group_reports) < min_reports:
            continue
            
        # Convert lat/lng to radians [latitude_radians, longitude_radians]
        coords_deg = np.array([[r["latitude"], r["longitude"]] for r in group_reports])
        coords_rad = np.radians(coords_deg)
        
        db = DBSCAN(eps=eps_rad, min_samples=min_reports, metric='haversine')
        labels = db.fit_predict(coords_rad)
        
        unique_labels = set(labels)
        for label in unique_labels:
            if label == -1:
                # Noise / Outliers that do not satisfy density threshold
                continue
                
            cluster_indices = np.where(labels == label)[0]
            cluster_items = [group_reports[i] for i in cluster_indices]
            cluster_coords_deg = coords_deg[cluster_indices]
            
            # Centroid calculation (arithmetic mean of coordinates)
            centroid_lat = float(np.mean(cluster_coords_deg[:, 0]))
            centroid_lng = float(np.mean(cluster_coords_deg[:, 1]))
            
            # Compute actual maximum geodesic distance from centroid to boundary
            distances_from_center = [
                haversine_distance_km(centroid_lat, centroid_lng, pt[0], pt[1])
                for pt in cluster_coords_deg
            ]
            max_dist_km = max(distances_from_center) if distances_from_center else 0.5
            bounding_radius_km = round(max(0.5, float(max_dist_km)), 2)
            
            # Distinct entities
            affected_farms = sorted(list(set(c["farm_id"] for c in cluster_items if c["farm_id"] != "unspecified_farm")))
            affected_villages = sorted(list(set(c["village"] for c in cluster_items if c["village"] != "Unknown")))
            affected_talukas = sorted(list(set(c["taluka"] for c in cluster_items if c["taluka"] != "Unknown")))
            affected_districts = sorted(list(set(c["district"] for c in cluster_items if c["district"] != "Unknown")))
            
            # Temporal metrics
            report_dates = [c["reported_at"] for c in cluster_items]
            earliest_dt = min(report_dates)
            latest_dt = max(report_dates)
            temporal_span_days = max(1, (latest_dt - earliest_dt).days + 1)
            
            # Risk quantification
            risk_scores = [c["risk_score"] for c in cluster_items]
            avg_risk_score = round(float(np.mean(risk_scores)), 1)
            
            # If any report is Critical, escalate cluster classification
            any_critical = any(c["risk_level"] == "Critical" or c["risk_score"] >= 81.0 for c in cluster_items)
            primary_risk_level = "Critical" if any_critical else "High"
            
            cluster_id = f"cluster_{uuid.uuid4().hex[:12]}"
            
            cluster_record = {
                "id": cluster_id,
                "cluster_id": cluster_id,
                "cluster_label": "Potential Disease Cluster",
                "pattern_type": "Emerging Risk Pattern",
                "disease": disease_name,
                "disease_name": disease_name,
                "risk_level": primary_risk_level,
                "average_risk_score": avg_risk_score,
                "report_count": len(cluster_items),
                "cases_count": len(cluster_items),  # Legacy compatibility
                "unique_farms_count": len(affected_farms) if affected_farms else 1,
                "affected_farms": affected_farms,
                "affected_cases": [c["id"] for c in cluster_items],
                "affected_reports": [c["report_id"] for c in cluster_items],
                "affected_animal_ids": list(set(c["animal_id"] for c in cluster_items if c["animal_id"])),
                "center_location": {
                    "latitude": round(centroid_lat, 5),
                    "longitude": round(centroid_lng, 5)
                },
                "centroid": {
                    "latitude": round(centroid_lat, 5),
                    "longitude": round(centroid_lng, 5)
                },
                "radius_km": bounding_radius_km,
                "radius": bounding_radius_km,  # Legacy compatibility
                "eps_threshold_km": eps_km,
                "min_reports_threshold": min_reports,
                "time_window_days": time_window_days,
                "temporal_span_days": temporal_span_days,
                "earliest_report_at": earliest_dt.isoformat(),
                "latest_report_at": latest_dt.isoformat(),
                "villages": affected_villages,
                "talukas": affected_talukas,
                "districts": affected_districts,
                "status": "EMERGING_RISK_PATTERN",
                "is_confirmed_outbreak": False,
                "is_veterinary_diagnosis": False,
                "disclaimer": (
                    "This is an AI-assisted spatio-temporal cluster detection (Emerging Risk Pattern) "
                    "derived from density clustering of high-risk reports. It does NOT constitute a "
                    "confirmed epidemiological outbreak or official veterinary diagnosis. Field verification "
                    "by a certified veterinary authority is required."
                ),
                "detected_at": datetime.now(timezone.utc).isoformat(),
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            
            detected_clusters.append(cluster_record)
            
    # Sort clusters by priority: Critical first, then highest average risk score, then report count
    detected_clusters.sort(
        key=lambda c: (1 if c["risk_level"] == "Critical" else 0, c["average_risk_score"], c["report_count"]),
        reverse=True
    )
    
    return detected_clusters

def detect_outbreak_clusters(cases_list, eps_km=5.0, min_cases=3, time_window_days=14):
    """
    Backward-compatible adapter forwarding to detect_potential_clusters.
    Maintains support for existing callers while enforcing standardized non-confirmed naming.
    """
    return detect_potential_clusters(
        reports_list=cases_list,
        eps_km=eps_km,
        min_reports=min_cases,
        time_window_days=time_window_days
    )
