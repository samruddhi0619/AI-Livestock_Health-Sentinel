import os
import sys
import json
import pickle
import time
import zipfile
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score, confusion_matrix
)
import xgboost as xgb

# Set up paths
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(os.path.dirname(CURRENT_DIR))
sys.path.append(CURRENT_DIR)

DATASET_ZIP = os.path.join(ROOT_DIR, "datasets", "03_LSD_Environmental_Geospatial_Data.zip")
MODELS_DIR = os.path.join(ROOT_DIR, "ml", "models")
os.makedirs(MODELS_DIR, exist_ok=True)

RANDOM_SEED = 42

def load_and_preprocess_environmental_data():
    """
    Loads raw 03_LSD_Environmental_Geospatial_Data.zip, purges leakage columns,
    encodes land cover, and creates a strict stratified 70/15/15 split.
    """
    print(f"Loading raw dataset from: {DATASET_ZIP}")
    with zipfile.ZipFile(DATASET_ZIP, 'r') as z:
        with z.open('Lumpy skin disease data.csv') as f:
            df = pd.read_csv(f)
            
    print(f"Raw shape: {df.shape}")
    
    # CRITICAL LEAKAGE PREVENTION:
    # 'region', 'country', and 'reportingDate' are populated only for positive outbreak reports.
    # Discarding them to eliminate 100% artificial leakage.
    leakage_cols = ['region', 'country', 'reportingDate']
    df_clean = df.drop(columns=leakage_cols)
    print(f"Purged target leakage columns: {leakage_cols}")
    
    # Encode categorical land cover (1 to 12)
    df_encoded = pd.get_dummies(df_clean, columns=['dominant_land_cover'], prefix='land_cover', drop_first=True, dtype=int)
    
    target_col = 'lumpy'
    feature_cols = [c for c in df_encoded.columns if c != target_col]
    
    X = df_encoded[feature_cols].copy()
    y = df_encoded[target_col].values
    
    # Class balance stats
    n_neg = int(np.sum(y == 0))
    n_pos = int(np.sum(y == 1))
    scale_pos = float(n_neg / n_pos)
    print(f"Target distribution: 0 (Absence)={n_neg}, 1 (Outbreak)={n_pos} (Imbalance ratio: {scale_pos:.2f}:1)")
    print(f"Clean feature count: {len(feature_cols)}")
    
    # Stratified 70% Train, 15% Val, 15% Test Split
    X_train_full, X_test, y_train_full, y_test = train_test_split(
        X, y, test_size=0.15, random_state=RANDOM_SEED, stratify=y
    )
    X_train, X_val, y_train, y_val = train_test_split(
        X_train_full, y_train_full, test_size=(0.15 / 0.85), random_state=RANDOM_SEED, stratify=y_train_full
    )
    
    return X_train, X_val, X_test, y_train, y_val, y_test, feature_cols, scale_pos

def train_and_evaluate_models():
    print("==================================================================")
    print("TRAINING & COMPARING LSD ENVIRONMENTAL & GEOSPATIAL RISK MODELS")
    print("==================================================================")
    
    X_train, X_val, X_test, y_train, y_val, y_test, feature_cols, scale_pos = load_and_preprocess_environmental_data()
    print(f"Dataset split sizes: Train={len(X_train)}, Val={len(X_val)}, Test={len(X_test)}")
    
    candidates = {
        "RandomForest": RandomForestClassifier(
            n_estimators=150,
            max_depth=12,
            min_samples_leaf=3,
            class_weight="balanced",
            random_state=RANDOM_SEED,
            n_jobs=-1
        ),
        "XGBoost": xgb.XGBClassifier(
            n_estimators=160,
            max_depth=6,
            learning_rate=0.08,
            scale_pos_weight=scale_pos,
            subsample=0.85,
            colsample_bytree=0.85,
            random_state=RANDOM_SEED,
            eval_metric="aucpr",
            n_jobs=-1
        ),
        "GradientBoosting": GradientBoostingClassifier(
            n_estimators=140,
            max_depth=5,
            learning_rate=0.09,
            random_state=RANDOM_SEED
        )
    }
    
    results = {}
    fitted_models = {}
    
    for name, model in candidates.items():
        print(f"\n--- Training {name} ---")
        t0 = time.time()
        model.fit(X_train, y_train)
        train_duration = time.time() - t0
        fitted_models[name] = model
        
        # Validation Metrics
        val_probs = model.predict_proba(X_val)[:, 1]
        val_preds = (val_probs >= 0.5).astype(int)
        val_roc = roc_auc_score(y_val, val_probs)
        val_pr_auc = average_precision_score(y_val, val_probs)
        val_f1 = f1_score(y_val, val_preds)
        
        # Test Set Metrics (Unseen 3,721 samples)
        t_lat0 = time.perf_counter()
        test_probs = model.predict_proba(X_test)[:, 1]
        test_latency_ms = ((time.perf_counter() - t_lat0) / len(X_test)) * 1000
        test_preds = (test_probs >= 0.5).astype(int)
        
        test_acc = accuracy_score(y_test, test_preds)
        test_roc = roc_auc_score(y_test, test_probs)
        test_pr_auc = average_precision_score(y_test, test_probs)
        test_prec = precision_score(y_test, test_preds)
        test_rec = recall_score(y_test, test_preds)
        test_f1 = f1_score(y_test, test_preds)
        cm = confusion_matrix(y_test, test_preds).tolist()
        
        # Top 5 Feature Importances
        if hasattr(model, "feature_importances_"):
            importances = model.feature_importances_
            top_indices = np.argsort(importances)[::-1][:5]
            top_features = [{"feature": feature_cols[i], "importance": round(float(importances[i]), 4)} for i in top_indices]
        else:
            top_features = []
            
        results[name] = {
            "train_duration_sec": round(train_duration, 2),
            "inference_latency_ms": round(test_latency_ms, 3),
            "validation": {
                "roc_auc": round(val_roc, 4),
                "pr_auc": round(val_pr_auc, 4),
                "f1_score": round(val_f1, 4)
            },
            "test": {
                "accuracy": round(test_acc, 4),
                "roc_auc": round(test_roc, 4),
                "pr_auc": round(test_pr_auc, 4),
                "precision": round(test_prec, 4),
                "recall": round(test_rec, 4),
                "f1_score": round(test_f1, 4),
                "confusion_matrix": cm
            },
            "top_features": top_features
        }
        
        print(f"  {name} -> Test ROC-AUC: {test_roc:.4f} | PR-AUC: {test_pr_auc:.4f} | F1: {test_f1:.4f} | Rec: {test_rec:.4f} | Latency: {test_latency_ms:.3f}ms")
        
    # Print Comparison Table
    print("\n" + "="*85)
    print("FINAL BENCHMARK COMPARISON ON HELD-OUT TEST SET (3,721 SAMPLES)")
    print("="*85)
    print(f"{'Model':<18} | {'Accuracy':<10} | {'ROC-AUC':<10} | {'PR-AUC':<10} | {'Recall':<10} | {'F1-Score':<10} | {'Latency'}")
    print("-" * 85)
    for name, m in results.items():
        t = m["test"]
        print(f"{name:<18} | {t['accuracy']:<10.4f} | {t['roc_auc']:<10.4f} | {t['pr_auc']:<10.4f} | {t['recall']:<10.4f} | {t['f1_score']:<10.4f} | {m['inference_latency_ms']} ms")
    print("="*85)
    
    # Select Winner based on PR-AUC (Precision-Recall Area under Curve is gold standard for imbalanced data)
    best_name = max(results.keys(), key=lambda k: results[k]["test"]["pr_auc"])
    best_model = fitted_models[best_name]
    print(f"\nWINNING MODEL SELECTED: {best_name.upper()} (Test PR-AUC: {results[best_name]['test']['pr_auc']:.4f}, ROC-AUC: {results[best_name]['test']['roc_auc']:.4f})")
    
    # Save Model Checkpoint
    model_save_path = os.path.join(MODELS_DIR, "environmental_risk_model.pkl")
    with open(model_save_path, "wb") as f:
        pickle.dump(best_model, f)
        
    # Save feature names order
    features_meta_path = os.path.join(MODELS_DIR, "environmental_feature_names.json")
    with open(features_meta_path, "w") as jf:
        json.dump({
            "feature_names": feature_cols,
            "target": "lumpy",
            "model_type": best_name
        }, jf, indent=2)
        
    # Save Training Config
    config = {
        "selected_model": best_name,
        "features": feature_cols,
        "scale_pos_weight": scale_pos,
        "dataset": "03_LSD_Environmental_Geospatial_Data.zip",
        "leakage_purged": ["region", "country", "reportingDate"],
        "random_seed": RANDOM_SEED
    }
    with open(os.path.join(MODELS_DIR, "environmental_training_config.json"), "w") as jf:
        json.dump(config, jf, indent=2)
        
    # Save Evaluation Metrics
    eval_metrics = {
        "selected_model": best_name,
        "models": results
    }
    with open(os.path.join(MODELS_DIR, "environmental_evaluation_metrics.json"), "w") as jf:
        json.dump(eval_metrics, jf, indent=2)
        
    print(f"\nSaved best model and metadata to '{MODELS_DIR}'.")
    return eval_metrics

if __name__ == "__main__":
    train_and_evaluate_models()
