import os
import sys
import pandas as pd
import numpy as np

# Add ml/symptom_prediction to path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(ROOT_DIR, "ml", "symptom_prediction"))

from preprocess import SYMPTOMS_LIST, BREEDS_MAP, GENDER_MAP, HISTORY_MAP, VACCINATION_MAP, DISEASES_LIST

def generate_csv(output_path, num_samples=500):
    np.random.seed(42)
    data = []
    
    for _ in range(num_samples):
        age = np.random.randint(1, 15)
        breed_name = np.random.choice(list(BREEDS_MAP.keys()))
        breed = BREEDS_MAP[breed_name]
        gender = np.random.choice(list(GENDER_MAP.values()))
        history = np.random.choice(list(HISTORY_MAP.values()), p=[0.7, 0.2, 0.1])
        vaccination = np.random.choice(list(VACCINATION_MAP.values()), p=[0.4, 0.6])
        
        disease_idx = np.random.choice(len(DISEASES_LIST))
        disease = DISEASES_LIST[disease_idx]
        
        symptoms = {s: 0.0 for s in SYMPTOMS_LIST}
        
        if disease == "Healthy":
            for s in SYMPTOMS_LIST:
                if np.random.rand() < 0.05:
                    symptoms[s] = 1.0
        elif disease == "Lumpy Skin Disease":
            symptoms["skin_abnormalities"] = 1.0 if np.random.rand() < 0.95 else 0.0
            symptoms["fever"] = 1.0 if np.random.rand() < 0.8 else 0.0
            symptoms["loss_of_appetite"] = 1.0 if np.random.rand() < 0.7 else 0.0
            symptoms["reduced_milk_production"] = 1.0 if np.random.rand() < 0.6 else 0.0
            symptoms["reduced_activity"] = 1.0 if np.random.rand() < 0.5 else 0.0
        elif disease == "Foot-and-Mouth Disease":
            symptoms["swelling"] = 1.0 if np.random.rand() < 0.9 else 0.0
            symptoms["fever"] = 1.0 if np.random.rand() < 0.85 else 0.0
            symptoms["nasal_discharge"] = 1.0 if np.random.rand() < 0.7 else 0.0
            symptoms["reduced_activity"] = 1.0 if np.random.rand() < 0.8 else 0.0
            symptoms["loss_of_appetite"] = 1.0 if np.random.rand() < 0.75 else 0.0
        elif disease == "Mastitis":
            symptoms["reduced_milk_production"] = 1.0 if np.random.rand() < 0.95 else 0.0
            symptoms["swelling"] = 1.0 if np.random.rand() < 0.9 else 0.0
            symptoms["fever"] = 1.0 if np.random.rand() < 0.6 else 0.0
            symptoms["loss_of_appetite"] = 1.0 if np.random.rand() < 0.5 else 0.0
        elif disease == "Bovine Respiratory Disease":
            symptoms["cough"] = 1.0 if np.random.rand() < 0.9 else 0.0
            symptoms["breathing_difficulty"] = 1.0 if np.random.rand() < 0.85 else 0.0
            symptoms["nasal_discharge"] = 1.0 if np.random.rand() < 0.8 else 0.0
            symptoms["fever"] = 1.0 if np.random.rand() < 0.7 else 0.0
            symptoms["reduced_activity"] = 1.0 if np.random.rand() < 0.6 else 0.0
        elif disease == "Brucellosis":
            symptoms["fever"] = 1.0 if np.random.rand() < 0.7 else 0.0
            symptoms["reduced_milk_production"] = 1.0 if np.random.rand() < 0.6 else 0.0
            symptoms["loss_of_appetite"] = 1.0 if np.random.rand() < 0.5 else 0.0
            symptoms["reduced_activity"] = 1.0 if np.random.rand() < 0.5 else 0.0
            if vaccination == 1:
                symptoms["fever"] = 1.0 if np.random.rand() < 0.3 else 0.0
        
        row = [age, breed_name, "Female" if gender == 0 else "Male", history, vaccination] + [symptoms[s] for s in SYMPTOMS_LIST] + [disease]
        data.append(row)
        
    cols = ["age", "breed", "gender", "history", "vaccination"] + SYMPTOMS_LIST + ["disease"]
    df = pd.DataFrame(data, columns=cols)
    df.to_csv(output_path, index=False)
    print(f"Generated {num_samples} sample records saved to: {output_path}")

if __name__ == "__main__":
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_cattle_symptoms.csv")
    generate_csv(out, num_samples=100)
