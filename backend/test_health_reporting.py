"""
Automated Verification Suite for Livestock Health Reporting & Disease Surveillance.
Tests:
1. Farmer selects animal, enters symptoms, uploads image, shares location.
2. System executes all available AI models (Image, Symptoms, Environmental).
3. Multi-modal risk engine calculates calibrated score and assigns risk tier.
4. Health report is persisted in database.
5. High/Critical risk triggers automated disease surveillance report, updates animal to SUSPECTED, and emits district alert.
6. Location privacy: Precise micro-coordinates are not exposed to unauthorized users; approximate (~1.1km) coordinates provided.
7. Role-based access control: Farmers cannot access or submit for other farmers' herds.
8. Ethical non-veterinary diagnosis disclaimers verified.
"""

import os
import io
import time
from PIL import Image
from fastapi.testclient import TestClient

from main import app
from database import db
from auth import create_access_token

client = TestClient(app)

def create_dummy_image_bytes(color=(140, 160, 120), size=(224, 224)) -> bytes:
    img = Image.new("RGB", size, color=color)
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()

def setup_test_users_and_animals():
    """Sets up clean test data for farmer1, farmer2, vet1, and test cattle."""
    # 1. Farmer 1
    farmer1_doc = {
        "_id": "user_farmer_1",
        "id": "user_farmer_1",
        "username": "ramesh_farmer",
        "fullname": "Ramesh Patil",
        "role": "FARMER",
        "village": "Wadgaon",
        "taluka": "Haveli",
        "district": "Pune"
    }
    db["users"].delete_one({"username": "ramesh_farmer"})
    db["users"].insert_one(farmer1_doc)

    # 2. Farmer 2 (different farm)
    farmer2_doc = {
        "_id": "user_farmer_2",
        "id": "user_farmer_2",
        "username": "suresh_farmer",
        "fullname": "Suresh Shinde",
        "role": "FARMER",
        "village": "Baramati",
        "taluka": "Baramati",
        "district": "Pune"
    }
    db["users"].delete_one({"username": "suresh_farmer"})
    db["users"].insert_one(farmer2_doc)

    # 3. Veterinarian
    vet_doc = {
        "_id": "user_vet_1",
        "id": "user_vet_1",
        "username": "dr_deshmukh_vet",
        "fullname": "Dr. Ananya Deshmukh",
        "role": "VETERINARIAN",
        "license_number": "MAH-VET-2024-8891",
        "district": "Pune"
    }
    db["users"].delete_one({"username": "dr_deshmukh_vet"})
    db["users"].insert_one(vet_doc)

    # 4. Animal belonging to Farmer 1
    animal1_doc = {
        "_id": "animal_cow_001",
        "id": "animal_cow_001",
        "animal_id": "MH-PUN-COW-9001",
        "species": "Cattle",
        "breed": "Gir",
        "age": 3.5,
        "gender": "Female",
        "owner_id": "ramesh_farmer",
        "owner_name": "Ramesh Patil",
        "health_status": "HEALTHY",
        "health_history": "none",
        "vaccination_status": "not_vaccinated",
        "latitude": 18.520432,
        "longitude": 73.856743,
        "village": "Wadgaon",
        "taluka": "Haveli",
        "district": "Pune"
    }
    db["animals"].delete_one({"animal_id": "MH-PUN-COW-9001"})
    db["animals"].insert_one(animal1_doc)

    # 5. Animal belonging to Farmer 2
    animal2_doc = {
        "_id": "animal_cow_002",
        "id": "animal_cow_002",
        "animal_id": "MH-PUN-COW-9002",
        "species": "Cattle",
        "breed": "Sahiwal",
        "age": 4.0,
        "gender": "Female",
        "owner_id": "suresh_farmer",
        "owner_name": "Suresh Shinde",
        "health_status": "HEALTHY",
        "health_history": "none",
        "vaccination_status": "vaccinated",
        "latitude": 18.151234,
        "longitude": 74.578912,
        "village": "Baramati",
        "taluka": "Baramati",
        "district": "Pune"
    }
    db["animals"].delete_one({"animal_id": "MH-PUN-COW-9002"})
    db["animals"].insert_one(animal2_doc)

def get_auth_header(username: str, role: str) -> dict:
    token = create_access_token({"sub": username, "role": role})
    return {"Authorization": f"Bearer {token}"}

def test_high_risk_health_report_submission():
    print("\n--- 1. Testing High-Risk Health Report Submission with Image & GPS ---")
    setup_test_users_and_animals()
    farmer1_headers = get_auth_header("ramesh_farmer", "FARMER")
    
    dummy_img = create_dummy_image_bytes()
    
    # Farmer 1 reports severe skin abnormalities on COW-9001
    payload_data = {
        "animal_id": "MH-PUN-COW-9001",
        "symptoms": '["skin_abnormalities", "fever", "loss_of_appetite"]',
        "latitude": "18.520432",
        "longitude": "73.856743",
        "share_location": "true",
        "village": "Wadgaon",
        "taluka": "Haveli",
        "district": "Pune",
        "body_temperature_c": "40.2",
        "clinical_notes": "Multiple raised circular skin nodules observed along the neck and flank."
    }
    
    t0 = time.time()
    response = client.post(
        "/api/reports/health",
        headers=farmer1_headers,
        data=payload_data,
        files={"image": ("skin_nodules.jpg", dummy_img, "image/jpeg")}
    )
    latency_ms = (time.time() - t0) * 1000
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    report = response.json()
    
    print(f"  Submission processed in {latency_ms:.1f}ms")
    print(f"  Report ID: {report.get('report_id')}")
    print(f"  Animal Tag: {report.get('animal_tag')}")
    print(f"  Multi-Modal Risk Score: {report['multi_modal_risk']['final_risk_score']}")
    print(f"  Risk Level: {report['multi_modal_risk']['risk_level']}")
    print(f"  Is Surveillance Triggered: {report.get('is_surveillance_triggered')}")
    print(f"  Surveillance Report ID: {report.get('surveillance_report_id')}")
    print(f"  Animal Health Status: {report.get('animal_health_status')}")
    print(f"  Location Access Level: {report.get('location_access_level')}")
    
    # Validations
    assert report["animal_tag"] == "MH-PUN-COW-9001"
    assert report["is_surveillance_triggered"] is True, "High risk must trigger automated surveillance!"
    assert report["surveillance_report_id"] is not None
    assert report["animal_health_status"] == "SUSPECTED"
    assert report["is_veterinary_diagnosis"] is False
    assert "not a veterinary diagnosis" in report["disclaimer"].lower()
    
    # Verify AI Analyses Ran
    analyses = report["ai_analyses"]
    assert "image" in analyses and analyses["image"] is not None
    assert "symptoms" in analyses and analyses["symptoms"] is not None
    assert "environment" in analyses and analyses["environment"] is not None
    assert "Lumpy Skin Disease" in analyses["symptoms"]["top_condition"]
    
    # Verify Database Persistence
    saved_rep = db["health_reports"].find_one({"_id": report["report_id"]})
    assert saved_rep is not None, "Health report must be persisted in database!"
    
    # Verify Automated Surveillance Case Created
    case = db["disease_reports"].find_one({"_id": report["surveillance_report_id"]})
    assert case is not None, "Disease surveillance case must be persisted!"
    assert case["status"] == "PENDING_REVIEW"
    assert case["is_quarantine_required"] is True
    
    # Verify Animal Ground Truth Updated in Animals Collection
    updated_animal = db["animals"].find_one({"animal_id": "MH-PUN-COW-9001"})
    assert updated_animal["health_status"] == "SUSPECTED"
    
    # Verify Early Warning Alert Dispatched to District Veterinarians
    alert = db["alerts"].find_one({"related_report_id": report["report_id"]})
    assert alert is not None, "Early warning alert must be emitted for high-risk cases!"
    assert alert["alert_type"] == "OUTBREAK_EARLY_WARNING"
    assert "Wadgaon" in alert["message"]
    print("  [PASS] High-risk report, AI orchestration, automated surveillance, and alert verified.")
    return report["report_id"]

def test_location_privacy_and_access_control(report_id: str):
    print("\n--- 2. Testing Location Privacy & Role-Based Access Control ---")
    farmer1_headers = get_auth_header("ramesh_farmer", "FARMER")
    farmer2_headers = get_auth_header("suresh_farmer", "FARMER")
    vet_headers = get_auth_header("dr_deshmukh_vet", "VETERINARIAN")
    
    # 1. Owning Farmer views their own report -> Has exact coordinates
    res_owner = client.get(f"/api/reports/health/{report_id}", headers=farmer1_headers)
    assert res_owner.status_code == 200
    owner_data = res_owner.json()["report"]
    print(f"  Owner View: Access level = {owner_data['location_access_level']}")
    assert owner_data["location_access_level"] == "authorized_exact"
    assert owner_data["location"]["latitude"] == 18.520432
    assert owner_data["location"]["longitude"] == 73.856743
    
    # 2. Other Farmer (farmer 2) tries to view farmer 1's report -> BLOCKED (403)
    res_other = client.get(f"/api/reports/health/{report_id}", headers=farmer2_headers)
    print(f"  Other Farmer Access: status = {res_other.status_code}")
    assert res_other.status_code == 403, "Farmers must NOT view other farmers' health reports!"
    
    # 3. Farmer 2 tries to submit a report for Farmer 1's animal -> BLOCKED (403)
    res_fake_sub = client.post(
        "/api/reports/health",
        headers=farmer2_headers,
        json={"animal_id": "MH-PUN-COW-9001", "symptoms": ["fever"]}
    )
    print(f"  Unauthorized Herd Report Submission: status = {res_fake_sub.status_code}")
    assert res_fake_sub.status_code == 403, "Farmers cannot report on animals they don't own!"
    
    # 4. Veterinarian views list of reports in area -> Receives approximate location for general view
    res_vet_list = client.get("/api/reports/health", headers=vet_headers)
    assert res_vet_list.status_code == 200
    vet_reports = res_vet_list.json()["reports"]
    target = next((r for r in vet_reports if r["report_id"] == report_id), None)
    assert target is not None
    print(f"  Veterinarian Queue View: approx_lat = {target['location']['approximate_latitude']}, village = {target['location']['village']}")
    assert target["location"]["approximate_latitude"] == 18.52 # Fuzzed ~1.1km grid
    assert target["location"]["approximate_longitude"] == 73.86
    assert "exact_latitude" not in target, "Exact coordinates must NEVER be leaked in public/list views!"
    print("  [PASS] Location privacy guardrails and role-based permissions strictly enforced.")

def test_low_risk_health_report_no_emergency():
    print("\n--- 3. Testing Low-Risk Report (No False Alarm Surveillance Trigger) ---")
    farmer2_headers = get_auth_header("suresh_farmer", "FARMER")
    
    # Farmer 2 reports mild lethargy on vaccinated cow
    payload = {
        "animal_id": "MH-PUN-COW-9002",
        "symptoms": ["loss_of_appetite"],
        "body_temperature_c": 38.6,
        "appetite_score": 0.8,
        "clinical_notes": "Slight reduction in morning concentrate intake."
    }
    
    response = client.post("/api/reports/health", headers=farmer2_headers, json=payload)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    report = response.json()
    
    print(f"  Low Risk Score: {report['multi_modal_risk']['final_risk_score']} ({report['multi_modal_risk']['risk_level']})")
    print(f"  Is Surveillance Triggered: {report.get('is_surveillance_triggered')}")
    print(f"  Animal Health Status: {report.get('animal_health_status')}")
    
    # Should NOT trigger emergency surveillance
    assert report["is_surveillance_triggered"] is False
    assert report["surveillance_report_id"] is None
    assert report["animal_health_status"] == "HEALTHY"
    
    # Animal in database should remain HEALTHY
    cow = db["animals"].find_one({"animal_id": "MH-PUN-COW-9002"})
    assert cow["health_status"] == "HEALTHY"
    print("  [PASS] Low-risk reporting avoids unnecessary emergency alerts.")

if __name__ == "__main__":
    print("=================================================================")
    print("   AI-LIVESTOCK HEALTH SENTINEL - HEALTH REPORTING TESTS         ")
    print("=================================================================")
    rep_id = test_high_risk_health_report_submission()
    test_location_privacy_and_access_control(rep_id)
    test_low_risk_health_report_no_emergency()
    print("\n>>> ALL HEALTH REPORTING & SURVEILLANCE TESTS PASSED! <<<\n")
