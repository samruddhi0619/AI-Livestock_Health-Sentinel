# API Plan & Specifications: AI-Livestock Health Sentinel

**API Standard:** RESTful over HTTPS with JSON Payloads  
**Base URL:** `/api/v1`  
**API Documentation:** Interactive Swagger UI at `/docs`, ReDoc at `/redoc`  
**Authentication:** HTTP Authorization Header with `Bearer <JWT_TOKEN>`  
**Date:** September 2026  

---

## 1. Global Standards, Headers & Error Handling

### Standard Request Headers
```http
Content-Type: application/json
Authorization: Bearer <access_token>
Accept-Language: en, mr;q=0.9
```

### Standard Response Envelope
All non-binary endpoints return standardized JSON payloads:
```json
{
  "success": true,
  "data": { ... },
  "message": "Operation completed successfully",
  "timestamp": "2026-09-03T14:30:00Z"
}
```

### Standard Error Response Format
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "detail": "Body temperature exceeds biological threshold (max 43.0 C).",
    "field": "temperature"
  },
  "timestamp": "2026-09-03T14:30:00Z"
}
```

### HTTP Status Code Conventions
- `200 OK`: Request succeeded.
- `201 Created`: Resource successfully created (e.g., animal, assessment).
- `400 Bad Request`: Validation failure or malformed payload.
- `401 Unauthorized`: Missing, expired, or invalid JWT bearer token.
- `403 Forbidden`: Insufficient role permissions for the endpoint.
- `404 Not Found`: Resource ID does not exist.
- `422 Unprocessable Entity`: Schema constraint failure (Pydantic).
- `500 Internal Server Error`: Unhandled server exception (gracefully trapped).

---

## 2. API Endpoint Inventory by Domain

```
/api/v1
├── /auth              # Identity, registration, tokens
├── /animals           # Herd registry, QR generation, Digital Health Passport
├── /assessments       # Multi-modal AI screening, OpenCV image check, SHAP
├── /cases             # Veterinary triage queue, clinical verification
├── /vaccinations      # Immunization schedules and logs
├── /surveillance      # Geospatial map data, DBSCAN clustering, containment orders
├── /alerts            # Multi-tier notifications, SMS/WhatsApp dispatch simulation
├── /dashboards        # Role-aggregated statistics (Farmer, Vet, Officer, Admin)
├── /admin             # Model parameters, system thresholds, audit trail
├── /telemetry         # IoT smart collar / ear-tag sensor streaming
└── /voice             # Marathi/Hindi voice symptom transcription
```

---

## 3. Domain 1: Authentication & RBAC (`/api/v1/auth`)

### 1.1 `POST /api/v1/auth/register`
- **Description**: Registers a new user account (Farmer, Veterinarian, Officer, Admin). If registering as a Farmer, automatically provisions their primary Farm entity.
- **Access**: Public
- **Request Body**:
```json
{
  "username": "farmer_ramesh",
  "password": "SecurePassword123!",
  "fullname": "Ramesh Patil",
  "role": "FARMER",
  "phone": "+91 9822011223",
  "district": "Pune",
  "taluka": "Haveli",
  "village": "Wadgaon",
  "farm_latitude": 18.5205,
  "farm_longitude": 73.8567
}
```
- **Response `201 Created`**:
```json
{
  "success": true,
  "message": "User and farm registered successfully",
  "data": {
    "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "username": "farmer_ramesh",
    "role": "FARMER"
  }
}
```

### 1.2 `POST /api/v1/auth/login`
- **Description**: Authenticates user credentials and issues a signed JWT access token.
- **Access**: Public
- **Request Body**:
```json
{
  "username": "farmer_ramesh",
  "password": "SecurePassword123!"
}
```
- **Response `200 OK`**:
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 3600,
    "user": {
      "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "username": "farmer_ramesh",
      "fullname": "Ramesh Patil",
      "role": "FARMER",
      "district": "Pune",
      "taluka": "Haveli",
      "village": "Wadgaon"
    }
  }
}
```

### 1.3 `GET /api/v1/auth/me`
- **Description**: Returns the authenticated profile and associated farm details.
- **Access**: Authenticated (`FARMER`, `VETERINARIAN`, `OFFICER`, `ADMIN`)

---

## 4. Domain 2: Animal Inventory & Digital Health Passport (`/api/v1/animals`)

### 2.1 `POST /api/v1/animals`
- **Description**: Registers a new cattle/livestock record. Generates a unique `qr_code_uuid`.
- **Access**: `FARMER`, `ADMIN`
- **Request Body**:
```json
{
  "tag_id": "MH-PUN-0042",
  "species": "Cattle",
  "breed": "Gir",
  "age": 3.5,
  "gender": "Female",
  "health_history": "None",
  "farm_id": "f1e2d3c4-b5a6-7890-1234-567890abcdef"
}
```
- **Response `201 Created`**:
```json
{
  "success": true,
  "data": {
    "id": "e1f2a3b4-5678-90ab-cdef-1234567890ab",
    "tag_id": "MH-PUN-0042",
    "qr_code_uuid": "98765432-abcd-ef01-2345-6789abcdef01",
    "qr_code_image_url": "/api/v1/animals/qr/98765432-abcd-ef01-2345-6789abcdef01/image"
  }
}
```

### 2.2 `GET /api/v1/animals`
- **Description**: Lists cattle. Role-scoped: Farmers see only their own animals; Vets, Officers, and Admins view all animals across their assigned jurisdiction.
- **Access**: Authenticated

### 2.3 `GET /api/v1/animals/{animal_id}/passport`
- **Description**: Returns the complete Digital Animal Health Passport payload including vaccination records, past verified diagnoses, and vital averages.
- **Access**: Authenticated
- **Response `200 OK`**:
```json
{
  "success": true,
  "data": {
    "passport_id": "PASSPORT-MH-PUN-0042",
    "animal": {
      "tag_id": "MH-PUN-0042",
      "species": "Cattle",
      "breed": "Gir",
      "age": 3.5,
      "gender": "Female",
      "farm": {
        "identifier": "MH-PUN-HAV-0012",
        "village": "Wadgaon",
        "taluka": "Haveli",
        "district": "Pune"
      }
    },
    "health_summary": {
      "total_assessments": 4,
      "latest_risk_level": "LOW",
      "last_assessment_date": "2026-08-28T09:15:00Z"
    },
    "vaccination_history": [
      {
        "vaccine_name": "FMD Quadrivalent Vaccine",
        "batch_number": "FMD-2026-B8",
        "date_administered": "2026-03-10",
        "next_due_date": "2026-09-10",
        "status": "UP_TO_DATE"
      }
    ],
    "qr_verification_url": "https://sentinel.gov.in/verify/98765432-abcd-ef01-2345-6789abcdef01"
  }
}
```

### 2.4 `GET /api/v1/animals/{animal_id}/passport/pdf`
- **Description**: Generates a downloadable, printable official PDF Animal Health Card complete with government branding, QR code, and vaccination table.
- **Access**: Authenticated

### 2.5 `GET /api/v1/animals/qr/{qr_uuid}`
- **Description**: Public verification endpoint accessed by field staff scanning the physical ear-tag QR code. Returns instant clearance status (*Verified Clear / Active Outbreak Zone / Treatment Ongoing*).
- **Access**: Public

---

## 5. Domain 3: Multi-Modal Health Assessment & AI (`/api/v1/assessments`)

### 3.1 `POST /api/v1/assessments/image-screening`
- **Description**: Uploads an animal symptom photo (e.g. skin lesion). Executes OpenCV image quality validation (blur, brightness, resolution) and PyTorch visual lesion classification.
- **Access**: `FARMER`, `VETERINARIAN`
- **Request**: Multipart Form Data (`file: UploadFile`)
- **Response `200 OK`**:
```json
{
  "success": true,
  "data": {
    "image_id": "img_7890abcdef",
    "image_url": "/uploads/lesion_20260903_143000.jpg",
    "quality": {
      "passed": true,
      "laplacian_blur_variance": 142.8,
      "mean_brightness": 128.4,
      "resolution": "1080x720"
    },
    "pytorch_visual_analysis": {
      "abnormality_detected": true,
      "target_condition": "Lumpy Skin Disease",
      "confidence": 0.884,
      "lesion_count": 5,
      "affected_area_ratio": 0.082,
      "visual_findings": "Multiple circular cutaneous nodules (5 lesions) identified on dorsal skin area."
    }
  }
}
```

### 3.2 `POST /api/v1/assessments/submit`
- **Description**: Full multi-modal assessment submission. Synthesizes symptom checklist, vitals, PyTorch image findings, and environmental risk into a fused risk score. Calculates SHAP feature attributions and triggers automated veterinary alerts if risk $\ge 40$.
- **Access**: `FARMER`, `VETERINARIAN`
- **Request Body**:
```json
{
  "animal_id": "e1f2a3b4-5678-90ab-cdef-1234567890ab",
  "image_id": "img_7890abcdef",
  "symptoms": ["fever", "skin_abnormalities", "loss_of_appetite", "reduced_milk_production"],
  "temperature": 40.5,
  "appetite": 0.0,
  "milk_yield_liters": 4.5,
  "activity": 0.0,
  "ambient_temp": 31.0,
  "humidity_percent": 82.0,
  "rainfall_mm": 18.0,
  "observations": "Nodules emerged 2 days ago after heavy rain."
}
```
- **Response `201 Created`**:
```json
{
  "success": true,
  "data": {
    "assessment_id": "ass_1234567890",
    "multi_modal_result": {
      "primary_disease": "Lumpy Skin Disease",
      "final_fused_risk_score": 84.5,
      "risk_level": "HIGH",
      "clinical_severity": "SEVERE",
      "component_scores": {
        "symptom_model_score": 88.0,
        "visual_lesion_score": 88.4,
        "vital_anomaly_score": 85.0,
        "environmental_vector_risk": 74.0
      }
    },
    "shap_explainability": [
      { "feature": "Skin Abnormalities", "contribution_percentage": 36.2 },
      { "feature": "High Fever (40.5 C)", "contribution_percentage": 26.8 },
      { "feature": "Milk Production Drop", "contribution_percentage": 18.5 },
      { "feature": "High Humidity (Vector Breeding)", "contribution_percentage": 11.2 }
    ],
    "clinical_guidance": [
      "Isolate the affected cow from herd immediately in a mosquito-screened enclosure.",
      "Apply mild antiseptic fly-repellent ointments to cutaneous nodules.",
      "Do not move cattle outside the farm boundary.",
      "Veterinary officer has been automatically alerted for clinical verification."
    ],
    "escalated_case_id": "case_9876543210"
  }
}
```

---

## 6. Domain 4: Veterinary Triage & Clinical Cases (`/api/v1/cases`)

### 4.1 `GET /api/v1/cases`
- **Description**: Lists suspected and verified livestock disease cases with filtering.
- **Access**: `VETERINARIAN`, `OFFICER`, `ADMIN`
- **Query Parameters**:
  - `status`: `SUSPECTED` | `VERIFIED` | `REJECTED`
  - `disease`: e.g. `Lumpy Skin Disease`
  - `district`: e.g. `Pune`
  - `risk_level`: `HIGH` | `MODERATE`

### 4.2 `PUT /api/v1/cases/{case_id}/verify`
- **Description**: Clinical verification by veterinary officer. Confirms or rejects AI flag, writes formal prescription and hygiene instructions, and dispatches an immediate notification to the farmer.
- **Access**: `VETERINARIAN`, `ADMIN`
- **Request Body**:
```json
{
  "status": "VERIFIED",
  "clinical_diagnosis": "Confirmed Lumpy Skin Disease (Capripoxvirus infection). Generalized skin nodules with secondary bacterial inflammation.",
  "treatment_prescription": "Administer Enrofloxacin 10% (5 mg/kg IM) for 5 days. Meloxicam (0.5 mg/kg IM) for fever. Topical Povidone-Iodine on ruptured nodules.",
  "follow_up_timeline": "7 days (Re-inspect herd for secondary vector spread)"
}
```
- **Response `200 OK`**:
```json
{
  "success": true,
  "message": "Case verified successfully. Treatment plan logged and alert sent to farmer."
}
```

---

## 7. Domain 5: Preventative Healthcare & Vaccination (`/api/v1/vaccinations`)

### 5.1 `POST /api/v1/vaccinations`
- **Description**: Logs an administered vaccination event.
- **Access**: `VETERINARIAN`, `FARMER`, `ADMIN`

### 5.2 `GET /api/v1/vaccinations/upcoming`
- **Description**: Returns cattle due for vaccination or booster doses in the next 30 days.
- **Access**: Authenticated

---

## 8. Domain 6: Geospatial Surveillance & Outbreaks (`/api/v1/surveillance`)

### 6.1 `GET /api/v1/surveillance/map-data`
- **Description**: PostGIS-optimized GeoJSON payload of all active cases, geocoded farms, and active outbreak clusters for instant rendering on React Leaflet maps.
- **Access**: Authenticated
- **Response `200 OK`**:
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": { "type": "Point", "coordinates": [73.8567, 18.5205] },
      "properties": {
        "entity_type": "CASE",
        "case_id": "case_9876543210",
        "disease": "Lumpy Skin Disease",
        "status": "VERIFIED",
        "risk_level": "HIGH",
        "animal_tag": "MH-PUN-0042",
        "village": "Wadgaon"
      }
    },
    {
      "type": "Feature",
      "geometry": {
        "type": "Polygon",
        "coordinates": [[[73.845, 18.515], [73.865, 18.515], [73.865, 18.535], [73.845, 18.535], [73.845, 18.515]]]
      },
      "properties": {
        "entity_type": "OUTBREAK_CLUSTER",
        "disease": "Lumpy Skin Disease",
        "cases_count": 6,
        "radius_km": 1.25,
        "affected_farms_count": 2,
        "risk_level": "HIGH",
        "status": "POTENTIAL DISEASE CLUSTER"
      }
    }
  ]
}
```

### 6.2 `POST /api/v1/surveillance/detect-clusters`
- **Description**: Executes DBSCAN clustering over cases from the last 14 days. Updates `outbreak_clusters` and triggers multi-tier outbreak warnings.
- **Access**: `OFFICER`, `ADMIN`
- **Request Body (Optional overrides)**:
```json
{
  "eps_km": 5.0,
  "min_cases": 3,
  "time_window_days": 14
}
```

### 6.3 `POST /api/v1/surveillance/containment-notice/{cluster_id}`
- **Description**: Generates an official printable government Epidemic Containment Circular / Movement Restriction Notice for police checkpoints and dairy collection centers.
- **Access**: `OFFICER`, `ADMIN`

---

## 9. Domain 7: Alerts & Notifications (`/api/v1/alerts`)

### 9.1 `GET /api/v1/alerts`
- **Description**: Retrieves active alerts and notifications for the authenticated user.
- **Access**: Authenticated

### 9.2 `POST /api/v1/alerts/simulate-dispatch`
- **Description**: Simulates the transmission of outbound SMS and WhatsApp alert payloads to farmers residing in an outbreak containment zone.
- **Access**: `OFFICER`, `ADMIN`
- **Response `200 OK`**:
```json
{
  "success": true,
  "data": {
    "dispatched_count": 14,
    "channel": "SMS_WHATSAPP_GATEWAY",
    "sample_message": "ALERT (Dept of Animal Husbandry): Lumpy Skin Disease cluster detected within 2km of Wadgaon. Restrict cattle movement and inspect for skin nodules. Helpline: 1800-123-4567."
  }
}
```

---

## 10. Domain 8: Dashboards (`/api/v1/dashboards`)

- `GET /api/v1/dashboards/farmer`: Total cattle, pending sync records, upcoming vaccinations, active health alerts.
- `GET /api/v1/dashboards/veterinarian`: Unreviewed triage queue count, high-risk cases breakdown, regional clusters.
- `GET /api/v1/dashboards/officer`: Statewide animal and farm totals, suspected vs. verified metrics, 7-day epidemic curve, disease prevalence distribution, taluka breakdown.
- `GET /api/v1/dashboards/admin`: System accounts count, ML model accuracy metrics, live system config thresholds, audit trail.

---

## 11. Domain 9: Administrator Configuration (`/api/v1/admin`)

- `GET /api/v1/admin/config`: Retrieves dynamic risk thresholds and DBSCAN clustering settings.
- `PUT /api/v1/admin/config`: Updates risk thresholds (`low_risk_threshold`, `high_risk_threshold`, `dbscan_eps_km`, `dbscan_min_cases`, `env_weights`).
- `GET /api/v1/admin/audit-logs`: Retrieves immutable security audit log entries.
- `GET /api/v1/admin/ml-metrics`: Returns benchmark performance metrics (Accuracy, Precision, Recall, F1, ROC-AUC) for all active models.

---

## 12. Domain 10: IoT Vitals Telemetry Simulator (`/api/v1/telemetry`)

### 12.1 `POST /api/v1/telemetry/stream`
- **Description**: Ingests high-frequency vitals telemetry from simulated smart collar / ear-tag hardware.
- **Access**: Authenticated / Device API Key
- **Request Body**:
```json
{
  "animal_tag": "MH-PUN-0042",
  "timestamp": "2026-09-03T14:35:00Z",
  "rectal_temp_c": 40.8,
  "rumination_minutes_daily": 140,
  "step_count": 820
}
```
- **Response `200 OK`**:
```json
{
  "success": true,
  "anomaly_flag": true,
  "alert_triggered": "Sudden rumination drop (>60%) and fever detected."
}
```

---

## 13. Domain 11: Voice & Natural Language (`/api/v1/voice`)

### 13.1 `POST /api/v1/voice/transcribe-symptoms`
- **Description**: Receives rural farmer voice audio notes (WebM/WAV) spoken in Marathi, Hindi, or English, transcribes medical vernacular, and maps spoken phrases to structured symptom checklist keys.
- **Access**: `FARMER`, `VETERINARIAN`
