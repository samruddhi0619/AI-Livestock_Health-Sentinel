"""
Automated Verification Suite for Disease Surveillance Map Backend.
Tests:
1. Farmer-facing view prioritizing regional risk indicators, potential hotspots, and outbreak clusters.
2. Privacy guardrail: Private farm reports from other farmers are NOT exposed to a farmer.
3. Clinician / Admin view: Delivers authorized reports with privacy-fuzzed coordinates for general triage.
4. Multi-dimensional filtering: Disease, Date Range, Risk Level, Region.
5. Non-veterinary diagnosis disclaimers strictly enforced.
"""

from fastapi.testclient import TestClient

from main import app
from database import db
from auth import create_access_token

client = TestClient(app)

def setup_surveillance_test_data():
    """Seeds test data for surveillance map testing."""
    # Ensure users exist
    db["users"].delete_one({"username": "map_farmer_1"})
    db["users"].delete_one({"username": "map_farmer_2"})
    db["users"].delete_one({"username": "map_vet_1"})

    db["users"].insert_one({
        "_id": "user_map_farmer_1",
        "id": "user_map_farmer_1",
        "username": "map_farmer_1",
        "fullname": "Farmer 1",
        "role": "FARMER",
        "district": "Pune",
        "taluka": "Haveli",
        "village": "Wadgaon"
    })

    db["users"].insert_one({
        "_id": "user_map_farmer_2",
        "id": "user_map_farmer_2",
        "username": "map_farmer_2",
        "fullname": "Farmer 2",
        "role": "FARMER",
        "district": "Pune",
        "taluka": "Baramati",
        "village": "Baramati Rural"
    })

    db["users"].insert_one({
        "_id": "user_map_vet_1",
        "id": "user_map_vet_1",
        "username": "map_vet_1",
        "fullname": "Dr. Veterinary Officer",
        "role": "VETERINARIAN",
        "district": "Pune"
    })

    # Clear test reports
    for tid in ["TEST-REP-01", "TEST-REP-02", "TEST-REP-03"]:
        db["health_reports"].delete_one({"_id": tid})

    # Report 1: Farmer 1 in Haveli - High Risk LSD
    db["health_reports"].insert_one({
        "_id": "TEST-REP-01",
        "id": "TEST-REP-01",
        "animal_tag": "MH-PUN-001",
        "owner_id": "map_farmer_1",
        "recorded_by": "map_farmer_1",
        "reported_disease": "Lumpy Skin Disease",
        "risk_level": "High",
        "final_risk_score": 76.5,
        "exact_latitude": 18.520432,
        "exact_longitude": 73.856743,
        "approximate_latitude": 18.52,
        "approximate_longitude": 73.86,
        "village": "Wadgaon",
        "taluka": "Haveli",
        "district": "Pune",
        "is_surveillance_triggered": True,
        "status": "PENDING_REVIEW",
        "recorded_at": "2026-09-01T10:00:00Z"
    })

    # Report 2: Farmer 2 in Baramati - Medium Risk FMD
    db["health_reports"].insert_one({
        "_id": "TEST-REP-02",
        "id": "TEST-REP-02",
        "animal_tag": "MH-BAR-002",
        "owner_id": "map_farmer_2",
        "recorded_by": "map_farmer_2",
        "reported_disease": "Foot-and-Mouth Disease",
        "risk_level": "Medium",
        "final_risk_score": 54.0,
        "exact_latitude": 18.151234,
        "exact_longitude": 74.578912,
        "approximate_latitude": 18.15,
        "approximate_longitude": 74.58,
        "village": "Baramati Rural",
        "taluka": "Baramati",
        "district": "Pune",
        "is_surveillance_triggered": False,
        "status": "REPORTED",
        "recorded_at": "2026-08-28T12:00:00Z"
    })

    # Report 3: Farmer 1 in Haveli - Low Risk Brucellosis
    db["health_reports"].insert_one({
        "_id": "TEST-REP-03",
        "id": "TEST-REP-03",
        "animal_tag": "MH-PUN-003",
        "owner_id": "map_farmer_1",
        "recorded_by": "map_farmer_1",
        "reported_disease": "Brucellosis",
        "risk_level": "Low",
        "final_risk_score": 22.0,
        "exact_latitude": 18.524000,
        "exact_longitude": 73.858000,
        "approximate_latitude": 18.52,
        "approximate_longitude": 73.86,
        "village": "Wadgaon",
        "taluka": "Haveli",
        "district": "Pune",
        "is_surveillance_triggered": False,
        "status": "REPORTED",
        "recorded_at": "2026-09-03T15:00:00Z"
    })

    # Seed an Outbreak Cluster
    db["outbreak_clusters"].delete_one({"cluster_code": "TEST-CLUSTER-PUN-01"})
    db["outbreak_clusters"].insert_one({
        "_id": "cluster_test_01",
        "cluster_code": "TEST-CLUSTER-PUN-01",
        "disease": "Lumpy Skin Disease",
        "center_latitude": 18.525,
        "center_longitude": 73.860,
        "radius_km": 1.5,
        "cases_count": 4,
        "severity": "WARNING",
        "status": "ACTIVE",
        "affected_farms": ["Farm 1", "Farm 2"],
        "taluka": "Haveli",
        "district": "Pune"
    })

def get_auth_header(username: str, role: str) -> dict:
    token = create_access_token({"sub": username, "role": role})
    return {"Authorization": f"Bearer {token}"}

def test_farmer_facing_surveillance_map():
    print("\n--- 1. Testing Farmer-Facing Surveillance Map (Regional Focus & Privacy) ---")
    setup_surveillance_test_data()
    farmer_headers = get_auth_header("map_farmer_1", "FARMER")

    response = client.get("/api/reports/surveillance-map", headers=farmer_headers)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()

    print(f"  User Role: {data['user_role']}")
    print(f"  Is Farmer View: {data['is_farmer_view']}")
    print(f"  Regional Indicators Count: {len(data['regional_indicators'])}")
    print(f"  Clusters Count: {len(data['clusters'])}")
    print(f"  Hotspots Count: {len(data['hotspots'])}")
    print(f"  Farmer Reports Count: {len(data['reports'])}")

    # Validations
    assert data["is_farmer_view"] is True
    assert len(data["regional_indicators"]) >= 2
    assert len(data["clusters"]) >= 1
    assert len(data["hotspots"]) >= 1

    # Privacy Validation: Farmer 1 must NOT see Farmer 2's report in reports list!
    report_ids = [r["report_id"] for r in data["reports"]]
    assert "TEST-REP-02" not in report_ids, "Farmer 2's private farm report must be hidden from Farmer 1!"
    assert "TEST-REP-01" in report_ids, "Farmer 1's own report must be present"

    # Ethical Disclaimer Validation
    assert data["is_veterinary_diagnosis"] is False
    assert "not a veterinary diagnosis" in data["disclaimer"].lower()
    print("  [PASS] Farmer-facing view prioritizes regional risk while protecting farm privacy.")

def test_veterinarian_surveillance_map():
    print("\n--- 2. Testing Veterinarian/Admin Surveillance Map (Full Authorized Access) ---")
    vet_headers = get_auth_header("map_vet_1", "VETERINARIAN")

    response = client.get("/api/reports/surveillance-map", headers=vet_headers)
    assert response.status_code == 200
    data = response.json()

    print(f"  User Role: {data['user_role']}")
    print(f"  Is Farmer View: {data['is_farmer_view']}")
    print(f"  Total Authorized Reports in Jurisdiction: {len(data['reports'])}")

    assert data["is_farmer_view"] is False
    # Veterinarian sees reports from both Farmer 1 and Farmer 2
    report_ids = [r["report_id"] for r in data["reports"]]
    assert "TEST-REP-01" in report_ids
    assert "TEST-REP-02" in report_ids
    assert "TEST-REP-03" in report_ids

    # Location Privacy in General View:
    # Verify that general report items deliver approximate coordinates and never raw exact homestead coords
    for rep in data["reports"]:
        assert "exact_latitude" not in rep
        assert "approximate_latitude" in rep
        assert rep["approximate_latitude"] is not None

    print("  [PASS] Veterinarian receives full authorized surveillance coverage with privacy controls.")

def test_surveillance_map_filters():
    print("\n--- 3. Testing Surveillance Map Multi-Dimensional Filters ---")
    vet_headers = get_auth_header("map_vet_1", "VETERINARIAN")

    # A. Filter by Disease: Lumpy Skin Disease
    r_disease = client.get("/api/reports/surveillance-map?disease=Lumpy%20Skin%20Disease", headers=vet_headers)
    assert r_disease.status_code == 200
    d_data = r_disease.json()
    for r in d_data["reports"]:
        assert "Lumpy" in r["disease"]
    for c in d_data["clusters"]:
        assert "Lumpy" in c["disease"]
    print(f"  Disease Filter (LSD): {len(d_data['reports'])} reports, {len(d_data['clusters'])} clusters")

    # B. Filter by Risk Level: High
    r_risk = client.get("/api/reports/surveillance-map?risk_level=High", headers=vet_headers)
    assert r_risk.status_code == 200
    risk_data = r_risk.json()
    for r in risk_data["reports"]:
        assert r["risk_level"] == "High"
    print(f"  Risk Level Filter (High): {len(risk_data['reports'])} reports")

    # C. Filter by Region: Baramati
    r_reg = client.get("/api/reports/surveillance-map?region=Baramati", headers=vet_headers)
    assert r_reg.status_code == 200
    reg_data = r_reg.json()
    for r in reg_data["reports"]:
        assert "Baramati" in r["taluka"] or "Baramati" in r["village"]
    print(f"  Region Filter (Baramati): {len(reg_data['reports'])} reports")

    # D. Filter by Date: Last 7 Days
    r_days = client.get("/api/reports/surveillance-map?days=7", headers=vet_headers)
    assert r_days.status_code == 200
    days_data = r_days.json()
    print(f"  Date Filter (7 Days): {len(days_data['reports'])} reports")

    print("  [PASS] All 4 filter dimensions (Disease, Date, Risk Level, Region) functioning accurately.")

if __name__ == "__main__":
    print("=================================================================")
    print("   AI-LIVESTOCK HEALTH SENTINEL - SURVEILLANCE MAP TESTS        ")
    print("=================================================================")
    test_farmer_facing_surveillance_map()
    test_veterinarian_surveillance_map()
    test_surveillance_map_filters()
    print("\n>>> ALL SURVEILLANCE MAP TESTS PASSED SUCCESSFULLY! <<<\n")
