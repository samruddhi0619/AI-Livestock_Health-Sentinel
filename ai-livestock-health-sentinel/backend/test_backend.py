import os
import sys
import unittest

# Setup PYTHONPATH to include backend and ml folders
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(PROJECT_ROOT, "backend"))
sys.path.append(os.path.join(PROJECT_ROOT, "ml", "symptom_model"))
sys.path.append(os.path.join(PROJECT_ROOT, "ml", "image_model"))
sys.path.append(os.path.join(PROJECT_ROOT, "ml", "anomaly"))
sys.path.append(os.path.join(PROJECT_ROOT, "ml", "outbreak"))

class SentinelSystemTests(unittest.TestCase):
    def test_database_fallback(self):
        """Verify the database is initialized and mock collections operate successfully."""
        from database import db, is_mock_db
        self.assertIsNotNone(db)
        
        # Test basic insert and lookup on temporary collection
        test_col = db["temp_test"]
        res = test_col.insert_one({"name": "Cow Test", "value": 100})
        self.assertIsNotNone(res.inserted_id)
        
        doc = test_col.find_one({"name": "Cow Test"})
        self.assertEqual(doc["value"], 100)
        
        # Clean up
        test_col.delete_one({"_id": res.inserted_id})
        
    def test_symptom_prediction_import(self):
        """Verify symptom models load and produce valid predictions."""
        from predict import predict_symptoms
        from explain import explain_prediction
        
        res = predict_symptoms(
            symptoms=["fever", "skin_abnormalities"],
            age=3,
            breed="Gir",
            gender="Female",
            history="None",
            vaccination="vaccinated"
        )
        self.assertIn("possible_disease", res)
        self.assertIn("risk_score", res)
        self.assertIn("risk_level", res)
        
        drivers = explain_prediction(
            symptoms=["fever", "skin_abnormalities"],
            age=3,
            breed="Gir",
            gender="Female",
            history="None",
            vaccination="vaccinated"
        )
        self.assertGreater(len(drivers), 0)
        self.assertEqual(drivers[0]["feature"], "Skin Abnormalities")

    def test_anomaly_detector(self):
        """Verify Isolation Forest detects vital outliers."""
        from isolation_forest import detect_anomaly
        
        # Test normal vital parameters
        is_anom, score = detect_anomaly(temperature=38.5, appetite=1.0, milk_production=18.0, activity=1.0)
        self.assertFalse(is_anom)
        
        # Test anomalous vitals (extreme fever + milk drop)
        is_anom_severe, score_severe = detect_anomaly(temperature=40.8, appetite=0.0, milk_production=2.0, activity=0.0)
        self.assertTrue(is_anom_severe)
        
    def test_outbreak_detector(self):
        """Verify DBSCAN groups nearby points accurately."""
        from cluster_detection import detect_outbreak_clusters
        
        # Set up a cluster of 3 cases in Pune
        cases = [
            {"id": "c1", "latitude": 18.520, "longitude": 73.856, "disease": "Foot-and-Mouth Disease", "farm_id": "f1", "risk_level": "HIGH", "date": "2026-08-22T10:00:00"},
            {"id": "c2", "latitude": 18.521, "longitude": 73.857, "disease": "Foot-and-Mouth Disease", "farm_id": "f2", "risk_level": "HIGH", "date": "2026-08-22T10:10:00"},
            {"id": "c3", "latitude": 18.520, "longitude": 73.855, "disease": "Foot-and-Mouth Disease", "farm_id": "f3", "risk_level": "MODERATE", "date": "2026-08-22T10:20:00"}
        ]
        
        clusters = detect_outbreak_clusters(cases, eps_km=5.0, min_cases=3, time_window_days=14)
        self.assertEqual(len(clusters), 1)
        self.assertEqual(clusters[0]["cases_count"], 3)
        self.assertEqual(clusters[0]["disease"], "Foot-and-Mouth Disease")

if __name__ == "__main__":
    unittest.main()
