import os
import sys
from fastapi.testclient import TestClient

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(PROJECT_ROOT, "backend"))
sys.path.append(os.path.join(PROJECT_ROOT, "ml", "symptom_model"))
sys.path.append(os.path.join(PROJECT_ROOT, "ml", "image_model"))
sys.path.append(os.path.join(PROJECT_ROOT, "ml", "anomaly"))

try:
    from main import app
    from database import db
    from auth import get_password_hash
    client = TestClient(app)
except Exception as e:
    import traceback
    traceback.print_exc()
    sys.exit(1)

def run_local_api_test():
    print("Pre-seeding test user...")
    # Ensure test user exists in the db
    hashed_pwd = get_password_hash("sih2026")
    db["users"].delete_one({"username": "test_farmer"})
    db["users"].insert_one({
        "username": "test_farmer",
        "password": hashed_pwd,
        "fullname": "Test Farmer",
        "role": "FARMER",
        "village": "Wadgaon",
        "taluka": "Haveli",
        "district": "Pune"
    })
    
    # Ensure test animal exists
    db["animals"].delete_one({"_id": "TEST-ANM-001"})
    db["animals"].insert_one({
        "_id": "TEST-ANM-001",
        "species": "Cattle",
        "breed": "Gir",
        "age": 4.5,
        "gender": "Female",
        "health_history": "None",
        "farm_id": "test_farmer",
        "latitude": 18.5205,
        "longitude": 73.8567,
        "village": "Wadgaon",
        "taluka": "Haveli",
        "district": "Pune"
    })
    
    # Get Login token
    print("Simulating Login...")
    login_res = client.post("/api/auth/login", json={
        "username": "test_farmer",
        "password": "sih2026"
    })
    if login_res.status_code != 200:
        print(f"Login failed: {login_res.text}")
        return
        
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test submission
    print("Testing submission endpoint...")
    payload = {
        "symptoms": ["fever", "loss_of_appetite", "swelling"],
        "temperature": 38.5,
        "appetite": 1.0,
        "milk_production": 15.0,
        "activity": 1.0,
        "observations": "Circular lumps on skin",
        "image_url": None,
        "latitude": 18.5204,
        "longitude": 73.8567,
        "village": "Wadgaon",
        "taluka": "Haveli",
        "district": "Pune"
    }
    
    try:
        res = client.post("/api/assessment/submit/TEST-ANM-001", json=payload, headers=headers)
        print(f"Status Code: {res.status_code}")
        print("Response:")
        print(res.text)
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_local_api_test()
