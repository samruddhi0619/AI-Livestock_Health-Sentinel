import os
import sys
import unittest
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient

# Path setup
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from main import app
from database import db
from auth import create_access_token
from services.alert_service import get_alert_service, FORBIDDEN_MEDICATION_PATTERN
from schemas import AlertTypeEnum, AlertSeverityEnum

class TestInAppAlertSystem(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.alert_service = get_alert_service()

        # Clean prior test alerts
        for a in (db["alerts"].find() or []):
            aid = a.get("id") or a.get("_id")
            if str(aid).startswith("test_") or "demo_" in str(aid):
                db["alerts"].delete_one({"_id": aid})

        # Ensure test users
        self.farmer_user = {
            "username": "alert_farmer_1",
            "fullname": "Ramesh Alert Farmer",
            "role": "FARMER",
            "district": "Pune",
            "taluka": "Haveli",
            "village": "Wagholi",
            "is_active": True
        }
        self.other_farmer_user = {
            "username": "alert_farmer_2",
            "fullname": "Suresh Other Farmer",
            "role": "FARMER",
            "district": "Pune",
            "taluka": "Baramati",
            "village": "Baramati Rural",
            "is_active": True
        }
        self.vet_user = {
            "username": "alert_vet_1",
            "fullname": "Dr. Kulkarni (Vet)",
            "role": "VETERINARIAN",
            "district": "Pune",
            "is_active": True
        }
        self.admin_user = {
            "username": "alert_admin_1",
            "fullname": "District Admin Deshmukh",
            "role": "ADMIN",
            "district": "Pune",
            "is_active": True
        }

        for u in [self.farmer_user, self.other_farmer_user, self.vet_user, self.admin_user]:
            if not db["users"].find_one({"username": u["username"]}):
                db["users"].insert_one(u)

        self.farmer_token = create_access_token({"sub": self.farmer_user["username"], "role": "FARMER"})
        self.other_farmer_token = create_access_token({"sub": self.other_farmer_user["username"], "role": "FARMER"})
        self.vet_token = create_access_token({"sub": self.vet_user["username"], "role": "VETERINARIAN"})
        self.admin_token = create_access_token({"sub": self.admin_user["username"], "role": "ADMIN"})

        self.farmer_headers = {"Authorization": f"Bearer {self.farmer_token}"}
        self.other_farmer_headers = {"Authorization": f"Bearer {self.other_farmer_token}"}
        self.vet_headers = {"Authorization": f"Bearer {self.vet_token}"}
        self.admin_headers = {"Authorization": f"Bearer {self.admin_token}"}

    def test_01_farmer_alerts_generation_and_scoping(self):
        """
        Farmer Alerts:
        - High-risk animal assessment
        - Vaccination due
        - Regional disease risk
        And verify another farmer does NOT receive personal herd alerts.
        """
        # 1. High-risk assessment alert
        animal = {"_id": "test_anim_f1", "animal_id": "COW-F1-01", "species": "Cattle"}
        report = {
            "id": "test_rep_f1",
            "top_condition": "Lumpy Skin Disease",
            "risk_level": "Critical",
            "final_risk_score": 88.0,
            "village": "Wagholi",
            "taluka": "Haveli",
            "district": "Pune"
        }
        alert1 = self.alert_service.trigger_farmer_high_risk_alert(
            farmer_username=self.farmer_user["username"],
            animal=animal,
            report=report
        )
        self.assertEqual(alert1["alert_type"], AlertTypeEnum.HIGH_RISK_ASSESSMENT.value)
        self.assertEqual(alert1["severity"], AlertSeverityEnum.CRITICAL.value)
        self.assertIn("COW-F1-01", alert1["title"])
        self.assertEqual(alert1["related_entity"]["animal_tag"], "COW-F1-01")
        self.assertEqual(alert1["related_entity"]["health_report_id"], "test_rep_f1")

        # 2. Vaccination due alert
        alert2 = self.alert_service.trigger_vaccination_due_alert(
            farmer_username=self.farmer_user["username"],
            animal=animal,
            vaccine_name="Foot-and-Mouth Disease (FMD) Booster",
            due_date_str="2026-09-12",
            is_overdue=False,
            vaccination_id="test_vax_f1"
        )
        self.assertEqual(alert2["alert_type"], AlertTypeEnum.VACCINATION_DUE.value)
        self.assertEqual(alert2["severity"], AlertSeverityEnum.MODERATE.value)
        self.assertIn("COW-F1-01", alert2["title"])
        self.assertEqual(alert2["related_entity"]["vaccination_id"], "test_vax_f1")

        # 3. Regional disease risk alert
        alert3 = self.alert_service.trigger_regional_disease_risk_alert(
            disease="Lumpy Skin Disease",
            taluka="Haveli",
            district="Pune",
            cluster_id="test_cluster_reg1"
        )
        self.assertEqual(alert3["alert_type"], AlertTypeEnum.REGIONAL_DISEASE_RISK.value)
        self.assertIn("Haveli", alert3["title"])

        # Fetch via API as Farmer 1
        res = self.client.get("/api/alerts", headers=self.farmer_headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        alert_types = [a["alert_type"] for a in data["alerts"]]
        self.assertIn(AlertTypeEnum.HIGH_RISK_ASSESSMENT.value, alert_types)
        self.assertIn(AlertTypeEnum.VACCINATION_DUE.value, alert_types)
        self.assertIn(AlertTypeEnum.REGIONAL_DISEASE_RISK.value, alert_types)

        # Verify Farmer 2 does NOT receive Farmer 1's personal herd alerts (HIGH_RISK_ASSESSMENT, VACCINATION_DUE)
        res2 = self.client.get("/api/alerts", headers=self.other_farmer_headers)
        self.assertEqual(res2.status_code, 200)
        f2_data = res2.json()
        f2_types = [a["alert_type"] for a in f2_data["alerts"]]
        self.assertNotIn(AlertTypeEnum.HIGH_RISK_ASSESSMENT.value, f2_types)
        self.assertNotIn(AlertTypeEnum.VACCINATION_DUE.value, f2_types)

    def test_02_veterinarian_alerts_generation_and_scoping(self):
        """
        Veterinarian Alerts:
        - High-risk reports requiring clinical review
        - Potential disease clusters
        """
        # 1. High-risk report review required
        animal = {"_id": "test_anim_v1", "animal_id": "BUFF-V1-09", "species": "Buffalo"}
        report = {
            "id": "test_rep_v1",
            "surveillance_case_id": "test_case_v1",
            "top_condition": "Foot-and-Mouth Disease",
            "risk_level": "High",
            "final_risk_score": 77.5,
            "village": "Hadapsar",
            "taluka": "Haveli",
            "district": "Pune"
        }
        alert1 = self.alert_service.trigger_vet_review_required_alert(animal, report)
        self.assertEqual(alert1["alert_type"], AlertTypeEnum.HIGH_RISK_REPORT_REVIEW.value)
        self.assertEqual(alert1["severity"], AlertSeverityEnum.HIGH.value)
        self.assertIn("BUFF-V1-09", alert1["message"])
        self.assertEqual(alert1["related_entity"]["disease_report_id"], "test_case_v1")

        # 2. Potential disease cluster
        cluster = {
            "cluster_id": "test_cluster_v1",
            "disease": "Foot-and-Mouth Disease",
            "report_count": 4,
            "unique_farms_count": 3,
            "radius_km": 3.8,
            "talukas": ["Haveli"],
            "districts": ["Pune"],
            "risk_level": "High"
        }
        alert2 = self.alert_service.trigger_vet_cluster_alert(cluster)
        self.assertEqual(alert2["alert_type"], AlertTypeEnum.POTENTIAL_DISEASE_CLUSTER.value)
        self.assertIn("Potential Foot-and-Mouth Disease Cluster", alert2["title"])
        self.assertIn("Emerging Risk Pattern", alert2["message"])

        # Fetch via API as Veterinarian
        res = self.client.get("/api/alerts", headers=self.vet_headers)
        self.assertEqual(res.status_code, 200)
        vet_data = res.json()
        vet_types = [a["alert_type"] for a in vet_data["alerts"]]
        self.assertIn(AlertTypeEnum.HIGH_RISK_REPORT_REVIEW.value, vet_types)
        self.assertIn(AlertTypeEnum.POTENTIAL_DISEASE_CLUSTER.value, vet_types)

        # Farmer should NOT see the internal clinical triage review alerts
        f_res = self.client.get("/api/alerts", headers=self.farmer_headers)
        f_types = [a["alert_type"] for a in f_res.json()["alerts"]]
        self.assertNotIn(AlertTypeEnum.HIGH_RISK_REPORT_REVIEW.value, f_types)
        self.assertNotIn(AlertTypeEnum.POTENTIAL_DISEASE_CLUSTER.value, f_types)

    def test_03_admin_alerts_generation(self):
        """
        Admin Alerts:
        - Emerging clusters
        - Critical risk patterns
        """
        # 1. Emerging clusters
        cluster1 = {
            "cluster_id": "test_cluster_adm1",
            "disease": "Lumpy Skin Disease",
            "report_count": 5,
            "unique_farms_count": 4,
            "talukas": ["Baramati", "Daund"],
            "districts": ["Pune"]
        }
        alert1 = self.alert_service.trigger_admin_emerging_cluster_alert(cluster1)
        self.assertEqual(alert1["alert_type"], AlertTypeEnum.EMERGING_CLUSTERS.value)
        self.assertIn("Emerging Cluster", alert1["title"])

        # 2. Critical risk pattern
        cluster2 = {
            "cluster_id": "test_cluster_adm2",
            "disease": "Anthrax (Suspected)",
            "report_count": 6,
            "average_risk_score": 93.0,
            "districts": ["Pune"]
        }
        alert2 = self.alert_service.trigger_admin_critical_risk_pattern_alert(cluster2)
        self.assertEqual(alert2["alert_type"], AlertTypeEnum.CRITICAL_RISK_PATTERNS.value)
        self.assertEqual(alert2["severity"], AlertSeverityEnum.CRITICAL.value)
        self.assertIn("Critical Risk Pattern", alert2["title"])

        # Fetch via API as Admin
        res = self.client.get("/api/alerts", headers=self.admin_headers)
        self.assertEqual(res.status_code, 200)
        admin_data = res.json()
        adm_types = [a["alert_type"] for a in admin_data["alerts"]]
        self.assertIn(AlertTypeEnum.EMERGING_CLUSTERS.value, adm_types)
        self.assertIn(AlertTypeEnum.CRITICAL_RISK_PATTERNS.value, adm_types)

    def test_04_mandatory_alert_fields_and_metadata(self):
        """
        Verify every alert strictly adheres to mandatory field schema:
        - alert_type
        - severity
        - timestamp
        - related_entity (animal, report, cluster, disease)
        - recommended_action
        """
        alerts = self.alert_service.get_alerts_for_user(self.admin_user, limit=50)
        self.assertGreaterEqual(len(alerts), 2)
        for a in alerts:
            self.assertIn("alert_type", a)
            self.assertIn("severity", a)
            self.assertIn("timestamp", a)
            self.assertIn("related_entity", a)
            self.assertIn("recommended_action", a)
            self.assertTrue(len(a["recommended_action"]) > 10)
            self.assertFalse(a.get("is_veterinary_prescription", True))
            self.assertIn("Notice:", a.get("safety_disclaimer", ""))

    def test_05_strict_no_unverified_medication_guardrail(self):
        """
        Verify that alerts NEVER include unverified medication instructions, drug dosages,
        or pharmaceutical regimens.
        """
        # Test direct sanitization filter
        dangerous_instruction = (
            "Administer 20 ml of oxytetracycline injection twice daily and 500mg paracetamol tablets."
        )
        safe_result = self.alert_service.sanitize_recommended_action(
            dangerous_instruction,
            fallback_action="Default biosecurity guidance."
        )
        # Should NOT contain pharmaceutical instructions
        self.assertNotIn("oxytetracycline", safe_result.lower())
        self.assertNotIn("20 ml", safe_result.lower())
        self.assertNotIn("paracetamol", safe_result.lower())
        self.assertIn("Do NOT administer unverified medications", safe_result)
        self.assertIn("licensed veterinarian", safe_result)

        # Inspect all alerts returned to users: NONE should have forbidden patterns
        for u in [self.farmer_user, self.vet_user, self.admin_user]:
            user_alerts = self.alert_service.get_alerts_for_user(u, limit=50)
            for a in user_alerts:
                rec_act = a.get("recommended_action", "")
                match = FORBIDDEN_MEDICATION_PATTERN.search(rec_act)
                self.assertIsNone(match, f"Forbidden medication detected in alert {a.get('id')}: {rec_act}")

    def test_06_alert_read_unread_dismiss_lifecycle(self):
        """
        Verify alert reading lifecycle:
        - GET /api/alerts/unread-count
        - POST /api/alerts/{id}/read
        - POST /api/alerts/read-all
        - POST /api/alerts/{id}/dismiss
        """
        # Seed test alert for Farmer
        test_alert = self.alert_service.create_alert(
            recipient_role="FARMER",
            recipient_id=self.farmer_user["username"],
            alert_type=AlertTypeEnum.HIGH_RISK_ASSESSMENT.value,
            severity="HIGH",
            title="Test Life Cycle Alert",
            message="Testing read/dismiss transitions",
            recommended_action="Maintain pen isolation and schedule clinical visit."
        )
        aid = test_alert["id"]

        # Check unread count
        count_res = self.client.get("/api/alerts/unread-count", headers=self.farmer_headers)
        self.assertEqual(count_res.status_code, 200)
        self.assertGreaterEqual(count_res.json()["total_unread"], 1)

        # Mark single alert read
        read_res = self.client.post(f"/api/alerts/{aid}/read", headers=self.farmer_headers)
        self.assertEqual(read_res.status_code, 200)
        self.assertTrue(read_res.json()["is_read"])

        # Mark all read
        read_all_res = self.client.post("/api/alerts/read-all", headers=self.farmer_headers)
        self.assertEqual(read_all_res.status_code, 200)

        # Dismiss alert
        dismiss_res = self.client.post(f"/api/alerts/{aid}/dismiss", headers=self.farmer_headers)
        self.assertEqual(dismiss_res.status_code, 200)
        self.assertTrue(dismiss_res.json()["is_dismissed"])

        # Dismissed alert should no longer appear in active list
        list_res = self.client.get("/api/alerts", headers=self.farmer_headers)
        active_ids = [a["id"] for a in list_res.json()["alerts"]]
        self.assertNotIn(aid, active_ids)

    def test_07_seed_samples_endpoint(self):
        """
        Test /api/alerts/seed-samples for development testing.
        """
        # Test for Farmer
        f_res = self.client.post("/api/alerts/seed-samples", headers=self.farmer_headers)
        self.assertEqual(f_res.status_code, 200)
        self.assertEqual(f_res.json()["seeded_count"], 3)

        # Test for Vet
        v_res = self.client.post("/api/alerts/seed-samples", headers=self.vet_headers)
        self.assertEqual(v_res.status_code, 200)
        self.assertEqual(v_res.json()["seeded_count"], 2)

        # Test for Admin
        a_res = self.client.post("/api/alerts/seed-samples", headers=self.admin_headers)
        self.assertEqual(a_res.status_code, 200)
        self.assertEqual(a_res.json()["seeded_count"], 2)

if __name__ == "__main__":
    unittest.main()
