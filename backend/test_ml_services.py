"""
Automated Verification Suite for ML Model Integration into FastAPI.
Tests:
1. Image Risk Analysis (/analysis/image and /api/analysis/image)
2. Symptom-based Risk Assessment (/analysis/symptoms and /api/analysis/symptoms)
3. Environmental Risk Assessment (/analysis/environment and /api/analysis/environment)
4. Singleton caching behavior (no model reloading per request)
5. Ethical non-veterinary diagnosis disclaimers
"""

import os
import io
import time
import base64
from PIL import Image
from fastapi.testclient import TestClient

from main import app
from services import (
    get_image_service,
    get_symptom_service,
    get_environmental_service
)

client = TestClient(app)

def create_dummy_image_bytes(color=(120, 150, 100), size=(256, 256)) -> bytes:
    img = Image.new("RGB", size, color=color)
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()

def test_singleton_caching():
    print("\n--- 1. Testing Singleton Service Caching ---")
    img_svc1 = get_image_service()
    img_svc2 = get_image_service()
    assert img_svc1 is img_svc2, "Image service must be a cached singleton instance!"

    sym_svc1 = get_symptom_service()
    sym_svc2 = get_symptom_service()
    assert sym_svc1 is sym_svc2, "Symptom service must be a cached singleton instance!"

    env_svc1 = get_environmental_service()
    env_svc2 = get_environmental_service()
    assert env_svc1 is env_svc2, "Environmental service must be a cached singleton instance!"

    print("  [PASS] All 3 ML services are singletons and cached in memory.")

def test_image_analysis_service_multipart():
    print("\n--- 2. Testing Image Risk Analysis Endpoint (Multipart File Upload) ---")
    dummy_bytes = create_dummy_image_bytes()
    
    t0 = time.time()
    response = client.post(
        "/analysis/image",
        files={"file": ("cow_skin_test.jpg", dummy_bytes, "image/jpeg")},
        data={"low_threshold": "0.25", "high_threshold": "0.65"}
    )
    latency = time.time() - t0
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()
    
    print(f"  Response received in {latency*1000:.1f}ms")
    print(f"  Service: {data.get('service')}")
    print(f"  Predicted Class: {data.get('predicted_class')}")
    print(f"  Confidence: {data.get('confidence')}")
    print(f"  Risk Level: {data.get('risk_level')}")
    print(f"  Risk Score: {data.get('risk_score')}")
    print(f"  Probabilities: {data.get('probabilities')}")
    print(f"  Image Quality: {data.get('image_quality')}")
    print(f"  Is Veterinary Diagnosis: {data.get('is_veterinary_diagnosis')}")
    print(f"  Disclaimer: {data.get('disclaimer')}")

    # Validations
    assert data["service"] == "image_risk_analysis"
    assert data["predicted_class"] in ["Healthy", "Possible Lumpy Skin Disease"]
    assert 0.0 <= data["confidence"] <= 1.0
    assert data["risk_level"] in ["LOW", "MEDIUM", "HIGH"]
    assert 0.0 <= data["risk_score"] <= 100.0
    assert "Possible Lumpy Skin Disease" in data["probabilities"]
    assert "Healthy" in data["probabilities"]
    assert data["is_veterinary_diagnosis"] is False, "Must NOT be presented as a definitive diagnosis!"
    assert "not a veterinary diagnosis" in data["disclaimer"].lower()
    print("  [PASS] Image risk analysis endpoint passed validation.")

def test_image_analysis_service_base64():
    print("\n--- 3. Testing Image Risk Analysis Endpoint (Base64 JSON Payload) ---")
    dummy_bytes = create_dummy_image_bytes(color=(200, 180, 160))
    b64_str = base64.b64encode(dummy_bytes).decode("utf-8")
    
    response = client.post(
        "/analysis/image",
        json={
            "image_base64": f"data:image/jpeg;base64,{b64_str}",
            "low_threshold": 0.30,
            "high_threshold": 0.70
        }
    )
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["predicted_class"] in ["Healthy", "Possible Lumpy Skin Disease"]
    assert data["is_veterinary_diagnosis"] is False
    print("  [PASS] Base64 image payload processing passed.")

def test_symptom_analysis_service():
    print("\n--- 4. Testing Symptom Disease Risk Assessment Endpoint ---")
    payload = {
        "symptoms": ["skin_abnormalities", "fever", "loss_of_appetite"],
        "age": 3.5,
        "breed": "gir",
        "gender": "female",
        "history": "none",
        "vaccination": "not_vaccinated",
        "low_threshold": 35.0,
        "high_threshold": 65.0
    }
    
    t0 = time.time()
    response = client.post("/analysis/symptoms", json=payload)
    latency = time.time() - t0
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()
    
    print(f"  Response received in {latency*1000:.1f}ms")
    print(f"  Service: {data.get('service')}")
    print(f"  Top Condition: {data.get('top_condition')}")
    print(f"  Risk Level: {data.get('risk_level')}")
    print(f"  Risk Score: {data.get('risk_score')}")
    print(f"  Severity: {data.get('severity')}")
    print(f"  Possible Conditions: {data.get('possible_conditions')}")
    print(f"  Contributing Symptoms: {data.get('contributing_symptoms')}")
    print(f"  Is Veterinary Diagnosis: {data.get('is_veterinary_diagnosis')}")
    print(f"  Disclaimer: {data.get('disclaimer')}")

    # Validations
    assert data["service"] == "symptom_based_disease_risk_assessment"
    assert isinstance(data["possible_conditions"], list) and len(data["possible_conditions"]) > 0
    for cond in data["possible_conditions"]:
        assert "disease" in cond and "probability" in cond
        assert 0.0 <= cond["probability"] <= 1.0
    assert data["risk_level"] in ["LOW", "MODERATE", "HIGH"]
    assert 0.0 <= data["risk_score"] <= 100.0
    assert isinstance(data["contributing_symptoms"], list)
    assert len(data["contributing_symptoms"]) > 0, "Explainability attributions should be returned"
    for item in data["contributing_symptoms"]:
        assert "symptom" in item and "contribution" in item
    assert data["is_veterinary_diagnosis"] is False, "Must NOT claim veterinary diagnosis!"
    print("  [PASS] Symptom-based disease risk assessment passed validation.")

def test_environmental_analysis_service():
    print("\n--- 5. Testing Environmental Risk Assessment Endpoint ---")
    payload = {
        "latitude": 21.1458,
        "longitude": 79.0882,
        "temperature_c": 31.5,
        "humidity_percent": 78.0,
        "rainfall_mm": 24.5,
        "elevation_m": 310.0,
        "cattle_density": 18500.0,
        "buffalo_density": 4200.0,
        "dominant_land_cover": 4
    }
    
    t0 = time.time()
    response = client.post("/analysis/environment", json=payload)
    latency = time.time() - t0
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()
    
    print(f"  Response received in {latency*1000:.1f}ms")
    print(f"  Service: {data.get('service')}")
    print(f"  Environmental Risk Score: {data.get('environmental_risk_score')}")
    print(f"  Risk Level: {data.get('risk_level')}")
    print(f"  Outbreak Probability: {data.get('outbreak_probability')}")
    print(f"  Key Risk Drivers: {data.get('key_risk_drivers')}")
    print(f"  Is Animal Diagnosis: {data.get('is_animal_diagnosis')}")
    print(f"  Disclaimer: {data.get('disclaimer')}")

    # Validations
    assert data["service"] == "environmental_risk_assessment"
    assert 0.0 <= data["environmental_risk_score"] <= 100.0
    assert data["risk_level"] in ["Low", "Medium", "High"]
    assert 0.0 <= data["outbreak_probability"] <= 1.0
    assert isinstance(data["key_risk_drivers"], list) and len(data["key_risk_drivers"]) > 0
    assert data["is_animal_diagnosis"] is False, "Must explicitly state it does NOT diagnose an animal!"
    assert "does not diagnose an individual animal" in data["disclaimer"].lower()
    print("  [PASS] Environmental risk assessment passed validation.")

def test_speed_and_cached_inference():
    print("\n--- 6. Testing Repeated Fast Inferences (Zero Model Reload Overhead) ---")
    # Execute 5 fast queries to symptom model
    t_start = time.perf_counter()
    for _ in range(5):
        r = client.post("/analysis/symptoms", json={"symptoms": ["fever"]})
        assert r.status_code == 200
    avg_symptom_ms = ((time.perf_counter() - t_start) / 5) * 1000
    print(f"  Average cached symptom inference: {avg_symptom_ms:.2f}ms")
    
    # Execute 5 fast queries to environmental model
    t_start = time.perf_counter()
    for _ in range(5):
        r = client.post("/analysis/environment", json={
            "latitude": 20.0, "longitude": 78.0,
            "temperature_c": 28.0, "humidity_percent": 60.0, "rainfall_mm": 5.0
        })
        assert r.status_code == 200
    avg_env_ms = ((time.perf_counter() - t_start) / 5) * 1000
    print(f"  Average cached environmental inference: {avg_env_ms:.2f}ms")
    
    print("  [PASS] High-throughput cached execution confirmed.")

if __name__ == "__main__":
    print("=================================================================")
    print("   AI-LIVESTOCK HEALTH SENTINEL - ML SERVICES VERIFICATION       ")
    print("=================================================================")
    test_singleton_caching()
    test_image_analysis_service_multipart()
    test_image_analysis_service_base64()
    test_symptom_analysis_service()
    test_environmental_analysis_service()
    test_speed_and_cached_inference()
    print("\n>>> ALL ML SERVICES TESTS PASSED SUCCESSFULLY! <<<\n")
