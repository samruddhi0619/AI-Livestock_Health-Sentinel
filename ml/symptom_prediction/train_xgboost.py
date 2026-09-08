import os
import pickle
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, roc_auc_score

try:
    from preprocess import SYMPTOMS_LIST, BREEDS_MAP, GENDER_MAP, HISTORY_MAP, VACCINATION_MAP, DISEASES_LIST
except ImportError:
    from ml.symptom_prediction.preprocess import SYMPTOMS_LIST, BREEDS_MAP, GENDER_MAP, HISTORY_MAP, VACCINATION_MAP, DISEASES_LIST

def generate_synthetic_data(num_samples=1200):
    np.random.seed(42)
    data = []
    
    for _ in range(num_samples):
        age = np.random.randint(1, 15)
        breed_name = np.random.choice(list(BREEDS_MAP.keys()))
        breed = BREEDS_MAP[breed_name]
        gender = np.random.choice(list(GENDER_MAP.values()))
        history = np.random.choice(list(HISTORY_MAP.values()), p=[0.7, 0.2, 0.1])
        vaccination = np.random.choice(list(VACCINATION_MAP.values()), p=[0.4, 0.6])
        
        disease_idx = np.random.choice(len(DISEASES_LIST))
        disease = DISEASES_LIST[disease_idx]
        
        symptoms = {s: 0.0 for s in SYMPTOMS_LIST}
        
        if disease == "Healthy":
            for s in SYMPTOMS_LIST:
                if np.random.rand() < 0.05:
                    symptoms[s] = 1.0
        elif disease == "Lumpy Skin Disease":
            symptoms["skin_abnormalities"] = 1.0 if np.random.rand() < 0.95 else 0.0
            symptoms["fever"] = 1.0 if np.random.rand() < 0.8 else 0.0
            symptoms["loss_of_appetite"] = 1.0 if np.random.rand() < 0.7 else 0.0
            symptoms["reduced_milk_production"] = 1.0 if np.random.rand() < 0.6 else 0.0
            symptoms["reduced_activity"] = 1.0 if np.random.rand() < 0.5 else 0.0
        elif disease == "Foot-and-Mouth Disease":
            symptoms["swelling"] = 1.0 if np.random.rand() < 0.9 else 0.0
            symptoms["fever"] = 1.0 if np.random.rand() < 0.85 else 0.0
            symptoms["nasal_discharge"] = 1.0 if np.random.rand() < 0.7 else 0.0
            symptoms["reduced_activity"] = 1.0 if np.random.rand() < 0.8 else 0.0
            symptoms["loss_of_appetite"] = 1.0 if np.random.rand() < 0.75 else 0.0
        elif disease == "Mastitis":
            symptoms["reduced_milk_production"] = 1.0 if np.random.rand() < 0.95 else 0.0
            symptoms["swelling"] = 1.0 if np.random.rand() < 0.9 else 0.0
            symptoms["fever"] = 1.0 if np.random.rand() < 0.6 else 0.0
            symptoms["loss_of_appetite"] = 1.0 if np.random.rand() < 0.5 else 0.0
        elif disease == "Bovine Respiratory Disease":
            symptoms["cough"] = 1.0 if np.random.rand() < 0.9 else 0.0
            symptoms["breathing_difficulty"] = 1.0 if np.random.rand() < 0.85 else 0.0
            symptoms["nasal_discharge"] = 1.0 if np.random.rand() < 0.8 else 0.0
            symptoms["fever"] = 1.0 if np.random.rand() < 0.7 else 0.0
            symptoms["reduced_activity"] = 1.0 if np.random.rand() < 0.6 else 0.0
        elif disease == "Brucellosis":
            symptoms["fever"] = 1.0 if np.random.rand() < 0.7 else 0.0
            symptoms["reduced_milk_production"] = 1.0 if np.random.rand() < 0.6 else 0.0
            symptoms["loss_of_appetite"] = 1.0 if np.random.rand() < 0.5 else 0.0
            symptoms["reduced_activity"] = 1.0 if np.random.rand() < 0.5 else 0.0
            if vaccination == 1:
                symptoms["fever"] = 1.0 if np.random.rand() < 0.3 else 0.0
        
        row = [age, breed, gender, history, vaccination] + [symptoms[s] for s in SYMPTOMS_LIST] + [disease_idx]
        data.append(row)
        
    cols = ["age", "breed", "gender", "history", "vaccination"] + SYMPTOMS_LIST + ["label"]
    return pd.DataFrame(data, columns=cols)

def main():
    print("Generating synthetic cattle disease dataset...")
    df = generate_synthetic_data(1200)
    
    X = df.drop(columns=["label"])
    y = df["label"]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # Check if XGBoost is available, else use GradientBoostingClassifier
    try:
        from xgboost import XGBClassifier
        print("Training XGBoost Classifier...")
        xgb = XGBClassifier(n_estimators=100, learning_rate=0.1, max_depth=4, random_state=42)
        xgb.fit(X_train, y_train)
        model = xgb
        model_type = "XGBoost"
    except ImportError:
        print("XGBoost library not found. Training Scikit-Learn GradientBoostingClassifier as benchmark...")
        gb = GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, max_depth=4, random_state=42)
        gb.fit(X_train, y_train)
        model = gb
        model_type = "GradientBoosting"
        
    print("Training Random Forest Classifier...")
    rf = RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42)
    rf.fit(X_train, y_train)
    
    models_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "models"))
    os.makedirs(models_dir, exist_ok=True)
    
    with open(os.path.join(models_dir, "symptom_model.pkl"), "wb") as f:
        pickle.dump(model, f)
    with open(os.path.join(models_dir, "rf_model.pkl"), "wb") as f:
        pickle.dump(rf, f)
    print(f"Models saved successfully in '{models_dir}'.")
    
    for name, m in [(model_type, model), ("RandomForest", rf)]:
        preds = m.predict(X_test)
        probs = m.predict_proba(X_test)
        acc = accuracy_score(y_test, preds)
        precision, recall, f1, _ = precision_recall_fscore_support(y_test, preds, average='weighted')
        try:
            auc = roc_auc_score(y_test, probs, multi_class='ovr')
        except Exception:
            auc = 0.0
            
        print(f"\n--- {name} Metrics ---")
        print(f"Accuracy:  {acc:.4f}")
        print(f"Precision: {precision:.4f}")
        print(f"Recall:    {recall:.4f}")
        print(f"F1-Score:  {f1:.4f}")
        print(f"ROC-AUC:   {auc:.4f}")

if __name__ == "__main__":
    main()
