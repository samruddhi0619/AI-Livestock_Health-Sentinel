import sys
import os
import unittest
from fastapi.testclient import TestClient

# Ensure backend directory is in path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, CURRENT_DIR)

from main import app

client = TestClient(app)

class TestFastAPIFoundation(unittest.TestCase):

    def test_root_endpoint(self):
        """Verify root endpoint returns operational metadata."""
        response = client.get("/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "operational")
        self.assertIn("version", data)
        self.assertEqual(data["documentation"], "/docs")

    def test_health_endpoints(self):
        """Verify all health-check endpoints: /api/health, /db, /live, /ready."""
        # 1. General health
        res = client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "online")
        self.assertIn("version", data)

        # 2. Database heartbeat
        res_db = client.get("/api/health/db")
        self.assertEqual(res_db.status_code, 200)
        db_data = res_db.json()
        self.assertIn(db_data["status"], ["UP", "DEGRADED"])
        self.assertIn("latency_ms", db_data)
        self.assertIn("engine_dialect", db_data)

        # 3. Liveness probe
        res_live = client.get("/api/health/live")
        self.assertEqual(res_live.status_code, 200)
        self.assertEqual(res_live.json()["status"], "alive")

        # 4. Readiness probe
        res_ready = client.get("/api/health/ready")
        self.assertEqual(res_ready.status_code, 200)
        self.assertTrue(res_ready.json()["ready"])

    def test_auth_registration_and_login_flow(self):
        """Test user registration with Pydantic validation, password hashing, and JWT login."""
        test_user = {
            "username": "test_vet_dr_sharma",
            "password": "SecurePassword2026!",
            "fullname": "Dr. Ramesh Sharma",
            "role": "VETERINARIAN",
            "phone": "+919876543210",
            "district": "Pune",
            "license_number": "MAH-VET-2026-99"
        }

        # Registration
        reg_res = client.post("/api/auth/register", json=test_user)
        # 201 Created or 400 if already exists in test run
        self.assertIn(reg_res.status_code, [201, 400])

        # Login
        login_payload = {
            "username": "test_vet_dr_sharma",
            "password": "SecurePassword2026!"
        }
        login_res = client.post("/api/auth/login", json=login_payload)
        self.assertEqual(login_res.status_code, 200)
        login_data = login_res.json()
        self.assertIn("access_token", login_data)
        self.assertEqual(login_data["token_type"], "bearer")
        self.assertEqual(login_data["user"]["role"], "VETERINARIAN")

        # Access /api/auth/me with Bearer Token
        token = login_data["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        me_res = client.get("/api/auth/me", headers=headers)
        self.assertEqual(me_res.status_code, 200)
        me_data = me_res.json()
        self.assertEqual(me_data["username"], "test_vet_dr_sharma")
        self.assertEqual(me_data["role"], "VETERINARIAN")

    def test_pydantic_validation_error_handling(self):
        """Verify centralized validation exception handler on invalid input."""
        invalid_payload = {
            "username": "ab", # Too short (min 3)
            "password": "123", # Too short (min 6)
            "fullname": "",
            "role": "INVALID_ROLE"
        }
        res = client.post("/api/auth/register", json=invalid_payload)
        self.assertEqual(res.status_code, 422)
        err_data = res.json()
        self.assertFalse(err_data["success"])
        self.assertEqual(err_data["error"], "ValidationError")
        self.assertIn("details", err_data)

    def test_role_based_access_control(self):
        """Verify that unauthorized role gets HTTP 403 Forbidden."""
        # Create farmer
        farmer_user = {
            "username": "test_farmer_kiran",
            "password": "FarmerPassword2026!",
            "fullname": "Kiran Shinde",
            "role": "FARMER"
        }
        client.post("/api/auth/register", json=farmer_user)
        login_res = client.post("/api/auth/login", json={"username": "test_farmer_kiran", "password": "FarmerPassword2026!"})
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Try to access an admin-protected endpoint (/api/admin/users)
        admin_res = client.get("/api/admin/users", headers=headers)
        # Should be forbidden (403) for FARMER
        self.assertEqual(admin_res.status_code, 403)
        self.assertEqual(admin_res.json()["status_code"], 403)

if __name__ == "__main__":
    unittest.main()
