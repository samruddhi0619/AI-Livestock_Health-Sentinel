# AI-Livestock Health Sentinel (SIH26128)

**Smart India Hackathon 2026 Prototype**
*Theme: Agriculture, FoodTech & Rural Development (Software Category)*
*Sponsor: Government of Maharashtra*
*Team: MetaMinds*

---

## 1. Executive Summary & Core USP

### Unique Selling Proposition (USP):
> **AI Disease Detection + Risk Assessment + Location-Based Outbreak Alerts**

"We are not building just a livestock disease prediction system; we are building an integrated early-warning and health-management platform that connects animal-level risk assessment with farm-level and regional disease surveillance."

---

## 2. System Architecture

The AI-Livestock Health Sentinel implements a four-stage workflow:

```
[ FARMER INPUT ]
  - Animal demographics (Age, Breed, History)
  - Vitals (Temperature, Activity, Milk production)
  - Symptom checklist & Uploaded hide photos (with OpenCV quality checks)
  - GPS coordinates (Browser Geolocation / Manual fallbacks)
       ↓
[ AI HEALTH ASSESSMENT ]
  - Symptom-based gradient boosted classifier (accuracy: 90.8%)
  - OpenCV hide lesion contour analyzer
  - Isolation Forest anomaly checker for vitals drops
  - SHAP (Explainable AI) feature contribution attributions
       ↓
[ OUTBREAK DETECTION ]
  - DBSCAN spatial clustering grouped by disease
  - Time-window (14-day) epidemic density filters
  - Alerts triggers for "POTENTIAL DISEASE CLUSTERS"
       ↓
[ SYSTEM OUTPUTS ]
  - Farmer quarantine instructions & safety warnings
  - Prioritized Vet Case Verification queue
  - District / Taluka / Village geographic surveillance maps
  - Government resource trend graphs
```

---

## 3. Four Challenges and MetaMinds Solutions

1. **Challenge: Limited Livestock Disease Datasets**
   - *Solution*: Pre-trained modular features pipeline combined with rule-based synthetic datasets modeled on Maharashtra clinical censuses for prototype evaluation.
2. **Challenge: Incorrect Farmer Inputs**
   - *Solution*: Multilingual guided forms (English/Marathi switcher), strict input constraints, and automated vitals checking.
3. **Challenge: Poor Photo Upload Quality**
   - *Solution*: Real-time OpenCV validation checking for blur (Laplacian variance), low lighting/overexposure (mean pixel intensity), and resolution.
4. **Challenge: Internet Blackouts in Rural Areas**
   - *Solution*: Local browser-level IndexedDB database caching farmer logs. Automatically synchronizes ("PENDING SYNC" -> "SYNCED") with uvicorn backend upon restoring connectivity.

---

## 4. Technology Stack

- **Frontend**: React.js (Vite) + Recharts Analytics + Leaflet maps (OpenStreetMap) + Lucide Icons + CSS variables (Agricultural Theme).
- **Backend**: FastAPI (Python) + PyJWT Authentication + Role-Based Access Control (RBAC).
- **Database**: PyMongo / Motor client. **Automatic Fallback to JSON Database Engine (`backend/data/db.json`)** if MongoDB service is not running locally.
- **AI/ML/CV**: Scikit-Learn (Gradient Boosting, Random Forest, Isolation Forest, DBSCAN) + SHAP + OpenCV.

---

## 5. Directory Structure

```
ai-livestock-health-sentinel/
├── backend/                  # FastAPI web server, configurations, and API endpoints
├── ml/                       # ML/CV training, inference, and clustering modules
├── frontend/                 # Vite React source code, style assets, and localization
├── uploads/                  # Temporary image upload folders
├── README.md                 # System overview and instruction manual
└── .env.example              # Environment variables template
```

---

## 6. Official References

- [Department of Animal Husbandry, Dairying & Fisheries (DAHD)](https://dahd.gov.in/en/schemes-programmes/lhdcp)
- [National Animal Disease Control Programme (NADCP)](https://dahd.gov.in/schemes/programmes/nadcp)
- [Indian Council of Agricultural Research (ICAR)](https://www.icar.gov.in/en/animal-science/animal-science-division)
- [ICAR - National Institute of Veterinary Epidemiology and Disease Informatics (NIVEDI)](https://icar.gov.in/en/icar-secretary-visits-icar-nivedi-bengaluru-calls-strengthening-advanced-disease-intelligence)

---

## 7. Setup & Run Instructions

Ensure Node.js and Python 3.10+ are installed.

### Step 1: Pre-Train Machine Learning Models
```bash
# Train the classifiers
cd ml/symptom_model
python train_xgboost.py

# Train the anomaly isolation forest
cd ../anomaly
python isolation_forest.py
```

### Step 2: Seed the Database
```bash
cd ../../backend
# Seeds 17+ animals, alerts, vaccinations, and the Wadgaon/Pune outbreak cluster
python generate_demo_data.py
```

### Step 3: Run the FastAPI Server
```bash
# Inside backend directory
pip install -r requirements.txt   # (Ensure fastapi, uvicorn, scikit-learn, opencv-python, motor, pyjwt, bcrypt are installed)
uvicorn main:app --reload --port 8000
```
API documentation will be available at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

### Step 4: Run the Vite React Frontend
```bash
cd ../frontend
npm run dev
```
Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## 8. Demo User Credentials (Password: `sih2026`)

- **Farmer (Farm A)**: `farmer_a`
- **Farmer (Farm B)**: `farmer_b`
- **Veterinarian**: `vet_officer`
- **Husbandry Officer**: `gov_officer`
- **System Admin**: `admin_user`
