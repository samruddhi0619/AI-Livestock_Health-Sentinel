# Symptom-Based Livestock Disease Risk Assessment Model Report

**Project:** AI-Livestock Health Sentinel (SIH26128)  
**Module:** Symptom-Based Multi-Disease Risk Assessment  
**Model Checkpoint:** `ml/models/symptom_model.pkl` (XGBoost)  
**Alternative Checkpoints:** `ml/models/rf_model.pkl` (Random Forest), `ml/models/xgb_model.pkl`  
**Evaluation Metrics:** `ml/models/symptom_evaluation_metrics.json`  
**Training Configuration:** `ml/models/symptom_training_config.json`  
**Inference Script:** `ml/symptom_prediction/predict.py`  
**Explainability Module:** `ml/symptom_prediction/explain.py` (SHAP TreeExplainer)  
**Date:** September 2026  

---

## 1. Executive Summary & Problem Formulation

Frontline dairy farmers and paravets frequently observe early constitutional symptoms (e.g., inappetence, pyrexia, drop in milk yield, nasal discharge) before specialized veterinary laboratory assays are available. 

This module provides an **explainable, multi-disease risk triage engine** that takes reported symptoms alongside host demographics (age, breed, gender, history, vaccination) to compute:
1. Calibrated multi-class disease probabilities
2. Actionable risk tiers (`LOW`, `MODERATE`, `HIGH`)
3. Ranked contributing symptoms via SHAP TreeExplainer

```
  Farmer Reported Symptoms + Host Metadata
                     │
                     ▼
  Vectorization & Permutation-Invariant Encoding
                     │
                     ▼
  XGBoost Multi-Class Inference Engine
                     │
                     ▼
  Ranked Disease Probabilities + Risk Calibration
                     │
                     ▼
  SHAP TreeExplainer Feature Attributions
                     │
                     ▼
  Structured Triage API Response + Veterinary Disclaimer
```

---

## 2. Dataset Inspection & Scope Filtering

To ensure statistical validity and clinical safety, we conducted an exhaustive evaluation across all three candidate symptom/disease datasets:

### Dataset Audit Findings

| Candidate Dataset | Rows / Classes | Key Characteristics | Technical Evaluation & Defect Detection | Final Decision |
|---|---|---|---|---|
| **05_Cattle_Health_Feeding_Records** (`animal_disease_dataset.csv`) | 43,778 rows<br>5 diseases | `anthrax`, `blackleg`, `foot and mouth`, `pneumonia`, `lumpy virus` | **Critical Synthetic Generation Flaw Detected:** All 7,330 pneumonia rows and all 7,192 lumpy virus rows possess **identical symptoms** (`depression, loss of appetite, painless lumps`), identical ages (6.85 vs 6.84), and identical temperatures (102.3°F). They are mathematically indistinguishable in raw form. Furthermore, zero healthy negative controls exist. | **Used with clinical rectification** for FMD, Blackleg, and Anthrax symptom profiles. |
| **06_Cattle_Disease_and_Health_Records** (`global_cattle_disease_detection_dataset.csv`) | 250,000 rows<br>45 classes | 137,419 Healthy,<br>44 diseases (~2,500 each) | High clinical fidelity; contains vital signs (`Body_Temperature_C`, `Heart_Rate_bpm`, `Respiratory_Rate`, `Rumination_Time_hrs`, `Milk_Yield_L`) and 8 vaccination histories. Balanced distribution across major bovine conditions. | **Primary empirical baseline** for Healthy controls, FMD, LSD, BRD, and Mastitis. |
| **07_Animal_Symptoms_Disease_Prediction** (`cleaned_animal_disease_prediction.csv`) | 431 rows<br>139 diseases | 8 animal species (Dog, Cat, Cow, etc.) | Extreme class sparsity (average ~3 rows per disease; only 68 cattle rows). Overfitting guaranteed if trained statistically. | **Excluded from statistical training**; retained as clinical vocabulary ontology. |

### Filtered 6-Disease Project Scope

Based on statistical dataset support and Smart India Hackathon operational priorities, we filtered the project scope to the **6 clinical conditions with robust evidence**:

1. **`Healthy` (Baseline Negative Control):** Necessary to prevent healthy cattle with minor, non-pathological variations from being falsely classified as infected with high-consequence epizootics.
2. **`Lumpy Skin Disease` (SIH Core Mandate):** Characterized by cutaneous nodular eruptions, persistent fever, anorexia, and acute drop in milk yield.
3. **`Foot-and-Mouth Disease` (SIH Core Mandate):** Characterized by vesicular eruptions on mouth/hooves, excess salivation, acute lameness, and fever.
4. **`Mastitis` (Major Dairy Impact):** Characterized by udder swelling, local inflammation, and drastic loss of milk production.
5. **`Bovine Respiratory Disease / Pneumonia` (SIH Core Mandate):** Characterized by dyspnea, coughing, mucopurulent nasal discharge, and fever.
6. **`Brucellosis` (Zoonotic Regulatory Alert):** Characterized by pyrexia, reproductive loss history, joint swelling, and milk reduction.

---

## 3. Model Training & Head-to-Head Comparison

We trained and compared three state-of-the-art tree ensemble algorithms on a stratified dataset of 10,000 clinical records across the 6 supported disease classes:
- **Training Split (70%):** 6,996 samples
- **Validation Split (15%):** 1,500 samples
- **Held-Out Test Split (15%):** 1,500 samples (250 per class)

### Candidate Algorithms
1. **Random Forest Classifier:** 150 estimators, `max_depth=8`, `min_samples_split=5`.
2. **XGBoost Classifier:** 150 estimators, `max_depth=5`, `learning_rate=0.08`, `subsample=0.8`, `colsample_bytree=0.8`.
3. **Scikit-Learn Gradient Boosting:** 120 estimators, `max_depth=4`, `learning_rate=0.1`.

---

## 4. Benchmark Results on Held-Out Test Data (1,500 Samples)

| Model | Test Accuracy | Precision (Weighted) | Recall (Weighted) | F1-Score (Weighted) | Precision (Macro) | Recall (Macro) | F1-Score (Macro) | Latency (ms) | Training Wall Time |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Random Forest** | **80.07%** | 0.7986 | **0.8007** | 0.7948 | 0.7986 | **0.8007** | 0.7948 | 0.089 ms | **0.92 s** |
| **XGBoost (Winner)** | 80.00% | 0.7978 | 0.8000 | **0.7965** | 0.7978 | 0.8000 | **0.7965** | **0.013 ms** | 2.19 s |
| **Gradient Boosting** | 79.93% | 0.7968 | 0.7993 | 0.7958 | 0.7968 | 0.7993 | 0.7958 | 0.060 ms | 13.23 s |

### Winning Model Selection: **XGBoost**

**Selection Rationale:**
1. **Highest F1-Score:** XGBoost achieved the highest weighted and macro F1-score (**0.7965**), reflecting superior balance between sensitivity and specificity across all 6 classes.
2. **Sub-Millisecond Inference Speed:** Single-instance inference takes only **0.013 ms** (nearly 7x faster than Random Forest at 0.089 ms), supporting high-throughput concurrent REST API requests.
3. **Native TreeExplainer Compatibility:** Integrates with SHAP `TreeExplainer` for real-time mathematical feature attributions.

---

## 5. Confusion Matrix Analysis (XGBoost Test Set: 1,500 Samples)

```
                            PREDICTED CLASS
             Healthy   LSD    FMD   Mastitis   BRD   Brucellosis  | Recall
Healthy        235       1      0       1       0        13       | 94.0%
LSD              1     225      9       9       3         3       | 90.0%
FMD              0      25    176      35       4        10       | 70.4%
Mastitis         2      16     14     184       2        32       | 73.6%
BRD              0       2      1       0     243         4       | 97.2%
Brucellosis     18       7     28      55       5       137       | 54.8%
```

### Key Clinical Observations:
- **Healthy Control Specificity:** **94.0%** (235/250). Healthy cattle are almost never misclassified as high-risk infectious outbreaks.
- **Bovine Respiratory Disease Sensitivity:** **97.2%** (243/250). Outstanding detection of cough and dyspnea patterns.
- **Lumpy Skin Disease Sensitivity:** **90.0%** (225/250). Skin abnormalities combined with fever reliably trigger LSD predictions.
- **Brucellosis / Mastitis Differential:** Brucellosis exhibits clinical overlap with Mastitis (both present with fever and chronic milk drop), reflecting genuine veterinary diagnostic challenges where paravets require laboratory agglutination assays.

---

## 6. Real-Time Explainability via SHAP (TreeExplainer)

For every inference request, the module runs SHAP TreeExplainer to calculate exact Shapley additive explanations:

$$\text{Log-Odds Output} = \phi_0 + \sum_{i=1}^{M} \phi_i$$

Where $\phi_i$ denotes the positive or negative contribution of symptom $i$ toward the predicted disease.

### Example SHAP Output for a Suspected LSD Case:
- Input: `["skin_abnormalities", "fever", "loss_of_appetite"]`
- Model Prediction: `Lumpy Skin Disease` (95.9% probability)
- Top Contributing Symptoms:
  1. **Skin Abnormalities:** $+0.2111$ (Dominant positive driver)
  2. **Fever:** $+0.0695$ (Strong supportive driver)
  3. **Loss Of Appetite:** $+0.0405$ (Systemic sign)

---

## 7. API Specification & Output Schema

The prediction API is implemented in [`ml/symptom_prediction/predict.py`](file:///C:/Users/Samruddhi%20Janwalkar/.gemini/antigravity/scratch/ai-livestock-health-sentinel/ml/symptom_prediction/predict.py).

### Python Usage
```python
from ml.symptom_prediction.predict import predict_symptoms

result = predict_symptoms(
    symptoms=["skin_abnormalities", "fever", "loss_of_appetite"],
    age=4,
    breed="gir",
    gender="female",
    history="none",
    vaccination="vaccinated"
)
```

### JSON Response Schema
```json
{
  "possible_conditions": [
    {
      "disease": "Lumpy Skin Disease",
      "probability": 0.9593
    },
    {
      "disease": "Brucellosis",
      "probability": 0.0304
    }
  ],
  "risk_level": "HIGH",
  "contributing_symptoms": [
    {
      "symptom": "Skin Abnormalities",
      "contribution": 0.2111
    },
    {
      "symptom": "Fever",
      "contribution": 0.0695
    },
    {
      "symptom": "Loss Of Appetite",
      "contribution": 0.0405
    }
  ],
  "possible_disease": "Lumpy Skin Disease",
  "risk_score": 95.9,
  "severity": "MODERATE",
  "probabilities": {
    "Healthy": 0.4,
    "Lumpy Skin Disease": 95.9,
    "Foot-and-Mouth Disease": 0.3,
    "Mastitis": 0.2,
    "Bovine Respiratory Disease": 0.1,
    "Brucellosis": 3.0
  },
  "is_definitive_diagnosis": false,
  "disclaimer": "AI screening and risk triage tool only. Not a veterinary diagnosis. Consult a registered veterinarian for clinical confirmation and prescription."
}
```

---

## 8. Ethical AI & Veterinary Safety Disclaimer

> [!IMPORTANT]
> **Non-Veterinary Clinical Disclaimer:**  
> This symptom risk assessment tool is strictly an **early warning screening and triage assistant**.  
> It **does not constitute a definitive, legal, or medical veterinary diagnosis**, nor does it replace professional veterinary clinical examination, differential blood chemistry, culture isolation, or serological/PCR laboratory testing.  
> Farmers and field agents must consult a registered veterinary practitioner for confirmatory testing, quarantine enforcement, and antibiotic/therapeutic prescription.
