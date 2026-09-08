from fastapi import APIRouter, Depends
from database import db
from auth import get_current_user
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

@router.get("/farmer")
def get_farmer_dashboard(current_user: dict = Depends(get_current_user)):
    username = current_user["username"]
    
    # Farmer specific items
    animals = db["animals"].find({"farm_id": username})
    animal_ids = [a["_id"] for a in animals]
    
    # Vitals, recent assessments
    recent_assessments = []
    if animal_ids:
        predictions = db["predictions"].find({"animal_id": {"$in": animal_ids}}).sort("created_at", -1).limit(5)
        for p in predictions:
            animal = next((a for a in animals if a["_id"] == p["animal_id"]), None)
            if animal:
                p["animal_details"] = f"{animal['breed']} ({animal['_id'][:6]})"
            recent_assessments.append(p)
            
    # Alerts/Notifications
    alerts = db["alerts"].find({"farm_id": username}).sort("created_at", -1).limit(10)
    
    # Upcoming vaccinations (due in next 30 days)
    upcoming_vaccinations = []
    if animal_ids:
        now_str = datetime.utcnow().isoformat()
        future_str = (datetime.utcnow() + timedelta(days=30)).isoformat()
        vaccs = db["vaccinations"].find({"animal_id": {"$in": animal_ids}})
        for v in vaccs:
            due = v.get("next_due_date", "")
            if now_str <= due <= future_str:
                animal = next((a for a in animals if a["_id"] == v["animal_id"]), None)
                v["animal_breed"] = animal["breed"] if animal else "Cattle"
                upcoming_vaccinations.append(v)
                
    return {
        "total_animals": len(animals),
        "recent_assessments": recent_assessments,
        "upcoming_vaccinations": upcoming_vaccinations,
        "alerts": alerts
    }

@router.get("/vet")
def get_vet_dashboard(current_user: dict = Depends(get_current_user)):
    # Cases pending verification
    pending_cases = db["disease_cases"].find({"status": "SUSPECTED"})
    for c in pending_cases:
        animal = db["animals"].find_one({"_id": c["animal_id"]})
        if animal:
            c["animal_details"] = f"{animal['breed']} ({animal['gender']}, {animal['age']} years)"
            
    # High risk active alerts
    high_risk_alerts = db["alerts"].find({"risk_level": "HIGH"}).sort("created_at", -1).limit(10)
    
    # Active clusters
    clusters = db["outbreak_clusters"].find()
    
    # General metrics
    total_suspected = db["disease_cases"].count_documents({"status": "SUSPECTED"})
    total_verified = db["disease_cases"].count_documents({"status": "VERIFIED"})
    
    return {
        "pending_cases": pending_cases,
        "high_risk_alerts": high_risk_alerts,
        "active_clusters_count": len(clusters),
        "suspected_count": total_suspected,
        "verified_count": total_verified
    }

@router.get("/officer")
def get_officer_dashboard():
    # Government surveillance metrics
    total_animals = db["animals"].count_documents()
    
    # Deduplicate farm ids to get total farms
    animals = db["animals"].find()
    farms = set([a["farm_id"] for a in animals if a.get("farm_id")])
    total_farms = len(farms)
    
    suspected_cases = db["disease_cases"].count_documents({"status": "SUSPECTED"})
    verified_cases = db["disease_cases"].count_documents({"status": "VERIFIED"})
    high_risk_cases = db["disease_cases"].count_documents({"risk_level": "HIGH", "status": "SUSPECTED"})
    clusters = db["outbreak_clusters"].find()
    
    # Village, Taluka, District distribution of cases
    cases = db["disease_cases"].find()
    district_dist = {}
    taluka_dist = {}
    village_dist = {}
    disease_dist = {}
    
    for c in cases:
        dis = c.get("disease", "Unknown")
        dist = c.get("district", "Unknown")
        tal = c.get("taluka", "Unknown")
        vil = c.get("village", "Unknown")
        
        disease_dist[dis] = disease_dist.get(dis, 0) + 1
        district_dist[dist] = district_dist.get(dist, 0) + 1
        taluka_dist[tal] = taluka_dist.get(tal, 0) + 1
        village_dist[vil] = village_dist.get(vil, 0) + 1
        
    # Disease trends over time (mocking past week trend lines based on cases dates)
    trends = []
    now = datetime.utcnow()
    for i in range(7):
        day = now - timedelta(days=i)
        day_str = day.strftime("%Y-%m-%d")
        
        # Count cases detected on that day
        day_cases = sum(1 for c in cases if c.get("detected_at", "").startswith(day_str))
        trends.append({"date": day_str, "cases": day_cases})
    trends.reverse()
    
    alerts = db["alerts"].find({"type": "OUTBREAK_ALERT"}).sort("created_at", -1).limit(5)
    
    return {
        "total_animals": total_animals,
        "total_farms": total_farms,
        "suspected_cases": suspected_cases,
        "verified_cases": verified_cases,
        "high_risk_cases": high_risk_cases,
        "active_clusters": len(clusters),
        "disease_distribution": disease_dist,
        "district_distribution": district_dist,
        "taluka_distribution": taluka_dist,
        "village_distribution": village_dist,
        "trends": trends,
        "recent_alerts": alerts
    }

@router.get("/admin")
def get_admin_dashboard():
    users = db["users"].find()
    role_dist = {}
    for u in users:
        role = u.get("role", "FARMER")
        role_dist[role] = role_dist.get(role, 0) + 1
        
    total_animals = db["animals"].count_documents()
    total_records = db["health_records"].count_documents()
    
    audit_logs = db["audit_logs"].find().sort("timestamp", -1).limit(10)
    
    # Mocking ML performance metrics
    ml_metrics = {
        "symptom_model": {
            "algorithm": "Gradient Boosting Classifier",
            "accuracy": 0.908,
            "precision": 0.920,
            "recall": 0.908,
            "f1_score": 0.906,
            "validation_samples": 240,
            "last_trained": "2026-08-22"
        },
        "anomaly_detector": {
            "algorithm": "Isolation Forest",
            "contamination_rate": 0.05,
            "status": "Operational"
        },
        "outbreak_clustering": {
            "algorithm": "DBSCAN",
            "eps_radius_km": 5.0,
            "min_samples": 3
        }
    }
    
    return {
        "users_count": len(users),
        "user_roles_distribution": role_dist,
        "total_animals": total_animals,
        "total_health_records": total_records,
        "ml_metrics": ml_metrics,
        "audit_logs": audit_logs
    }
