import os
import pickle
import numpy as np

try:
    from preprocess import encode_input, get_feature_names, DISEASES_LIST
except ImportError:
    from ml.symptom_prediction.preprocess import encode_input, get_feature_names, DISEASES_LIST

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "models", "symptom_model.pkl"))

def explain_prediction(symptoms, age, breed, gender, history, vaccination):
    """
    Explains model prediction by calculating feature contributions (SHAP values or surrogate weights).
    """
    feature_names = get_feature_names()
    X_vector = encode_input(symptoms, age, breed, gender, history, vaccination)
    
    if not os.path.exists(MODEL_PATH):
        return [{"feature": f, "contribution": 0.0} for f in feature_names[:5]]
        
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)
        
    # Attempt native SHAP TreeExplainer
    try:
        import shap
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X_vector)
        
        probs = model.predict_proba(X_vector)[0]
        pred_idx = int(np.argmax(probs))
        
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
            
        contributions = sorted(contributions, key=lambda x: abs(x["contribution"]), reverse=True)
        return contributions[:5]
        
    except Exception:
        # Fallback to feature importance weighting
        importances = getattr(model, "feature_importances_", None)
        if importances is None:
            importances = np.ones(len(feature_names)) / len(feature_names)
            
        x_flat = X_vector.flatten()
        contributions = []
        
        for i, (name, val) in enumerate(zip(feature_names, x_flat)):
            if i < 5 or val > 0.0:
                importance = importances[i]
                factor = val if i >= 5 else (val / 10.0 if name == "age" else 1.0)
                contribution_score = float(importance * factor)
                if contribution_score > 0:
                    contributions.append({
                        "feature": name.replace("_", " ").title(),
                        "contribution": round(contribution_score, 4)
                    })
                    
        contributions = sorted(contributions, key=lambda x: x["contribution"], reverse=True)
        if not contributions:
            contributions = [{"feature": "Symptom Pattern", "contribution": 0.1}]
            
        return contributions[:5]
