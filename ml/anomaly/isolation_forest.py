import os
import pickle
import numpy as np
from sklearn.ensemble import IsolationForest

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "anomaly_model.pkl")

def generate_normal_health_data(num_samples=500):
    np.random.seed(42)
    # Normal Cattle Baseline parameters:
    # Temperature: 38.0 - 39.5 C
    # Appetite: 1 (Normal) or 2 (High)
    # Milk Production: 12 - 25 Liters/day (for lactating cattle)
    # Activity: 1 (Normal) or 2 (High)
    
    temps = np.random.uniform(38.0, 39.5, num_samples)
    appetites = np.random.choice([1.0, 2.0], size=num_samples, p=[0.8, 0.2])
    milk = np.random.uniform(12.0, 25.0, size=num_samples)
    activities = np.random.choice([1.0, 2.0], size=num_samples, p=[0.8, 0.2])
    
    return np.column_stack((temps, appetites, milk, activities))

def train_anomaly_model():
    """
    Trains an Isolation Forest on normal baseline cattle data to flag outliers.
    """
    X_normal = generate_normal_health_data()
    
    # Contamination set to 5% for prototype
    model = IsolationForest(contamination=0.05, random_state=42)
    model.fit(X_normal)
    
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)
    print("Isolation Forest anomaly model trained and saved successfully.")

def detect_anomaly(temperature, appetite, milk_production, activity):
    """
    Detects if the inputs constitute an abnormal health pattern.
    Returns: (is_anomaly, anomaly_score)
    """
    if not os.path.exists(MODEL_PATH):
        try:
            train_anomaly_model()
        except Exception:
            # Fallback heuristic if training fails
            is_anom = float(temperature) > 40.0 or float(temperature) < 37.0 or float(milk_production) < 5.0 or float(activity) == 0.0
            return is_anom, 0.8 if is_anom else 0.1
            
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)
        
    X_input = np.array([[float(temperature), float(appetite), float(milk_production), float(activity)]])
    
    # IsolationForest outputs -1 for anomalies and 1 for inliers
    pred = model.predict(X_input)[0]
    score = model.score_samples(X_input)[0] # Raw score in [-1.0, 0.0] (lower is more anomalous)
    
    # Map raw score to positive factor (0.0 to 1.0, higher is more anomalous)
    # Since score is negative, -score gives direct range [0.0, 1.0]
    anomaly_factor = float(-score)
    
    is_anomaly = bool(pred == -1 or anomaly_factor > 0.6)
    
    # Double check: absolute medical safety overrides
    # If temp is extremely high or milk production drops by 70%, it is a definite anomaly
    if float(temperature) > 40.2 or float(temperature) < 37.2 or float(milk_production) < 4.0:
        is_anomaly = True
        anomaly_factor = max(anomaly_factor, 0.75)
        
    return is_anomaly, round(anomaly_factor, 2)

if __name__ == "__main__":
    train_anomaly_model()
