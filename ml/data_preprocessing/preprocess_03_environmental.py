import os
import zipfile
import json
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

from base_preprocessor import ensure_dir, stratified_split_indices

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ZIP_PATH = os.path.join(ROOT_DIR, "datasets", "03_LSD_Environmental_Geospatial_Data.zip")
OUTPUT_DIR = os.path.join(ROOT_DIR, "datasets", "processed", "03_environmental")

RANDOM_SEED = 42

def process_dataset_03():
    print("==========================================================")
    print("PREPROCESSING DATASET 03: LSD Environmental & Geospatial Data")
    print("==========================================================")
    
    if not os.path.exists(ZIP_PATH):
        raise FileNotFoundError(f"Source archive not found: {ZIP_PATH}")
        
    ensure_dir(OUTPUT_DIR)
    
    # 1. Load CSV from zip
    with zipfile.ZipFile(ZIP_PATH, 'r') as z:
        with z.open('Lumpy skin disease data.csv') as f:
            df = pd.read_csv(f)
            
    print(f"Loaded raw dataset shape: {df.shape}")
    
    # 2. CRITICAL ANTI-LEAKAGE STEP:
    # 'region', 'country', and 'reportingDate' are populated only when lumpy == 1.
    # Discarding them to prevent artificial 100% accuracy shortcut.
    leakage_columns = ['region', 'country', 'reportingDate']
    df_cleaned = df.drop(columns=leakage_columns)
    print(f"Dropped leakage columns: {leakage_columns}")
    
    # 3. Categorical encoding for dominant_land_cover (1 to 12)
    # Using one-hot encoding
    df_encoded = pd.get_dummies(df_cleaned, columns=['dominant_land_cover'], prefix='land_cover', drop_first=True)
    
    # Separate features and target
    target_col = 'lumpy'
    feature_cols = [c for c in df_encoded.columns if c != target_col]
    
    X = df_encoded[feature_cols].copy()
    y = df_encoded[target_col].values
    
    print(f"Total features after encoding: {len(feature_cols)}")
    print(f"Class counts: 0 (Absence)={sum(y==0)}, 1 (Outbreak)={sum(y==1)}")
    
    # 4. Stratified Split (70% train, 15% val, 15% test)
    train_idx, val_idx, test_idx = stratified_split_indices(y, 0.70, 0.15, 0.15, RANDOM_SEED)
    
    X_train, y_train = X.iloc[train_idx].copy(), y[train_idx]
    X_val, y_val = X.iloc[val_idx].copy(), y[val_idx]
    X_test, y_test = X.iloc[test_idx].copy(), y[test_idx]
    
    # 5. Feature Scaling (Fitted ONLY on training data to prevent leakage)
    # Scale continuous climatic and density columns, keep coordinates and dummy flags unscaled or normalized
    continuous_cols = ['cld', 'dtr', 'frs', 'pet', 'pre', 'tmn', 'tmp', 'tmx', 'vap', 'wet', 'elevation', 'X5_Ct_2010_Da', 'X5_Bf_2010_Da']
    
    scaler = StandardScaler()
    scaler.fit(X_train[continuous_cols])
    
    X_train[continuous_cols] = scaler.transform(X_train[continuous_cols])
    X_val[continuous_cols] = scaler.transform(X_val[continuous_cols])
    X_test[continuous_cols] = scaler.transform(X_test[continuous_cols])
    
    # Combine with target for export
    train_df = X_train.copy()
    train_df[target_col] = y_train
    
    val_df = X_val.copy()
    val_df[target_col] = y_val
    
    test_df = X_test.copy()
    test_df[target_col] = y_test
    
    # Export splits
    train_df.to_csv(os.path.join(OUTPUT_DIR, "train.csv"), index=False)
    val_df.to_csv(os.path.join(OUTPUT_DIR, "val.csv"), index=False)
    test_df.to_csv(os.path.join(OUTPUT_DIR, "test.csv"), index=False)
    
    # Export scaler parameters
    scaler_params = {
        "features": continuous_cols,
        "mean": scaler.mean_.tolist(),
        "scale": scaler.scale_.tolist()
    }
    with open(os.path.join(OUTPUT_DIR, "scaler_params.json"), "w") as jf:
        json.dump(scaler_params, jf, indent=2)
        
    summary = {
        "dataset_name": "03_LSD_Environmental_Geospatial_Data",
        "total_rows": len(df_encoded),
        "total_features": len(feature_cols),
        "target": target_col,
        "train_rows": len(train_df),
        "val_rows": len(val_df),
        "test_rows": len(test_df),
        "class_imbalance_ratio": float(sum(y==0) / sum(y==1)),
        "leakage_dropped": leakage_columns,
        "scaling": "StandardScaler (fitted on train only)"
    }
    with open(os.path.join(OUTPUT_DIR, "summary.json"), "w") as jf:
        json.dump(summary, jf, indent=2)
        
    print(f"[SUCCESS] Dataset 03 processed. Saved to {OUTPUT_DIR}")
    print(f"Summary: {summary}")

if __name__ == "__main__":
    process_dataset_03()
