import os
import sys

# Support UTF-8 output on Windows consoles
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(ROOT_DIR, "backend"))
sys.path.append(os.path.join(ROOT_DIR, "ml", "symptom_prediction"))
sys.path.append(os.path.join(ROOT_DIR, "ml", "image_lsd"))
sys.path.append(os.path.join(ROOT_DIR, "ml", "anomaly"))
sys.path.append(os.path.join(ROOT_DIR, "ml", "outbreak"))
sys.path.append(os.path.join(ROOT_DIR, "ml", "environmental_risk"))

def test_database():
    print("[1/5] Testing Database Connection...")
    from database import db, is_mock_db
    users_count = db["users"].count_documents()
    animals_count = db["animals"].count_documents()
    print(f"  [PASS] Database operational (is_mock_db={is_mock_db}). Found {users_count} users, {animals_count} animals.")
    return True

def test_symptom_ml():
    print("[2/5] Testing Symptom Prediction & SHAP...")
    from predict import predict_symptoms
    from explain import explain_prediction
    
    res = predict_symptoms(
        symptoms=["fever", "skin_abnormalities"],
        age=3,
        breed="Gir",
        gender="Female",
        history="None",
        vaccination="vaccinated"
    )
    assert "possible_disease" in res, "Missing possible_disease in result"
    assert res["risk_score"] > 0, "Risk score should be > 0"
    
    drivers = explain_prediction(
        symptoms=["fever", "skin_abnormalities"],
        age=3,
        breed="Gir",
        gender="Female",
        history="None",
        vaccination="vaccinated"
    )
    assert len(drivers) > 0, "Explainability drivers should not be empty"
    print(f"  [PASS] Symptom ML passed. Predicted: {res['possible_disease']} (Risk: {res['risk_score']}%, Top Driver: {drivers[0]['feature']}).")
    return True

def test_anomaly_detector():
    print("[3/5] Testing Isolation Forest Vitals Anomaly Detector...")
    from isolation_forest import detect_anomaly
    is_normal, _ = detect_anomaly(temperature=38.5, appetite=1.0, milk_production=16.0, activity=1.0)
    is_anom, score = detect_anomaly(temperature=40.8, appetite=0.0, milk_production=2.0, activity=0.0)
    assert not is_normal, "Normal vitals should not be flagged"
    assert is_anom, "Extreme fever + milk drop should be flagged as anomaly"
    print(f"  [PASS] Anomaly Detector passed. Normal correctly cleared, severe vitals drop flagged (score: {score}).")
    return True

def test_environmental_risk():
    print("[4/5] Testing Environmental Vector Risk Engine...")
    from environmental_risk import calculate_environmental_risk
    res = calculate_environmental_risk(temperature_c=31.0, humidity_percent=82.0, rainfall_mm=18.0)
    assert res["environmental_risk_score"] > 50.0, "Warm humid conditions should yield elevated risk score"
    print(f"  [PASS] Environmental Risk passed. Score: {res['environmental_risk_score']} ({res['risk_category']}).")
    return True

def test_outbreak_clustering():
    print("[5/5] Testing DBSCAN Outbreak Clustering...")
    from cluster_detection import detect_outbreak_clusters
    cases_cluster = [
        {"id": "c1", "latitude": 18.520, "longitude": 73.856, "disease": "LSD", "farm_id": "f1", "risk_level": "HIGH", "date": "2026-08-22T10:00:00"},
        {"id": "c2", "latitude": 18.521, "longitude": 73.857, "disease": "LSD", "farm_id": "f2", "risk_level": "HIGH", "date": "2026-08-22T10:10:00"},
        {"id": "c3", "latitude": 18.522, "longitude": 73.858, "disease": "LSD", "farm_id": "f3", "risk_level": "MODERATE", "date": "2026-08-22T10:20:00"}
    ]
    clusters = detect_outbreak_clusters(cases_cluster, eps_km=5.0, min_cases=3, time_window_days=14)
    assert len(clusters) == 1, "DBSCAN should detect exactly 1 cluster for 3 proximal points"
    print(f"  [PASS] Outbreak Clustering passed. Detected cluster with {clusters[0]['cases_count']} cases.")
    return True

if __name__ == "__main__":
    print("==================================================")
    print("Verifying AI-Livestock Health Sentinel System Components")
    print("==================================================")
    try:
        test_database()
        test_symptom_ml()
        test_anomaly_detector()
        test_environmental_risk()
        test_outbreak_clustering()
        print("==================================================")
        print("ALL 5 SYSTEM VERIFICATION TESTS PASSED SUCCESSFULLY! [OK]")
        print("==================================================")
    except Exception as e:
        print(f"\nVerification failed with error: {e}")
        sys.exit(1)
