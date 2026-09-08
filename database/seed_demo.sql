-- ==============================================================================
-- AI-LIVESTOCK HEALTH SENTINEL: PRODUCTION DEMO SEED DATA
-- Smart India Hackathon 2026 (SIH26128)
-- ==============================================================================

-- 1. Insert Users (FARMER, VETERINARIAN, ADMIN)
INSERT INTO users (id, username, password_hash, fullname, role, phone, district, taluka, village, license_number, is_active)
VALUES 
  ('a0000001-0000-0000-0000-000000000001', 'farmer_ramesh', 'pbkdf2:sha256:fakehash_ramesh', 'Ramesh Patil', 'FARMER', '+919822012345', 'Pune', 'Haveli', 'Wagholi', NULL, TRUE),
  ('a0000001-0000-0000-0000-000000000002', 'farmer_suresh', 'pbkdf2:sha256:fakehash_suresh', 'Suresh Deshmukh', 'FARMER', '+919822067890', 'Pune', 'Haveli', 'Manjari', NULL, TRUE),
  ('a0000001-0000-0000-0000-000000000003', 'dr_anita_vet', 'pbkdf2:sha256:fakehash_anita', 'Dr. Anita Kulkarni (B.V.Sc & A.H.)', 'VETERINARIAN', '+919890123456', 'Pune', 'Haveli', 'Hadapsar', 'MAH-VET-2018-4921', TRUE),
  ('a0000001-0000-0000-0000-000000000004', 'admin_dahd', 'pbkdf2:sha256:fakehash_admin', 'State Epizootic Surveillance Officer', 'ADMIN', '+919811122233', 'Pune', 'Central', 'Shivajinagar', NULL, TRUE)
ON CONFLICT (username) DO NOTHING;

-- 2. Insert Animals (Tagged, QR coded, Demographics, Health Status)
INSERT INTO animals (id, animal_id, qr_code_identifier, species, breed, age, gender, owner_id, health_status, latitude, longitude, village, taluka, district)
VALUES
  ('b0000001-0000-0000-0000-000000000001', 'TAG-MH-2026-0041', 'QR-LIVESTOCK-MH-41A8F', 'Cattle', 'Gir', 4.5, 'Female', 'a0000001-0000-0000-0000-000000000001', 'CONFIRMED_SICK', 18.578400, 73.982100, 'Wagholi', 'Haveli', 'Pune'),
  ('b0000001-0000-0000-0000-000000000002', 'TAG-MH-2026-0042', 'QR-LIVESTOCK-MH-42B9C', 'Cattle', 'Sahiwal', 3.0, 'Female', 'a0000001-0000-0000-0000-000000000001', 'HEALTHY', 18.578900, 73.982500, 'Wagholi', 'Haveli', 'Pune'),
  ('b0000001-0000-0000-0000-000000000003', 'TAG-MH-2026-0089', 'QR-LIVESTOCK-MH-89C1D', 'Buffalo', 'Murrah', 5.2, 'Female', 'a0000001-0000-0000-0000-000000000002', 'SUSPECTED', 18.514200, 73.978500, 'Manjari', 'Haveli', 'Pune'),
  ('b0000001-0000-0000-0000-000000000004', 'TAG-MH-2026-0090', 'QR-LIVESTOCK-MH-90D2E', 'Cattle', 'Holstein Friesian', 2.5, 'Female', 'a0000001-0000-0000-0000-000000000002', 'HEALTHY', 18.514800, 73.979100, 'Manjari', 'Haveli', 'Pune')
ON CONFLICT (animal_id) DO NOTHING;

-- 3. Insert Animal Health Records (Physiological Vitals)
INSERT INTO animal_health_records (id, animal_id, recorded_by_id, body_temperature_c, heart_rate_bpm, respiratory_rate_bpm, appetite_score, milk_yield_liters, activity_score, rumination_hours, notes, recorded_at)
VALUES
  ('c0000001-0000-0000-0000-000000000001', 'b0000001-0000-0000-0000-000000000001', 'a0000001-0000-0000-0000-000000000001', 40.6, 88, 38, 0.2, 4.5, 0.2, 2.0, 'Severe fever, visible skin eruptions, acute inappetence.', CURRENT_TIMESTAMP - INTERVAL '3 days'),
  ('c0000001-0000-0000-0000-000000000002', 'b0000001-0000-0000-0000-000000000002', 'a0000001-0000-0000-0000-000000000001', 38.6, 62, 22, 1.0, 16.2, 1.0, 7.5, 'Normal vital signs. Good rumen fill.', CURRENT_TIMESTAMP - INTERVAL '1 day'),
  ('c0000001-0000-0000-0000-000000000003', 'b0000001-0000-0000-0000-000000000003', 'a0000001-0000-0000-0000-000000000002', 39.8, 76, 28, 0.5, 9.0, 0.5, 4.0, 'Mild fever, lameness, slight salivation observed.', CURRENT_TIMESTAMP - INTERVAL '2 days')
ON CONFLICT (id) DO NOTHING;

-- 4. Insert Vaccination Records
INSERT INTO vaccination_records (id, animal_id, vaccine_name, batch_number, administered_date, next_due_date, administered_by_id, status)
VALUES
  ('d0000001-0000-0000-0000-000000000001', 'b0000001-0000-0000-0000-000000000001', 'Lumpy Skin Disease Homologous Neethling', 'LSD-BAT-2025-08', '2025-09-15', '2026-09-15', 'a0000001-0000-0000-0000-000000000003', 'ADMINISTERED'),
  ('d0000001-0000-0000-0000-000000000002', 'b0000001-0000-0000-0000-000000000001', 'Foot-and-Mouth Disease (FMD) Quadrivalent', 'FMD-BAT-2025-11', '2025-11-20', '2026-05-20', 'a0000001-0000-0000-0000-000000000003', 'OVERDUE'),
  ('d0000001-0000-0000-0000-000000000003', 'b0000001-0000-0000-0000-000000000002', 'Lumpy Skin Disease Homologous Neethling', 'LSD-BAT-2025-08', '2025-09-15', '2026-09-15', 'a0000001-0000-0000-0000-000000000003', 'ADMINISTERED')
ON CONFLICT (id) DO NOTHING;

-- 5. Insert Symptom Reports
INSERT INTO symptom_reports (id, health_record_id, reported_by_id, symptoms, onset_days_ago, severity_level, clinical_notes)
VALUES
  ('e0000001-0000-0000-0000-000000000001', 'c0000001-0000-0000-0000-000000000001', 'a0000001-0000-0000-0000-000000000001', '["skin_abnormalities", "fever", "loss_of_appetite", "reduced_milk_production"]'::jsonb, 3, 'SEVERE', 'Firm circumscribed nodules on neck and flank.')
ON CONFLICT (id) DO NOTHING;

-- 6. Insert Image Reports
INSERT INTO image_reports (id, health_record_id, uploaded_by_id, image_url, image_hash_sha256, body_part, quality_check_passed, blur_laplacian_var, brightness_score)
VALUES
  ('f0000001-0000-0000-0000-000000000001', 'c0000001-0000-0000-0000-000000000001', 'a0000001-0000-0000-0000-000000000001', '/uploads/images/lsd_cow_tag41.jpg', 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', 'Flank/Hide', TRUE, 412.5, 128.4)
ON CONFLICT (id) DO NOTHING;

-- 7. Insert AI Predictions (PROBABILISTIC - NEVER STORED AS PERMANENT MEDICAL TRUTH)
INSERT INTO ai_predictions (id, health_record_id, symptom_report_id, image_report_id, prediction_type, predicted_condition, confidence_score, risk_level, risk_score, all_class_probabilities, contributing_symptoms, model_version, is_veterinary_diagnosis, disclaimer)
VALUES
  ('10000001-0000-0000-0000-000000000001', 'c0000001-0000-0000-0000-000000000001', 'e0000001-0000-0000-0000-000000000001', 'f0000001-0000-0000-0000-000000000001', 'MULTIMODAL_FUSION', 'Possible Lumpy Skin Disease', 0.9420, 'HIGH', 94.20, '{"Lumpy Skin Disease": 0.942, "Healthy": 0.005, "Foot-and-Mouth Disease": 0.021, "Mastitis": 0.012, "Bovine Respiratory Disease": 0.010, "Brucellosis": 0.010}'::jsonb, '[{"symptom": "Skin Abnormalities", "contribution": 0.38}, {"symptom": "Fever", "contribution": 0.25}, {"symptom": "Loss of Appetite", "contribution": 0.15}]'::jsonb, 'Fusion-v1.0 (MobileNetV3+XGBoost)', FALSE, 'AI screening and risk triage tool only. Not a veterinary diagnosis. Confirmatory testing required.')
ON CONFLICT (id) DO NOTHING;

-- 8. Insert Disease Clusters (DBSCAN Geospatial Hotspots)
INSERT INTO disease_clusters (id, cluster_code, disease_name, center_latitude, center_longitude, radius_km, case_count, severity, status, district, detected_at, last_case_at)
VALUES
  ('20000001-0000-0000-0000-000000000001', 'CLUSTER-MH-PUN-001', 'Lumpy Skin Disease', 18.578000, 73.982000, 4.20, 5, 'EMERGENCY', 'ACTIVE', 'Pune', CURRENT_TIMESTAMP - INTERVAL '4 days', CURRENT_TIMESTAMP - INTERVAL '1 day')
ON CONFLICT (cluster_code) DO NOTHING;

-- 9. Insert Disease Reports (Case Tracking)
INSERT INTO disease_reports (id, animal_id, health_record_id, ai_prediction_id, reported_disease, reporting_source, latitude, longitude, status, is_quarantine_required, cluster_id, reported_at)
VALUES
  ('30000001-0000-0000-0000-000000000001', 'b0000001-0000-0000-0000-000000000001', 'c0000001-0000-0000-0000-000000000001', '10000001-0000-0000-0000-000000000001', 'Lumpy Skin Disease', 'AI_SENTINEL_SCREENING', 18.578400, 73.982100, 'VERIFIED_POSITIVE', TRUE, '20000001-0000-0000-0000-000000000001', CURRENT_TIMESTAMP - INTERVAL '3 days')
ON CONFLICT (id) DO NOTHING;

-- 10. Insert Veterinarian Reviews (INDEPENDENT CLINICAL ADJUDICATION)
INSERT INTO veterinarian_reviews (id, disease_report_id, veterinarian_id, review_decision, clinical_diagnosis, laboratory_test_type, laboratory_result, treatment_plan, prescribed_medications, quarantine_order_issued, quarantine_duration_days, revisit_date, clinical_notes, reviewed_at)
VALUES
  ('40000001-0000-0000-0000-000000000001', '30000001-0000-0000-0000-000000000001', 'a0000001-0000-0000-0000-000000000003', 'CONFIRMED_POSITIVE', 'Confirmed Lumpy Skin Disease (Moderate nodular cutaneous form)', 'PCR Skin Biopsy', 'POSITIVE', 'Strict isolation from herd. Anti-inflammatory, antibiotic coverage for secondary bacterial complications, fly-repellent wound spray.', 'Meloxicam 0.5mg/kg IM, Enrofloxacin 5mg/kg IM for 5 days, Topical Ivermectin fly repellant spray.', TRUE, 28, CURRENT_DATE + INTERVAL '7 days', 'Clinical presentation corroborates positive PCR. Ring vaccination of surrounding 5km radius advised.', CURRENT_TIMESTAMP - INTERVAL '2 days')
ON CONFLICT (disease_report_id) DO NOTHING;

-- 11. Insert Alerts (Early Warnings)
INSERT INTO alerts (id, recipient_id, alert_type, severity, title, message, related_cluster_id, related_animal_id, is_read, created_at)
VALUES
  ('50000001-0000-0000-0000-000000000001', 'a0000001-0000-0000-0000-000000000001', 'OUTBREAK_EARLY_WARNING', 'CRITICAL', 'EPIDEMIC ALERT: LSD Cluster Detected within 5 km', 'DBSCAN cluster CLUSTER-MH-PUN-001 active in Wagholi/Haveli. 5 positive cases identified. Ensure strict vector control and isolate symptomatic animals immediately.', '20000001-0000-0000-0000-000000000001', 'b0000001-0000-0000-0000-000000000001', FALSE, CURRENT_TIMESTAMP - INTERVAL '3 days'),
  ('50000001-0000-0000-0000-000000000002', 'a0000001-0000-0000-0000-000000000001', 'VACCINATION_OVERDUE', 'MODERATE', 'Vaccination Overdue: Animal TAG-MH-2026-0041', 'Foot-and-Mouth Disease booster was due on May 20, 2026. Schedule paravet appointment.', NULL, 'b0000001-0000-0000-0000-000000000001', TRUE, CURRENT_TIMESTAMP - INTERVAL '5 days'),
  ('50000001-0000-0000-0000-000000000003', 'a0000001-0000-0000-0000-000000000003', 'CASE_TRIAGE_REQUIRED', 'CRITICAL', 'High-Risk AI Screening Requires Clinical Adjudication', 'Animal TAG-MH-2026-0041 flagged with 94.2% LSD probability by Sentinel AI. Please review clinical case and issue order.', NULL, 'b0000001-0000-0000-0000-000000000001', TRUE, CURRENT_TIMESTAMP - INTERVAL '3 days')
ON CONFLICT (id) DO NOTHING;
