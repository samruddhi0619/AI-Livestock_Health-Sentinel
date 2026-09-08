# AI-Livestock Health Sentinel (SIH26128)

**Smart India Hackathon 2026 Prototype**  
*Theme: Agriculture, FoodTech & Rural Development (Software Category)*  
*Target: Livestock Disease Early-Warning, Risk Assessment & Spatial Surveillance*  
*Team: MetaMinds*  

---

## 1. Executive Summary & Core USP

### Unique Selling Proposition (USP):
> **AI Disease Detection + Risk Assessment + Location-Based Outbreak Alerts**

"We are not building just a livestock disease prediction system; we are building an integrated early-warning and health-management platform that connects animal-level risk assessment with farm-level and regional disease surveillance."

---

## 2. Production Directory Structure

```
AI-Livestock-Health-Sentinel/
├── backend/                  # FastAPI web server, routers, auth, and database layer
│   ├── routes/               # Modular REST API routers (auth, animals, assessment, etc.)
│   ├── data/                 # Sandbox JSON database store (zero-config fallback)
│   ├── auth.py               # JWT bearer auth & Bcrypt hashing
│   ├── database.py           # Dual-mode DB client (PostgreSQL/Mongo + fallback)
│   ├── main.py               # Application factory & CORS configuration
│   └── requirements.txt      # Backend dependencies
├── frontend/                 # Vite + React 19 SPA & PWA
│   ├── src/                  # Components, context, dashboards, and localization
│   └── package.json          # Frontend packages
├── ml/                       # Machine learning, deep vision, and spatial intelligence
│   ├── image_lsd/            # Lumpy Skin Disease visual screening (OpenCV + PyTorch)
│   ├── symptom_prediction/   # Tabular multi-disease risk classifier (Gradient Boosting)
│   ├── environmental_risk/   # Weather & vector breeding risk multiplier
│   ├── anomaly/              # Physiological vitals anomaly detector (Isolation Forest)
│   ├── outbreak/             # Spatio-temporal DBSCAN epidemic cluster detection
│   └── models/               # Model binary checkpoints (.pkl, .pt)
├── database/                 # Production PostgreSQL + PostGIS schemas and seeds
│   ├── schema.sql            # Relational DDL & GIST spatial indexes
│   └── seed_demo.sql         # Seed records for demonstration
├── datasets/                 # Reference data schemas and synthetic data generators
│   ├── generate_dataset.py   # Reproducible synthetic dataset generator
│   └── sample_cattle_symptoms.csv # Demonstration sample dataset
├── docs/                     # Comprehensive architectural & design specifications
│   ├── PROJECT_ANALYSIS.md   # Full codebase audit & upgrade roadmap
│   ├── SYSTEM_ARCHITECTURE.md# End-to-end multi-modal architecture
│   ├── DATABASE_DESIGN.md    # PostgreSQL + PostGIS ER model & queries
│   └── API_PLAN.md           # RESTful API specifications (11 domains)
├── scripts/                  # Developer automation and deployment scripts
│   ├── run_dev.bat           # One-click Windows launch (Backend + Frontend)
│   ├── run_dev.ps1           # PowerShell dev runner
│   ├── seed_database.py      # Demo database population script
│   ├── train_all_models.py   # Multi-model training pipeline
│   └── verify_system.py      # End-to-end system smoke tests
├── uploads/                  # User symptom photo upload staging
├── requirements.txt          # Root Python dependencies
└── .gitignore                # Comprehensive ignore rules (models, node_modules, datasets)
```

---

## 3. Quick Start Guide

### Prerequisites
- Python 3.10+
- Node.js 18+

### Step 1: Install Dependencies
```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Frontend dependencies
cd frontend && npm install && cd ..
```

### Step 2: Initialize / Seed Demo Database
```bash
python scripts/seed_database.py
```

### Step 3: Run the Development Servers
**Option A (One-Click Windows Script):**
```bash
scripts\run_dev.bat
```

**Option B (Manual Launch):**
```bash
# Terminal 1 - Backend (FastAPI on Port 8000)
cd backend && uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2 - Frontend (Vite on Port 5173)
cd frontend && npm run dev
```

- **Web Application**: [http://localhost:5173](http://localhost:5173)
- **Interactive Swagger API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 4. Demo User Credentials (Password: `sih2026`)

| Role | Username | Description |
|---|---|---|
| **Farmer (Farm A)** | `farmer_a` | Ramesh Patil (Wadgaon, Pune) - Herd management & AI assessment |
| **Farmer (Farm B)** | `farmer_b` | Suresh Jadhav (Wadgaon, Pune) - Neighboring farm in outbreak zone |
| **Veterinarian** | `vet_officer` | Dr. Sunita Bhave - Clinical triage queue & prescriptions |
| **Husbandry Officer** | `gov_officer` | Rajesh Deshmukh (IAS) - Statewide surveillance & DBSCAN alerts |
| **System Administrator** | `admin_user` | Model parameter tuning & security audit logs |

---

## 5. System Verification Smoke Tests

To verify that all database, machine learning, and geospatial components are operating correctly:
```bash
python scripts/verify_system.py
```

---

## 6. Official Government References

- [Department of Animal Husbandry & Dairying (DAHD)](https://dahd.gov.in)
- [National Animal Disease Control Programme (NADCP)](https://dahd.gov.in/schemes/programmes/nadcp)
- [Indian Council of Agricultural Research (ICAR)](https://www.icar.gov.in)
- [ICAR - National Institute of Veterinary Epidemiology and Disease Informatics (NIVEDI)](https://nivedi.res.in)
