import os
import sys
import pickle
import time
from typing import List, Dict, Any, Optional
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_DIR = os.path.dirname(BASE_DIR)

# Include ml/symptom_prediction in sys.path
ML_SYMPTOM_DIR = os.path.join(ROOT_DIR, "ml", "symptom_prediction")
if ML_SYMPTOM_DIR not in sys.path:
    sys.path.insert(0, ML_SYMPTOM_DIR)

from preprocess import SYMPTOMS_LIST, BREEDS_MAP, GENDER_MAP, HISTORY_MAP, VACCINATION_MAP, DISEASES_LIST, encode_input, get_feature_names

MODEL_CHECKPOINT_PATH = os.path.join(ROOT_DIR, "ml", "models", "symptom_model.pkl")

class SymptomRiskService:
    """
    Dedicated Tabular Machine Learning Service for multi-disease risk assessment.
    Maintains an in-memory cached XGBoost classifier and SHAP TreeExplainer.
    """
    _instance: Optional["SymptomRiskService"] = None

    def __init__(self):
        self._model = None
        self._explainer = None
        self._feature_names = get_feature_names()
        self._load_model_once()

    @classmethod
    def get_instance(cls) -> "SymptomRiskService":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _load_model_once(self):
        """Loads and caches the XGBoost symptom model and SHAP explainer once."""
        if self._model is not None:
            return
            
        t0 = time.time()
        if os.path.exists(MODEL_CHECKPOINT_PATH):
            try:
                print(f"[SYMPTOM SERVICE] Loading symptom model from {MODEL_CHECKPOINT_PATH}...")
                with open(MODEL_CHECKPOINT_PATH, "rb") as f:
                    self._model = pickle.load(f)
                    
                # Initialize SHAP TreeExplainer for instantaneous local attributions
                try:
                    import shap
                    self._explainer = shap.TreeExplainer(self._model)
                    print("[SYMPTOM SERVICE] SHAP TreeExplainer initialized and cached.")
                except Exception as e:
                    print(f"[SYMPTOM SERVICE] Notice: SHAP TreeExplainer fallback: {e}")
                    self._explainer = None
                    
                load_time = time.time() - t0
                print(f"[SYMPTOM SERVICE] Model loaded and cached successfully in {load_time:.2f}s.")
            except Exception as exc:
                print(f"[SYMPTOM SERVICE] Error loading symptom model: {exc}")
                self._model = None
        else:
            print(f"[SYMPTOM SERVICE] Warning: Model checkpoint not found at {MODEL_CHECKPOINT_PATH}.")

    def analyze_symptoms(
        self,
        symptoms: List[str],
        age: float = 4.0,
        breed: str = "gir",
        gender: str = "female",
        history: str = "none",
        vaccination: str = "not_vaccinated",
        low_threshold: float = 35.0,
        high_threshold: float = 65.0
    ) -> Dict[str, Any]:
        """
        Executes independent multi-disease risk assessment and SHAP explainability.
        """
        t0 = time.perf_counter()
        
        if self._model is None:
            self._load_model_once()
            if self._model is None:
                raise RuntimeError("Symptom model checkpoint is not available. Please verify model training.")
                
        # 1. Encode demographic & symptom vector
        X_vec = encode_input(symptoms, age, breed, gender, history, vaccination)
        
        # 2. Multi-class prediction (Reuses cached model in memory)
        probs = self._model.predict_proba(X_vec)[0]
        latency_ms = round((time.perf_counter() - t0) * 1000, 3)
        
        # 3. Format ranked conditions
        ranked_indices = np.argsort(probs)[::-1]
        possible_conditions = []
        for idx in ranked_indices:
            p_val = float(round(probs[idx], 4))
            if p_val >= 0.01:
                possible_conditions.append({
                    "disease": DISEASES_LIST[idx],
                    "probability": p_val
                })
                
        top_idx = ranked_indices[0]
        top_disease = DISEASES_LIST[top_idx]
        top_prob = float(probs[top_idx])
        
        # 4. Calibrated risk score
        if top_disease == "Healthy":
            risk_score = (1.0 - top_prob) * 100.0
            if len(possible_conditions) > 1 and possible_conditions[1]["probability"] >= 0.25:
                risk_score = max(risk_score, possible_conditions[1]["probability"] * 100.0)
        else:
            risk_score = top_prob * 100.0
            
        risk_score = max(0.0, min(100.0, float(round(risk_score, 1))))
        
        # 5. Determine Risk Tier
        if risk_score < low_threshold:
            risk_level = "LOW"
        elif risk_score < high_threshold:
            risk_level = "MODERATE"
        else:
            risk_level = "HIGH"
            
        # 6. Clinical Severity estimation
        active_count = sum(1 for s in symptoms if str(s).strip())
        if active_count <= 1 and risk_level == "LOW":
            severity = "MILD"
        elif active_count <= 3 or risk_level == "MODERATE":
            severity = "MODERATE"
        else:
            severity = "SEVERE"
            
        normalized_symptoms = [s.lower().strip().replace(" ", "_") for s in symptoms]
        if "breathing_difficulty" in normalized_symptoms and risk_level in ["MODERATE", "HIGH"]:
            severity = "SEVERE"
            
        # 7. Compute Feature Contributions via SHAP Explainer
        contributing_symptoms = self._compute_contributions(X_vec, top_idx)
        
        return {
            "service": "symptom_based_disease_risk_assessment",
            "possible_conditions": possible_conditions,
            "top_condition": top_disease,
            "risk_level": risk_level,
            "risk_score": risk_score,
            "severity": severity,
            "contributing_symptoms": contributing_symptoms,
            "probabilities": {
                DISEASES_LIST[i]: round(float(probs[i]) * 100.0, 1)
                for i in range(len(DISEASES_LIST))
            },
            "risk_thresholds": {
                "low_threshold": low_threshold,
                "high_threshold": high_threshold
            },
            "model_metadata": {
                "architecture": "XGBoost Multi-Class Classifier",
                "checkpoint": "ml/models/symptom_model.pkl",
                "framework": "XGBoost + SHAP TreeExplainer",
                "inference_latency_ms": latency_ms
            },
            # Mandatory Ethical Non-Diagnosis Disclaimer
            "is_veterinary_diagnosis": False,
            "disclaimer": (
                "AI screening and risk triage tool only. Not a veterinary diagnosis. "
                "Consult a registered veterinarian for clinical confirmation and prescription."
            )
        }

    def _compute_contributions(self, X_vec: np.ndarray, pred_idx: int) -> List[Dict[str, Any]]:
        """Computes top contributing symptoms using SHAP or feature importance surrogate."""
        if self._explainer is not None:
            try:
                shap_vals = self._explainer.shap_values(X_vec)
                if isinstance(shap_vals, list):
                    class_shap = shap_vals[pred_idx][0]
                elif len(shap_vals.shape) == 3:
                    class_shap = shap_vals[pred_idx, 0, :]
                else:
                    class_shap = shap_vals[0]
                    
                contributions = []
                for name, val in zip(self._feature_names, class_shap):
                    clean_name = name.replace("_", " ").title()
                    # Focus on active symptom contributions
                    if name in SYMPTOMS_LIST:
                        contributions.append({
                            "symptom": clean_name,
                            "contribution": round(float(val), 4)
                        })
                        
                # Sort positive drivers descending
                contributions = sorted(contributions, key=lambda x: x["contribution"], reverse=True)
                return [c for c in contributions if c["contribution"] > 0][:5]
            except Exception:
                pass
                
        # Surrogate fallback
        importances = getattr(self._model, "feature_importances_", None)
        if importances is None:
            return [{"symptom": "Reported Clinical Signs", "contribution": 0.5}]
            
        x_flat = X_vec.flatten()
        contributions = []
        for i, (name, val) in enumerate(zip(self._feature_names, x_flat)):
            if name in SYMPTOMS_LIST and val > 0.0:
                contributions.append({
                    "symptom": name.replace("_", " ").title(),
                    "contribution": round(float(importances[i]), 4)
                })
        contributions = sorted(contributions, key=lambda x: x["contribution"], reverse=True)
        return contributions[:5] if contributions else [{"symptom": "Reported Clinical Signs", "contribution": 0.1}]

def get_symptom_service() -> SymptomRiskService:
    return SymptomRiskService.get_instance()
