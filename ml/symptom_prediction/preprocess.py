import numpy as np
import pandas as pd

# List of symptoms supported by the Sentinel system
SYMPTOMS_LIST = [
    "fever",
    "cough",
    "loss_of_appetite",
    "reduced_milk_production",
    "nasal_discharge",
    "diarrhea",
    "breathing_difficulty",
    "skin_abnormalities",
    "swelling",
    "reduced_activity"
]

BREEDS_MAP = {
    "gir": 0,
    "sahiwal": 1,
    "holstein_friesian": 2,
    "jersey": 3,
    "indigenous": 4,
    "other": 5
}

GENDER_MAP = {
    "female": 0,
    "male": 1
}

HISTORY_MAP = {
    "none": 0,
    "previous_illness": 1,
    "chronic": 2
}

VACCINATION_MAP = {
    "not_vaccinated": 0,
    "vaccinated": 1
}

DISEASES_LIST = [
    "Healthy",
    "Lumpy Skin Disease",
    "Foot-and-Mouth Disease",
    "Mastitis",
    "Bovine Respiratory Disease",
    "Brucellosis"
]

def encode_input(symptoms, age, breed, gender, history, vaccination):
    """
    Converts raw animal symptoms and details into a numerical feature vector.
    """
    features = []
    
    # 1. Demographic Features
    features.append(float(age))
    features.append(float(BREEDS_MAP.get(str(breed).lower().replace(" ", "_"), 5)))
    features.append(float(GENDER_MAP.get(str(gender).lower(), 0)))
    features.append(float(HISTORY_MAP.get(str(history).lower(), 0)))
    features.append(float(VACCINATION_MAP.get(str(vaccination).lower(), 0)))
    
    # 2. Symptoms (binary one-hot encoded)
    symptom_set = {s.lower().strip().replace(" ", "_") for s in symptoms}
    for symptom in SYMPTOMS_LIST:
        features.append(1.0 if symptom in symptom_set else 0.0)
        
    return np.array(features).reshape(1, -1)

def get_feature_names():
    """
    Returns the order of features used in the model.
    """
    return ["age", "breed", "gender", "history", "vaccination"] + SYMPTOMS_LIST
