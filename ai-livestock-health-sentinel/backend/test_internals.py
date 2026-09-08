import os
import sys
import traceback

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(PROJECT_ROOT, "backend"))
sys.path.append(os.path.join(PROJECT_ROOT, "ml", "symptom_model"))
sys.path.append(os.path.join(PROJECT_ROOT, "ml", "image_model"))
sys.path.append(os.path.join(PROJECT_ROOT, "ml", "anomaly"))

try:
    print("Testing ML module imports...")
    from predict import predict_symptoms
    from explain import explain_prediction
    from isolation_forest import detect_anomaly
    from database import db
    print("Imports successful.")
except Exception as e:
    print("Import failed!")
    traceback.print_exc()
    sys.exit(1)

# Diagnostic test run
try:
    print("\n1. Running predict_symptoms...")
    symptom_res = predict_symptoms(
        symptoms=["fever", "loss_of_appetite", "swelling"],
        age=4.5,
        breed="Gir",
        gender="Female",
        history="None",
        vaccination="vaccinated"
    )
    print(f"Result: {symptom_res}")
    
    print("\n2. Running explain_prediction...")
    explain_res = explain_prediction(
        symptoms=["fever", "loss_of_appetite", "swelling"],
        age=4.5,
        breed="Gir",
        gender="Female",
        history="None",
        vaccination="vaccinated"
    )
    print(f"Result: {explain_res}")

    print("\n3. Running detect_anomaly...")
    anomaly_res = detect_anomaly(
        temperature=38.5,
        appetite=1.0,
        milk_production=15.0,
        activity=1.0
    )
    print(f"Result: {anomaly_res}")
    
    print("\n4. Running DB query for ANM-001...")
    animal = db["animals"].find_one({"_id": "ANM-001"})
    print(f"Result: {animal}")

    print("\n5. Testing full DB insertion logic flow...")
    # Check if we fail during save_data on mock DB
    pred_doc = {
        "animal_id": "ANM-001",
        "possible_disease": "Mastitis",
        "risk_score": 82.0,
        "risk_level": "HIGH",
        "severity": "MODERATE",
        "model_used": "Test",
        "explanation": "Test explanation",
        "is_anomaly": False,
        "anomaly_score": 0.1,
        "image_findings": "",
        "created_at": "2026-08-22T00:00:00"
    }
    db["predictions"].insert_one(pred_doc)
    print("Insert complete.")

except Exception as e:
    print("\nExecution crashed!")
    traceback.print_exc()
