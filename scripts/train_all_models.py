import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(ROOT_DIR, "ml", "symptom_prediction"))
sys.path.append(os.path.join(ROOT_DIR, "ml", "anomaly"))

print("==================================================")
print("Training AI-Livestock Health Sentinel ML Models")
print("==================================================")

# 1. Train Symptom Classifier
print("\n[1/2] Training Symptom Multi-Disease Classifier (XGBoost / Gradient Boosting)...")
try:
    from train_xgboost import main as train_symptoms
    train_symptoms()
    print("Symptom model training complete.")
except Exception as e:
    print(f"Error training symptom model: {e}")

# 2. Train Vitals Anomaly Detector
print("\n[2/2] Training Isolation Forest Vitals Anomaly Detector...")
try:
    from isolation_forest import train_anomaly_model
    train_anomaly_model()
    print("Anomaly model training complete.")
except Exception as e:
    print(f"Error training anomaly model: {e}")

print("\nAll models trained and checkpoints saved in 'ml/models/'.")
