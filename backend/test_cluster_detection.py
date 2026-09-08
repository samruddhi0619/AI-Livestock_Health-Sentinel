import os
import sys
import unittest
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient

# Ensure backend directory is in path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from main import app
from database import db
from auth import create_access_token
from ml.outbreak.cluster_detection import (
    haversine_distance_km,
    detect_potential_clusters,
    normalize_disease_name
)
from services.cluster_service import get_cluster_service

class TestPotentialDiseaseClusterDetection(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.cluster_service = get_cluster_service()
        
        # Ensure test users exist in db["users"]
        for u in [
            {"username": "vet_dr_sharma", "fullname": "Dr. Sharma", "role": "VETERINARIAN", "is_active": True},
            {"username": "admin_patil", "fullname": "Admin Patil", "role": "ADMIN", "is_active": True},
            {"username": "farmer_ramesh", "fullname": "Ramesh Farmer", "role": "FARMER", "is_active": True},
        ]:
            if not db["users"].find_one({"username": u["username"]}):
                db["users"].insert_one(u)
        
        # Test auth tokens
        self.vet_token = create_access_token({"sub": "vet_dr_sharma", "role": "VETERINARIAN"})
        self.admin_token = create_access_token({"sub": "admin_patil", "role": "ADMIN"})
        self.farmer_token = create_access_token({"sub": "farmer_ramesh", "role": "FARMER"})
        
        self.vet_headers = {"Authorization": f"Bearer {self.vet_token}"}
        self.admin_headers = {"Authorization": f"Bearer {self.admin_token}"}
        self.farmer_headers = {"Authorization": f"Bearer {self.farmer_token}"}

    def test_01_haversine_distance_calculation(self):
        """Verify geodesic distance accuracy using known points in Pune."""
        # Point A: Pune Center (18.5204, 73.8567)
        # Point B: ~3.3 km North (18.5500, 73.8567)
        dist = haversine_distance_km(18.5204, 73.8567, 18.5500, 73.8567)
        self.assertAlmostEqual(dist, 3.29, delta=0.2)

    def test_02_detect_potential_cluster_close_proximity(self):
        """
        Verify that multiple high-risk reports of the same disease within 5km
        during the past 7 days form a Potential Disease Cluster.
        """
        now = datetime.now(timezone.utc)
        reports = [
            {
                "id": "rep_101",
                "animal_id": "cow_01",
                "farm_id": "farm_alpha",
                "disease": "Foot-and-Mouth Disease",
                "risk_score": 75.0,
                "risk_level": "High",
                "latitude": 18.5204,
                "longitude": 73.8567,
                "village": "Wagholi",
                "taluka": "Haveli",
                "district": "Pune",
                "reported_at": (now - timedelta(days=2)).isoformat()
            },
            {
                "id": "rep_102",
                "animal_id": "cow_02",
                "farm_id": "farm_beta",
                "disease": "FMD",  # Tests normalization
                "risk_score": 82.0,
                "risk_level": "Critical",
                "latitude": 18.5250,
                "longitude": 73.8600,
                "village": "Wagholi",
                "taluka": "Haveli",
                "district": "Pune",
                "reported_at": (now - timedelta(days=1)).isoformat()
            },
            {
                "id": "rep_103",
                "animal_id": "cow_03",
                "farm_id": "farm_gamma",
                "disease": "Foot and Mouth Disease",
                "risk_score": 70.0,
                "risk_level": "High",
                "latitude": 18.5180,
                "longitude": 73.8520,
                "village": "Wagholi",
                "taluka": "Haveli",
                "district": "Pune",
                "reported_at": (now - timedelta(hours=8)).isoformat()
            }
        ]

        clusters = detect_potential_clusters(
            reports_list=reports,
            eps_km=5.0,
            min_reports=3,
            time_window_days=14,
            reference_time=now
        )

        self.assertEqual(len(clusters), 1)
        c = clusters[0]
        self.assertEqual(c["disease"], "Foot-and-Mouth Disease (FMD)")
        self.assertEqual(c["report_count"], 3)
        self.assertEqual(c["unique_farms_count"], 3)
        self.assertEqual(c["cluster_label"], "Potential Disease Cluster")
        self.assertEqual(c["pattern_type"], "Emerging Risk Pattern")
        self.assertEqual(c["risk_level"], "Critical")  # Because rep_102 is Critical
        self.assertFalse(c["is_confirmed_outbreak"])
        self.assertFalse(c["is_veterinary_diagnosis"])
        self.assertIn("AI-assisted", c["disclaimer"])
        self.assertNotIn("CONFIRMED OUTBREAK", c["cluster_label"].upper())

    def test_03_reject_noise_and_distant_reports(self):
        """
        Verify that isolated cases (>20km away) or insufficient report counts
        do not form a cluster.
        """
        now = datetime.now(timezone.utc)
        sparse_reports = [
            {
                "id": "rep_far_1",
                "disease": "Foot-and-Mouth Disease",
                "risk_level": "High",
                "latitude": 18.5204,
                "longitude": 73.8567,  # Pune
                "reported_at": now.isoformat()
            },
            {
                "id": "rep_far_2",
                "disease": "Foot-and-Mouth Disease",
                "risk_level": "High",
                "latitude": 18.1500,
                "longitude": 74.5800,  # Baramati (~75 km away)
                "reported_at": now.isoformat()
            }
        ]
        clusters = detect_potential_clusters(
            reports_list=sparse_reports,
            eps_km=5.0,
            min_reports=3,
            time_window_days=14,
            reference_time=now
        )
        self.assertEqual(len(clusters), 0)

    def test_04_exclude_low_risk_baseline_cases(self):
        """
        Verify that low-risk healthy or minor cases do NOT trigger or join clusters,
        even if geographically adjacent.
        """
        now = datetime.now(timezone.utc)
        reports = [
            {
                "id": "rep_low_1",
                "disease": "Foot-and-Mouth Disease",
                "risk_level": "Low",
                "risk_score": 25.0,
                "latitude": 18.5204,
                "longitude": 73.8567,
                "reported_at": now.isoformat()
            },
            {
                "id": "rep_low_2",
                "disease": "Foot-and-Mouth Disease",
                "risk_level": "Low",
                "risk_score": 20.0,
                "latitude": 18.5210,
                "longitude": 73.8570,
                "reported_at": now.isoformat()
            },
            {
                "id": "rep_low_3",
                "disease": "Foot-and-Mouth Disease",
                "risk_level": "Low",
                "risk_score": 18.0,
                "latitude": 18.5200,
                "longitude": 73.8560,
                "reported_at": now.isoformat()
            }
        ]
        clusters = detect_potential_clusters(
            reports_list=reports,
            eps_km=5.0,
            min_reports=3,
            time_window_days=14,
            reference_time=now
        )
        self.assertEqual(len(clusters), 0)

    def test_05_exclude_expired_time_window_reports(self):
        """
        Verify reports outside the configurable time window (e.g. 25 days ago)
        are excluded from active cluster detection.
        """
        now = datetime.now(timezone.utc)
        old_reports = [
            {
                "id": "rep_old_1",
                "disease": "Lumpy Skin Disease",
                "risk_level": "High",
                "latitude": 18.5204,
                "longitude": 73.8567,
                "reported_at": (now - timedelta(days=25)).isoformat()
            },
            {
                "id": "rep_old_2",
                "disease": "Lumpy Skin Disease",
                "risk_level": "High",
                "latitude": 18.5210,
                "longitude": 73.8570,
                "reported_at": (now - timedelta(days=20)).isoformat()
            },
            {
                "id": "rep_old_3",
                "disease": "Lumpy Skin Disease",
                "risk_level": "High",
                "latitude": 18.5200,
                "longitude": 73.8560,
                "reported_at": (now - timedelta(days=18)).isoformat()
            }
        ]
        clusters = detect_potential_clusters(
            reports_list=old_reports,
            eps_km=5.0,
            min_reports=3,
            time_window_days=14,  # window is 14 days
            reference_time=now
        )
        self.assertEqual(len(clusters), 0)

    def test_06_api_trigger_and_listing(self):
        """
        Test API endpoints:
        - POST /api/clusters/detect (RBAC checks and successful detection)
        - GET /api/clusters
        - GET /api/clusters/{cluster_id}
        """
        # 1. Non-vet/admin should receive 403 Forbidden
        farmer_res = self.client.post("/api/clusters/detect", headers=self.farmer_headers, json={})
        self.assertEqual(farmer_res.status_code, 403)

        # 2. Seed 3 high-risk reports in db["disease_reports"]
        now_iso = datetime.now(timezone.utc).isoformat()
        test_case_ids = []
        for i in range(3):
            cid = f"test_surv_case_{i}"
            test_case_ids.append(cid)
            db["disease_reports"].insert_one({
                "_id": cid,
                "id": cid,
                "animal_id": f"anim_{i}",
                "animal_tag": f"TAG-00{i}",
                "disease": "Lumpy Skin Disease",
                "reported_disease": "Lumpy Skin Disease",
                "risk_score": 76.0 + i,
                "risk_level": "High",
                "exact_latitude": 18.5200 + (i * 0.005),
                "exact_longitude": 73.8560 + (i * 0.005),
                "village": "Loni Kalbhor",
                "taluka": "Haveli",
                "district": "Pune",
                "reported_at": now_iso
            })

        # 3. Trigger detection as Veterinarian
        detect_res = self.client.post(
            "/api/clusters/detect",
            headers=self.vet_headers,
            json={
                "geo_radius_km": 5.0,
                "min_reports": 3,
                "time_window_days": 14
            }
        )
        self.assertEqual(detect_res.status_code, 200)
        data = detect_res.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["pattern_type"], "Emerging Risk Pattern")
        self.assertFalse(data["is_confirmed_outbreak"])
        self.assertFalse(data["is_veterinary_diagnosis"])
        self.assertGreaterEqual(data["total_clusters_detected"], 1)

        first_cluster = data["clusters"][0]
        c_id = first_cluster["cluster_id"]

        # 4. List clusters
        list_res = self.client.get("/api/clusters", headers=self.farmer_headers)
        self.assertEqual(list_res.status_code, 200)
        list_data = list_res.json()
        self.assertIn("clusters", list_data)
        self.assertGreaterEqual(list_data["total_clusters"], 1)
        self.assertFalse(list_data["is_confirmed_outbreak"])

        # 5. Get cluster by ID
        get_res = self.client.get(f"/api/clusters/{c_id}", headers=self.farmer_headers)
        self.assertEqual(get_res.status_code, 200)
        c_details = get_res.json()
        self.assertEqual(c_details["cluster"]["cluster_id"], c_id)
        self.assertEqual(c_details["cluster"]["cluster_label"], "Potential Disease Cluster")
        self.assertFalse(c_details["is_confirmed_outbreak"])

        # Cleanup synthetic test records
        for cid in test_case_ids:
            db["disease_reports"].delete_one({"_id": cid})

if __name__ == "__main__":
    unittest.main()
