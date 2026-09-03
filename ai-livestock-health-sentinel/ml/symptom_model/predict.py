import os
import pickle
import numpy as np
from preprocess import encode_input, get_feature_names, DISEASES_LIST

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "symptom_model.pkl")

def load_model():
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Model file not found at {MODEL_PATH}. Please run training first.")
    with open(MODEL_PATH, "rb") as f:
        return pickle.load(f)

def predict_symptoms(symptoms, age, breed, gender, history, vaccination):
    """
    Predicts disease, risk level, severity, and score from symptom inputs.
    """
    try:
        model = load_model()
    except Exception as e:
        return {
            "error": f"Model loading failed: {str(e)}",
            "possible_disease": "Unknown",
            "risk_score": 0.0,
            "risk_level": "LOW",
            "severity": "MILD"
        }
        
    X_vector = encode_input(symptoms, age, breed, gender, history, vaccination)
    
    # Run prediction
    probs = model.predict_proba(X_vector)[0]
    pred_idx = np.argmax(probs)
    predicted_disease = DISEASES_LIST[pred_idx]
    
    # Calculate risk score based on predicted disease probability
    # If the predicted disease is 'Healthy', the risk score is 100 - healthy_prob
    if predicted_disease == "Healthy":
        risk_score = (1.0 - probs[pred_idx]) * 100.0
        # Re-evaluate disease if risk is moderate/high but primary is healthy
        if risk_score > 40.0:
            # Find the second highest index
            second_idx = np.argsort(probs)[-2]
            predicted_disease = DISEASES_LIST[second_idx]
            risk_score = probs[second_idx] * 100.0
    else:
        risk_score = probs[pred_idx] * 100.0
        
    # Scale risk score to ensure logical range (0 to 100)
    risk_score = max(0.0, min(100.0, float(risk_score)))
    
    # Risk Level mapping
    if risk_score < 40.0:
        risk_level = "LOW"
    elif risk_score < 70.0:
        risk_level = "MODERATE"
    else:
        risk_level = "HIGH"
        
    # Severity mapping (number of positive symptoms)
    active_symptoms_count = sum(1 for s in symptoms if s.strip())
    
    if active_symptoms_count <= 2:
        severity = "MILD"
    elif active_symptoms_count <= 4:
        severity = "MODERATE"
    else:
        severity = "SEVERE"
        
    # Special medical validation: if breathing difficulty is active and risk is moderate/high -> severe
    if "breathing_difficulty" in [s.lower().strip().replace(" ", "_") for s in symptoms] and risk_level in ["MODERATE", "HIGH"]:
        severity = "SEVERE"
        
    return {
        "possible_disease": predicted_disease,
        "risk_score": round(risk_score, 1),
        "risk_level": risk_level,
        "severity": severity,
        "probabilities": {DISEASES_LIST[i]: round(float(probs[i]) * 100, 1) for i in range(len(DISEASES_LIST))}
    }
