# Machine Learning & AI Intelligence (`ml/`)

This directory contains the machine learning pipelines, deep learning vision models, physiological anomaly detectors, and geospatial clustering engines for the AI-Livestock Health Sentinel.

## Directory Structure

```
ml/
├── image_lsd/             # Visual screening for Lumpy Skin Disease (OpenCV + PyTorch)
│   ├── image_quality.py   # Resolution, blur (Laplacian variance), and illumination checks
│   ├── predict_image.py   # HSV thresholding and contour-based lesion scoring
│   └── README.md
├── symptom_prediction/    # Tabular multi-disease risk classifier (Gradient Boosting / XGBoost)
│   ├── preprocess.py      # Feature vector encoding (10 symptoms + 5 demographics)
│   ├── train_xgboost.py   # Training script with stratified k-fold cross-validation
│   ├── predict.py         # Multi-class inference and risk score mapper (0-100)
│   ├── explain.py         # SHAP TreeExplainer feature attributions
│   └── README.md
├── environmental_risk/    # Weather & vector breeding risk multiplier
│   ├── environmental_risk.py # Ambient temperature, relative humidity, and precipitation scoring
│   └── README.md
├── anomaly/               # Physiological vitals anomaly detector
│   └── isolation_forest.py # Unsupervised Isolation Forest tracking vital drops
├── outbreak/              # Regional epidemic surveillance
│   └── cluster_detection.py # DBSCAN spatio-temporal cluster detector
└── models/                # Serialized model binary checkpoints (.pkl, .pt)
```

## Model Artifacts & Git LFS
Trained model weights (`*.pkl`, `*.pt`, `*.pth`) are ignored from standard Git commits via `.gitignore`. In production, version these binaries using Git LFS or download them from a model registry.
