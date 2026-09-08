# Symptom-Based Multi-Disease Prediction (`ml/symptom_prediction`)

This module houses the tabular machine learning models for early disease screening and risk classification.

## Features
- **Pre-processing (`preprocess.py`)**: Vectorizes 10 clinical symptoms and 5 animal demographics into normalized numeric feature vectors.
- **Ensemble Training (`train_xgboost.py`)**: Trains Gradient Boosting and Random Forest multi-class classifiers across 6 conditions:
  - *Healthy*
  - *Lumpy Skin Disease*
  - *Foot-and-Mouth Disease*
  - *Mastitis*
  - *Bovine Respiratory Disease*
  - *Brucellosis*
- **Prediction Engine (`predict.py`)**: Computes multi-class probability vectors, maps probabilities to a continuous $0 - 100$ risk score, assigns risk levels (`LOW`, `MODERATE`, `HIGH`), and determines clinical severity (`MILD`, `MODERATE`, `SEVERE`) with deterministic medical overrides.
- **Explainable AI (`explain.py`)**: Employs SHAP TreeExplainer to produce interpretable percentage feature attributions for farmers and veterinarians.
