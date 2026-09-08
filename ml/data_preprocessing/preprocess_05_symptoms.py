import os
import zipfile
import json
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

from base_preprocessor import ensure_dir, stratified_split_indices

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ZIP_PATH = os.path.join(ROOT_DIR, "datasets", "05_Cattle_Health_Feeding_Records.zip")
OUTPUT_DIR = os.path.join(ROOT_DIR, "datasets", "processed", "05_symptoms")

RANDOM_SEED = 42

def process_dataset_05():
    print("==========================================================")
    print("PREPROCESSING DATASET 05: Cattle Health Feeding & Symptoms")
    print("==========================================================")
    
    if not os.path.exists(ZIP_PATH):
        raise FileNotFoundError(f"Source archive not found: {ZIP_PATH}")
        
    ensure_dir(OUTPUT_DIR)
    
    with zipfile.ZipFile(ZIP_PATH, 'r') as z:
        with z.open('animal_disease_dataset.csv') as f:
            df = pd.read_csv(f)
            
    print(f"Loaded raw dataset shape: {df.shape}")
    
    # 1. Temperature Unit Conversion: Fahrenheit -> Celsius
    # System vitals expect Celsius (38-42 C). Raw values are 100.5 - 105.0 F.
    df['Temperature_C'] = round((df['Temperature'] - 32.0) * (5.0 / 9.0), 2)
    df = df.drop(columns=['Temperature'])
    print(f"Converted Temperature to Celsius. Range: {df['Temperature_C'].min()}C to {df['Temperature_C'].max()}C")
    
    # 2. Extract unique clinical symptoms across all 3 slots
    all_symptoms = set(df['Symptom 1'].dropna().unique()) | set(df['Symptom 2'].dropna().unique()) | set(df['Symptom 3'].dropna().unique())
    all_symptoms = sorted(list(all_symptoms))
    print(f"Found {len(all_symptoms)} distinct clinical symptoms.")
    
    # 3. Create permutation-invariant binary multi-hot symptom matrix
    symptom_matrix = np.zeros((len(df), len(all_symptoms)), dtype=int)
    for i, s in enumerate(all_symptoms):
        s_match = (df['Symptom 1'] == s) | (df['Symptom 2'] == s) | (df['Symptom 3'] == s)
        symptom_matrix[:, i] = s_match.astype(int)
        
    symptom_cols = [f"sym_{s.lower().replace(' ', '_')}" for s in all_symptoms]
    symptom_df = pd.DataFrame(symptom_matrix, columns=symptom_cols)
    
    # 4. One-hot encode Animal species
    animal_dummies = pd.get_dummies(df['Animal'], prefix='animal', drop_first=False, dtype=int)
    
    # 5. Target Label Encoding
    diseases = sorted(df['Disease'].unique().tolist())
    disease_to_idx = {d: i for i, d in enumerate(diseases)}
    idx_to_disease = {i: d for i, d in enumerate(diseases)}
    y = df['Disease'].map(disease_to_idx).values
    
    # Combine feature dataframe
    features_df = pd.concat([df[['Age', 'Temperature_C']], animal_dummies, symptom_df], axis=1)
    
    print(f"Processed feature matrix: {features_df.shape[1]} features")
    print(f"Disease classes: {disease_to_idx}")
    
    # 6. Stratified Split (70% train, 15% val, 15% test)
    train_idx, val_idx, test_idx = stratified_split_indices(y, 0.70, 0.15, 0.15, RANDOM_SEED)
    
    X_train, y_train = features_df.iloc[train_idx].copy(), y[train_idx]
    X_val, y_val = features_df.iloc[val_idx].copy(), y[val_idx]
    X_test, y_test = features_df.iloc[test_idx].copy(), y[test_idx]
    
    # 7. Scale numeric features (Age, Temperature_C) fitted on train only
    scaler = StandardScaler()
    num_cols = ['Age', 'Temperature_C']
    scaler.fit(X_train[num_cols])
    
    X_train[num_cols] = scaler.transform(X_train[num_cols])
    X_val[num_cols] = scaler.transform(X_val[num_cols])
    X_test[num_cols] = scaler.transform(X_test[num_cols])
    
    # Re-attach target
    train_df = X_train.copy()
    train_df['target_disease'] = y_train
    
    val_df = X_val.copy()
    val_df['target_disease'] = y_val
    
    test_df = X_test.copy()
    test_df['target_disease'] = y_test
    
    # Export CSV splits
    train_df.to_csv(os.path.join(OUTPUT_DIR, "train.csv"), index=False)
    val_df.to_csv(os.path.join(OUTPUT_DIR, "val.csv"), index=False)
    test_df.to_csv(os.path.join(OUTPUT_DIR, "test.csv"), index=False)
    
    # Export encoders metadata
    meta = {
        "dataset_name": "05_Cattle_Health_Feeding_Records",
        "total_rows": len(df),
        "total_features": features_df.shape[1],
        "symptoms_encoded": symptom_cols,
        "disease_mapping": disease_to_idx,
        "scaler_params": {
            "features": num_cols,
            "mean": scaler.mean_.tolist(),
            "scale": scaler.scale_.tolist()
        },
        "train_rows": len(train_df),
        "val_rows": len(val_df),
        "test_rows": len(test_df)
    }
    with open(os.path.join(OUTPUT_DIR, "encoder_metadata.json"), "w") as jf:
        json.dump(meta, jf, indent=2)
        
    print(f"[SUCCESS] Dataset 05 processed. Saved to {OUTPUT_DIR}")
    print(f"Summary: {meta['total_rows']} rows, {meta['total_features']} features, {len(diseases)} disease classes.")

if __name__ == "__main__":
    process_dataset_05()
