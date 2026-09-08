# Transparent Multi-Modal Livestock Health Risk Engine

## 1. Overview & Objective

The **Multi-Modal Livestock Health Risk Engine** synthesizes four heterogeneous epidemiological modalities into a single, calibrated, transparent early-warning risk score for cattle and buffaloes. 

Unlike black-box ensemble classifiers, this engine enforces **transparent factor accounting**: each individual model retains its autonomy and distinct prediction score, and the engine produces a mathematical audit trail showing exactly how much each factor contributed to the final risk assessment.

> [!IMPORTANT]
> **Ethical & Regulatory Disclaimer**:
> This engine is an **AI-assisted risk triage and prioritization tool**, **NOT a veterinary diagnosis**. It does not prescribe medications or issue statutory disease declarations. All high-risk alerts must be clinically reviewed by a registered veterinarian and confirmed via laboratory testing (e.g., PCR or ELISA).

---

## 2. Modality Inputs & Default Weight Configuration

The engine combines four distinct risk streams using **configurable weights**. These values can be modified globally via environment variables or overridden per request via runtime parameters.

### Default Weight Distribution

| Modality | Weight | Config Variable (`.env`) | Description |
| :--- | :---: | :--- | :--- |
| **Image AI Risk** | **40%** (`0.40`) | `RISK_WEIGHT_IMAGE` | Deep learning visual skin lesion screening (PyTorch MobileNetV3). |
| **Symptom AI Risk** | **35%** (`0.35`) | `RISK_WEIGHT_SYMPTOM` | Multi-class clinical symptom screening and SHAP driver ranking (XGBoost). |
| **Environmental Risk** | **15%** (`0.15`) | `RISK_WEIGHT_ENVIRONMENT` | Geospatial and bioclimatic vector-breeding suitability (XGBoost geospatial). |
| **Health & Vaccination Context** | **10%** (`0.10`) | `RISK_WEIGHT_CONTEXT` | Biological host susceptibility based on immunization records and past medical history. |
| **Total** | **100%** (`1.00`) | — | Weights must sum to 1.0. |

### Configuration Mechanisms

1. **Global Configuration (`backend/config.py` & `.env`)**:
   ```env
   RISK_WEIGHT_IMAGE=0.40
   RISK_WEIGHT_SYMPTOM=0.35
   RISK_WEIGHT_ENVIRONMENT=0.15
   RISK_WEIGHT_CONTEXT=0.10
   ```
2. **Per-Request Runtime Override (`custom_weights`)**:
   Clients can customize weights for specialized workflows (e.g., field surveys where image capture is unavailable, or quarantine inspection stations where vaccination history carries higher weight):
   ```json
   {
     "custom_weights": {
       "image": 0.30,
       "symptoms": 0.40,
       "environment": 0.10,
       "context": 0.20
     }
   }
   ```

---

## 3. Mathematical Formulation

### 3.1 Dynamic Weight Renormalization

In rural field conditions, some modalities may be unavailable (e.g., lack of camera equipment, omitted GPS coordinates). To avoid corrupting the score scale, the engine dynamically recalculates the **effective weights** of all active modalities:

\[
w'_i = \frac{w_i}{\sum_{j \in \mathcal{M}_{\text{active}}} w_j}
\]

Where:
- \(\mathcal{M}_{\text{active}}\) is the subset of modalities present in the request.
- \(w_i\) is the configured base weight of modality \(i\).
- \(w'_i\) is the normalized effective weight, guaranteeing that:
  \[
  \sum_{i \in \mathcal{M}_{\text{active}}} w'_i = 1.0 \quad (100\%)
  \]

### 3.2 Final Risk Score Calculation

The final health risk score is the linear combination of raw modality scores scaled by their effective weights:

\[
\text{Final Risk Score} = \sum_{i \in \mathcal{M}_{\text{active}}} \left( \text{Raw Score}_i \times w'_i \right)
\]

The final score is clamped to the range \([0.0, 100.0]\) and rounded to one decimal place.

### 3.3 Contribution and Percentage Accounting

For every modality \(i\), the engine computes:
1. **Weighted Contribution**:
   \[
   C_i = \text{Raw Score}_i \times w'_i
   \]
2. **Percentage of Total Risk**:
   \[
   P_i = \begin{cases} 
   \left( \frac{C_i}{\text{Final Risk Score}} \right) \times 100 & \text{if } \text{Final Risk Score} > 0 \\ 
   0.0 & \text{otherwise} 
   \end{cases}
   \]

Contributing factors are sorted **descending by weighted contribution** in the response, allowing veterinarians and farmers to immediately see the dominant risk drivers.

---

## 4. Host Susceptibility & Context Scoring Matrix

The context score (\(0 - 100\)) represents the animal's baseline biological vulnerability, combining immunization history (70% context weight) and clinical history (30% context weight):

\[
\text{Context Score} = (0.70 \times S_{\text{vac}}) + (0.30 \times S_{\text{history}})
\]

### Vaccination Susceptibility Matrix (\(S_{\text{vac}}\))

| Status | Susceptibility Score | Clinical Rationale |
| :--- | :---: | :--- |
| `vaccinated` / `up_to_date` | **5.0** | Current immunization; strong humoral protection. |
| `partially_vaccinated` | **45.0** | Incomplete vaccination regimen; partial antibody titers. |
| `overdue` / `booster_due` | **65.0** | Waning antibody titers; elevated vulnerability to wild strains. |
| `not_vaccinated` / `unvaccinated` | **85.0** | Immunologically naive; maximum host susceptibility. |
| `unknown` | **50.0** | Unverified record; conservative baseline assumed. |

### Health History Predisposition Matrix (\(S_{\text{history}}\))

| Category | Indicators | Score | Rationale |
| :--- | :--- | :---: | :--- |
| **Clean** | `none`, `healthy`, `nil` | **5.0** | No documented prior chronic or epidemic illness. |
| **Moderate** | `fever`, `respiratory`, `mastitis`, `underweight` | **50.0** | Past episodes indicate compromised baseline immunity. |
| **High** | `past_lsd`, `past_fmd`, `anthrax`, `chronic`, `recurrent` | **80.0** | Documented prior severe infection or endemic herd exposure. |

---

## 5. Risk Level Classification & Triage Protocol

| Score Range | Risk Level | Clinical Interpretation | Recommended Action |
| :---: | :---: | :--- | :--- |
| **0 – 30** | **Low** | Baseline healthy indicators; minimal contagion risk. | Routine herd health monitoring; maintain standard biosecurity. |
| **31 – 60** | **Medium** | Moderate clinical signs or environmental suitability. | Isolate from lactating herd; increase observation frequency; log daily temperature. |
| **61 – 80** | **High** | Strong visual, clinical, or vector hazard confluence. | Strict physical quarantine; initiate tele-veterinary triage; prepare vector barrier netting. |
| **81 – 100** | **Critical** | Acute epidemic indicators in a highly vulnerable host. | Emergency containment; dispatch official veterinarian for PCR sampling; report to district surveillance. |

---

## 6. API Reference

### `POST /analysis/multi-modal` (Alias: `POST /api/analysis/multi-modal`)

#### Request Payload (`MultiModalRiskRequest`)

```json
{
  "image_risk_score": 78.5,
  "symptom_risk_score": 64.0,
  "environmental_risk_score": 52.0,
  "vaccination_status": "not_vaccinated",
  "health_history": "past_respiratory",
  "custom_weights": {
    "image": 0.40,
    "symptoms": 0.35,
    "environment": 0.15,
    "context": 0.10
  }
}
```

#### Response Payload (`MultiModalRiskResponse`)

```json
{
  "final_risk_score": 69.0,
  "risk_level": "High",
  "contributing_factors": [
    {
      "factor": "Image AI Risk",
      "modality_key": "image",
      "raw_score": 78.5,
      "weight": 0.40,
      "weighted_contribution": 31.4,
      "percentage_of_total_risk": 45.5,
      "description": "Visual computer vision screening detected significant skin lesions/nodules (78.5/100)."
    },
    {
      "factor": "Symptom AI Risk",
      "modality_key": "symptoms",
      "raw_score": 64.0,
      "weight": 0.35,
      "weighted_contribution": 22.4,
      "percentage_of_total_risk": 32.5,
      "description": "Reported acute clinical symptoms strongly match infectious disease profiles (64.0/100)."
    },
    {
      "factor": "Environmental Risk",
      "modality_key": "environment",
      "raw_score": 52.0,
      "weight": 0.15,
      "weighted_contribution": 7.8,
      "percentage_of_total_risk": 11.3,
      "description": "Moderate ambient humidity/temperature favorable for vector survival (52.0/100)."
    },
    {
      "factor": "Health/Vaccination Context",
      "modality_key": "context",
      "raw_score": 74.5,
      "weight": 0.10,
      "weighted_contribution": 7.45,
      "percentage_of_total_risk": 10.8,
      "description": "Animal is completely unvaccinated; high biological susceptibility to viral/bacterial contagion. Documented past mild febrile/respiratory episodes indicating compromised baseline resistance. (Context score: 74.5/100)."
    }
  ],
  "individual_model_scores": {
    "image_risk": 78.5,
    "symptom_risk": 64.0,
    "environmental_risk": 52.0,
    "context_risk": 74.5
  },
  "risk_thresholds": {
    "Low": "0-30",
    "Medium": "31-60",
    "High": "61-80",
    "Critical": "81-100"
  },
  "calculation_details": {
    "configured_weights": {
      "image": 0.4,
      "symptoms": 0.35,
      "environment": 0.15,
      "context": 0.1
    },
    "effective_weights": {
      "image": 0.4,
      "symptoms": 0.35,
      "environment": 0.15,
      "context": 0.1
    },
    "active_modalities_count": 4,
    "is_dynamically_renormalized": false,
    "formula": "final_risk_score = sum(raw_score_i * effective_weight_i)"
  },
  "is_veterinary_diagnosis": false,
  "disclaimer": "This score is an AI-assisted multi-modal risk assessment tool and NOT a veterinary diagnosis. It synthesizes visual computer vision triage, reported symptoms, geospatial vector risk, and immunization history to provide early warning triage for farmers and veterinarians. Clinical decisions, prescriptions, and statutory quarantine actions must be confirmed by a licensed veterinarian."
}
```

---

## 7. Verification & Benchmark Summary

The engine was verified across the automated test suite ([test_multi_modal_engine.py](file:///C:/Users/Samruddhi%20Janwalkar/.gemini/antigravity/scratch/ai-livestock-health-sentinel/backend/test_multi_modal_engine.py)):
- **Default Weight Accuracy**: Verified exact match on mathematical weighted sums.
- **Risk Level Boundaries**: Confirmed strict categorization across `Low` (13.0), `Medium` (47.3), `High` (69.0), and `Critical` (91.3).
- **Custom Overrides**: Validated that user-specified weights override defaults cleanly.
- **Dynamic Renormalization**: Confirmed that missing modalities (e.g., omitted image) renormalize active weights to exactly 1.0000.
- **Context Scoring Matrix**: Confirmed host susceptibility modeling for clean, partial, overdue, and chronic histories.
- **Inference Latency**: Sub-millisecond mathematical synthesis (~0.2ms) without disk I/O.
