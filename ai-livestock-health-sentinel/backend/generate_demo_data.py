import os
import sys
from datetime import datetime, timedelta
from database import db
from auth import get_password_hash

def seed_demo_data():
    print("Seeding database with realistic demo data...")
    
    # 1. Clear existing collections to ensure fresh runs
    collections = ["users", "animals", "health_records", "predictions", "disease_cases", "vaccinations", "alerts", "outbreak_clusters", "audit_logs"]
    for c in collections:
        if hasattr(db[c], "db_path"):
            # Mock DB cleanup
            data = db[c]._load_data()
            data[c] = []
            db[c]._save_data(data)
        else:
            # Real MongoDB cleanup
            db[c].delete_many({})
            
    # 2. Add Users with hashed passwords (password = 'sih2026')
    hashed_pwd = get_password_hash("sih2026")
    users = [
        {
            "username": "farmer_a",
            "password": hashed_pwd,
            "fullname": "Ramesh Patil (Farm A)",
            "role": "FARMER",
            "phone": "+91 9822011223",
            "village": "Wadgaon",
            "taluka": "Haveli",
            "district": "Pune",
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "username": "farmer_b",
            "password": hashed_pwd,
            "fullname": "Sanjay Deshmukh (Farm B)",
            "role": "FARMER",
            "phone": "+91 9822099887",
            "village": "Wadgaon",
            "taluka": "Haveli",
            "district": "Pune",
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "username": "vet_officer",
            "password": hashed_pwd,
            "fullname": "Dr. Sunita Bhave (Vet Officer)",
            "role": "VETERINARIAN",
            "phone": "+91 9922001122",
            "village": "Haveli Center",
            "taluka": "Haveli",
            "district": "Pune",
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "username": "gov_officer",
            "password": hashed_pwd,
            "fullname": "Shri. R. K. Chavan (Husbandry Officer)",
            "role": "OFFICER",
            "phone": "+91 9422001144",
            "village": "Pune City",
            "taluka": "Pune",
            "district": "Pune",
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "username": "admin_user",
            "password": hashed_pwd,
            "fullname": "Sentinel Administrator",
            "role": "ADMIN",
            "phone": "+91 9000000000",
            "village": "Mumbai",
            "taluka": "Mumbai",
            "district": "Mumbai",
            "created_at": datetime.utcnow().isoformat()
        }
    ]
    for u in users:
        db["users"].insert_one(u)
    print("Users seeded (farmer_a, farmer_b, vet_officer, gov_officer, admin_user). Password is 'sih2026'")
    
    # 3. Seed Animals
    # Farm A coordinates: 18.5205, 73.8567
    # Farm B coordinates (nearby, ~1.2 km): 18.5285, 73.8612
    animals_data = [
        # Farm A
        {"_id": "ANM-001", "species": "Cattle", "breed": "Gir", "age": 4.5, "gender": "Female", "health_history": "None", "farm_id": "farmer_a", "latitude": 18.5205, "longitude": 73.8567, "village": "Wadgaon", "taluka": "Haveli", "district": "Pune"},
        {"_id": "ANM-002", "species": "Cattle", "breed": "Sahiwal", "age": 3.0, "gender": "Female", "health_history": "None", "farm_id": "farmer_a", "latitude": 18.5204, "longitude": 73.8568, "village": "Wadgaon", "taluka": "Haveli", "district": "Pune"},
        {"_id": "ANM-003", "species": "Cattle", "breed": "Gir", "age": 5.0, "gender": "Female", "health_history": "None", "farm_id": "farmer_a", "latitude": 18.5206, "longitude": 73.8566, "village": "Wadgaon", "taluka": "Haveli", "district": "Pune"},
        {"_id": "ANM-004", "species": "Cattle", "breed": "Jersey", "age": 2.5, "gender": "Female", "health_history": "None", "farm_id": "farmer_a", "latitude": 18.5205, "longitude": 73.8565, "village": "Wadgaon", "taluka": "Haveli", "district": "Pune"},
        {"_id": "ANM-005", "species": "Cattle", "breed": "Gir", "age": 6.0, "gender": "Female", "health_history": "Healthy", "farm_id": "farmer_a", "latitude": 18.5205, "longitude": 73.8567, "village": "Wadgaon", "taluka": "Haveli", "district": "Pune"},
        {"_id": "ANM-006", "species": "Cattle", "breed": "Sahiwal", "age": 4.0, "gender": "Female", "health_history": "None", "farm_id": "farmer_a", "latitude": 18.5205, "longitude": 73.8567, "village": "Wadgaon", "taluka": "Haveli", "district": "Pune"},
        # Farm B
        {"_id": "ANM-011", "species": "Cattle", "breed": "Holstein Friesian", "age": 3.5, "gender": "Female", "health_history": "None", "farm_id": "farmer_b", "latitude": 18.5285, "longitude": 73.8612, "village": "Wadgaon", "taluka": "Haveli", "district": "Pune"},
        {"_id": "ANM-012", "species": "Cattle", "breed": "Holstein Friesian", "age": 4.0, "gender": "Female", "health_history": "None", "farm_id": "farmer_b", "latitude": 18.5284, "longitude": 73.8613, "village": "Wadgaon", "taluka": "Haveli", "district": "Pune"},
        {"_id": "ANM-013", "species": "Cattle", "breed": "Jersey", "age": 5.5, "gender": "Female", "health_history": "None", "farm_id": "farmer_b", "latitude": 18.5286, "longitude": 73.8611, "village": "Wadgaon", "taluka": "Haveli", "district": "Pune"}
    ]
    for a in animals_data:
        db["animals"].insert_one(a)
    print("Animals seeded.")
    
    # 4. Seed Vaccinations
    vaccinations = [
        {"animal_id": "ANM-001", "vaccine_name": "FMD Vaccine", "date_administered": "2026-03-10", "next_due_date": "2026-09-10"},
        {"animal_id": "ANM-005", "vaccine_name": "Brucellosis Vaccine", "date_administered": "2026-01-15", "next_due_date": "2027-01-15"},
        {"animal_id": "ANM-013", "vaccine_name": "FMD Vaccine", "date_administered": "2026-02-20", "next_due_date": "2026-08-20"}
    ]
    for v in vaccinations:
        db["vaccinations"].insert_one(v)
        
    # 5. Outbreak Scenario: 4 animals in Farm A show symptoms, 2 in Farm B show symptoms
    outbreak_symptoms = ["fever", "skin_abnormalities", "loss_of_appetite", "reduced_milk_production", "reduced_activity"]
    now = datetime.utcnow()
    
    # Cases array to insert
    cases = [
        # Farm A Cases (3 days ago to today)
        {"animal_id": "ANM-001", "days_ago": 3, "temp": 40.5, "milk": 4.5, "disease": "Lumpy Skin Disease", "risk": "HIGH", "severity": "SEVERE"},
        {"animal_id": "ANM-002", "days_ago": 2, "temp": 39.9, "milk": 6.2, "disease": "Lumpy Skin Disease", "risk": "HIGH", "severity": "MODERATE"},
        {"animal_id": "ANM-003", "days_ago": 2, "temp": 40.1, "milk": 5.0, "disease": "Lumpy Skin Disease", "risk": "HIGH", "severity": "SEVERE"},
        {"animal_id": "ANM-004", "days_ago": 1, "temp": 39.8, "milk": 7.1, "disease": "Lumpy Skin Disease", "risk": "MODERATE", "severity": "MODERATE"},
        # Farm B Cases (1 day ago to today)
        {"animal_id": "ANM-011", "days_ago": 1, "temp": 40.3, "milk": 3.8, "disease": "Lumpy Skin Disease", "risk": "HIGH", "severity": "SEVERE"},
        {"animal_id": "ANM-012", "days_ago": 0, "temp": 39.7, "milk": 8.0, "disease": "Lumpy Skin Disease", "risk": "MODERATE", "severity": "MODERATE"}
    ]
    
    case_ids = []
    for c in cases:
        animal = next(a for a in animals_data if a["_id"] == c["animal_id"])
        record_date = (now - timedelta(days=c["days_ago"])).isoformat()
        
        # Health record
        hr_doc = {
            "animal_id": c["animal_id"],
            "symptoms": outbreak_symptoms,
            "temperature": c["temp"],
            "appetite": 0.0, # Loss of appetite
            "milk_production": c["milk"],
            "activity": 0.0, # Reduced activity
            "observations": "Circular lumps on skin, high fever.",
            "image_url": "/uploads/demo_lumpy.png", # demo reference
            "recorded_at": record_date
        }
        db["health_records"].insert_one(hr_doc)
        
        # Prediction record
        pred_doc = {
            "animal_id": c["animal_id"],
            "possible_disease": c["disease"],
            "risk_score": 82.0 if c["risk"] == "HIGH" else 58.0,
            "risk_level": c["risk"],
            "severity": c["severity"],
            "model_used": "Hybrid AI (GradientBoosting + OpenCV CV Scanner)",
            "explanation": "Key drivers: Skin Abnormalities (+35%), Fever (+24%), Reduced Milk Production (+12%)",
            "is_anomaly": True,
            "anomaly_score": 0.82,
            "image_findings": "Cutaneous nodules detected by OpenCV contours.",
            "created_at": record_date
        }
        db["predictions"].insert_one(pred_doc)
        
        # Case record
        case_doc = {
            "animal_id": c["animal_id"],
            "disease": c["disease"],
            "status": "SUSPECTED",
            "risk_level": c["risk"],
            "location": {
                "latitude": animal["latitude"],
                "longitude": animal["longitude"]
            },
            "village": animal["village"],
            "taluka": animal["taluka"],
            "district": animal["district"],
            "detected_at": record_date,
            "verified_by": None,
            "verification_date": None
        }
        res = db["disease_cases"].insert_one(case_doc)
        case_ids.append(res.inserted_id)
        
        # Vet Alert
        alert_doc = {
            "type": "VETERINARY_ALERT",
            "animal_id": c["animal_id"],
            "farm_id": animal["farm_id"],
            "disease": c["disease"],
            "risk_level": c["risk"],
            "village": animal["village"],
            "taluka": animal["taluka"],
            "message": f"Suspicious case of {c['disease']} in {animal['village']} ({c['risk']} RISK).",
            "status": "UNREAD",
            "created_at": record_date
        }
        db["alerts"].insert_one(alert_doc)
        
    print("Outbreak Scenario Health records, predictions and disease cases generated.")
    
    # 6. Add Outbreak Cluster
    # Calculate geographical center
    lats = [a["latitude"] for a in animals_data if a["_id"] in [c["animal_id"] for c in cases]]
    lngs = [a["longitude"] for a in animals_data if a["_id"] in [c["animal_id"] for c in cases]]
    center_lat = sum(lats) / len(lats)
    center_lng = sum(lngs) / len(lngs)
    
    cluster_doc = {
        "disease": "Lumpy Skin Disease",
        "cases_count": len(cases),
        "affected_cases": case_ids,
        "affected_farms": ["farmer_a", "farmer_b"],
        "center_location": {
            "latitude": center_lat,
            "longitude": center_lng
        },
        "radius": 1.25, # km
        "time_window": "14 days",
        "risk_level": "HIGH",
        "status": "POSSIBLE OUTBREAK / POTENTIAL DISEASE CLUSTER",
        "created_at": now.isoformat()
    }
    db["outbreak_clusters"].insert_one(cluster_doc)
    
    # Add Outbreak Alert
    outbreak_alert = {
        "type": "OUTBREAK_ALERT",
        "disease": "Lumpy Skin Disease",
        "risk_level": "HIGH",
        "village": "Wadgaon",
        "taluka": "Haveli",
        "message": f"POSSIBLE REGIONAL OUTBREAK CLUSTER: {len(cases)} suspected cases of Lumpy Skin Disease detected in Wadgaon within a 1.3km radius affecting 2 farms.",
        "status": "UNREAD",
        "created_at": now.isoformat()
    }
    db["alerts"].insert_one(outbreak_alert)
    print("Outbreak Cluster and alert generated.")
    
    # 7. Add Audit Log
    audit_doc = {
        "action": "SEED_DEMO_DATA",
        "user": "SYSTEM",
        "details": "Successfully seeded initial hackathon demonstration database.",
        "timestamp": datetime.utcnow().isoformat()
    }
    db["audit_logs"].insert_one(audit_doc)
    print("Audit logs seeded.")
    print("--- Database Seeding Complete ---")

if __name__ == "__main__":
    # If running directly, adjust PYTHONPATH to backend
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    seed_demo_data()
