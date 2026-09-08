# Comprehensive Project Analysis: AI-Livestock Health Sentinel (SIH26128)

**Project Name:** AI-Livestock Health Sentinel  
**Problem Statement ID:** SIH26128  
**Theme:** Agriculture, FoodTech & Rural Development  
**Target Beneficiaries:** Smallholder Farmers, Veterinary Officers, District Animal Husbandry Commissioners  
**Repository:** [github.com/samruddhi0619/AI-Livestock_Health-Sentinel](https://github.com/samruddhi0619/AI-Livestock_Health-Sentinel)  
**Date of Analysis:** September 2026  

---

## 1. Current Project Architecture

The **AI-Livestock Health Sentinel** is designed as a four-tier distributed livestock health intelligence platform that combines animal-level diagnostic support with regional spatio-temporal epidemic surveillance.

```
┌────────────────────────────────────────────────────────────────────────┐
│                          1. CLIENT / UI TIER                           │
│  Vite + React 19 SPA (React Router v7, Lucide Icons, Recharts, Leaflet)│
│  - Role-Specific Views: Farmer | Veterinarian | Officer | Admin        │
│  - Offline Layer: IndexedDB ('sentinel_offline_db') with Auto-Sync    │
│  - Localization: English / Marathi ('en.json', 'mr.json')              │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ HTTP / JSON (REST + JWT Bearer)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                         2. API & GATEWAY TIER                          │
│  FastAPI (Python 3.10+) + Uvicorn ASGI Server                          │
│  - Security: PyJWT (HS256) + Raw Bcrypt Password Hashing               │
│  - RBAC Middleware: RoleChecker ([FARMER, VETERINARIAN, OFFICER, ADMIN])│
│  - Static Asset Serving: /uploads for skin lesion imagery              │
│  - Routers: auth, animals, assessment, cases, vaccinations,            │
│             outbreaks, dashboard, admin                                │
└───────────────────┬────────────────────────────────┬───────────────────┘
                    │                                │
                    ▼                                ▼
┌──────────────────────────────────────┐ ┌───────────────────────────────┐
│           3. DATA TIER               │ │       4. AI / ML TIER         │
│  Hybrid Storage Engine               │ │  Scikit-Learn, SHAP, OpenCV   │
│  - Primary: MongoDB Atlas / Local    │ │  - Symptom Classifier         │
│    (pymongo / motor driver)          │ │    (GradientBoosting / XGB)   │
│  - Fallback: Local JSON Sandbox DB   │ │  - Vital Anomaly Detector     │
│    ('backend/data/db.json' via       │ │    (Isolation Forest)         │
│    stateless MockDatabase client)    │ │  - Explainability Engine      │
│  - Collections: users, animals,      │ │    (TreeExplainer / Weights)  │
│    health_records, predictions,      │ │  - Hide Lesion Analyzer       │
│    disease_cases, vaccinations,      │ │    (OpenCV HSV + Contours)    │
│    alerts, outbreak_clusters,        │ │  - Outbreak Cluster Detector  │
│    audit_logs, system_config         │ │    (DBSCAN Spatio-Temporal)   │
└──────────────────────────────────────┘ └───────────────────────────────┘
```

### Architectural Highlights
- **Dual Database Strategy**: Gracefully falls back to a file-based JSON database engine (`backend/data/db.json`) if MongoDB is unavailable, guaranteeing that evaluators and hackathon judges can run the system immediately without database setup.
- **Offline-First Data Pipeline**: Employs browser-native IndexedDB to queue assessments during rural connectivity loss, displaying an explicit "Sync Pending" badge and syncing when connectivity returns.
- **Multi-Modal Decision Fusion**: Combines clinical symptom classification, vital sign anomaly detection, and visual skin lesion contouring into an integrated risk score (0–100) with clinical override safety constraints.

---

## 2. Existing Features (Already Implemented)

### A. Role-Based Portals & Authentication
- **Multi-Role Authentication**: Secure login and registration with four distinct roles:
  - `FARMER`: Manages herd, registers livestock, records health assessments, views vaccination schedules.
  - `VETERINARIAN`: Clinical triage queue for suspected high-risk cases, writes formal diagnoses, prescribes treatment plans, sets follow-up dates.
  - `OFFICER`: Statewide surveillance overview, 7-day epidemiological trend line, disease prevalence distribution, taluka/village case breakdown, active outbreak clusters.
  - `ADMIN`: User accounts directory, dynamic system risk threshold tuning, DBSCAN hyperparameter configuration, ML model performance monitoring, security audit logs.
- **Pre-Seeded Hackathon Accounts**: Ready-to-demo credentials (`sih2026`) for `farmer_a`, `farmer_b`, `vet_officer`, `gov_officer`, and `admin_user`.

### B. Livestock Registry & Herd Management
- Registration of cattle with species, breed (Gir, Sahiwal, Holstein Friesian, Jersey, Indigenous), age, gender, medical history, farm identifier, and village/taluka/district coordinates.
- Role-scoped visibility: Farmers only see their own herd; Vets, Officers, and Admins view all registered animals across the jurisdiction.

### C. Multi-Modal AI Health Assessment
- **Symptom Classifier**: Gradient Boosted Decision Trees trained on clinical symptom profiles across 6 health classes:
  - *Healthy*, *Lumpy Skin Disease (LSD)*, *Foot-and-Mouth Disease (FMD)*, *Mastitis*, *Bovine Respiratory Disease (BRD)*, and *Brucellosis*.
  - Achieves **90.8% test accuracy** and **0.906 F1-Score**.
- **Vital Sign Anomaly Detector**: Unsupervised Isolation Forest tracking body temperature, appetite status, milk yield (L/day), and physical activity. Identifies sub-clinical vital drops before physical symptoms appear.
- **Explainable AI (XAI)**: SHAP (SHapley Additive exPlanations) TreeExplainer integration providing human-interpretable percentage contributions for each symptom driver (e.g., *Skin Abnormalities +35%*, *Fever +24%*).
- **OpenCV Lesion Scanner**:
  - Validates photo upload quality: file size (<10MB), minimum resolution (256x256), brightness bounds (40–225), and blur detection via Laplacian variance (threshold: 50.0).
  - Segments cutaneous nodules and crusty scabs via dual HSV color masks, applies morphological opening/closing filters, extracts contours, and computes affected hide area ratio.
- **Automatic Veterinary Case Escalation**: Assessments resulting in `MODERATE` or `HIGH` risk automatically generate a suspected `disease_case` record and dispatch a high-priority alert to the local veterinary officer.

### D. Regional Outbreak Surveillance & GIS Mapping
- **DBSCAN Spatio-Temporal Clustering**: Groups cases by specific disease within a 14-day rolling window, calculates geospatial distance matrices (1° ≈ 111 km), computes cluster centroids, warning radius, and affected farm counts.
- **Interactive Leaflet GIS Map (`DiseaseMap.jsx`)**: Color-coded risk markers (Red: High, Yellow: Moderate, Green: Low), solid borders for verified diagnoses, and dashed concentric red circles visualizing active outbreak cluster zones with popup metadata.

### E. Offline Resilience & Bilingual Support
- **IndexedDB Storage**: Saves assessments locally if internet connectivity is dropped or if the backend is unreachable.
- **Automatic & Manual Synchronization**: Automatically retries sync when the browser `online` event fires; includes a manual sync reload button in the sidebar.
- **Bilingual Interface**: Seamless instant toggle between English and Marathi (`मराठी`), covering application labels, symptoms, and clinical advice.

---

## 3. Missing Features Required for the Final SIH Prototype

To transform this solid prototype into a winning Smart India Hackathon submission, the following high-impact features are required:

| # | Missing Feature | Purpose & Value for SIH Evaluation | Priority |
|---|-----------------|------------------------------------|----------|
| **1** | **Voice-to-Text Symptom Input (Marathi/Hindi/English)** | Rural farmers often have limited literacy. A microphone button allowing the farmer to speak symptoms in Marathi or Hindi directly populates checkboxes. | **CRITICAL** |
| **2** | **Exportable Livestock Health Card & Quarantine Notice (PDF/Print)** | Farmers need a downloadable "Animal Health Passport" (with QR Code). Officers need a one-click official "Epidemic Containment Circular / Movement Restriction Notice" for local police checkpoints. | **HIGH** |
| **3** | **Simulated SMS / WhatsApp Alert Dispatch** | Rural early-warning systems must reach farmers without smartphones. Adding an SMS/WhatsApp dispatch simulator (mock or Twilio-backed) displaying notification payloads sent to registered phone numbers. | **HIGH** |
| **4** | **IoT Collar / Ear-Tag Real-Time Telemetry Simulator** | Demonstrates smart-farming readiness. A real-time simulator that streams live sensor data (temperature, rumination minutes, step count) with anomaly threshold alerts. | **HIGH** |
| **5** | **Mobile Responsive / Progressive Web App (PWA) Manifest** | Allows farmers to install the app on Android phones like a native application with an offline service worker. | **HIGH** |
| **6** | **Weather & Vector-Borne Outbreak Risk Multiplier** | Integrates rainfall/humidity factors (or Open-Meteo API) to adjust Lumpy Skin Disease (mosquito/tick vector) and FMD risk scores based on local weather. | **MEDIUM** |
| **7** | **Veterinary Teleconsultation & Prescription Chat** | In-app messaging or structured advice thread between the farmer and the verifying veterinarian. | **MEDIUM** |
| **8** | **Cattle Breed Photo Identification (Transfer Learning)** | Automatic breed identification from the uploaded image (e.g. distinguishing Gir from Jersey) using MobileNet. | **MEDIUM** |

---

## 4. Problems and Technical Debt

### A. Missing `requirements.txt`
- **Issue**: The README refers to `pip install -r requirements.txt`, but no `requirements.txt` file exists in either the root or `backend/` directory.
- **Impact**: New evaluators or team members must guess dependencies (`fastapi`, `uvicorn`, `scikit-learn`, `bcrypt`, `pyjwt`, `opencv-python`, `shap`, `pandas`, `numpy`).

### B. Python 3.12+ Deprecation Warnings
- **Issue**: Multiple files (`generate_demo_data.py`, `assessment.py`, `cases.py`, `outbreaks.py`) use `datetime.utcnow()`.
- **Impact**: Python 3.12+ outputs `DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal`. Should be replaced with `datetime.now(timezone.utc)`.

### C. Hardcoded Localhost API URLs
- **Issue**: `API_BASE_URL = 'http://localhost:8000'` is hardcoded in `AuthContext.jsx`.
- **Impact**: Deploying the frontend to Vercel, Netlify, or running on a local network for mobile phone testing breaks API connectivity. Needs `import.meta.env.VITE_API_URL || 'http://localhost:8000'`.

### D. File-Based Database Concurrency Risk
- **Issue**: `MockDatabase` in `database.py` reads and writes `backend/data/db.json` on every request without cross-thread or cross-process file locks.
- **Impact**: Rapid concurrent submissions (e.g., multi-record sync) can cause JSON read/write race conditions or file corruption.

### E. CDN-Dependent Map Assets
- **Issue**: `DiseaseMap.jsx` loads Leaflet marker images and tile layers from `https://unpkg.com` and `https://{s}.tile.openstreetmap.org`.
- **Impact**: If the laptop loses internet during a live hackathon demo, the map view will fail to render tile backgrounds. Needs offline fallback caching or embedded SVG markers.

### F. Partial Marathi Localization
- **Issue**: While `mr.json` contains core keys, many sub-views, table headers, and guidance strings in `FarmerDashboard.jsx` and `OfficerDashboard.jsx` still contain hardcoded English strings.

---

## 5. Recommended Improvements

### Immediate Fixes
1. **Create `backend/requirements.txt`**: Pin exact, tested versions of all backend packages.
2. **Environment Variable Integration**: Use `VITE_API_URL` in `frontend/.env` to allow seamless switching between `localhost:8000` and cloud deployment URLs.
3. **Timezone-Aware Timestamps**: Refactor all `datetime.utcnow()` to `datetime.now(timezone.utc)`.
4. **File Locking in `MockCollection`**: Implement Python's `threading.Lock` or filelock mechanism to safeguard `db.json` from concurrent writes.

### UI / UX Enhancements
1. **PWA Support**: Add `manifest.json` and a service worker so the app can be installed on Android devices.
2. **Mobile Bottom Navigation**: Introduce a responsive bottom navigation bar on mobile screens (<768px) to replace the desktop sidebar.
3. **Toast Notification System**: Replace inline error banners with an animated toast system (e.g., success toasts on animal registration or case verification).

### Algorithmic & Analytical Upgrades
1. **Confidence Interval & Secondary Diagnosis**: Rather than displaying a single predicted disease, display top-2 differential diagnoses with confidence bars (e.g., *Primary: Lumpy Skin Disease (82%), Secondary: Foot-and-Mouth Disease (14%)*).
2. **Integrated Veterinary Decision Rules**: Augment the ML output with clinical guideline rules (e.g., if rectal temperature > 41°C, trigger an automatic "EMERGENCY HYPERTHERMIA" warning).

---

## 6. Step-by-Step Upgrade Plan for SIH 2026

```
  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
  │   PHASE 1    │ ──> │   PHASE 2    │ ──> │   PHASE 3    │ ──> │   PHASE 4    │
  │ Foundation & │     │ High-Impact  │     │ Surveillance │     │  Demo Polish │
  │ Stability    │     │ SIH Features │     │  & Telemetry │     │ & Pitch Pack │
  └──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
```

### Phase 1: Foundation & Technical Debt Cleanup
- [ ] Create clean, pinned `backend/requirements.txt` and `backend/.env.example`.
- [ ] Replace hardcoded `API_BASE_URL` in frontend with `import.meta.env.VITE_API_URL`.
- [ ] Fix all `datetime.utcnow()` deprecations across backend routers.
- [ ] Add thread locking to `database.py` file operations to prevent `db.json` corruption.
- [ ] Clean up temporary test scratch files (`test_post.py`, `test_internals.py`, `test_api_locally.py`, `read_db.py`, `test_seeder_step.py`).

### Phase 2: Farmer-Centric High-Impact Features
- [ ] **Web Speech API Voice Input**: Add a microphone button next to the symptoms checklist allowing farmers to speak their observations in Marathi or Hindi, auto-checking symptom tags.
- [ ] **Downloadable Animal Health Card (PDF)**: Generate a printable/downloadable digital animal health passport with animal details, vaccination history, and QR code verification link.
- [ ] **Full Marathi Localization**: Translate remaining dashboard strings and clinical guidance tips into `mr.json`.
- [ ] **Mobile-Responsive Optimization**: Implement mobile layout breakpoints with a bottom navigation bar for handheld devices.

### Phase 3: Veterinary & Surveillance Enhancements
- [ ] **SMS / WhatsApp Alert Dispatch Simulation**: Build an alert preview drawer in Officer/Vet dashboards displaying simulated SMS text and WhatsApp alert payloads sent to farmers in containment zones.
- [ ] **Official Outbreak Containment Notice Generator**: Create a one-click PDF/print quarantine order generator for District Husbandry Officers specifying restricted movement zones and bio-security protocols.
- [ ] **IoT Collar Telemetry Simulator**: Add a real-time vitals streaming demo widget in the farmer dashboard showing continuous temperature and step-count graphs with anomaly detection trigger points.

### Phase 4: AI/ML Robustness & Performance
- [ ] **Differential Diagnosis Probabilities**: Render a multi-class probability breakdown in the assessment results card showing top-3 disease likelihoods.
- [ ] **Weather Risk Integration**: Incorporate temperature and humidity indicators into the outbreak detection engine to compute vector-borne disease transmission potential.
- [ ] **Offline Leaflet Marker Resilience**: Embed base64/SVG map markers so the interactive map displays pins even with zero internet connectivity.

### Phase 5: Demo Readiness & Presentation Kit
- [ ] **One-Click Quick Start Script (`run_demo.bat` / `run_demo.ps1`)**: Single script that starts both backend and frontend simultaneously with automated browser launch.
- [ ] **Interactive Demo Scenarios Guide**: Step-by-step presentation script showing the complete workflow:
  1. *Farmer A reports high fever and skin nodules.*
  2. *AI triggers high-risk alert and saves offline if disconnected.*
  3. *Dr. Sunita Bhave (Vet) verifies the case and prescribes antibiotics.*
  4. *Farmer B reports similar symptoms 1 km away.*
  5. *Husbandry Officer runs DBSCAN, uncovering a live Wadgaon outbreak cluster.*
  6. *Officer issues containment order and dispatches SMS alerts.*
