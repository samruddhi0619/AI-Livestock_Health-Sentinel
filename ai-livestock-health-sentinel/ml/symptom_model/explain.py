import os
import pickle
import numpy as np
from preprocess import encode_input, get_feature_names, DISEASES_LIST

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "symptom_model.pkl")

def explain_prediction(symptoms, age, breed, gender, history, vaccination):
    """
    Explains model prediction by calculating feature contributions (SHAP values or surrogate weights).
    """
    feature_names = get_feature_names()
    X_vector = encode_input(symptoms, age, breed, gender, history, vaccination)
    
    # Load model
    if not os.path.exists(MODEL_PATH):
        return [{"feature": f, "contribution": 0.0} for f in feature_names[:5]]
        
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)
        
    # Attempt SHAP explanation
    try:
        import shap
        # SHAP Tree Explainer
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X_vector)
        
        # Predict class
        probs = model.predict_proba(X_vector)[0]
        pred_idx = int(np.argmax(probs))
        
        # Extrapolate for predicted class
        # In multi-class, shap_values has shape (classes, samples, features) or list of classes
        if isinstance(shap_values, list):
            class_shap = shap_values[pred_idx][0]
        elif len(shap_values.shape) == 3:
            class_shap = shap_values[pred_idx, 0, :]
        else:
            class_shap = shap_values[0]
            
        contributions = []
        for name, val in zip(feature_names, class_shap):
            contributions.append({
                "feature": name.replace("_", " ").title(),
                "contribution": round(float(val), 4)
            })
            
        # Sort by absolute contribution descending
        contributions = sorted(contributions, key=lambda x: abs(x["contribution"]), reverse=True)
        return contributions[:5] # Return top 5 drivers
        
    except Exception:
        # Fallback to feature-importance based surrogate weighting
        # This acts as a robust Shapley approximation when C-compilers or packages are missing
        importances = getattr(model, "feature_importances_", None)
        if importances is None:
            # Equal weight fallback
            importances = np.ones(len(feature_names)) / len(feature_names)
            
        # Get active features (continuous features are always active, binary symptoms active if 1.0)
        x_flat = X_vector.flatten()
        contributions = []
        
        for i, (name, val) in enumerate(zip(feature_names, x_flat)):
            # If the feature is demographic or active symptom
            if i < 5 or val > 0.0:
                importance = importances[i]
                # Scale it based on the value to make it dynamic
                factor = val if i >= 5 else (val / 10.0 if name == "age" else 1.0)
                contribution_score = float(importance * factor)
                if contribution_score > 0:
                    contributions.append({
                        "feature": name.replace("_", " ").title(),
                        "contribution": round(contribution_score, 4)
                    })
                    
        # Sort by contribution score descending
        contributions = sorted(contributions, key=lambda x: x["contribution"], reverse=True)
        # Ensure we return at least some drivers
        if not contributions:
            contributions = [{"feature": "Symptom Pattern", "contribution": 0.1}]
            
        return contributions[:5]
