import os
import zipfile
import json
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split

from base_preprocessor import ensure_dir

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ZIP_PATH = os.path.join(ROOT_DIR, "datasets", "06_Cattle_Disease_and_Health_Records.zip")
OUTPUT_DIR = os.path.join(ROOT_DIR, "datasets", "processed", "06_disease_telemetry")

RANDOM_SEED = 42

def process_dataset_06():
    print("==========================================================")
    print("PREPROCESSING DATASET 06: Global Cattle Disease & Vitals")
    print("==========================================================")
    
    if not os.path.exists(ZIP_PATH):
        raise FileNotFoundError(f"Source archive not found: {ZIP_PATH}")
        
    ensure_dir(OUTPUT_DIR)
    
    # 1. Load the Disease Detection CSV
    print("Loading global_cattle_disease_detection_dataset.csv (250k rows)...")
    with zipfile.ZipFile(ZIP_PATH, 'r') as z:
        with z.open('global_cattle_disease_detection_dataset.csv') as f:
            df = pd.read_csv(f)
            
    print(f"Loaded raw dataset shape: {df.shape}")
    
    # Drop pure ID and timestamp columns that would cause artificial memorization
    drop_cols = ['Cattle_ID', 'Date', 'Farm_ID']
    df_clean = df.drop(columns=drop_cols)
    
    target_col = 'Disease_Status'
    y_raw = df_clean[target_col].values
    
    # Encode target disease classes
    le_target = LabelEncoder()
    y = le_target.fit_transform(y_raw)
    disease_classes = le_target.classes_.tolist()
    print(f"Target classes count: {len(disease_classes)}")
    
    # Categorical columns
    cat_cols = ['Breed', 'Region', 'Country', 'Climate_Zone', 'Management_System', 'Lactation_Stage', 'Feed_Type', 'Season']
    
    # One-hot encode categorical features
    X_raw = df_clean.drop(columns=[target_col])
    X_encoded = pd.get_dummies(X_raw, columns=cat_cols, drop_first=True, dtype=int)
    feature_names = X_encoded.columns.tolist()
    print(f"Total features after one-hot encoding: {len(feature_names)}")
    
    # Continuous vital and production columns to scale
    continuous_cols = [
        'Age_Months', 'Weight_kg', 'Days_in_Milk', 'Feed_Quantity_kg', 'Water_Intake_L',
        'Walking_Distance_km', 'Grazing_Duration_hrs', 'Rumination_Time_hrs', 'Resting_Hours',
        'Body_Temperature_C', 'Heart_Rate_bpm', 'Respiratory_Rate', 'Ambient_Temperature_C',
        'Humidity_percent', 'Housing_Score', 'Milk_Yield_L', 'Previous_Week_Avg_Yield'
    ]
    
    # 2. Stratified Train / Validation / Test Split (70% / 15% / 15%)
    indices = np.arange(len(df_clean))
    train_idx, temp_idx, y_train, y_temp = train_test_split(
        indices, y, test_size=0.30, stratify=y, random_state=RANDOM_SEED
    )
    val_idx, test_idx, y_val, y_test = train_test_split(
        temp_idx, y_temp, test_size=0.50, stratify=y_temp, random_state=RANDOM_SEED
    )
    
    X_train = X_encoded.iloc[train_idx].copy()
    X_val = X_encoded.iloc[val_idx].copy()
    X_test = X_encoded.iloc[test_idx].copy()
    
    # 3. Fit scaler ONLY on train data
    scaler = StandardScaler()
    scaler.fit(X_train[continuous_cols])
    
    X_train[continuous_cols] = scaler.transform(X_train[continuous_cols])
    X_val[continuous_cols] = scaler.transform(X_val[continuous_cols])
    X_test[continuous_cols] = scaler.transform(X_test[continuous_cols])
    
    # 4. Save processed dataset splits (using CSV format)
    X_train[target_col] = y_train
    X_val[target_col] = y_val
    X_test[target_col] = y_test
    
    print(f"Exporting train ({len(X_train)}), val ({len(X_val)}), test ({len(X_test)}) splits...")
    X_train.to_csv(os.path.join(OUTPUT_DIR, "train.csv"), index=False)
    X_val.to_csv(os.path.join(OUTPUT_DIR, "val.csv"), index=False)
    X_test.to_csv(os.path.join(OUTPUT_DIR, "test.csv"), index=False)
    
    # Also save a 10k-sample CSV for lightweight inspector tools
    X_train.head(10000).to_csv(os.path.join(OUTPUT_DIR, "train_sample_10k.csv"), index=False)
    
    # 5. Extract and export healthy cattle vitals baseline for Isolation Forest Anomaly model
    healthy_label = le_target.transform(['Healthy'])[0]
    healthy_vitals = df_clean[df_clean[target_col] == 'Healthy'][['Body_Temperature_C', 'Heart_Rate_bpm', 'Respiratory_Rate', 'Rumination_Time_hrs', 'Milk_Yield_L']].copy()
    healthy_vitals.to_csv(os.path.join(OUTPUT_DIR, "healthy_vitals_baseline.csv"), index=False)
    print(f"Exported healthy vitals baseline ({len(healthy_vitals)} rows) for anomaly detector training.")
    
    # Export metadata and mappings
    meta = {
        "dataset_name": "06_Cattle_Disease_and_Health_Records",
        "total_rows": len(df_clean),
        "total_features": len(feature_names),
        "target_col": target_col,
        "disease_classes": {int(i): name for i, name in enumerate(disease_classes)},
        "continuous_cols_scaled": continuous_cols,
        "scaler_params": {
            "mean": scaler.mean_.tolist(),
            "scale": scaler.scale_.tolist()
        },
        "train_rows": len(X_train),
        "val_rows": len(X_val),
        "test_rows": len(X_test),
        "dropped_leakage_identifiers": drop_cols
    }
    with open(os.path.join(OUTPUT_DIR, "metadata.json"), "w") as jf:
        json.dump(meta, jf, indent=2)
        
    print(f"[SUCCESS] Dataset 06 processed. Saved to {OUTPUT_DIR}")

if __name__ == "__main__":
    process_dataset_06()
