"""
Automated Verification Suite for the Transparent Multi-Modal Livestock Health Risk Engine.
Tests:
1. Default configurable weights (Image: 40%, Symptoms: 35%, Environment: 15%, Context: 10%)
2. All 4 risk tiers: Low (0-30), Medium (31-60), High (61-80), Critical (81-100)
3. Custom weight overrides per request
4. Dynamic weight renormalization for partial modalities (e.g. missing image score)
5. Host susceptibility context scoring matrix (vaccination + history)
6. FastAPI endpoints: POST /analysis/multi-modal & POST /api/analysis/multi-modal
7. Ethical non-veterinary diagnosis disclaimers
"""

import sys
import time
from fastapi.testclient import TestClient

from main import app
from services import get_multi_modal_engine

client = TestClient(app)

def test_engine_direct_calculation():
    print("\n--- 1. Testing MultiModalRiskEngine Direct Calculation & Default Weights ---")
    engine = get_multi_modal_engine()
    
    # Inputs
    image_score = 80.0
    symptom_score = 70.0
    env_score = 40.0
    vac_status = "not_vaccinated" # 85.0
    history = "none"              # 5.0
    # Expected context: 0.70*85.0 + 0.30*5.0 = 61.0
    # Expected weighted sum: 80*0.40 (32.0) + 70*0.35 (24.5) + 40*0.15 (6.0) + 61*0.10 (6.1) = 68.6
    
    result = engine.evaluate(
        image_risk_score=image_score,
        symptom_risk_score=symptom_score,
        environmental_risk_score=env_score,
        vaccination_status=vac_status,
        health_history=history
    )
    
    print(f"  Calculated Final Score: {result['final_risk_score']}")
    print(f"  Assigned Risk Level: {result['risk_level']}")
    print(f"  Individual Model Scores: {result['individual_model_scores']}")
    print(f"  Calculation Details: {result['calculation_details']}")
    
    assert abs(result["final_risk_score"] - 68.6) < 0.2, f"Expected ~68.6, got {result['final_risk_score']}"
    assert result["risk_level"] == "High", f"Expected High, got {result['risk_level']}"
    assert len(result["contributing_factors"]) == 4
    
    # Check factor sorting (descending by weighted contribution)
    contributions = [f["weighted_contribution"] for f in result["contributing_factors"]]
    assert contributions == sorted(contributions, reverse=True), "Contributing factors must be sorted descending!"
    
    # Check top factor is Image Risk (32.0)
    top_factor = result["contributing_factors"][0]
    assert top_factor["modality_key"] == "image"
    assert top_factor["weighted_contribution"] == 32.0
    assert abs(top_factor["percentage_of_total_risk"] - (32.0 / 68.6 * 100)) < 0.5
    
    # Verify non-diagnostic boundaries
    assert result["is_veterinary_diagnosis"] is False
    assert "not a veterinary diagnosis" in result["disclaimer"].lower()
    print("  [PASS] Direct calculation with default weights passed.")

def test_risk_level_boundaries():
    print("\n--- 2. Testing All 4 Risk Level Boundaries (Low, Medium, High, Critical) ---")
    engine = get_multi_modal_engine()
    
    # Tier 1: Low (0 - 30)
    res_low = engine.evaluate(
        image_risk_score=15.0, symptom_risk_score=10.0, environmental_risk_score=20.0,
        vaccination_status="vaccinated", health_history="none"
    )
    print(f"  Tier 1 Score: {res_low['final_risk_score']} -> {res_low['risk_level']}")
    assert res_low["final_risk_score"] <= 30.0
    assert res_low["risk_level"] == "Low"
    
    # Tier 2: Medium (31 - 60)
    res_med = engine.evaluate(
        image_risk_score=50.0, symptom_risk_score=45.0, environmental_risk_score=55.0,
        vaccination_status="partially_vaccinated", health_history="none"
    )
    print(f"  Tier 2 Score: {res_med['final_risk_score']} -> {res_med['risk_level']}")
    assert 30.0 < res_med["final_risk_score"] <= 60.0
    assert res_med["risk_level"] == "Medium"
    
    # Tier 3: High (61 - 80)
    res_high = engine.evaluate(
        image_risk_score=75.0, symptom_risk_score=70.0, environmental_risk_score=65.0,
        vaccination_status="overdue", health_history="none"
    )
    print(f"  Tier 3 Score: {res_high['final_risk_score']} -> {res_high['risk_level']}")
    assert 60.0 < res_high["final_risk_score"] <= 80.0
    assert res_high["risk_level"] == "High"
    
    # Tier 4: Critical (81 - 100)
    res_crit = engine.evaluate(
        image_risk_score=95.0, symptom_risk_score=92.0, environmental_risk_score=85.0,
        vaccination_status="not_vaccinated", health_history="past_lsd"
    )
    print(f"  Tier 4 Score: {res_crit['final_risk_score']} -> {res_crit['risk_level']}")
    assert res_crit["final_risk_score"] > 80.0
    assert res_crit["risk_level"] == "Critical"
    
    print("  [PASS] All 4 risk tiers strictly validated.")

def test_custom_weight_overrides():
    print("\n--- 3. Testing Per-Request Custom Weight Overrides ---")
    engine = get_multi_modal_engine()
    
    # Custom weight: Heavy on symptoms (60%) and environmental (40%), ignoring image and context
    custom_w = {
        "image": 0.0,
        "symptoms": 0.60,
        "environment": 0.40,
        "context": 0.0
    }
    
    res = engine.evaluate(
        image_risk_score=100.0,  # Should be ignored (weight 0)
        symptom_risk_score=50.0, # 50 * 0.60 = 30.0
        environmental_risk_score=80.0, # 80 * 0.40 = 32.0
        vaccination_status="not_vaccinated", # context weight 0
        health_history="chronic",
        custom_weights=custom_w
    )
    
    # Expected: 30.0 + 32.0 = 62.0 -> High
    print(f"  Custom Weighted Score: {res['final_risk_score']} -> {res['risk_level']}")
    print(f"  Effective Weights: {res['calculation_details']['effective_weights']}")
    
    assert abs(res["final_risk_score"] - 62.0) < 0.2
    assert res["risk_level"] == "High"
    assert res["calculation_details"]["effective_weights"]["symptoms"] == 0.60
    assert res["calculation_details"]["effective_weights"]["environment"] == 0.40
    print("  [PASS] Custom weight overrides functioning properly.")

def test_dynamic_reweighting_partial_modalities():
    print("\n--- 4. Testing Dynamic Reweighting for Omitted Modalities ---")
    engine = get_multi_modal_engine()
    
    # Scenario: Field worker has NO image (e.g. feature phone or camera failure)
    # Active: Symptoms (base 0.35), Environment (base 0.15), Context (base 0.10)
    # Sum active base = 0.60
    # Normalized weights:
    #   symptoms: 0.35 / 0.60 = 0.5833 (58.33%)
    #   environment: 0.15 / 0.60 = 0.2500 (25.00%)
    #   context: 0.10 / 0.60 = 0.1667 (16.67%)
    
    res = engine.evaluate(
        image_risk_score=None, # Omitted!
        symptom_risk_score=60.0,
        environmental_risk_score=40.0,
        vaccination_status="vaccinated",
        health_history="none"
    )
    
    eff_w = res["calculation_details"]["effective_weights"]
    sum_eff_w = sum(eff_w.values())
    print(f"  Missing Image Handling: Effective weights = {eff_w} (Sum: {sum_eff_w:.4f})")
    print(f"  Final Score: {res['final_risk_score']}, Risk Level: {res['risk_level']}")
    
    assert "image" not in eff_w, "Image should not have an effective weight when omitted"
    assert abs(sum_eff_w - 1.0) < 0.001, "Effective weights must sum to 1.0"
    assert res["calculation_details"]["is_dynamically_renormalized"] is True
    assert res["individual_model_scores"]["image_risk"] is None
    print("  [PASS] Dynamic reweighting cleanly handles missing modalities.")

def test_context_scoring_matrix():
    print("\n--- 5. Testing Health & Vaccination Context Scoring Matrix ---")
    engine = get_multi_modal_engine()
    
    # Vaccinated + Clean history
    ctx_best = engine.calculate_context_risk(vaccination_status="vaccinated", health_history="none")
    print(f"  Best Context (Vaccinated + None): {ctx_best['context_score']}/100")
    assert ctx_best["context_score"] < 15.0
    
    # Unvaccinated + Chronic history
    ctx_worst = engine.calculate_context_risk(vaccination_status="not_vaccinated", health_history="past_lsd, chronic")
    print(f"  Worst Context (Unvaccinated + Chronic LSD): {ctx_worst['context_score']}/100")
    assert ctx_worst["context_score"] > 80.0
    
    # Overdue booster + mild history
    ctx_mid = engine.calculate_context_risk(vaccination_status="overdue", health_history="fever")
    print(f"  Mid Context (Overdue + Past Fever): {ctx_mid['context_score']}/100")
    assert 50.0 <= ctx_mid["context_score"] <= 75.0
    
    print("  [PASS] Context scoring matrix accurately models biological susceptibility.")

def test_api_multi_modal_endpoint():
    print("\n--- 6. Testing FastAPI Multi-Modal Endpoint (POST /analysis/multi-modal) ---")
    payload = {
        "image_risk_score": 78.5,
        "symptom_risk_score": 64.0,
        "environmental_risk_score": 52.0,
        "vaccination_status": "not_vaccinated",
        "health_history": "past_respiratory",
        "custom_weights": {
            "image": 0.40,
            "symptoms": 0.35,
            "environment": 0.15,
            "context": 0.10
        }
    }
    
    t0 = time.time()
    response = client.post("/analysis/multi-modal", json=payload)
    latency_ms = (time.time() - t0) * 1000
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()
    
    print(f"  Endpoint latency: {latency_ms:.2f}ms")
    print(f"  Final Risk Score: {data['final_risk_score']}")
    print(f"  Risk Level: {data['risk_level']}")
    print(f"  Top Contributing Factor: {data['contributing_factors'][0]['factor']} ({data['contributing_factors'][0]['percentage_of_total_risk']}%)")
    print(f"  Individual Model Scores: {data['individual_model_scores']}")
    print(f"  Is Veterinary Diagnosis: {data['is_veterinary_diagnosis']}")
    print(f"  Disclaimer: {data['disclaimer']}")
    
    assert "final_risk_score" in data
    assert data["risk_level"] in ["Low", "Medium", "High", "Critical"]
    assert len(data["contributing_factors"]) == 4
    assert data["is_veterinary_diagnosis"] is False
    assert "not a veterinary diagnosis" in data["disclaimer"].lower()
    
    # Test alias route /api/analysis/multi-modal
    alias_resp = client.post("/api/analysis/multi-modal", json=payload)
    assert alias_resp.status_code == 200
    print("  [PASS] REST API endpoints /analysis/multi-modal & /api/analysis/multi-modal passed.")

if __name__ == "__main__":
    print("=================================================================")
    print("   AI-LIVESTOCK HEALTH SENTINEL - MULTI-MODAL RISK ENGINE TESTS   ")
    print("=================================================================")
    test_engine_direct_calculation()
    test_risk_level_boundaries()
    test_custom_weight_overrides()
    test_dynamic_reweighting_partial_modalities()
    test_context_scoring_matrix()
    test_api_multi_modal_endpoint()
    print("\n>>> ALL MULTI-MODAL RISK ENGINE TESTS PASSED SUCCESSFULLY! <<<\n")
