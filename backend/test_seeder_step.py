import os
import sys
import json
from datetime import datetime, timedelta

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(PROJECT_ROOT, "backend"))

from database import db, is_mock_db
from auth import get_password_hash

def test_seeder_step():
    print(f"Is Mock DB: {is_mock_db}")
    db_path = db.db_path
    
    # Clean up file first
    if os.path.exists(db_path):
        os.remove(db_path)
    
    # Helper to check file keys
    def check_keys(step_name):
        if os.path.exists(db_path):
            with open(db_path, "r") as f:
                content = json.load(f)
            print(f"[{step_name}] keys in file: {list(content.keys())}")
            if "users" in content:
                print(f"[{step_name}] users count: {len(content['users'])}")
        else:
            print(f"[{step_name}] file does not exist yet")

    # Step 1: Cleanup loop
    collections = ["users", "animals", "health_records", "predictions", "disease_cases", "vaccinations", "alerts", "outbreak_clusters", "audit_logs"]
    for c in collections:
        data = db[c]._load_data()
        data[c] = []
        db[c]._save_data(data)
    check_keys("After Cleanup")

    # Step 2: Seed Users
    hashed_pwd = get_password_hash("sih2026")
    users = [
        {"username": "farmer_a", "password": hashed_pwd, "role": "FARMER"},
        {"username": "farmer_b", "password": hashed_pwd, "role": "FARMER"},
        {"username": "vet_officer", "password": hashed_pwd, "role": "VETERINARIAN"},
        {"username": "gov_officer", "password": hashed_pwd, "role": "OFFICER"},
        {"username": "admin_user", "password": hashed_pwd, "role": "ADMIN"}
    ]
    for u in users:
        db["users"].insert_one(u)
    check_keys("After Users Seeding")

    # Step 3: Seed Animals
    animals_data = [
        {"_id": "ANM-001", "species": "Cattle", "farm_id": "farmer_a"},
        {"_id": "ANM-002", "species": "Cattle", "farm_id": "farmer_b"}
    ]
    for a in animals_data:
        db["animals"].insert_one(a)
    check_keys("After Animals Seeding")

    # Step 4: Seed Vaccinations
    vaccinations = [
        {"animal_id": "ANM-001", "vaccine_name": "FMD Vaccine"}
    ]
    for v in vaccinations:
        db["vaccinations"].insert_one(v)
    check_keys("After Vaccinations Seeding")

if __name__ == "__main__":
    test_seeder_step()
