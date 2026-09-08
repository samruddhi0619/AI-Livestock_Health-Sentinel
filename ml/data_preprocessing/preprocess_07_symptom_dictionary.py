import os
import zipfile
import json
import re
import pandas as pd
from base_preprocessor import ensure_dir

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ZIP_PATH = os.path.join(ROOT_DIR, "datasets", "07_Animal_Symptoms_Disease_Prediction.zip")
OUTPUT_DIR = os.path.join(ROOT_DIR, "datasets", "processed", "07_symptom_dictionary")

def clean_temp(val):
    """Sanitizes corrupted temperature strings (e.g. '39.5C' -> 39.5)."""
    if pd.isnull(val):
        return None
    cleaned = re.sub(r'[^\d.]', '', str(val))
    try:
        return float(cleaned)
    except ValueError:
        return None

def normalize_symptom_name(sym):
    """Standardizes synonymous symptom descriptions."""
    if not isinstance(sym, str):
        return ""
    s = sym.strip().lower()
    if s in ['appetite loss', 'loss of appetite', 'reduced appetite']:
        return 'loss_of_appetite'
    if s in ['decreased milk yield', 'reduced milk production']:
        return 'reduced_milk_production'
    if s in ['labored breathing', 'breathing difficulty']:
        return 'breathing_difficulty'
    if s in ['skin lesions', 'skin abnormalities']:
        return 'skin_abnormalities'
    return s.replace(' ', '_')

def process_dataset_07():
    print("==========================================================")
    print("PREPROCESSING DATASET 07: Animal Symptoms & Disease Reference")
    print("==========================================================")
    
    if not os.path.exists(ZIP_PATH):
        raise FileNotFoundError(f"Source archive not found: {ZIP_PATH}")
        
    ensure_dir(OUTPUT_DIR)
    
    with zipfile.ZipFile(ZIP_PATH, 'r') as z:
        with z.open('cleaned_animal_disease_prediction.csv') as f:
            df = pd.read_csv(f)
            
    print(f"Loaded raw dataset shape: {df.shape}")
    
    # 1. Remove duplicate rows
    initial_len = len(df)
    df_unique = df.drop_duplicates().copy()
    print(f"Removed {initial_len - len(df_unique)} duplicate rows. Clean rows: {len(df_unique)}")
    
    # 2. Sanitize corrupted Body_Temperature
    df_unique['Body_Temperature_C'] = df_unique['Body_Temperature'].apply(clean_temp)
    
    # 3. Filter Cattle / Bovine cohort
    cow_df = df_unique[df_unique['Animal_Type'].str.lower() == 'cow'].copy()
    print(f"Extracted {len(cow_df)} cattle clinical reference rows.")
    
    # 4. Extract standardized symptom-to-disease clinical associations
    symptom_disease_map = {}
    for _, row in cow_df.iterrows():
        disease = row['Disease_Prediction'].strip()
        symptoms = []
        for slot in ['Symptom_1', 'Symptom_2', 'Symptom_3', 'Symptom_4']:
            raw_s = row.get(slot)
            if pd.notnull(raw_s) and str(raw_s).strip():
                symptoms.append(normalize_symptom_name(raw_s))
                
        # Check explicit flags
        for flag in ['Appetite_Loss', 'Diarrhea', 'Coughing', 'Labored_Breathing', 'Lameness', 'Skin_Lesions', 'Nasal_Discharge']:
            if str(row.get(flag, '')).strip().lower() == 'yes':
                symptoms.append(normalize_symptom_name(flag))
                
        symptoms = sorted(list(set([s for s in symptoms if s])))
        if disease not in symptom_disease_map:
            symptom_disease_map[disease] = []
        symptom_disease_map[disease].append({
            "breed": row.get('Breed'),
            "age": row.get('Age'),
            "temp_c": row.get('Body_Temperature_C'),
            "symptoms": symptoms
        })
        
    # 5. Export sanitized clinical ontology reference
    out_json = os.path.join(OUTPUT_DIR, "bovine_symptom_ontology.json")
    with open(out_json, "w") as jf:
        json.dump(symptom_disease_map, jf, indent=2)
        
    # Also save sanitized dataframe
    cow_df.to_csv(os.path.join(OUTPUT_DIR, "cleaned_cattle_records.csv"), index=False)
    
    summary = {
        "dataset_name": "07_Animal_Symptoms_Disease_Prediction",
        "raw_rows": initial_len,
        "unique_rows": len(df_unique),
        "cattle_reference_rows": len(cow_df),
        "diseases_cataloged": len(symptom_disease_map),
        "output_file": "bovine_symptom_ontology.json",
        "purpose": "Clinical symptom ontology and vocabulary mapping reference"
    }
    with open(os.path.join(OUTPUT_DIR, "summary.json"), "w") as jf:
        json.dump(summary, jf, indent=2)
        
    print(f"[SUCCESS] Dataset 07 processed. Saved to {OUTPUT_DIR}")
    print(f"Summary: {summary}")

if __name__ == "__main__":
    process_dataset_07()
