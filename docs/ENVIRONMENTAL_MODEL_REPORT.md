# Environmental & Geospatial Lumpy Skin Disease Risk Prediction Model Report

**Project:** AI-Livestock Health Sentinel (SIH26128)  
**Module:** Geospatial & Meteorological Vector-Breeding Risk Assessment  
**Dataset Archive:** `datasets/03_LSD_Environmental_Geospatial_Data.zip` (`Lumpy skin disease data.csv`)  
**Winning Model Checkpoint:** `ml/models/environmental_risk_model.pkl` (XGBoost)  
**Evaluation Metrics:** `ml/models/environmental_evaluation_metrics.json`  
**Training Configuration:** `ml/models/environmental_training_config.json`  
**Feature Names Order:** `ml/models/environmental_feature_names.json`  
**Inference Script:** `ml/environmental_risk/environmental_risk.py`  
**Date:** September 2026  

---

## 1. Executive Summary & Epidemiological Objective

Lumpy Skin Disease (LSD) is a high-consequence poxviral disease of cattle and water buffalo transmitted predominantly via mechanical vector transmission (hematophagous arthropods including stable flies *Stomoxys calcitrans*, mosquitoes *Aedes aegypti*, and hard ticks *Rhipicephalus appendiculatus*).

Vector propagation, flight activity, and viral persistence depend heavily on ambient bioclimatic conditions:
- Heavy precipitation creates stagnant surface water pooling for vector oviposition.
- Warm ambient temperatures ($24^\circ\text{C} - 33^\circ\text{C}$) accelerate larval metamorphosis and biting frequency.
- Elevated humidity ($>70\%$) extends adult insect survival.
- Freezing events (frost days) kill active vector populations.
- Dense bovine host populations facilitate rapid mechanical transmission between herds.

```
                     GEOSPATIAL & ENVIRONMENTAL RISK TIER
 ┌────────────────────────────────────────────────────────────────────────┐
 │ INPUTS: Location (Lat/Long), Precipitation, Ambient Temp, Humidity,    │
 │         Elevation, Land Cover, Cattle/Buffalo Host Density             │
 └───────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
 ┌────────────────────────────────────────────────────────────────────────┐
 │ LEAKAGE PURGE: Permanent discard of region, country, and reportingDate │
 └───────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
 ┌────────────────────────────────────────────────────────────────────────┐
 │ XGBOOST INFERENCE: 26 Bioclimatic & Geospatial Features                │
 │ Scale-Pos-Weight (7.16:1) Imbalance Handling                           │
 └───────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
 ┌────────────────────────────────────────────────────────────────────────┐
 │ OUTPUT: Environmental Risk Score (0 - 100)                             │
 │         Calibrated Tier: LOW (0-35) | MEDIUM (35-65) | HIGH (65-100)   │
 │         Identified Ecological Risk Drivers                             │
 └────────────────────────────────────────────────────────────────────────┘
```

> [!NOTE]
> **Scope Clarification:** This model estimates **regional environmental vulnerability and vector-breeding risk** for an area. It **does not diagnose an individual animal**.

---

## 2. Target Column & Feature Inventory

- **Total Samples:** 24,803 geospatial data points
- **Exact Target Column:** `lumpy` (binary integer: `0` or `1`)
  - `0` (Absence / Control Pseudo-Absence Background): 21,764 samples (**87.75%**)
  - `1` (Presence / Confirmed Outbreak Event): 3,039 samples (**12.25%**)
  - **Class Imbalance Ratio:** $7.16 : 1$

### Data Leakage Audit & Purged Features

During our initial technical inspection, a **catastrophic target leakage flaw** was detected in the raw dataset:

| Column | Non-Null Count | Null Count (%) | Leakage Hazard Analysis | Action Taken |
|---|---|---|---|---|
| `reportingDate` | 3,039 | 21,764 (87.75%) | **100% Target Leakage.** Populated **only** when `lumpy == 1`. When `lumpy == 0`, it is null. Any tree model will achieve 100% artificial accuracy by checking `reportingDate is not null`. | **PERMANENTLY PURGED** |
| `region` | 3,039 | 21,764 (87.75%) | **100% Target Leakage.** Populated only for positive outbreak reports. | **PERMANENTLY PURGED** |
| `country` | 3,039 | 21,764 (87.75%) | **100% Target Leakage.** Populated only for positive outbreak reports. | **PERMANENTLY PURGED** |

### Appropriate Features Retained (26 Dimensions After Encoding)

All 15 raw environmental, geospatial, and host density features have **0 missing values** and were retained:

| Feature Category | Variable Name | Description | Empirical Correlation with Outbreak (`lumpy`) |
|---|---|---|:---:|
| **Geospatial Coordinates** | `x`, `y` | Longitude & Latitude (WGS84) | Latitudinal & longitudinal climatic belts |
| **Precipitation & Wetness** | `pre` | Monthly precipitation (mm) | **+0.4197** (Strongest positive driver) |
| | `wet` | Wet day frequency (days/month) | +0.0996 |
| **Temperature Profile** | `tmn` | Minimum monthly temperature (°C) | **+0.3086** (Warm nights sustain larvae) |
| | `tmp` | Mean monthly temperature (°C) | +0.2834 |
| | `tmx` | Maximum monthly temperature (°C) | +0.2581 |
| | `dtr` | Diurnal temperature range (°C) | **-0.2163** (Wide swings suppress vectors) |
| **Humidity & Evapotranspiration** | `vap` | Water vapor pressure (hPa) | +0.1694 |
| | `cld` | Cloud cover percentage (%) | +0.2378 |
| | `pet` | Potential evapotranspiration (mm/day) | +0.0617 |
| **Thermal Barriers** | `frs` | Frost day frequency (days) | **-0.1728** (Freezing eliminates vectors) |
| | `elevation` | Elevation above sea level (meters) | **-0.1124** (Vector abundance drops with altitude) |
| **Host Population Density** | `X5_Ct_2010_Da` | Cattle population density (heads/$\text{km}^2$) | +0.0689 |
| | `X5_Bf_2010_Da` | Buffalo population density (heads/$\text{km}^2$) | -0.0389 |
| **Land Cover (1-12)** | `dominant_land_cover` | One-hot encoded into 11 dummy variables (`land_cover_2` to `land_cover_12`) | Croplands & riparian marshes foster vector habitats |

---

## 3. Model Training & Head-to-Head Comparison

We trained and evaluated three ensemble algorithms on a strict stratified split:
- **Training Set (70%):** 17,361 samples (Absence: 15,234, Presence: 2,127)
- **Validation Set (15%):** 3,721 samples (Absence: 3,265, Presence: 456)
- **Held-Out Test Set (15%):** 3,721 samples (Absence: 3,265, Presence: 456)

Class imbalance was countered by assigning `scale_pos_weight = 7.16` in XGBoost and `class_weight='balanced'` in Random Forest.

### Benchmark Results on Held-Out Test Data (3,721 Unseen Samples)

| Model | Test Accuracy | ROC-AUC | PR-AUC (Gold Standard) | Outbreak Recall | Outbreak Precision | F1-Score | Inference Latency |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Random Forest** | 96.75% | 0.9913 | 0.9596 | 94.52% | 81.78% | 0.8769 | 0.028 ms |
| **XGBoost (Winner)** | **97.18%** | **0.9930** | **0.9675** | **95.61%** | **83.69%** | **0.8925** | **0.004 ms** |
| **Gradient Boosting** | 98.15% | 0.9933 | 0.9661 | 90.13% | 94.48% | 0.9226 | 0.008 ms |

### Winning Model: **XGBoost**

**Why XGBoost Was Selected:**
1. **Highest PR-AUC:** Achieved **0.9675 PR-AUC** (Area Under the Precision-Recall Curve), which is the most reliable metric for heavily imbalanced epidemiological datasets.
2. **Superior Outbreak Sensitivity (Recall):** Caught **95.61%** of all true outbreak presence points (436 out of 456), compared to 90.13% for Gradient Boosting. In epidemic early warning, missing an active outbreak (false negative) is catastrophic.
3. **Ultra-Low Latency:** Single-coordinate inference takes only **0.004 ms** (4 microseconds), enabling real-time raster map rendering across thousands of spatial grid cells.

### XGBoost Confusion Matrix (Held-Out Test Set: 3,721 Samples)
```
                          PREDICTED
                     Absence (0)    Outbreak (1)
ACTUAL  Absence (0)     3,180            85         (97.40% Specificity)
        Outbreak (1)       20           436         (95.61% Sensitivity / Recall)
```
- **False Negatives:** Only 20 missed outbreaks out of 456 true occurrences.
- **Precision:** 83.69% (436 / 521).

---

## 4. Top Feature Importances (Ecological Drivers)

Analysis of XGBoost split gains reveals the primary ecological determinants of Lumpy Skin Disease outbreaks:

| Rank | Feature Name | Description | Relative Gain | Ecological Mechanism |
|:---:|---|---|:---:|---|
| **1** | `frs` | Frost Day Frequency | **27.18%** | Freezing temperatures kill adult biting flies and disrupt overwintering. Zero frost days allows year-round vector transmission. |
| **2** | `x` | Longitude Coordinates | **17.45%** | Captures regional climate zones (e.g., the humid monsoonal Indo-Gangetic and Bengal plains vs arid plateaus). |
| **3** | `X5_Ct_2010_Da` | Cattle Population Density | **6.17%** | High host density per square kilometer increases biting contact rates and mechanical transmission between herds. |
| **4** | `land_cover_2` | Cropland / Floodplain Mosaic | **5.91%** | Agricultural irrigation and flooded paddy fields provide breeding pools for biting flies. |
| **5** | `dtr` | Diurnal Temperature Range | **5.35%** | Narrow day-night temperature swings protect insect metabolic activity. |

---

## 5. Risk Tiers & Calibrated Scoring Formula

The raw probability $P(\text{outbreak})$ from the model is calibrated relative to the baseline background prevalence ($P_0 = 12.25\%$) using an odds-ratio sigmoidal transformation:

$$\text{Odds Ratio (OR)} = \frac{P(\text{outbreak}) / (1 - P(\text{outbreak}))}{P_0 / (1 - P_0)}$$

$$\text{Risk Score} = \frac{100}{1 + \exp(-1.2 \cdot \ln(\text{OR}) + 0.2)}$$

The final environmental risk score (0.0 to 100.0) is categorized into three actionable administrative tiers:

| Environmental Risk Score | Risk Level | Meaning & Early Warning Protocol |
|---|:---:|---|
| **0.0 to 35.0** | **Low** | Baseline ecological conditions. Minimal vector breeding threat. Routine vector control and biosecurity. |
| **35.0 to 65.0** | **Medium** | Elevated temperature and humidity conducive to vector multiplication. Advise farmers to deploy insect repellents, clear stagnant surface pools, and verify cattle vaccination status. |
| **65.0 to 100.0** | **High** | **Active Vector Surge / Outbreak Alert.** Peak monsoonal warmth and surface pooling. District animal husbandry departments should alert veterinary clinics, establish ring-vaccination corridors, and deploy aerial/ground vector spraying. |

---

## 6. API Output Schema & Example Requests

Implemented in [`ml/environmental_risk/environmental_risk.py`](file:///C:/Users/Samruddhi%20Janwalkar/.gemini/antigravity/scratch/ai-livestock-health-sentinel/ml/environmental_risk/environmental_risk.py).

### Example 1: High-Risk Monsoon Outbreak Hotspot
- Input: Latitude 22.44, Longitude 90.38, Temp 31.5°C, Humidity 84%, Rainfall 45 mm, Cattle Density 28,000/$\text{km}^2$.

```json
{
  "environmental_risk_score": 78.6,
  "risk_level": "High",
  "outbreak_probability": 0.206,
  "location": {
    "latitude": 22.44,
    "longitude": 90.38
  },
  "environmental_factors": {
    "temperature_c": 31.5,
    "humidity_percent": 84.0,
    "rainfall_mm": 45.0,
    "elevation_m": 45.0,
    "cattle_density_km2": 28000.0
  },
  "key_risk_drivers": [
    "Elevated precipitation (45.0 mm) facilitates stagnant water pooling for biting vectors",
    "Mean temperature (31.5°C) resides in the peak viral transmission range for Stomoxys flies",
    "High relative humidity (84.0%) extends vector lifespan and reproductive rate",
    "High local bovine host density (28,000 head/km²) increases mechanical transmission probability",
    "Absence of frost days permits uninterrupted overwintering of vector colonies"
  ],
  "is_animal_diagnosis": false,
  "disclaimer": "This score estimates regional environmental and vector-breeding disease risk for an area. It does not diagnose an individual animal."
}
```

### Example 2: Low-Risk Dry High-Altitude Winter Zone
- Input: Latitude 31.10, Longitude 77.17, Temp 12.0°C, Humidity 38%, Rainfall 1 mm, Elevation 2,200m, Cattle Density 4,000/$\text{km}^2$.

```json
{
  "environmental_risk_score": 25.1,
  "risk_level": "Low",
  "outbreak_probability": 0.0543,
  "location": {
    "latitude": 31.1,
    "longitude": 77.17
  },
  "environmental_factors": {
    "temperature_c": 12.0,
    "humidity_percent": 38.0,
    "rainfall_mm": 1.0,
    "elevation_m": 2200.0,
    "cattle_density_km2": 4000.0
  },
  "key_risk_drivers": [
    "Absence of frost days permits uninterrupted overwintering of vector colonies",
    "High elevation (2200 m) acts as a natural climatic barrier to vector proliferation"
  ],
  "is_animal_diagnosis": false,
  "disclaimer": "This score estimates regional environmental and vector-breeding disease risk for an area. It does not diagnose an individual animal."
}
```

---

## 7. Non-Diagnostic Environmental Disclaimer

> [!IMPORTANT]
> **Environmental Risk Non-Diagnostic Disclaimer:**  
> This module quantifies **regional environmental vulnerability, bioclimatic suitability, and vector transmission risk** for a geographic area.  
> It **does not diagnose an individual cow or buffalo**. An individual animal in a high-risk zone may remain uninfected, while an individual animal in a low-risk zone may develop symptoms through direct animal-to-animal contact or animal transport. Individual health assessments must be performed via clinical examination and symptom reporting.
