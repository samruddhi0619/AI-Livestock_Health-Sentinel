import os
import sys
import unittest
from fastapi.testclient import TestClient

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, CURRENT_DIR)

from main import app

client = TestClient(app)

class TestDigitalAnimalHealthPassport(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # 1. Login as Farmer Ramesh
        res = client.post("/api/auth/login", json={"username": "farmer_ramesh", "password": "sih2026"})
        cls.farmer_token = res.json()["access_token"]
        cls.farmer_headers = {"Authorization": f"Bearer {cls.farmer_token}"}

        # 2. Login as Dr. Anita (Veterinarian)
        res_vet = client.post("/api/auth/login", json={"username": "dr_anita", "password": "sih2026"})
        cls.vet_token = res_vet.json()["access_token"]
        cls.vet_headers = {"Authorization": f"Bearer {cls.vet_token}"}

    def test_01_register_animal_and_generate_ids(self):
        """Feature 1, 2, 3: Register animal, generate unique Animal ID and QR code."""
        new_cow_payload = {
            "species": "Cattle",
            "breed": "Gir",
            "age": 3.5,
            "gender": "Female",
            "health_history": "None",
            "latitude": 18.5784,
            "longitude": 73.9821,
            "village": "Wagholi",
            "taluka": "Haveli",
            "district": "Pune"
        }

        response = client.post("/api/animals", json=new_cow_payload, headers=self.farmer_headers)
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertTrue(data["success"])
        
        # Verify Unique Animal ID format
        animal_id = data["animal_id"]
        self.assertTrue(animal_id.startswith("TAG-"))
        self.assertIn("2026", animal_id)
        
        # Verify QR code generation
        qr_token = data["qr_code_identifier"]
        self.assertTrue(qr_token.startswith("QR-SENTINEL-"))
        self.assertTrue(data["qr_code_base64"].startswith("data:image/png;base64,"))
        self.assertTrue(data["qr_code_url"].startswith("/uploads/qrcodes/"))

        # Verify Real Application Data flag
        animal = data["animal"]
        self.assertFalse(animal["is_simulated_demo"])
        self.assertEqual(animal["health_status"], "HEALTHY")

        TestDigitalAnimalHealthPassport.created_animal_id = animal_id
        TestDigitalAnimalHealthPassport.created_qr_token = qr_token

    def test_02_view_complete_animal_profile(self):
        """Feature 4: View complete animal profile."""
        animal_id = self.created_animal_id
        res = client.get(f"/api/animals/{animal_id}", headers=self.farmer_headers)
        self.assertEqual(res.status_code, 200)
        profile = res.json()
        self.assertEqual(profile["animal_id"], animal_id)
        self.assertEqual(profile["species"], "Cattle")
        self.assertEqual(profile["breed"], "Gir")
        self.assertEqual(profile["health_status"], "HEALTHY")
        self.assertIn("qr_code_base64", profile)

    def test_03_digital_passport_three_tier_separation(self):
        """Verify Digital Passport strictly separates Farmer, AI, and Vet tiers."""
        # Use existing simulated demo animal with rich records
        demo_tag = "TAG-MH-2026-SIM01"
        res = client.get(f"/api/animals/{demo_tag}/passport", headers=self.vet_headers)
        self.assertEqual(res.status_code, 200)
        passport = res.json()

        # 1. Passport Metadata
        meta = passport["passport_metadata"]
        self.assertEqual(meta["passport_number"], f"PASSPORT-{demo_tag}")
        self.assertTrue(meta["is_simulated_demo"])
        self.assertEqual(meta["data_provenance"], "Simulated Demo Dataset")

        # 2. Animal Profile
        profile = passport["animal_profile"]
        self.assertEqual(profile["animal_id"], demo_tag)
        self.assertEqual(profile["confirmed_health_status"], "CONFIRMED_SICK")

        # 3. TIER 1: Farmer-Reported Information
        farmer_data = passport["farmer_reported_information"]
        self.assertIn("total_checkups", farmer_data)
        self.assertIn("checkup_records", farmer_data)
        self.assertIn("disclaimer", farmer_data)
        self.assertIn("farmer", farmer_data["disclaimer"].lower())

        # 4. TIER 2: AI-Generated Risk Assessments
        ai_data = passport["ai_generated_risk_assessments"]
        self.assertIn("total_screenings", ai_data)
        self.assertIn("screening_records", ai_data)
        self.assertFalse(ai_data["is_veterinary_diagnosis"]) # Strictly False
        self.assertIn("AI screening and risk triage tool only", ai_data["disclaimer"])

        # 5. TIER 3: Veterinarian-Reviewed Information
        vet_data = passport["veterinarian_reviewed_information"]
        self.assertIn("total_reviews", vet_data)
        self.assertIn("review_records", vet_data)
        self.assertIn("registered veterinary medical officer", vet_data["disclaimer"])
        self.assertGreater(len(vet_data["review_records"]), 0)
        self.assertEqual(vet_data["review_records"][0]["review_decision"], "CONFIRMED_POSITIVE")

        # 6. Vaccination Ledger
        vax_data = passport["vaccination_history"]
        self.assertIn("total_vaccinations", vax_data)
        self.assertGreater(len(vax_data["records"]), 0)

    def test_04_public_qr_code_scan_endpoint(self):
        """Feature 3: Scan QR code identifier to resolve health passport."""
        qr_token = "QR-SENTINEL-SIM01"
        res = client.get(f"/api/animals/qr/{qr_token}")
        self.assertEqual(res.status_code, 200)
        passport = res.json()
        self.assertEqual(passport["animal_profile"]["animal_id"], "TAG-MH-2026-SIM01")
        self.assertIn("farmer_reported_information", passport)
        self.assertIn("ai_generated_risk_assessments", passport)
        self.assertIn("veterinarian_reviewed_information", passport)

    def test_05_health_history_endpoint(self):
        """Feature 5: View health history endpoint."""
        demo_tag = "TAG-MH-2026-SIM01"
        res = client.get(f"/api/animals/{demo_tag}/health-history", headers=self.vet_headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertGreater(data["total_records"], 0)
        first_record = data["health_records"][0]
        self.assertEqual(first_record["body_temperature_c"], 40.6)

    def test_06_vaccination_history_endpoint(self):
        """Feature 6: View vaccination history endpoint."""
        demo_tag = "TAG-MH-2026-SIM01"
        res = client.get(f"/api/animals/{demo_tag}/vaccinations", headers=self.vet_headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertGreater(data["total_vaccinations"], 0)

    def test_07_ai_assessments_endpoint(self):
        """Feature 7: View AI assessments endpoint."""
        demo_tag = "TAG-MH-2026-SIM01"
        res = client.get(f"/api/animals/{demo_tag}/assessments", headers=self.vet_headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertFalse(data["is_veterinary_diagnosis"])
        self.assertGreater(data["total_screenings"], 0)

    def test_08_veterinarian_reviews_endpoint(self):
        """Feature 8: View veterinarian reviews endpoint."""
        demo_tag = "TAG-MH-2026-SIM01"
        res = client.get(f"/api/animals/{demo_tag}/reviews", headers=self.vet_headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertGreater(data["total_reviews"], 0)
        self.assertEqual(data["veterinarian_reviews"][0]["clinical_diagnosis"], "Confirmed Lumpy Skin Disease (Moderate nodular cutaneous form)")

    def test_09_update_confirmed_health_status(self):
        """Verify updating confirmed health status by licensed veterinarian."""
        animal_id = self.created_animal_id
        
        # 1. Attempt by unauthorized farmer should fail (403 Forbidden)
        forbidden_res = client.patch(
            f"/api/animals/{animal_id}/health-status",
            json={"health_status": "UNDER_TREATMENT", "clinical_reason": "Testing"},
            headers=self.farmer_headers
        )
        self.assertEqual(forbidden_res.status_code, 403)

        # 2. Update by licensed Veterinarian should succeed
        vet_res = client.patch(
            f"/api/animals/{animal_id}/health-status",
            json={"health_status": "UNDER_TREATMENT", "clinical_reason": "Post-vaccination therapeutic monitoring"},
            headers=self.vet_headers
        )
        self.assertEqual(vet_res.status_code, 200)
        self.assertEqual(vet_res.json()["health_status"], "UNDER_TREATMENT")

        # Verify updated status in profile
        check_res = client.get(f"/api/animals/{animal_id}", headers=self.vet_headers)
        self.assertEqual(check_res.json()["health_status"], "UNDER_TREATMENT")

if __name__ == "__main__":
    unittest.main()
