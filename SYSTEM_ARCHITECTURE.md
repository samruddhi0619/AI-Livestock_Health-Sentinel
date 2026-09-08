# System Architecture: AI-Livestock Health Sentinel

**Project Title:** AI-Livestock Health Sentinel  
**Problem Statement ID:** SIH26128  
**Theme:** Agriculture, FoodTech & Rural Development  
**Target Beneficiaries:** Farmers, Field Veterinarians, District Animal Husbandry Officers, State Animal Health Commissioners  
**Date:** September 2026  

---

## 1. Executive Summary & Problem Scope

Livestock diseases such as **Lumpy Skin Disease (LSD)**, **Foot-and-Mouth Disease (FMD)**, **Bovine Respiratory Disease (BRD)**, **Mastitis**, and **Brucellosis** cause catastrophic economic losses to Indian dairy farmers and disrupt the national rural economy. Conventional disease management suffers from:
1. **Delayed Detection**: Farmers recognize symptoms late, allowing contagious pathogens to spread.
2. **Limited Veterinary Access**: Remote rural villages have high animal-to-vet ratios (>10,000:1 in many districts).
3. **Absence of Real-Time Surveillance**: Outbreak clusters are detected weeks after initial cases, preventing targeted ring-vaccination and containment.
4. **Poor Digital Literacy & Rural Internet Deficits**: Complex forms and unreliable network connectivity impede digital adoption.

The **AI-Livestock Health Sentinel** is an integrated early-warning, health management, and epidemic intelligence platform that connects animal-level multi-modal diagnosis with farm-level and regional geospatial disease surveillance.

---

## 2. High-Level Architecture Overview

```
                                  USER INTERFACE LAYER
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        React + Vite + Tailwind CSS Web & PWA                           │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  ┌────────────────┐ │
│  │ Farmer Portal    │  │ Vet Portal       │  │ Officer Portal   │  │ Admin Portal   │ │
│  │ - Digital Pass   │  │ - Triage Queue   │  │ - Geo Surveillance│ │ - ML Config    │ │
│  │ - Multi-modal AI │  │ - Case Verify    │  │ - DBSCAN Clusters│  │ - User Admin   │ │
│  │ - Voice Check    │  │ - Prescription   │  │ - Containment Ord│  │ - Audit Logs   │ │
│  │ - QR Scanner     │  │ - GIS Risk Map   │  │ - Epidemic Curve │  │ - Accuracy Mon │ │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘  └────────────────┘ │
│                                                                                        │
│  ┌──────────────────────────────────────────────────────────────────────────────────┐  │
│  │ Local Offline Pipeline: IndexedDB ('sentinel_offline_db') + Web Speech API      │  │
│  └──────────────────────────────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            │ HTTPS / RESTful JSON / JWT Bearer
                                            ▼
                                  API GATEWAY & BACKEND
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                               FastAPI (Python 3.10+)                                   │
│  ┌───────────────────┐  ┌───────────────────┐  ┌──────────────────┐  ┌──────────────┐  │
│  │ Auth & RBAC Guard │  │ Passport & QR     │  │ Case & Treatment │  │ Surveillance │  │
│  │ JWT, Bcrypt, Roles│  │ QR Code Generator │  │ Escalation & Log │  │ GeoJSON Pipe │  │
│  └───────────────────┘  └───────────────────┘  └──────────────────┘  └──────────────┘  │
│  ┌───────────────────┐  ┌───────────────────┐  ┌──────────────────┐  ┌──────────────┐  │
│  │ Multi-Modal Engine│  │ Anomaly Processor │  │ Outbreak Engine  │  │ Early Alert  │  │
│  │ Fusion & Overrides│  │ Vitals Validation │  │ DBSCAN Clustering│  │ SMS/WhatsApp │  │
│  └───────────────────┘  └───────────────────┘  └──────────────────┘  └──────────────┘  │
└───────────────────────┬───────────────────────────────────────┬────────────────────────┘
                        │                                       │
                        ▼                                       ▼
             DATA & PERSISTENCE LAYER                 AI & MACHINE LEARNING PIPELINE
┌──────────────────────────────────────────────┐  ┌──────────────────────────────────────┐
│       PostgreSQL 16 + PostGIS Extension      │  │  1. PyTorch Visual Classifier        │
│  - Spatial Geometries (Point, Polygon 4326)  │  │     MobileNetV3 / ResNet-18 (LSD)    │
│  - GIST Spatial Indexing (ST_DWithin)        │  │     + OpenCV Image Quality Filter    │
│  - Relational Schemas: Users, Farms, Animals,│  │  2. Scikit-Learn Symptom Model       │
│    Records, Screenings, Predictions, Cases,  │  │     Gradient Boosting (6 Diseases)   │
│    Vaccinations, Clusters, Alerts, Audits    │  │  3. Isolation Forest Anomaly Checker │
│                                              │  │     Vitals Outliers & Drop Detection │
│  ┌────────────────────────────────────────┐  │  │  4. Geospatial & Environmental Model │
│  │ Fallback Mode: Local Sandbox Engine    │  │  │     LSD Weather & Vector Risk Index  │
│  │ (stateless JSON store for zero-config) │  │  │  5. Multi-Modal Fusion Synthesizer   │
│  └────────────────────────────────────────┘  │  │     Fused Risk Index (0-100) + SHAP  │
└──────────────────────────────────────────────┘  └──────────────────────────────────────┘
```

---

## 3. Core Functional Modules

### 1. Animal Registration & Digital Health Passport (QR-Based)
- **Unique Identification**: Each registered animal receives a globally unique `tag_id` and a UUID-backed QR code.
- **Digital Health Passport**: A printable and exportable digital card displaying:
  - Animal demographics (Breed, Age, Gender, Species, Farm ID).
  - Complete vaccination history with batch numbers and upcoming booster dates.
  - Historical health log (past diagnoses, verified clinical treatments, vital baselines).
  - Dynamic QR code that, when scanned by field veterinarians or checkpoint officers, immediately resolves the live health status of the animal.

### 2. Multi-Modal AI Health Screening Pipeline

The diagnostic intelligence is organized as an ensemble of 4 distinct analytical layers:

```
[ Farm Input: Symptoms ]    [ Animal Photo ]       [ Physiological Vitals ]    [ Geospatial Coordinates ]
           │                       │                          │                           │
           ▼                       ▼                          ▼                           ▼
┌──────────────────────┐ ┌──────────────────────┐ ┌──────────────────────┐  ┌───────────────────────────┐
│ Scikit-Learn Tabular │ │ PyTorch Image Model  │ │ Isolation Forest     │  │ Environmental Risk Engine │
│ Gradient Boosting    │ │ MobileNetV3 / CNN    │ │ Vitals Anomaly Model │  │ Temp, Humidity, Rain,     │
│ Symptom Classifier   │ │ Visual Lesion Score  │ │ Unsupervised Outlier │  │ Vector Breeding Potential │
└──────────┬───────────┘ └──────────┬───────────┘ └──────────┬───────────┘  └─────────────┬─────────────┘
           │                        │                        │                            │
           │ (Weight: 45%)          │ (Weight: 25%)          │ (Weight: 15%)              │ (Weight: 15%)
           └────────────────────────┼────────────────────────┴────────────────────────────┘
                                    │
                                    ▼
                 ┌──────────────────────────────────────┐
                 │    MULTI-MODAL FUSION SYNTHESIZER    │
                 │ - Computes Fused Risk Score (0-100)  │
                 │ - Clinical Safety Override Engine    │
                 │ - Generates SHAP Feature Drivers     │
                 │ - Derives Clinical Severity Level    │
                 └──────────────────┬───────────────────┘
                                    │
                  ┌─────────────────┴─────────────────┐
                  ▼                                   ▼
        [ Low Risk (<40) ]                 [ Moderate / High (≥40) ]
        - Preventive care tips             - Immediate quarantine instructions
        - Schedule monitoring              - Automatic suspected case generation
                                           - Urgent veterinary alert dispatch
```

#### A. PyTorch Visual Lesion Classifier
- **Image Pre-Validation**: OpenCV pipeline checks resolution ($\ge 256\times 256$), file size ($\le 10$ MB), illumination (mean intensity between 40 and 225), and focus blur via Laplacian variance ($\text{Var} \ge 50.0$).
- **Deep Visual Screening**: Pre-trained deep convolutional neural network (MobileNetV3-Small fine-tuned for bovine dermatological lesions) identifying:
  - Nodular circumscribed lesions (Lumpy Skin Disease pathognomonic sign).
  - Epithelial erosions and vesicles (Foot-and-Mouth Disease).
  - Healthy hide baseline.
- **Output**: Visual abnormality probability ($0.0 - 1.0$), detected lesion count, and visual severity category.

#### B. Symptom-Based Multi-Disease Classifier
- **Input Features**: 10 clinical symptoms (Fever, Cough, Loss of appetite, Milk drop, Nasal discharge, Diarrhea, Breathing difficulty, Skin nodules, Swelling, Lethargy) + 5 demographic covariates (Age, Breed, Gender, History, Vaccination status).
- **Model**: Multi-class Gradient Boosting Classifier trained with stratified k-fold cross-validation.
- **Target Conditions**:
  1. Healthy
  2. Lumpy Skin Disease (LSD)
  3. Foot-and-Mouth Disease (FMD)
  4. Mastitis
  5. Bovine Respiratory Disease (BRD)
  6. Brucellosis
- **Output**: Multi-class probability distribution, primary disease prediction, and baseline symptom score ($0 - 100$).

#### C. Physiological Vital Sign Anomaly Detector
- **Model**: Unsupervised Isolation Forest trained on normal bovine baseline parameters:
  - Rectal temperature: $38.0^\circ\text{C} - 39.5^\circ\text{C}$
  - Daily milk yield: $12 - 25\text{ L/day}$
  - Appetite status & Activity level (categorical index)
- **Output**: Binary anomaly flag ($\text{is\_anomaly}$) and continuous anomaly score ($0.0 - 1.0$).
- **Safety Overrides**: If temperature exceeds $40.2^\circ\text{C}$ or milk yield drops $>70\%$, anomaly flag is set to `True` unconditionally.

#### D. Environmental & Geospatial LSD Risk Engine
- **Rationale**: Lumpy Skin Disease transmission is strongly correlated with vector populations (biting flies *Stomoxys calcitrans*, mosquitoes *Aedes aegypti*, and *Rhipicephalus* ticks), driven by temperature, precipitation, and relative humidity.
- **Formula**:
  $$\text{EnvRisk} = w_1 \cdot f(\text{Temp}) + w_2 \cdot f(\text{Humidity}) + w_3 \cdot f(\text{Rainfall}) + w_4 \cdot \text{ProximityToWaterBodies}$$
- **Output**: Geospatial Environmental Risk Multiplier ($0.0 - 1.0$).

#### E. Multi-Modal Fusion Synthesizer
- **Fused Risk Score ($S$)**:
  $$S = \min\left(100, \; 0.45 \cdot S_{\text{symptom}} + 0.25 \cdot (P_{\text{visual}} \times 100) + 0.15 \cdot (A_{\text{vital}} \times 100) + 0.15 \cdot (\text{EnvRisk} \times 100)\right)$$
- **Deterministic Clinical Overrides**:
  - If visual skin lesions confirmed **AND** fever $>40.0^\circ\text{C}$, minimum risk score is clamped to **$80.0$ (HIGH)**.
  - If breathing difficulty is active with fever, clinical severity is locked to **SEVERE**.
- **Explainable AI (XAI)**: SHAP TreeExplainer computes the exact percentage contribution of each feature to the final prediction, returned to the farmer and veterinarian.

---

### 3. Spatial Outbreak Detection & Early Warning

```
               [ Suspected & Verified Disease Cases ]
                                │
                                ▼
         ┌──────────────────────────────────────────────┐
         │     PostGIS Temporal & Spatial Query         │
         │ - Filter cases in last 14 days by disease    │
         │ - Extract Coordinates: ST_X(geom), ST_Y(geom)│
         └──────────────────────┬───────────────────────┘
                                │
                                ▼
         ┌──────────────────────────────────────────────┐
         │         DBSCAN Clustering Algorithm          │
         │ - Epsilon (ε): 5.0 km (Configurable by Admin)│
         │ - MinPts (Min Cases): 3 cases                │
         │ - Metric: Haversine / Great-Circle Distance  │
         └──────────────────────┬───────────────────────┘
                                │
                                ▼
         ┌──────────────────────────────────────────────┐
         │           Cluster Geometric Synthesis        │
         │ - Centroid: ST_Centroid(ST_Collect(geom))    │
         │ - Radius: Max distance from centroid         │
         │ - Warning Zone: ST_Buffer(centroid, radius)  │
         │ - Affected Farms: Distinct farm_id count     │
         └──────────────────────┬───────────────────────┘
                                │
                                ▼
         ┌──────────────────────────────────────────────┐
         │            Multi-Tier Alert Dispatch         │
         │ 1. Officer Dashboard: Active Cluster Map     │
         │ 2. Vet Notification: Containment Protocols   │
         │ 3. Farmer SMS/App Warning: Ring-Fence Notice │
         └──────────────────────────────────────────────┘
```

---

## 4. User Role Portals & Capabilities

| Feature | Farmer | Veterinarian | Husbandry Officer | Administrator |
|---|:---:|:---:|:---:|:---:|
| **Animal Registration & Herd List** | Full (Own) | Read (All) | Read (All) | Full (All) |
| **Digital Health Passport & QR View** | Yes | Yes | Yes | Yes |
| **Run Multi-Modal Health Assessment** | Yes | Yes | No | No |
| **Voice-to-Text Input (Marathi/Hindi)**| Yes | No | No | No |
| **Offline IndexedDB Auto-Sync** | Yes | No | No | No |
| **Clinical Verification & Prescriptions**| No | Full | No | No |
| **Regional Geospatial Risk Map** | Herd Pins | Regional Pins | Statewide GIS | Statewide GIS |
| **DBSCAN Outbreak Cluster Detection** | No | View Clusters | Trigger & View | Configure & View |
| **Official Quarantine Notice Generator**| No | No | Generate & Sign | View |
| **SMS/WhatsApp Alert Simulation** | Receive | Receive | Dispatch & Preview| Configure |
| **Threshold & ML Parameter Tuning** | No | No | No | Full |
| **Audit Logs & ML Accuracy Monitoring** | No | No | View | Full |

---

## 5. Offline-First Resilience Architecture

1. **Client-Side Storage**: In remote rural areas with intermittent cellular coverage, all submitted health assessments are stored in the browser's native **IndexedDB** (`sentinel_offline_db`, object store: `pending_assessments`).
2. **Visual Status Feedback**:
   - `SYNCED`: Green badge, zero pending records.
   - `OFFLINE`: Amber badge, displaying count of pending local records.
   - `SYNCING`: Spinning indicator during active transmission.
3. **Reconnection Listener**: A window event listener (`online`) automatically executes the sync pipeline as soon as network packets are restored, re-submitting records in FIFO order with authorization headers.
4. **Offline Map Graceful Degradation**: Map marker coordinates are stored locally; if OpenStreetMap tile servers are unreachable, pins are rendered on an SVG grid with coordinate callouts.

---

## 6. Security, Compliance & Data Governance

1. **Authentication**: JWT (JSON Web Tokens) with HS256 signature and 60-minute expiration.
2. **Password Security**: Bcrypt with salted rounds ($2^{12}$).
3. **Role-Based Access Control (RBAC)**: Enforced via FastAPI dependency injection (`RoleChecker(["VETERINARIAN", "ADMIN"])`).
4. **Data Privacy**: Farmers cannot view records or locations of other farmers' herds; geospatial data at the public level is obfuscated to village/taluka centroids to preserve farmer privacy.
5. **Audit Trail**: Every critical action (`CREATE_ANIMAL`, `VERIFY_CASE`, `UPDATE_CONFIG`, `DISPATCH_CONTAINMENT`) writes an immutable record to the `audit_logs` table with username, timestamp, and action parameters.

---

## 7. Technology Stack Summary

- **Frontend**: React 19, Vite, Tailwind CSS, React Router v7, React Leaflet, Lucide Icons, Recharts, IndexedDB API, Web Speech API.
- **Backend**: Python 3.10+, FastAPI, Uvicorn, Pydantic v2, SQLAlchemy 2.0.
- **Database**: PostgreSQL 16 with PostGIS spatial extension (with automatic local JSON sandbox fallback).
- **Machine Learning**: PyTorch (MobileNetV3 for image lesion analysis), Scikit-Learn (Gradient Boosting for symptoms, Isolation Forest for vitals, DBSCAN for clusters), SHAP (Explainable AI), OpenCV (Image quality validation).
- **Mapping**: OpenStreetMap tile layer, React Leaflet vector layers (CircleMarker, Polygon buffer).
