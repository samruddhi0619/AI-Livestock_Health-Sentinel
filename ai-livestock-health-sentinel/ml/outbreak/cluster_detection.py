import numpy as np
from datetime import datetime, timedelta
from sklearn.cluster import DBSCAN

def detect_outbreak_clusters(cases_list, eps_km=5.0, min_cases=3, time_window_days=14):
    """
    Detects potential disease clusters using DBSCAN over spatial coordinates
    filtered by a time window (days) and grouped by disease category.
    
    cases_list structure: list of dicts, each with:
      - id: str/int
      - latitude: float
      - longitude: float
      - date: datetime object or ISO string
      - disease: str
      - farm_id: str
      - risk_level: str
    """
    now = datetime.utcnow()
    cutoff_date = now - timedelta(days=time_window_days)
    
    # 1. Filter and parse cases within the time window
    recent_cases = []
    for c in cases_list:
        c_date = c.get("date")
        if isinstance(c_date, str):
            try:
                # support ISO format
                c_date = datetime.fromisoformat(c_date.replace("Z", "+00:00"))
            except ValueError:
                c_date = datetime.utcnow() # fallback
                
        # Make naive for comparison
        c_date = c_date.replace(tzinfo=None) if c_date.tzinfo else c_date
        
        if c_date >= cutoff_date:
            recent_cases.append({
                "id": c.get("id") or c.get("_id"),
                "latitude": float(c.get("latitude")),
                "longitude": float(c.get("longitude")),
                "disease": c.get("disease"),
                "farm_id": c.get("farm_id"),
                "risk_level": c.get("risk_level", "MODERATE"),
                "date": c_date
            })
            
    if len(recent_cases) < min_cases:
        return [] # Insufficient cases to form any cluster
        
    # Group cases by disease
    by_disease = {}
    for c in recent_cases:
        dis = c["disease"]
        if dis not in by_disease:
            by_disease[dis] = []
        by_disease[dis].append(c)
        
    clusters_detected = []
    
    # 2. Apply DBSCAN for each disease group
    # 1 degree of latitude is ~111 km. 
    # For eps_km, eps_degrees = eps_km / 111.0
    eps_deg = eps_km / 111.0
    
    for disease, dis_cases in by_disease.items():
        if len(dis_cases) < min_cases:
            continue
            
        # Extract coordinates
        coords = np.array([[c["latitude"], c["longitude"]] for c in dis_cases])
        
        db = DBSCAN(eps=eps_deg, min_samples=min_cases, metric='euclidean')
        labels = db.fit_predict(coords)
        
        # Parse labels
        unique_labels = set(labels)
        for label in unique_labels:
            if label == -1:
                continue # Outliers / Noise
                
            # Get indices of cases in this cluster
            cluster_indices = np.where(labels == label)[0]
            cluster_cases = [dis_cases[i] for i in cluster_indices]
            
            # Calculate cluster metrics
            cluster_coords = coords[cluster_indices]
            center_lat = float(np.mean(cluster_coords[:, 0]))
            center_lng = float(np.mean(cluster_coords[:, 1]))
            
            # Calculate radius (max distance from center to any node in cluster)
            # 1 degree is ~111 km
            dists = np.sqrt(np.sum((cluster_coords - np.array([center_lat, center_lng]))**2, axis=1))
            radius_km = float(np.max(dists) * 111.0)
            
            affected_farms = list(set([c["farm_id"] for c in cluster_cases if c.get("farm_id")]))
            
            # Determine aggregate risk level
            risk_levels = [c["risk_level"] for c in cluster_cases]
            if "HIGH" in risk_levels:
                cluster_risk = "HIGH"
            elif "MODERATE" in risk_levels:
                cluster_risk = "MODERATE"
            else:
                cluster_risk = "LOW"
                
            clusters_detected.append({
                "disease": disease,
                "cases_count": len(cluster_cases),
                "affected_cases": [c["id"] for c in cluster_cases],
                "affected_farms": affected_farms,
                "center_location": {
                    "latitude": center_lat,
                    "longitude": center_lng
                },
                "radius": round(max(0.5, radius_km), 2),
                "time_window": f"{time_window_days} days",
                "risk_level": cluster_risk,
                "status": "POSSIBLE OUTBREAK / POTENTIAL DISEASE CLUSTER",
                "created_at": datetime.utcnow().isoformat()
            })
            
    return clusters_detected
