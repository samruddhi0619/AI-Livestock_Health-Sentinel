# Utility Scripts (`scripts/`)

This directory contains developer automation, database initialization, model training, and smoke-testing scripts for the AI-Livestock Health Sentinel.

## Script Catalog

| Script | Platform | Purpose |
|---|---|---|
| `run_dev.bat` | Windows CMD | Launches both FastAPI backend (`http://localhost:8000`) and Vite frontend (`http://localhost:5173`) in concurrent terminal windows. |
| `run_dev.ps1` | Windows PowerShell | PowerShell script launching both development servers. |
| `seed_database.py` | Python 3 | Seeds the demo database with 5 accounts (`farmer_a`, `farmer_b`, `vet_officer`, `gov_officer`, `admin_user`), 9 cattle records, historical assessments, and an active Lumpy Skin Disease cluster. |
| `train_all_models.py` | Python 3 | Trains and persists the Gradient Boosting symptom model and the Isolation Forest vitals anomaly model into `ml/models/`. |
| `verify_system.py` | Python 3 | End-to-end smoke test verifying database connectivity, symptom ML prediction, SHAP drivers, vital anomaly detection, environmental risk scoring, and DBSCAN cluster detection. |
