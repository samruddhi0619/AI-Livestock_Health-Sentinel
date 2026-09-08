import requests

def run_test():
    url = "http://localhost:8000"
    
    # 1. Login to get token
    login_data = {
        "username": "farmer_a",
        "password": "sih2026"
    }
    
    try:
        r = requests.post(f"{url}/api/auth/login", json=login_data)
        r.raise_for_status()
        token = r.json()["access_token"]
        print("Successfully logged in. Token acquired.")
    except Exception as e:
        print(f"Login failed: {e}")
        if 'r' in locals():
            print(f"Response: {r.text}")
        return

    # 2. Submit health record
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
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
        res = requests.post(f"{url}/api/assessment/submit/ANM-001", json=payload, headers=headers)
        print(f"Status Code: {res.status_code}")
        print("Response Content:")
        print(res.text)
    except Exception as e:
        print(f"Post request failed: {e}")

if __name__ == "__main__":
    run_test()
