import os
import sys
import json
import pickle
import time
from typing import Dict, Any, Optional, List
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_DIR = os.path.dirname(BASE_DIR)

MODEL_CHECKPOINT_PATH = os.path.join(ROOT_DIR, "ml", "models", "environmental_risk_model.pkl")
FEATURE_NAMES_PATH = os.path.join(ROOT_DIR, "ml", "models", "environmental_feature_names.json")

class EnvironmentalRiskService:
    """
    Dedicated Geospatial & Bioclimatic Machine Learning Service for vector-borne disease risk.
    Maintains an in-memory cached XGBoost classifier and spatial feature mappings.
    """
    _instance: Optional["EnvironmentalRiskService"] = None

    def __init__(self):
        self._model = None
        self._feature_names: List[str] = []
        self._load_model_once()

    @classmethod
    def get_instance(cls) -> "EnvironmentalRiskService":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _load_model_once(self):
        """Loads and caches the XGBoost environmental model and feature names once."""
        if self._model is not None:
            return
            
        t0 = time.time()
        if os.path.exists(MODEL_CHECKPOINT_PATH) and os.path.exists(FEATURE_NAMES_PATH):
            try:
                print(f"[ENVIRONMENTAL SERVICE] Loading model from {MODEL_CHECKPOINT_PATH}...")
                with open(MODEL_CHECKPOINT_PATH, "rb") as f:
                    self._model = pickle.load(f)
                with open(FEATURE_NAMES_PATH, "r") as f:
                    meta = json.load(f)
                    self._feature_names = meta.get("feature_names", [])
                load_time = time.time() - t0
                print(f"[ENVIRONMENTAL SERVICE] Model loaded and cached successfully in {load_time:.2f}s ({len(self._feature_names)} features).")
            except Exception as exc:
                print(f"[ENVIRONMENTAL SERVICE] Error loading model: {exc}")
                self._model = None
        else:
            print(f"[ENVIRONMENTAL SERVICE] Checkpoint {MODEL_CHECKPOINT_PATH} not found.")

    def calibrate_score(self, prob: float, baseline_prior: float = 0.1225) -> float:
        """Calibrates presence-absence odds ratio into standard 0-100 risk score."""
        prob = max(1e-4, min(1.0 - 1e-4, float(prob)))
        odds_ratio = (prob / (1.0 - prob)) / (baseline_prior / (1.0 - baseline_prior))
        calibrated = 100.0 / (1.0 + np.exp(-1.2 * np.log(odds_ratio + 1e-6) + 0.2))
        return float(round(max(0.0, min(100.0, calibrated)), 1))

    def compute_meteorological_suitability(self, temp: float, hum: float, rain: float) -> float:
        """Computes entomological suitability index for Stomoxys and biting fly breeding."""
        # 1. Temperature suitability
        if 24.0 <= temp <= 35.0:
            temp_factor = 1.0 - (abs(temp - 30.0) / 15.0)
        elif temp > 35.0:
            temp_factor = max(0.2, 1.0 - ((temp - 35.0) / 10.0))
        else:
            temp_factor = max(0.1, (temp - 10.0) / 14.0)
        temp_factor = max(0.0, min(1.0, temp_factor))
        
        # 2. Humidity suitability
        if hum >= 70.0:
            hum_factor = min(1.0, 0.7 + ((hum - 70.0) / 100.0))
        elif hum >= 50.0:
            hum_factor = 0.4 + ((hum - 50.0) / 60.0)
        else:
            hum_factor = max(0.1, hum / 125.0)
        hum_factor = max(0.0, min(1.0, hum_factor))
        
        # 3. Rain factor
        if rain > 15.0:
            rain_factor = 0.95
        elif rain > 5.0:
            rain_factor = 0.70
        elif rain > 0.0:
            rain_factor = 0.40
        else:
            rain_factor = 0.20
            
        meteo_score = (0.35 * temp_factor + 0.40 * hum_factor + 0.25 * rain_factor) * 100.0
        return float(meteo_score)

    def analyze_environment(
        self,
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
        Executes independent environmental & geospatial Lumpy Skin Disease risk estimation.
        """
        t0 = time.perf_counter()
        
        if self._model is None:
            self._load_model_once()
            
        # 1. Derive climatic variables
        tmp = float(temperature_c)
        tmn = max(5.0, tmp - 6.0)
        tmx = tmp + 6.0
        dtr = tmx - tmn
        pre = float(rainfall_mm) * 3.0
        wet = min(30.0, pre / 8.0)
        
        es = 6.112 * np.exp((17.67 * tmp) / (tmp + 243.5))
        vap = float(es * (humidity_percent / 100.0))
        cld = min(100.0, max(10.0, humidity_percent * 0.8))
        frs = 0.0 if tmn > 2.0 else max(0.0, (2.0 - tmn) * 2.0)
        pet = max(1.0, 0.013 * (tmp + 10.0) * es)
        
        # 2. Build feature dictionary
        feat_dict = {
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
        for c in range(2, 13):
            feat_dict[f"land_cover_{c}"] = 1 if dominant_land_cover == c else 0
            
        meteo_score = self.compute_meteorological_suitability(tmp, humidity_percent, rainfall_mm)
        
        # 3. Model Inference (Reuses cached model in memory)
        if self._model is not None and self._feature_names:
            X_vec = np.array([feat_dict.get(fn, 0.0) for fn in self._feature_names]).reshape(1, -1)
            probs = self._model.predict_proba(X_vec)[0]
            outbreak_prob = float(round(probs[1], 4))
            ml_score = self.calibrate_score(outbreak_prob)
            combined_score = (0.40 * ml_score) + (0.60 * meteo_score)
        else:
            outbreak_prob = float(round(meteo_score / 100.0, 4))
            combined_score = meteo_score
            
        latency_ms = round((time.perf_counter() - t0) * 1000, 3)
        risk_score = max(0.0, min(100.0, float(round(combined_score, 1))))
        
        # 4. Determine Environmental Risk Level
        if risk_score < 35.0:
            risk_level = "Low"
        elif risk_score < 65.0:
            risk_level = "Medium"
        else:
            risk_level = "High"
            
        # 5. Extract Ecological Risk Drivers
        drivers = []
        if pre > 40.0 or rainfall_mm > 10.0:
            drivers.append(f"Elevated precipitation ({rainfall_mm:.1f} mm) facilitates stagnant water pooling for biting vectors")
        if 24.0 <= tmp <= 35.0:
            drivers.append(f"Mean temperature ({tmp:.1f}°C) resides in peak biting fly viral incubation range")
        if humidity_percent >= 70.0:
            drivers.append(f"High relative humidity ({humidity_percent:.1f}%) extends vector adult lifespan and transmission window")
        if cattle_density > 15000.0:
            drivers.append(f"High bovine host density ({cattle_density:,.0f} head/km²) accelerates mechanical contact between herds")
        if frs == 0.0:
            drivers.append("Absence of frost days permits uninterrupted overwintering of vector colonies")
        if elevation_m > 1500.0:
            drivers.append(f"High elevation ({elevation_m:.0f} m) acts as a natural climatic barrier to vector proliferation")
        if not drivers:
            drivers.append("Ambient weather, elevation, and vector-breeding factors reside within baseline endemic limits")
            
        return {
            "service": "environmental_risk_assessment",
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
                "cattle_density_km2": round(float(cattle_density), 1),
                "buffalo_density_km2": round(float(buffalo_density), 1)
            },
            "key_risk_drivers": drivers,
            "model_metadata": {
                "architecture": "XGBoost Geospatial Classifier",
                "checkpoint": "ml/models/environmental_risk_model.pkl",
                "framework": "XGBoost",
                "inference_latency_ms": latency_ms
            },
            # Mandatory Ethical Non-Diagnosis Disclaimer
            "is_animal_diagnosis": False,
            "disclaimer": (
                "This score estimates regional environmental and vector-breeding disease risk for an area. "
                "It does not diagnose an individual animal."
            )
        }

def get_environmental_service() -> EnvironmentalRiskService:
    return EnvironmentalRiskService.get_instance()
