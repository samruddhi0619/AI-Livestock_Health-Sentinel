import os
import json
import pickle
import numpy as np
from typing import Dict, Any, Optional

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(os.path.dirname(BASE_DIR))
MODEL_PATH = os.path.join(ROOT_DIR, "ml", "models", "environmental_risk_model.pkl")
FEATURES_PATH = os.path.join(ROOT_DIR, "ml", "models", "environmental_feature_names.json")

_CACHED_MODEL = None
_CACHED_FEATURES = None

def load_environmental_model():
    global _CACHED_MODEL, _CACHED_FEATURES
    if _CACHED_MODEL is not None and _CACHED_FEATURES is not None:
        return _CACHED_MODEL, _CACHED_FEATURES
        
    if not os.path.exists(MODEL_PATH) or not os.path.exists(FEATURES_PATH):
        return None, None
        
    with open(MODEL_PATH, "rb") as f:
        _CACHED_MODEL = pickle.load(f)
    with open(FEATURES_PATH, "r") as f:
        meta = json.load(f)
        _CACHED_FEATURES = meta.get("feature_names", [])
        
    return _CACHED_MODEL, _CACHED_FEATURES

def calibrate_outbreak_risk_score(prob: float, baseline_prior: float = 0.1225) -> float:
    """
    Calibrates ecological presence-absence probability (where background prior is 12.25%)
    into a standardized epidemiological risk index between 0.0 and 100.0.
    """
    prob = max(1e-4, min(1.0 - 1e-4, float(prob)))
    odds_ratio = (prob / (1.0 - prob)) / (baseline_prior / (1.0 - baseline_prior))
    calibrated = 100.0 / (1.0 + np.exp(-1.2 * np.log(odds_ratio + 1e-6) + 0.2))
    return float(round(max(0.0, min(100.0, calibrated)), 1))

def calculate_meteorological_suitability(temp_c: float, humidity_pct: float, rainfall_mm: float) -> float:
    """
    Computes entomological suitability index for Stomoxys and biting insect vector breeding.
    """
    temp = float(temp_c)
    humidity = float(humidity_pct)
    rain = float(rainfall_mm)
    
    # 1. Temperature suitability score (optimal 25 - 33 C for biting flies)
    if 24.0 <= temp <= 35.0:
        temp_factor = 1.0 - (abs(temp - 30.0) / 15.0)
    elif temp > 35.0:
        temp_factor = max(0.2, 1.0 - ((temp - 35.0) / 10.0))
    else:
        temp_factor = max(0.1, (temp - 10.0) / 14.0)
    temp_factor = max(0.0, min(1.0, temp_factor))
    
    # 2. Humidity suitability score (>70% extends vector adult lifespan)
    if humidity >= 70.0:
        humidity_factor = min(1.0, 0.7 + ((humidity - 70.0) / 100.0))
    elif humidity >= 50.0:
        humidity_factor = 0.4 + ((humidity - 50.0) / 60.0)
    else:
        humidity_factor = max(0.1, humidity / 125.0)
    humidity_factor = max(0.0, min(1.0, humidity_factor))
    
    # 3. Rainfall / surface water pooling suitability
    if rain > 15.0:
        rain_factor = 0.95
    elif rain > 5.0:
        rain_factor = 0.70
    elif rain > 0.0:
        rain_factor = 0.40
    else:
        rain_factor = 0.20
        
    meteo_score = (0.35 * temp_factor + 0.40 * humidity_factor + 0.25 * rain_factor) * 100.0
    return float(meteo_score)

def predict_environmental_risk(
    latitude: float = 20.59,
    longitude: float = 78.96,
    temperature_c: float = 28.0,
    humidity_percent: float = 65.0,
    rainfall_mm: float = 20.0,
    elevation_m: float = 180.0,
    cattle_density: float = 15000.0,
    buffalo_density: float = 3000.0,
    dominant_land_cover: int = 4
) -> Dict[str, Any]:
    """
    Estimates regional environmental and geospatial risk of Lumpy Skin Disease (LSD) outbreak.
    
    IMPORTANT: This model estimates regional ecological and vector transmission vulnerability.
    It DOES NOT diagnose an individual animal.
    
    Returns:
    {
      "environmental_risk_score": float (0.0 to 100.0),
      "risk_level": "Low" | "Medium" | "High",
      "outbreak_probability": float (0.0 to 1.0),
      "location": {"latitude": float, "longitude": float},
      "environmental_factors": dict,
      "key_risk_drivers": list of str,
      "is_animal_diagnosis": False,
      "disclaimer": "This score estimates regional environmental disease risk..."
    }
    """
    model, feature_names = load_environmental_model()
    
    # 1. Derive climatic variables from meteorological inputs
    tmp = float(temperature_c)
    tmn = max(5.0, tmp - 6.0)
    tmx = tmp + 6.0
    dtr = tmx - tmn
    pre = float(rainfall_mm) * 3.0
    wet = min(30.0, pre / 8.0)
    
    # Clausius-Clapeyron saturation vapor pressure
    es = 6.112 * np.exp((17.67 * tmp) / (tmp + 243.5))
    vap = float(es * (humidity_percent / 100.0))
    cld = min(100.0, max(10.0, humidity_percent * 0.8))
    frs = 0.0 if tmn > 2.0 else max(0.0, (2.0 - tmn) * 2.0)
    pet = max(1.0, 0.013 * (tmp + 10.0) * es)
    
    # 2. Build feature vector
    raw_feature_dict = {
        "x": float(longitude),
        "y": float(latitude),
        "cld": cld,
        "dtr": dtr,
        "frs": frs,
        "pet": pet,
        "pre": pre,
        "tmn": tmn,
        "tmp": tmp,
        "tmx": tmx,
        "vap": vap,
        "wet": wet,
        "elevation": float(elevation_m),
        "X5_Ct_2010_Da": float(cattle_density),
        "X5_Bf_2010_Da": float(buffalo_density)
    }
    
    for c_idx in range(2, 13):
        col_name = f"land_cover_{c_idx}"
        raw_feature_dict[col_name] = 1 if dominant_land_cover == c_idx else 0
        
    # 3. Model Inference & Meteorological Fusion
    meteo_score = calculate_meteorological_suitability(temperature_c, humidity_percent, rainfall_mm)
    
    if model is not None and feature_names is not None:
        X_vec = np.array([raw_feature_dict.get(fn, 0.0) for fn in feature_names]).reshape(1, -1)
        probs = model.predict_proba(X_vec)[0]
        outbreak_prob = float(round(probs[1], 4))
        ml_score = calibrate_outbreak_risk_score(outbreak_prob)
        # Fuse geospatial presence-absence prediction with real-time meteorological factor
        combined_score = (0.40 * ml_score) + (0.60 * meteo_score)
    else:
        outbreak_prob = float(round(meteo_score / 100.0, 4))
        combined_score = meteo_score
        
    risk_score = max(0.0, min(100.0, float(round(combined_score, 1))))
    
    # 4. Output: Low / Medium / High environmental risk
    if risk_score < 35.0:
        risk_level = "Low"
    elif risk_score < 65.0:
        risk_level = "Medium"
    else:
        risk_level = "High"
        
    # 5. Key Risk Drivers
    drivers = []
    if pre > 40.0 or rainfall_mm > 10.0:
        drivers.append(f"Elevated precipitation ({rainfall_mm:.1f} mm) facilitates stagnant water pooling for biting vectors")
    if 24.0 <= tmp <= 35.0:
        drivers.append(f"Mean temperature ({tmp:.1f}°C) resides in the peak viral transmission range for Stomoxys flies")
    if humidity_percent >= 70.0:
        drivers.append(f"High relative humidity ({humidity_percent:.1f}%) extends vector lifespan and reproductive rate")
    if cattle_density > 15000.0:
        drivers.append(f"High local bovine host density ({cattle_density:,.0f} head/km²) increases mechanical transmission probability")
    if frs == 0.0:
        drivers.append("Absence of frost days permits uninterrupted overwintering of vector colonies")
    if elevation_m > 1500.0:
        drivers.append(f"High elevation ({elevation_m:.0f} m) acts as a natural climatic barrier to vector proliferation")
    if not drivers:
        drivers.append("Ambient weather, elevation, and vector-breeding factors reside within baseline endemic limits")
        
    return {
        "environmental_risk_score": risk_score,
        "risk_level": risk_level,
        "outbreak_probability": outbreak_prob,
        "location": {
            "latitude": round(float(latitude), 4),
            "longitude": round(float(longitude), 4)
        },
        "environmental_factors": {
            "temperature_c": round(float(temperature_c), 1),
            "humidity_percent": round(float(humidity_percent), 1),
            "rainfall_mm": round(float(rainfall_mm), 1),
            "elevation_m": round(float(elevation_m), 1),
            "cattle_density_km2": round(float(cattle_density), 1)
        },
        "key_risk_drivers": drivers,
        "is_animal_diagnosis": False,
        "disclaimer": "This score estimates regional environmental and vector-breeding disease risk for an area. It does not diagnose an individual animal."
    }

# Backward-compatible function wrapper for existing routes and smoke tests
def calculate_environmental_risk(temperature_c, humidity_percent, rainfall_mm=0.0):
    """
    Maintains 100% backward compatibility with existing backend routes.
    """
    res = predict_environmental_risk(
        temperature_c=temperature_c,
        humidity_percent=humidity_percent,
        rainfall_mm=rainfall_mm
    )
    return {
        "environmental_risk_score": res["environmental_risk_score"],
        "risk_category": res["risk_level"].upper(),
        "factors_summary": "; ".join(res["key_risk_drivers"]),
        "risk_level": res["risk_level"],
        "is_animal_diagnosis": False,
        "disclaimer": res["disclaimer"]
    }

if __name__ == "__main__":
    # Test High-Risk Monsoon Scenario
    high_test = predict_environmental_risk(
        latitude=22.44, longitude=90.38,
        temperature_c=31.5, humidity_percent=84.0, rainfall_mm=45.0,
        elevation_m=45.0, cattle_density=28000.0
    )
    print("High Risk Monsoon Scenario:\n", json.dumps(high_test, indent=2))
    
    # Test Low-Risk Dry Winter Scenario
    low_test = predict_environmental_risk(
        latitude=31.10, longitude=77.17,
        temperature_c=12.0, humidity_percent=38.0, rainfall_mm=1.0,
        elevation_m=2200.0, cattle_density=4000.0
    )
    print("\nLow Risk Dry High-Altitude Scenario:\n", json.dumps(low_test, indent=2))
