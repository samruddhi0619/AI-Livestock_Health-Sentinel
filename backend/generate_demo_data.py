import os
import sys
import uuid
from datetime import datetime, timedelta, timezone
from database import db
from auth import get_password_hash
from utils.passport_generator import generate_qr_code_assets
from services.cluster_service import ClusterDetectionService

# Standard internal tracking metadata for controlled SIH prototype data
DEMO_LABELS = {
    "is_simulated_demo": True,
    "is_prototype_demo": True,
    "data_provenance": "Simulated Prototype SIH Dataset",
    "dataset_label": "SIMULATED_DEMO_SIH_2026",
    "ml_training_eligible": False,  # Strict isolation: Do NOT mix with actual ML training datasets!
    "disclaimer": "Simulated prototype data for SIH demonstration only. Not for ML model training or official veterinary reporting."
}

def seed_demo_data():
    print("==========================================================================")
    print("  SEEDING CONTROLLED SIH DEMONSTRATION DATASET")
    print("  All records tagged with is_simulated_demo=True & ml_training_eligible=False")
    print("==========================================================================")
    
    # 1. Clear existing collections to ensure a clean, deterministic demonstration environment
    collections = [
        "users", "animals", "health_records", "health_reports", "ai_predictions",
        "disease_cases", "disease_reports", "vaccinations", "alerts",
        "disease_clusters", "outbreak_clusters", "veterinarian_reviews", "audit_logs"
    ]
    for c in collections:
        if hasattr(db[c], "db_path"):
            data = db[c]._load_data()
            data[c] = []
            db[c]._save_data(data)
            
    # 2. Seed Role-Based Users with hashed passwords (password = 'sih2026')
    hashed_pwd = get_password_hash("sih2026")
    now_dt = datetime.now(timezone.utc)
    now_str = now_dt.isoformat()
    
    users = [
        {
            "_id": "usr_farmer_ramesh",
            "username": "farmer_ramesh",
            "password": hashed_pwd,
            "fullname": "Ramesh Patil",
            "role": "FARMER",
            "phone": "+91 9822011223",
            "village": "Wagholi",
            "taluka": "Haveli",
            "district": "Pune",
            "is_active": True,
            "created_at": now_str,
            **DEMO_LABELS
        },
        {
            "_id": "usr_farmer_suresh",
            "username": "farmer_suresh",
            "password": hashed_pwd,
            "fullname": "Suresh Deshmukh",
            "role": "FARMER",
            "phone": "+91 9822099887",
            "village": "Wagholi",
            "taluka": "Haveli",
            "district": "Pune",
            "is_active": True,
            "created_at": now_str,
            **DEMO_LABELS
        },
        {
            "_id": "usr_farmer_ganesh",
            "username": "farmer_ganesh",
            "password": hashed_pwd,
            "fullname": "Ganesh Shinde",
            "role": "FARMER",
            "phone": "+91 9822077665",
            "village": "Bakori",
            "taluka": "Haveli",
            "district": "Pune",
            "is_active": True,
            "created_at": now_str,
            **DEMO_LABELS
        },
        {
            "_id": "usr_dr_anita",
            "username": "dr_anita",
            "password": hashed_pwd,
            "fullname": "Dr. Anita Kulkarni (B.V.Sc & A.H.)",
            "role": "VETERINARIAN",
            "phone": "+91 9922001122",
            "village": "Wagholi Veterinary Dispensary",
            "taluka": "Haveli",
            "district": "Pune",
            "license_number": "MAH-VET-2018-4921",
            "is_active": True,
            "created_at": now_str,
            **DEMO_LABELS
        },
        {
            "_id": "usr_dr_patil",
            "username": "dr_patil",
            "password": hashed_pwd,
            "fullname": "Dr. Vikram Patil (M.V.Sc Epidemiology)",
            "role": "VETERINARIAN",
            "phone": "+91 9922003344",
            "village": "Baramati Veterinary Clinic",
            "taluka": "Baramati",
            "district": "Pune",
            "license_number": "MAH-VET-2020-8812",
            "is_active": True,
            "created_at": now_str,
            **DEMO_LABELS
        },
        {
            "_id": "usr_admin_officer",
            "username": "admin_officer",
            "password": hashed_pwd,
            "fullname": "Shri. R. K. Chavan (District AH Officer)",
            "role": "ADMIN",
            "phone": "+91 9000000000",
            "village": "Central Administrative Complex",
            "taluka": "Pune",
            "district": "Pune",
            "is_active": True,
            "created_at": now_str,
            **DEMO_LABELS
        }
    ]
    for u in users:
        db["users"].insert_one(u)
    print(" -> Seeded 6 Users (3 Farmers, 2 Vets, 1 Admin). Default Password: 'sih2026'")
    
    # 3. Seed Animals with Digital QR Passports
    animals_raw = [
        {
            "tag": "TAG-MH-2026-SIM01",
            "qr": "QR-SENTINEL-SIM01",
            "species": "Cattle",
            "breed": "Gir",
            "age": 4.5,
            "gender": "Female",
            "owner": "farmer_ramesh",
            "owner_name": "Ramesh Patil",
            "status": "SUSPECTED",
            "lat": 18.5784,
            "lng": 73.9821,
            "village": "Wagholi"
        },
        {
            "tag": "TAG-MH-2026-SIM02",
            "qr": "QR-SENTINEL-SIM02",
            "species": "Cattle",
            "breed": "Sahiwal",
            "age": 3.0,
            "gender": "Female",
            "owner": "farmer_ramesh",
            "owner_name": "Ramesh Patil",
            "status": "HEALTHY",
            "lat": 18.5789,
            "lng": 73.9825,
            "village": "Wagholi"
        },
        {
            "tag": "TAG-MH-2026-SIM05",
            "qr": "QR-SENTINEL-SIM05",
            "species": "Cattle",
            "breed": "Sahiwal",
            "age": 3.8,
            "gender": "Female",
            "owner": "farmer_suresh",
            "owner_name": "Suresh Deshmukh",
            "status": "SUSPECTED",
            "lat": 18.5795,
            "lng": 73.9840,
            "village": "Wagholi"
        },
        {
            "tag": "TAG-MH-2026-SIM06",
            "qr": "QR-SENTINEL-SIM06",
            "species": "Cattle",
            "breed": "Crossbreed (HF x Sahiwal)",
            "age": 2.9,
            "gender": "Female",
            "owner": "farmer_suresh",
            "owner_name": "Suresh Deshmukh",
            "status": "SUSPECTED",
            "lat": 18.5810,
            "lng": 73.9815,
            "village": "Wagholi"
        },
        {
            "tag": "TAG-MH-2026-SIM07",
            "qr": "QR-SENTINEL-SIM07",
            "species": "Cattle",
            "breed": "Holstein Friesian",
            "age": 4.1,
            "gender": "Female",
            "owner": "farmer_ganesh",
            "owner_name": "Ganesh Shinde",
            "status": "SUSPECTED",
            "lat": 18.5825,
            "lng": 73.9850,
            "village": "Bakori"
        },
        {
            "tag": "TAG-MH-2026-SIM03",
            "qr": "QR-SENTINEL-SIM03",
            "species": "Buffalo",
            "breed": "Murrah",
            "age": 5.2,
            "gender": "Female",
            "owner": "farmer_suresh",
            "owner_name": "Suresh Deshmukh",
            "status": "HEALTHY",
            "lat": 18.5142,
            "lng": 73.9785,
            "village": "Manjari"
        },
        {
            "tag": "TAG-MH-2026-SIM04",
            "qr": "QR-SENTINEL-SIM04",
            "species": "Cattle",
            "breed": "Holstein Friesian",
            "age": 2.5,
            "gender": "Female",
            "owner": "farmer_ramesh",
            "owner_name": "Ramesh Patil",
            "status": "HEALTHY",
            "lat": 18.5780,
            "lng": 73.9818,
            "village": "Wagholi"
        }
    ]
    
    for a in animals_raw:
        verify_url = f"/api/animals/qr/{a['qr']}"
        file_url, b64_uri = generate_qr_code_assets(verify_url, a["tag"])
        
        doc = {
            "animal_id": a["tag"],
            "qr_code_identifier": a["qr"],
            "qr_code_url": file_url,
            "qr_code_base64": b64_uri,
            "species": a["species"],
            "breed": a["breed"],
            "age": a["age"],
            "gender": a["gender"],
            "health_history": "Monitored under Sentinel Digital Passport Program.",
            "owner_id": a["owner"],
            "owner_name": a["owner_name"],
            "owner_phone": "+91 9822011223" if a["owner"] == "farmer_ramesh" else "+91 9822099887",
            "health_status": a["status"],
            "latitude": a["lat"],
            "longitude": a["lng"],
            "village": a["village"],
            "taluka": "Haveli",
            "district": "Pune",
            "created_at": (now_dt - timedelta(days=45)).isoformat(),
            "updated_at": now_str,
            **DEMO_LABELS
        }
        db["animals"].insert_one(doc)
    print(f" -> Seeded {len(animals_raw)} Livestock Animals with QR Passports & Coordinates.")
    
    # 4. Seed Immunization Ledger (Vaccinations)
    vaccinations = [
        {
            "animal_id": "TAG-MH-2026-SIM01",
            "vaccine_name": "Lumpy Skin Disease Homologous Neethling Strain",
            "batch_number": "LSD-BAT-2025-08",
            "administered_date": "2025-09-15",
            "next_due_date": "2026-09-15",
            "status": "ADMINISTERED",
            "administered_by": "Dr. Anita Kulkarni",
            **DEMO_LABELS
        },
        {
            "animal_id": "TAG-MH-2026-SIM01",
            "vaccine_name": "Foot-and-Mouth Disease (FMD) Quadrivalent Booster",
            "batch_number": "FMD-BAT-2025-11",
            "administered_date": "2025-11-20",
            "next_due_date": "2026-05-20",
            "status": "OVERDUE",
            "administered_by": "Dr. Anita Kulkarni",
            **DEMO_LABELS
        },
        {
            "animal_id": "TAG-MH-2026-SIM02",
            "vaccine_name": "Lumpy Skin Disease Homologous Neethling Strain",
            "batch_number": "LSD-BAT-2025-08",
            "administered_date": "2025-09-15",
            "next_due_date": "2026-09-15",
            "status": "ADMINISTERED",
            "administered_by": "Dr. Anita Kulkarni",
            **DEMO_LABELS
        },
        {
            "animal_id": "TAG-MH-2026-SIM05",
            "vaccine_name": "Foot-and-Mouth Disease (FMD) Quadrivalent Booster",
            "batch_number": "FMD-BAT-2025-11",
            "administered_date": "2025-11-20",
            "next_due_date": "2026-05-20",
            "status": "OVERDUE",
            "administered_by": "Dr. Anita Kulkarni",
            **DEMO_LABELS
        }
    ]
    for v in vaccinations:
        db["vaccinations"].insert_one(v)
    print(" -> Seeded Vaccination Immunization Records.")

    # 5. Seed Baseline Farmer Health Vitals
    health_records = [
        {
            "animal_id": "TAG-MH-2026-SIM01",
            "body_temperature_c": 40.8,
            "heart_rate_bpm": 92,
            "respiratory_rate_bpm": 42,
            "symptoms": ["skin_abnormalities", "fever", "loss_of_appetite", "reduced_milk_production"],
            "appetite": "Low (0.1)",
            "activity": "Lethargic (0.1)",
            "milk_yield_liters": 2.1,
            "observations": "High pyrexia, severe nodular eruptions across neck, flank, and udder. Milk yield dropped abruptly.",
            "recorded_by": "farmer_ramesh",
            "recorded_at": (now_dt - timedelta(hours=14)).isoformat(),
            **DEMO_LABELS
        },
        {
            "animal_id": "TAG-MH-2026-SIM05",
            "body_temperature_c": 40.5,
            "heart_rate_bpm": 88,
            "respiratory_rate_bpm": 38,
            "symptoms": ["skin_abnormalities", "fever", "loss_of_appetite", "lameness"],
            "appetite": "Low (0.2)",
            "activity": "Lethargic (0.2)",
            "milk_yield_liters": 3.0,
            "observations": "Multiple cutaneous nodules, stiffness in limbs, high fever.",
            "recorded_by": "farmer_suresh",
            "recorded_at": (now_dt - timedelta(hours=12)).isoformat(),
            **DEMO_LABELS
        },
        {
            "animal_id": "TAG-MH-2026-SIM06",
            "body_temperature_c": 40.2,
            "heart_rate_bpm": 85,
            "respiratory_rate_bpm": 36,
            "symptoms": ["skin_abnormalities", "fever", "eye_discharge", "loss_of_appetite"],
            "appetite": "Low (0.2)",
            "activity": "Lethargic (0.3)",
            "milk_yield_liters": 3.5,
            "observations": "Nodular skin lesions around head and neck, bilateral mucopurulent ocular discharge.",
            "recorded_by": "farmer_suresh",
            "recorded_at": (now_dt - timedelta(hours=10)).isoformat(),
            **DEMO_LABELS
        },
        {
            "animal_id": "TAG-MH-2026-SIM07",
            "body_temperature_c": 40.6,
            "heart_rate_bpm": 90,
            "respiratory_rate_bpm": 40,
            "symptoms": ["skin_abnormalities", "fever", "reduced_milk_production", "loss_of_appetite"],
            "appetite": "Low (0.15)",
            "activity": "Lethargic (0.2)",
            "milk_yield_liters": 4.0,
            "observations": "Firm circumscribed lumps on chest and legs. Animal in discomfort.",
            "recorded_by": "farmer_ganesh",
            "recorded_at": (now_dt - timedelta(hours=6)).isoformat(),
            **DEMO_LABELS
        }
    ]
    for hr in health_records:
        db["health_records"].insert_one(hr)
    print(" -> Seeded Farmer Vitals & Clinical Health Records.")

    # 6. INTENTIONAL SIMULATED SCENARIO:
    # "Several cattle in a nearby region submit high-risk reports with similar symptoms and AI risk patterns within a short time period."
    # We populate 4 high-risk health reports & disease reports in Wagholi/Bakori (within <2 km radius) filed in the past 24 hours.
    
    simulated_reports = [
        {
            "report_id": "rep_sim_wagholi_01",
            "animal_id": "TAG-MH-2026-SIM01",
            "animal_tag": "TAG-MH-2026-SIM01",
            "owner_id": "farmer_ramesh",
            "owner_name": "Ramesh Patil",
            "species": "Cattle",
            "breed": "Gir",
            "village": "Wagholi",
            "taluka": "Haveli",
            "district": "Pune",
            "latitude": 18.5784,
            "longitude": 73.9821,
            "reported_disease": "Lumpy Skin Disease",
            "symptoms": ["skin_abnormalities", "fever", "loss_of_appetite", "reduced_milk_production"],
            "vitals": {"temperature_c": 40.8, "heart_rate": 92, "respiratory_rate": 42},
            "final_risk_score": 94.2,
            "risk_score": 94.2,
            "risk_level": "Critical",
            "reported_at": (now_dt - timedelta(hours=14)).isoformat(),
            "created_at": (now_dt - timedelta(hours=14)).isoformat(),
            "status": "PENDING_VET_REVIEW",
            "is_quarantine_required": True,
            **DEMO_LABELS
        },
        {
            "report_id": "rep_sim_wagholi_02",
            "animal_id": "TAG-MH-2026-SIM05",
            "animal_tag": "TAG-MH-2026-SIM05",
            "owner_id": "farmer_suresh",
            "owner_name": "Suresh Deshmukh",
            "species": "Cattle",
            "breed": "Sahiwal",
            "village": "Wagholi",
            "taluka": "Haveli",
            "district": "Pune",
            "latitude": 18.5795,
            "longitude": 73.9840,
            "reported_disease": "Lumpy Skin Disease",
            "symptoms": ["skin_abnormalities", "fever", "loss_of_appetite", "lameness"],
            "vitals": {"temperature_c": 40.5, "heart_rate": 88, "respiratory_rate": 38},
            "final_risk_score": 88.5,
            "risk_score": 88.5,
            "risk_level": "Critical",
            "reported_at": (now_dt - timedelta(hours=12)).isoformat(),
            "created_at": (now_dt - timedelta(hours=12)).isoformat(),
            "status": "PENDING_VET_REVIEW",
            "is_quarantine_required": True,
            **DEMO_LABELS
        },
        {
            "report_id": "rep_sim_wagholi_03",
            "animal_id": "TAG-MH-2026-SIM06",
            "animal_tag": "TAG-MH-2026-SIM06",
            "owner_id": "farmer_suresh",
            "owner_name": "Suresh Deshmukh",
            "species": "Cattle",
            "breed": "Crossbreed (HF x Sahiwal)",
            "village": "Wagholi",
            "taluka": "Haveli",
            "district": "Pune",
            "latitude": 18.5810,
            "longitude": 73.9815,
            "reported_disease": "Lumpy Skin Disease",
            "symptoms": ["skin_abnormalities", "fever", "eye_discharge", "loss_of_appetite"],
            "vitals": {"temperature_c": 40.2, "heart_rate": 85, "respiratory_rate": 36},
            "final_risk_score": 91.0,
            "risk_score": 91.0,
            "risk_level": "Critical",
            "reported_at": (now_dt - timedelta(hours=10)).isoformat(),
            "created_at": (now_dt - timedelta(hours=10)).isoformat(),
            "status": "PENDING_VET_REVIEW",
            "is_quarantine_required": True,
            **DEMO_LABELS
        },
        {
            "report_id": "rep_sim_wagholi_04",
            "animal_id": "TAG-MH-2026-SIM07",
            "animal_tag": "TAG-MH-2026-SIM07",
            "owner_id": "farmer_ganesh",
            "owner_name": "Ganesh Shinde",
            "species": "Cattle",
            "breed": "Holstein Friesian",
            "village": "Bakori",
            "taluka": "Haveli",
            "district": "Pune",
            "latitude": 18.5825,
            "longitude": 73.9850,
            "reported_disease": "Lumpy Skin Disease",
            "symptoms": ["skin_abnormalities", "fever", "reduced_milk_production", "loss_of_appetite"],
            "vitals": {"temperature_c": 40.6, "heart_rate": 90, "respiratory_rate": 40},
            "final_risk_score": 89.8,
            "risk_score": 89.8,
            "risk_level": "Critical",
            "reported_at": (now_dt - timedelta(hours=6)).isoformat(),
            "created_at": (now_dt - timedelta(hours=6)).isoformat(),
            "status": "PENDING_VET_REVIEW",
            "is_quarantine_required": True,
            **DEMO_LABELS
        }
    ]

    for rep in simulated_reports:
        # Insert into both health_reports and disease_reports for full system compatibility
        db["health_reports"].insert_one(rep)
        db["disease_reports"].insert_one(rep)

        # AI Prediction Record for Multi-Modal Fusion
        ai_pred = {
            "prediction_id": f"ai_pred_{rep['report_id']}",
            "health_report_id": rep["report_id"],
            "animal_id": rep["animal_id"],
            "predicted_condition": "Lumpy Skin Disease",
            "confidence_score": round(rep["final_risk_score"] / 100.0, 3),
            "risk_level": rep["risk_level"],
            "final_risk_score": rep["final_risk_score"],
            "model_weights": {"image": 0.40, "symptom": 0.35, "environment": 0.15, "vaccination": 0.10},
            "is_veterinary_diagnosis": False,
            "disclaimer": "AI risk assessment only. Not a veterinary diagnosis.",
            "created_at": rep["created_at"],
            **DEMO_LABELS
        }
        db["ai_predictions"].insert_one(ai_pred)

    print(" -> Seeded 4 High-Risk Cattle Reports (Wagholi/Bakori Cluster Scenario).")

    # 7. EXECUTE AUTOMATED DBSCAN SPATIO-TEMPORAL CLUSTER DETECTION
    print(" -> Executing Haversine DBSCAN Spatial Cluster Detection...")
    cluster_service = ClusterDetectionService.get_instance()
    detected_clusters = cluster_service.run_detection(
        geo_radius_km=5.0,
        min_reports=3,
        time_window_days=7,
        disease_filter=None,
        persist=True,
        emit_alerts=True
    )
    
    print(f" -> DETECTED {len(detected_clusters)} POTENTIAL DISEASE CLUSTER(S).")
    for cl in detected_clusters:
        c_lat = cl.get('centroid', {}).get('latitude') or cl.get('center_location', {}).get('latitude')
        c_lng = cl.get('centroid', {}).get('longitude') or cl.get('center_location', {}).get('longitude')
        d_name = cl.get('disease_name') or cl.get('disease')
        print(f"    [CLUSTER ID: {cl.get('cluster_id')}] Disease: {d_name}, Reports: {cl.get('report_count')}, Villages: {cl.get('villages')}, Centroid: ({c_lat}, {c_lng})")

    print("\n==========================================================================")
    print("  CONTROLLED SIH DEMONSTRATION DATASET SEEDED SUCCESSFULLY")
    print("  All data contains explicit 'is_simulated_demo: True' internal tags.")
    print("==========================================================================")

if __name__ == "__main__":
    seed_demo_data()
