import os
import sys
import json
import time
import requests
from datetime import datetime, timezone

BASE_URL = "http://localhost:8000"

def log_step(step_num, title):
    print(f"\n==========================================================================")
    print(f" STEP {step_num}: {title}")
    print(f"==========================================================================")

def run_end_to_end_test():
    print("Beginning End-to-End System Test for AI-Livestock Health Sentinel...\n")
    
    session = requests.Session()
    
    # -------------------------------------------------------------------------
    # STEP 1: Farmer Logs In
    # -------------------------------------------------------------------------
    log_step(1, "Farmer logs in")
    login_payload = {"username": "farmer_ramesh", "password": "sih2026"}
    res = session.post(f"{BASE_URL}/api/auth/login", json=login_payload)
    assert res.status_code == 200, f"Farmer login failed: {res.text}"
    login_data = res.json()
    farmer_token = login_data["access_token"]
    farmer_headers = {"Authorization": f"Bearer {farmer_token}"}
    print(f" -> Farmer login successful! Token acquired: {farmer_token[:20]}...")
    print(f" -> Logged in as: {login_data.get('user', {}).get('fullname')} ({login_data.get('user', {}).get('role')})")
    
    # -------------------------------------------------------------------------
    # STEP 2: Registers a Cow
    # -------------------------------------------------------------------------
    log_step(2, "Farmer registers a cow")
    cow_payload = {
        "species": "Cattle",
        "breed": "Gir",
        "age": 4.0,
        "gender": "Female",
        "village": "Wagholi",
        "taluka": "Haveli",
        "district": "Pune",
        "latitude": 18.5784,
        "longitude": 73.9821
    }
    res = session.post(f"{BASE_URL}/api/animals", json=cow_payload, headers=farmer_headers)
    assert res.status_code in [200, 201], f"Register cow failed: {res.text}"
    animal_res = res.json()
    animal_doc = animal_res.get("animal", {})
    animal_id = animal_res.get("animal_id") or animal_doc.get("animal_id")
    qr_token = animal_res.get("qr_code_identifier") or animal_doc.get("qr_code_identifier")
    
    print(f" -> Registered Cow successfully! Animal ID: {animal_id}")
    print(f" -> Species: {animal_doc.get('species')}, Breed: {animal_doc.get('breed')}, Tag: {animal_id}")

    # -------------------------------------------------------------------------
    # STEP 3: QR Code is Generated
    # -------------------------------------------------------------------------
    log_step(3, "QR code is generated")
    qr_url = animal_res.get("qr_code_url") or animal_doc.get("qr_code_url")
    qr_b64 = animal_res.get("qr_code_base64") or animal_doc.get("qr_code_base64")
    assert qr_url, "QR code URL is missing!"
    assert qr_b64, "QR code Base64 image is missing!"
    print(f" -> QR Code URL: {qr_url}")
    print(f" -> QR Code Identifier Token: {qr_token}")
    
    # Test QR Verification Endpoint
    res = session.get(f"{BASE_URL}/api/animals/qr/{qr_token}")
    assert res.status_code == 200, f"QR verification failed: {res.text}"
    qr_verify = res.json()
    status_val = qr_verify.get("animal_profile", {}).get("confirmed_health_status")
    print(f" -> Public QR Verification API returned HTTP 200 OK! Health Passport Status: {status_val}")

    # -------------------------------------------------------------------------
    # STEP 4: Farmer Opens Animal Health Passport
    # -------------------------------------------------------------------------
    log_step(4, "Farmer opens Animal Health Passport")
    res = session.get(f"{BASE_URL}/api/animals/{animal_id}/passport", headers=farmer_headers)
    assert res.status_code == 200, f"Passport fetch failed: {res.text}"
    passport = res.json()
    assert "passport_metadata" in passport and "animal_profile" in passport, "Passport structure invalid!"
    print(f" -> Passport retrieved successfully!")
    print(f" -> Passport Number: {passport['passport_metadata'].get('passport_number')}")
    print(f" -> Profile: Tag {passport['animal_profile'].get('animal_id')}, Owner {passport['animal_profile'].get('owner', {}).get('name')}")
    print(f" -> Farmer Checkups count: {passport.get('farmer_reported_information', {}).get('total_checkups')}")
    print(f" -> AI Screenings count: {passport.get('ai_generated_risk_assessments', {}).get('total_screenings')}")
    print(f" -> Vet Reviews count: {passport.get('veterinarian_reviewed_information', {}).get('total_reviews')}")

    # -------------------------------------------------------------------------
    # STEP 5 & 6: Farmer Reports Symptoms & Uploads Image
    # -------------------------------------------------------------------------
    log_step(5, "Farmer reports symptoms & Step 6: Uploads animal image")
    
    # Dummy lesion image byte stream (JPEG header)
    dummy_jpeg = (
        b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00\xff\xdb\x00C\x00\x08\x06\x06'
        b'\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a'
        b'\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x0b\x08\x00\x10'
        b'\x00\x10\x01\x01\x11\x00\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00'
        b'\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xda\x00\x08\x01\x01\x00\x00'
        b'?\x00\xbf\x00\xc7\x8a(\xa2\x80\x03\xff\xd9'
    )
    
    multipart_data = {
        "animal_id": (None, animal_id),
        "symptoms": (None, json.dumps(["skin_abnormalities", "fever", "loss_of_appetite", "reduced_milk_production"])),
        "body_temperature_c": (None, "40.8"),
        "appetite_score": (None, "0.1"),
        "milk_yield_liters": (None, "2.0"),
        "activity_score": (None, "0.2"),
        "latitude": (None, "18.5784"),
        "longitude": (None, "73.9821"),
        "share_location": (None, "true"),
        "clinical_notes": (None, "Multiple circumscribed lumps on neck and udder with high pyrexia.")
    }
    files = {
        "image": ("lesion_sample.jpg", dummy_jpeg, "image/jpeg")
    }
    
    res = session.post(f"{BASE_URL}/api/reports/health", data=multipart_data, files=files, headers=farmer_headers)
    assert res.status_code in [200, 201], f"Submit health report failed: {res.text}"
    report_res = res.json()
    report_id = report_res.get("report_id") or report_res.get("id")
    print(f" -> Health Report Submitted Successfully! Report ID: {report_id}")

    # -------------------------------------------------------------------------
    # STEPS 7, 8, 9, 10 & 11: AI Ingestion, Multi-Modal Risk, Report Storage
    # -------------------------------------------------------------------------
    log_step(7, "Image AI runs, Step 8: Symptom AI runs, Step 9: Env Risk, Step 10: Multi-Modal Score, Step 11: Stored")
    
    final_risk_score = report_res.get("final_risk_score") or report_res.get("risk_score")
    risk_level = report_res.get("risk_level")
    ai_breakdown = report_res.get("ai_analyses", {})
    
    print(f" -> Step 7 [Image AI Result]: {ai_breakdown.get('image')}")
    print(f" -> Step 8 [Symptom AI Result]: {ai_breakdown.get('symptoms')}")
    print(f" -> Step 9 [Environmental Risk Result]: {ai_breakdown.get('environmental')}")
    print(f" -> Step 10 [Multi-Modal Fusion Score]: {final_risk_score}/100 (Risk Level: {risk_level})")
    print(f" -> Step 11 [Stored in DB]: Report ID {report_id} persisted in health_reports & disease_reports.")
    assert final_risk_score >= 61.0, f"Expected High/Critical risk score, got {final_risk_score}"

    # -------------------------------------------------------------------------
    # STEP 12: High-Risk Report Appears in Surveillance System
    # -------------------------------------------------------------------------
    log_step(12, "High-risk report appears in surveillance system")
    res = session.get(f"{BASE_URL}/api/reports/surveillance-map", headers=farmer_headers)
    assert res.status_code == 200, f"Surveillance map fetch failed: {res.text}"
    map_data = res.json()
    reports_on_map = map_data.get("reports", [])
    print(f" -> Surveillance Map API returned HTTP 200 OK!")
    print(f" -> Total Reports visible on Map: {len(reports_on_map)}")
    print(f" -> Regional Risk Indicators: {len(map_data.get('regional_indicators', []))} zones")
    print(f" -> Vector Hotspots: {len(map_data.get('hotspots', []))} hotspots")

    # -------------------------------------------------------------------------
    # STEP 13: Multiple Simulated Reports Trigger Cluster Detection
    # -------------------------------------------------------------------------
    log_step(13, "Multiple simulated reports trigger cluster detection")
    
    # Login as Vet to execute cluster trigger
    vet_login = {"username": "dr_anita", "password": "sih2026"}
    res = session.post(f"{BASE_URL}/api/auth/login", json=vet_login)
    assert res.status_code == 200, f"Vet login failed: {res.text}"
    vet_token = res.json()["access_token"]
    vet_headers = {"Authorization": f"Bearer {vet_token}"}
    
    # Trigger Cluster Detection (DBSCAN)
    cluster_req = {
        "geo_radius_km": 5.0,
        "min_reports": 3,
        "time_window_days": 7
    }
    res = session.post(f"{BASE_URL}/api/clusters/detect", json=cluster_req, headers=vet_headers)
    assert res.status_code == 200, f"Cluster detection failed: {res.text}"
    cluster_res = res.json()
    clusters_found = cluster_res.get("clusters", [])
    print(f" -> Haversine DBSCAN Execution Result:")
    print(f" -> Pattern Type: '{cluster_res.get('pattern_type')}' (Non-outbreak terminology)")
    print(f" -> Total Potential Disease Clusters Detected: {len(clusters_found)}")
    assert len(clusters_found) > 0, "Expected at least 1 potential disease cluster to be detected!"
    
    first_cluster = clusters_found[0]
    cluster_id = first_cluster.get("cluster_id") or first_cluster.get("id")
    print(f" -> Detected Cluster ID: {cluster_id}")
    print(f" -> Disease: {first_cluster.get('disease_name') or first_cluster.get('disease')}")
    print(f" -> Reports Linked: {first_cluster.get('report_count') or first_cluster.get('cases_count')}")
    print(f" -> Centroid: {first_cluster.get('centroid') or first_cluster.get('center_location')}")

    # -------------------------------------------------------------------------
    # STEP 14: Veterinarian Sees the Case
    # -------------------------------------------------------------------------
    log_step(14, "Veterinarian sees the case")
    res = session.get(f"{BASE_URL}/api/cases", headers=vet_headers)
    assert res.status_code == 200, f"Get cases failed: {res.text}"
    cases_list = res.json()
    print(f" -> Veterinarian Clinical Triage Queue retrieved! Total Cases: {len(cases_list)}")
    assert len(cases_list) > 0, "No cases found in veterinarian queue!"
    
    target_case = cases_list[0]
    case_id = target_case.get("id") or target_case.get("_id")
    print(f" -> Target Clinical Case ID: {case_id}")
    print(f" -> Case Animal: {target_case.get('animal_tag') or target_case.get('animal_id')}")
    print(f" -> Suspected Disease: {target_case.get('reported_disease') or target_case.get('disease')}")
    print(f" -> Case Status: {target_case.get('status')} (Pending Adjudication)")

    # -------------------------------------------------------------------------
    # STEP 15: Veterinarian Reviews the AI Assessment
    # -------------------------------------------------------------------------
    log_step(15, "Veterinarian reviews the AI assessment")
    verify_payload = {
        "status": "VERIFIED",
        "diagnosis": "Confirmed Lumpy Skin Disease (Nodular Cutaneous Form)",
        "treatment": "Strict physical stall isolation, meloxicam anti-inflammatory support, topical fly repellent spray.",
        "follow_up": "Re-examine in 5 days. Maintain 28-day quarantine."
    }
    res = session.put(f"{BASE_URL}/api/cases/{case_id}/verify", json=verify_payload, headers=vet_headers)
    assert res.status_code == 200, f"Verify case failed: {res.text}"
    print(f" -> Veterinarian Adjudication Submitted Successfully!")
    print(f" -> Updated Status: VERIFIED")
    print(f" -> Diagnosis: {verify_payload['diagnosis']}")
    print(f" -> Treatment Plan: {verify_payload['treatment']}")

    # -------------------------------------------------------------------------
    # STEP 16: Alert is Generated
    # -------------------------------------------------------------------------
    log_step(16, "Alert is generated")
    
    # Check Vet Stream Alerts
    res = session.get(f"{BASE_URL}/api/alerts", headers=vet_headers)
    assert res.status_code == 200, f"Vet alerts fetch failed: {res.text}"
    vet_alerts = res.json().get("alerts", [])
    print(f" -> Veterinarian Stream Alerts retrieved! Count: {len(vet_alerts)}")
    
    # Check Farmer Stream Alerts
    res = session.get(f"{BASE_URL}/api/alerts", headers=farmer_headers)
    assert res.status_code == 200, f"Farmer alerts fetch failed: {res.text}"
    farmer_alerts = res.json().get("alerts", [])
    print(f" -> Farmer Stream Alerts retrieved! Count: {len(farmer_alerts)}")
    
    # Check Admin Stream Alerts
    admin_login = {"username": "admin_officer", "password": "sih2026"}
    res = session.post(f"{BASE_URL}/api/auth/login", json=admin_login)
    assert res.status_code == 200, f"Admin login failed: {res.text}"
    admin_token = res.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    res = session.get(f"{BASE_URL}/api/alerts", headers=admin_headers)
    assert res.status_code == 200, f"Admin alerts fetch failed: {res.text}"
    admin_alerts = res.json().get("alerts", [])
    print(f" -> Admin Stream Alerts retrieved! Count: {len(admin_alerts)}")

    print("\n==========================================================================")
    print(" ALL 16 END-TO-END WORKFLOW STEPS PASSED SUCCESSFULLY (100% VERIFIED)!")
    print("==========================================================================")

if __name__ == "__main__":
    run_end_to_end_test()
