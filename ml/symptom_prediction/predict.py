import os
import pickle
import numpy as np
from typing import List, Dict, Any, Optional

try:
    from preprocess import encode_input, get_feature_names, DISEASES_LIST
    from explain import explain_prediction
except ImportError:
    from ml.symptom_prediction.preprocess import encode_input, get_feature_names, DISEASES_LIST
    from ml.symptom_prediction.explain import explain_prediction

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "models", "symptom_model.pkl"))

_CACHED_MODEL = None

def load_model():
    global _CACHED_MODEL
    if _CACHED_MODEL is not None:
        return _CACHED_MODEL
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Model file not found at {MODEL_PATH}. Please run training first.")
    with open(MODEL_PATH, "rb") as f:
        _CACHED_MODEL = pickle.load(f)
    return _CACHED_MODEL

def predict_symptoms(
    symptoms: List[str],
    age: float = 4.0,
    breed: str = "gir",
    gender: str = "female",
    history: str = "none",
    vaccination: str = "not_vaccinated",
    low_threshold: float = 30.0,
    high_threshold: float = 70.0
) -> Dict[str, Any]:
    """
    Symptom-based livestock disease risk assessment API.
    
    Returns:
    {
      "possible_conditions": [
        {"disease": str, "probability": float}
      ],
      "risk_level": "LOW" | "MODERATE" | "HIGH",
      "contributing_symptoms": [
        {"symptom": str, "contribution": float}
      ],
      "is_definitive_diagnosis": False,
      "disclaimer": "AI screening tool only..."
    }
    """
    try:
        model = load_model()
    except Exception as e:
        return {
            "possible_conditions": [{"disease": "Unknown", "probability": 0.0}],
            "risk_level": "LOW",
            "contributing_symptoms": [],
            "error": f"Model loading failed: {str(e)}",
            "is_definitive_diagnosis": False,
            "disclaimer": "AI screening and risk triage tool only. Not a veterinary diagnosis."
        }
        
    X_vector = encode_input(symptoms, age, breed, gender, history, vaccination)
    probs = model.predict_proba(X_vector)[0]
    
    # 1. Format ranked possible conditions
    ranked_indices = np.argsort(probs)[::-1]
    possible_conditions = []
    for idx in ranked_indices:
        prob_val = float(round(probs[idx], 4))
        if prob_val >= 0.01: # Filter out negligible probabilities
            possible_conditions.append({
                "disease": DISEASES_LIST[idx],
                "probability": prob_val
            })
            
    top_disease = DISEASES_LIST[ranked_indices[0]]
    top_prob = float(probs[ranked_indices[0]])
    
    # 2. Compute calibrated Risk Score (0 - 100)
    if top_disease == "Healthy":
        # Risk score is inverted probability of healthy
        risk_score = (1.0 - top_prob) * 100.0
        # If second condition has non-trivial probability, elevate risk
        if len(possible_conditions) > 1 and possible_conditions[1]["probability"] >= 0.25:
            risk_score = max(risk_score, possible_conditions[1]["probability"] * 100.0)
    else:
        risk_score = top_prob * 100.0
        
    risk_score = max(0.0, min(100.0, float(round(risk_score, 1))))
    
    # 3. Categorize Risk Level based on configurable thresholds
    if risk_score < low_threshold:
        risk_level = "LOW"
    elif risk_score < high_threshold:
        risk_level = "MODERATE"
    else:
        risk_level = "HIGH"
        
    # 4. Severity Assessment
    active_symptoms_count = sum(1 for s in symptoms if str(s).strip())
    if active_symptoms_count <= 1 and risk_level == "LOW":
        severity = "MILD"
    elif active_symptoms_count <= 3 or risk_level == "MODERATE":
        severity = "MODERATE"
    else:
        severity = "SEVERE"
        
    normalized_symptoms = [s.lower().strip().replace(" ", "_") for s in symptoms]
    if "breathing_difficulty" in normalized_symptoms and risk_level in ["MODERATE", "HIGH"]:
        severity = "SEVERE"
        
    # 5. Extract Contributing Symptoms via SHAP Explainability
    raw_explanations = explain_prediction(symptoms, age, breed, gender, history, vaccination)
    contributing_symptoms = []
    for item in raw_explanations:
        feat = item.get("feature", "")
        # Filter demographic features unless relevant, focus on symptoms
        if any(feat.lower() == s.replace("_", " ") for s in ["fever", "cough", "loss of appetite", "reduced milk production", "nasal discharge", "diarrhea", "breathing difficulty", "skin abnormalities", "swelling", "reduced activity"]):
            contributing_symptoms.append({
                "symptom": feat,
                "contribution": round(float(item.get("contribution", 0.0)), 4)
            })
        elif len(contributing_symptoms) < 3 and feat not in ["Breed", "Gender"]:
            contributing_symptoms.append({
                "symptom": feat,
                "contribution": round(float(item.get("contribution", 0.0)), 4)
            })
            
    return {
        "possible_conditions": possible_conditions,
        "risk_level": risk_level,
        "contributing_symptoms": contributing_symptoms,
        # Backward-compatible fields for existing dashboard routes
        "possible_disease": top_disease,
        "risk_score": risk_score,
        "severity": severity,
        "probabilities": {DISEASES_LIST[i]: round(float(probs[i]) * 100, 1) for i in range(len(DISEASES_LIST))},
        "is_definitive_diagnosis": False,
        "disclaimer": "AI screening and risk triage tool only. Not a veterinary diagnosis. Consult a registered veterinarian for clinical confirmation and prescription."
    }

if __name__ == "__main__":
    test_symptoms = ["skin_abnormalities", "fever", "loss_of_appetite"]
    res = predict_symptoms(test_symptoms, age=4, breed="gir", gender="female")
    import json
    print(json.dumps(res, indent=2))
