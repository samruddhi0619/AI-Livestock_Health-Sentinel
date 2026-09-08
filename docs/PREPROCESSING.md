# Data Preprocessing Documentation: AI-Livestock Health Sentinel

**Project:** AI-Livestock Health Sentinel (SIH26128)  
**Pipeline Location:** `ml/data_preprocessing/`  
**Processed Data Location:** `datasets/processed/`  
**Date:** September 2026  

---

## 1. Preprocessing Philosophy & Architecture

To support robust multi-modal machine learning across computer vision, tabular symptoms, physiological telemetry, and bioclimatic risk prediction, all 7 datasets are preprocessed through dedicated, reproducible pipelines.

```
                      RAW ARCHIVES (datasets/*.zip) [UNTOUCHED]
                                          │
                                          ▼
                      ml/data_preprocessing/
 ┌────────────────────────────────────────┬────────────────────────────────────────┐
 │            IMAGE PIPELINES             │            TABULAR PIPELINES           │
 │  01: Whole-Cow LSD Screening           │  03: LSD Environmental (Leakage Free)  │
 │  02: FMD Lesion Object Detection       │  05: Symptom Disease (Fahrenheit -> C) │
 │  04: Dermoscopic Skin Lesion Patches   │  06: Global Cattle Vitals (250k rows)  │
 │                                        │  07: Clinical Symptom Ontology Map     │
 └────────────────────────────────────────┴────────────────────────────────────────┘
                                          │
                                          ▼
                   datasets/processed/ [SEPARATELY STORED]
 ┌───────────────────┬───────────────────┬───────────────────┬───────────────────┐
 │ Train (70%)       │ Val (15%)         │ Test (15%)        │ Metadata & Scalers│
 │ (Augmented/Scaled)│ (Unaugmented/Raw) │ (Unaugmented/Raw) │ JSON/CSV params   │
 └───────────────────┴───────────────────┴───────────────────┴───────────────────┘
```

### Core Anti-Leakage & Governance Rules

1. **Preservation of Raw Archives:** Original zip files in `datasets/` are treated as strictly immutable and read-only. No raw file is overwritten, modified, or re-compressed.
2. **Train-Only Augmentation:** For image datasets, spatial rotations, color jitter, and horizontal reflections are applied **only** to the training split. Validation and testing sets are strictly unaugmented to guarantee honest, uninflated evaluation.
3. **Scaler Fitting Isolation:** For tabular datasets, all scalers (`StandardScaler`) and label encoders are fitted **strictly on the training split**. Validation and test partitions are transformed using the pre-fitted parameters to prevent distribution leakage.
4. **Target Leakage Elimination:** In `03_LSD_Environmental_Geospatial_Data.zip`, variables that are 100% correlated with positive outbreak labels (`region`, `country`, `reportingDate`) are explicitly purged prior to feature matrix construction.
5. **Slot-Order Invariance:** In `05_Cattle_Health_Feeding_Records.zip`, separate symptom columns (`Symptom 1`, `Symptom 2`, `Symptom 3`) are mapped to a unified multi-hot binary bag-of-symptoms representation, removing artificial column-order bias.
6. **Physical Unit Standardization:** Rectal temperatures in `05_Cattle_Health_Feeding_Records.zip` are converted from Fahrenheit to Celsius ($T_C = (T_F - 32) \times \frac{5}{9}$) to align with clinical veterinary standards.

---

## 2. Summary of Preprocessing Pipelines

| Dataset Pipeline | Raw Input | Clean Samples | Output Split Sizes | Key Transformations | Output Directory |
|---|---|:---:|:---:|---|---|
| **01_lsd_images** | `01_LSD_vs_Healthy_Cattle_Images.zip` | 935 images (1 dup removed) | Train: 654<br>Val: 140<br>Test: 141 | Palette $\to$ RGB, Lanczos resize to $224 \times 224$, train-only flips/jitter | `datasets/processed/01_lsd_images/` |
| **02_fmd_detection** | `02_FMD_Cattle_Image_Detection.zip` | 80 images (81 bboxes) | Train: 56<br>Val: 16<br>Test: 8 | BBox coordinates bounds validation, sanitization of split COCO annotations | `datasets/processed/02_fmd_detection/` |
| **03_environmental** | `03_LSD_Environmental_Geospatial_Data.zip` | 24,803 rows | Train: 17,362<br>Val: 3,720<br>Test: 3,721 | **Purged target leakage columns**, one-hot land cover, StandardScaler on continuous bioclimatic features | `datasets/processed/03_environmental/` |
| **04_skin_images** | `04_LSD_vs_Normal_Skin_Images.zip` | 1,019 images (5 dups removed) | Train: 713<br>Val: 153<br>Test: 153 | RGBA $\to$ RGB strip, standardized $256 \times 256$ crop, train-only rotational/photometric augmentation | `datasets/processed/04_skin_images/` |
| **05_symptoms** | `05_Cattle_Health_Feeding_Records.zip` | 43,778 rows | Train: 30,644<br>Val: 6,567<br>Test: 6,567 | Fahrenheit $\to$ Celsius conversion, 24-symptom multi-hot bag-of-words encoding, StandardScaler on Age and Temp | `datasets/processed/05_symptoms/` |
| **06_disease_telemetry** | `06_Cattle_Disease_and_Health_Records.zip` | 250,000 rows | Train: 175,000<br>Val: 37,500<br>Test: 37,500 | Purged ID/Date tokens, one-hot 40 breeds, 45-class target encoder, 17 scaled vitals, exported 137k healthy vitals baseline | `datasets/processed/06_disease_telemetry/` |
| **07_symptom_dictionary** | `07_Animal_Symptoms_Disease_Prediction.zip` | 421 rows (10 dups removed) | 66 cattle clinical profiles | String temperature regex cleanup (`39.5C` $\to$ 39.5), synonym unification, exported JSON clinical ontology | `datasets/processed/07_symptom_dictionary/` |

---

## 3. Detailed Step-by-Step Pipeline Specifications

### Pipeline 01: Whole-Cow LSD Visual Screening (`preprocess_01_lsd_images.py`)

- **Input:** `datasets/01_LSD_vs_Healthy_Cattle_Images.zip`
- **Output:** `datasets/processed/01_lsd_images/`
- **Inspection & Integrity Checks:**
  - Decoded 936 candidate images via PIL `Image.verify()`.
  - Identified and removed 1 content-identical MD5 hash duplicate (`imgs204.jpg`).
  - Identified 4 images in 8-bit palette mode (`P`) and converted them to standard 3-channel `RGB`.
- **Target Resizing:**
  - High-quality Lanczos resampling to $224 \times 224$ pixels (standard convolutional receptive field).
- **Stratified Partitioning:**
  - Stratified 70% / 15% / 15% split preserving exact class ratios (`healthycows`: 55.08%, `lumpycows`: 44.92%).
  - Train: 654 images (`healthycows`: 360, `lumpycows`: 294)
  - Validation: 140 images (`healthycows`: 77, `lumpycows`: 63)
  - Testing: 141 images (`healthycows`: 78, `lumpycows`: 63)
- **Train-Only Augmentation:**
  - Horizontal mirror flip ($p = 0.5$).
  - Random slight rotation ($\pm 10^\circ$, bicubic interpolation).
  - Photometric jitter (Brightness: $0.85 - 1.15$, Contrast: $0.85 - 1.15$).
  - Validation and Test splits are saved strictly unaugmented.
- **Generated Artifacts:**
  - `train/{healthycows, lumpycows}/`
  - `val/{healthycows, lumpycows}/`
  - `test/{healthycows, lumpycows}/`
  - `metadata.csv` (filename, class, split, original width/height, MD5 hash)
  - `summary.json`

---

### Pipeline 02: FMD Lesion Object Detection (`preprocess_02_fmd_detection.py`)

- **Input:** `datasets/02_FMD_Cattle_Image_Detection.zip`
- **Output:** `datasets/processed/02_fmd_detection/`
- **Integrity Validation:**
  - Validated 80 JPEG images across Roboflow splits (`train`: 56, `valid`: 16, `test`: 8).
  - Checked 81 bounding boxes for non-zero positive dimensions ($w > 0, h > 0$) and coordinate boundaries within image bounds.
- **Color Normalization:**
  - Verified all 80 images decode cleanly as 3-channel RGB.
- **Split Normalization:**
  - Standardized directory naming: `valid` $\to$ `val`.
  - Re-exported sanitized COCO format JSON files: `train/_annotations.coco.json`, `val/_annotations.coco.json`, `test/_annotations.coco.json`.
- **Generated Artifacts:**
  - `train/` (56 images, 57 bounding boxes)
  - `val/` (16 images, 16 bounding boxes)
  - `test/` (8 images, 8 bounding boxes)
  - `summary.json`

---

### Pipeline 03: LSD Environmental & Geospatial Risk (`preprocess_03_environmental.py`)

- **Input:** `datasets/03_LSD_Environmental_Geospatial_Data.zip` (`Lumpy skin disease data.csv`)
- **Output:** `datasets/processed/03_environmental/`
- **Target Leakage Remediation:**
  - `region`, `country`, and `reportingDate` are 100% missing for negative labels (`lumpy == 0`) and present only for positive outbreak reports (`lumpy == 1`).
  - **Action:** Permanently purged `region`, `country`, and `reportingDate` from the feature matrix.
- **Categorical Feature Encoding:**
  - `dominant_land_cover` (indices 1 to 12) encoded via one-hot dummy variables with reference drop (`drop_first=True`), expanding into 11 binary indicators.
- **Stratified Partitioning (70/15/15):**
  - Total records: 24,803 (Absence: 21,764, Presence: 3,039)
  - Train: 17,362 rows (Absence: 15,235, Presence: 2,127)
  - Validation: 3,720 rows (Absence: 3,264, Presence: 456)
  - Testing: 3,721 rows (Absence: 3,265, Presence: 456)
- **Feature Scaling:**
  - Continuous climatic predictors (`cld`, `dtr`, `frs`, `pet`, `pre`, `tmn`, `tmp`, `tmx`, `vap`, `wet`) and livestock densities (`X5_Ct_2010_Da`, `X5_Bf_2010_Da`) standardized using `StandardScaler` fitted **strictly on the 17,362 training rows**.
  - Validation and testing rows normalized using pre-fitted training means and standard deviations.
- **Generated Artifacts:**
  - `train.csv` (17,362 rows $\times$ 27 columns)
  - `val.csv` (3,720 rows $\times$ 27 columns)
  - `test.csv` (3,721 rows $\times$ 27 columns)
  - `scaler_params.json` (fitted means and scales for real-time inference)
  - `summary.json`

---

### Pipeline 04: Dermoscopic Skin Lesion Patches (`preprocess_04_skin_images.py`)

- **Input:** `datasets/04_LSD_vs_Normal_Skin_Images.zip`
- **Output:** `datasets/processed/04_skin_images/`
- **Inspection & Deduplication:**
  - Screened 1,024 candidate skin patch images.
  - Removed 5 content-identical duplicates based on byte hash. Clean images: 1,019.
  - Stripped 4th alpha channel from 13 RGBA PNGs, standardizing all files to 3-channel RGB.
- **Standardized Sizing:**
  - All images confirmed as $256 \times 256$ square crops.
- **Stratified Split (70/15/15):**
  - Total clean: 1,019 images (`Normal_Skin`: 697, `Lumpy_Skin`: 322)
  - Train: 713 images (`Normal_Skin`: 488, `Lumpy_Skin`: 225)
  - Validation: 153 images (`Normal_Skin`: 104, `Lumpy_Skin`: 49)
  - Testing: 153 images (`Normal_Skin`: 105, `Lumpy_Skin`: 48)
- **Train-Only Augmentation:**
  - Random horizontal and vertical flips ($p = 0.5$, dermatological patches are rotationally invariant).
  - Random orthogonal rotation ($0^\circ, 90^\circ, 180^\circ, 270^\circ$).
  - Mild contrast and brightness scaling ($0.9 - 1.1$).
  - Validation and test splits preserved in pristine unaugmented state.
- **Generated Artifacts:**
  - `train/{Normal_Skin, Lumpy_Skin}/`
  - `val/{Normal_Skin, Lumpy_Skin}/`
  - `test/{Normal_Skin, Lumpy_Skin}/`
  - `metadata.csv`
  - `summary.json`

---

### Pipeline 05: Cattle Health Feeding & Symptoms (`preprocess_05_symptoms.py`)

- **Input:** `datasets/05_Cattle_Health_Feeding_Records.zip` (`animal_disease_dataset.csv`)
- **Output:** `datasets/processed/05_symptoms/`
- **Temperature Standardization:**
  - Raw `Temperature` is recorded in Fahrenheit ($100.5^\circ\text{F} - 105.0^\circ\text{F}$).
  - Converted to Celsius ($37.78^\circ\text{C} - 40.56^\circ\text{C}$):
    $$\text{Temperature\_C} = (\text{Temperature} - 32) \times \frac{5}{9}$$
- **Permutation-Invariant Multi-Hot Symptom Encoding:**
  - `Symptom 1`, `Symptom 2`, and `Symptom 3` draw from 24 distinct clinical terms.
  - Rather than treating slot positions as independent features, encoded each symptom as a binary column (`sym_blisters_on_mouth`, `sym_painless_lumps`, `sym_swelling_in_limb`, etc.). A cow exhibiting painless lumps in any slot receives `sym_painless_lumps = 1`.
- **Target & Species Encodings:**
  - `Animal` one-hot encoded (`animal_cow`, `animal_buffalo`, `animal_sheep`, `animal_goat`).
  - Target `Disease` encoded to integers (`anthrax: 0`, `blackleg: 1`, `foot and mouth: 2`, `lumpy virus: 3`, `pneumonia: 4`).
- **Partitioning & Scaling:**
  - 70% train (30,644 rows), 15% val (6,567 rows), 15% test (6,567 rows).
  - Continuous features (`Age`, `Temperature_C`) scaled via `StandardScaler` fitted on train only.
- **Generated Artifacts:**
  - `train.csv` (30,644 rows $\times$ 31 columns)
  - `val.csv` (6,567 rows $\times$ 31 columns)
  - `test.csv` (6,567 rows $\times$ 31 columns)
  - `encoder_metadata.json` (symptom mapping, disease index, scaler parameters)

---

### Pipeline 06: Global Cattle Disease & Vitals Telemetry (`preprocess_06_disease_telemetry.py`)

- **Input:** `datasets/06_Cattle_Disease_and_Health_Records.zip` (`global_cattle_disease_detection_dataset.csv`)
- **Output:** `datasets/processed/06_disease_telemetry/`
- **Anti-Leakage Identifier Drop:**
  - Dropped `Cattle_ID`, `Farm_ID`, and `Date` to prevent artificial memorization of specific herds or time stamps.
- **Feature Encodings:**
  - One-hot encoded 8 categorical features: `Breed` (40 breeds), `Region`, `Country`, `Climate_Zone`, `Management_System`, `Lactation_Stage`, `Feed_Type`, `Season`, yielding 108 numeric feature columns.
  - Label-encoded target `Disease_Status` across all 45 classes (`Healthy: 0`, `Lumpy_Skin_Disease: 24`, `Foot_and_Mouth: 16`, etc.).
- **Continuous Vitals Normalization:**
  - 17 physiological vitals and production indicators (`Body_Temperature_C`, `Heart_Rate_bpm`, `Respiratory_Rate`, `Rumination_Time_hrs`, `Resting_Hours`, `Milk_Yield_L`, etc.) scaled using `StandardScaler` fitted strictly on the 175,000 training rows.
- **Partitioning (70/15/15):**
  - Train: 175,000 rows
  - Validation: 37,500 rows
  - Testing: 37,500 rows
- **Healthy Vitals Anomaly Baseline Export:**
  - Filtered all 137,419 healthy cattle rows and exported their raw vitals (`Body_Temperature_C`, `Heart_Rate_bpm`, `Respiratory_Rate`, `Rumination_Time_hrs`, `Milk_Yield_L`) as `healthy_vitals_baseline.csv` to train the unsupervised Isolation Forest anomaly model.
- **Generated Artifacts:**
  - `train.csv` (175,000 rows $\times$ 109 columns)
  - `val.csv` (37,500 rows $\times$ 109 columns)
  - `test.csv` (37,500 rows $\times$ 109 columns)
  - `train_sample_10k.csv` (10,000-row lightweight preview)
  - `healthy_vitals_baseline.csv` (137,419 rows)
  - `metadata.json`

---

### Pipeline 07: Clinical Symptom Ontology & Vocabulary (`preprocess_07_symptom_dictionary.py`)

- **Input:** `datasets/07_Animal_Symptoms_Disease_Prediction.zip` (`cleaned_animal_disease_prediction.csv`)
- **Output:** `datasets/processed/07_symptom_dictionary/`
- **Deduplication & Sanitization:**
  - Removed 10 duplicate rows.
  - Sanitized corrupted non-ASCII temperature strings (`'39.5C'` $\to 39.5$).
- **Synonym Normalization:**
  - Unified synonymous terms (`Appetite Loss` $\to$ `loss_of_appetite`, `Reduced Milk Production` $\to$ `reduced_milk_production`, `Labored Breathing` $\to$ `breathing_difficulty`).
- **Ontology Extraction:**
  - Extracted standardized symptom-disease relationships across 20 cattle diseases into a clean JSON ontology mapping.
- **Generated Artifacts:**
  - `bovine_symptom_ontology.json`
  - `cleaned_cattle_records.csv`
  - `summary.json`

---

## 4. Execution Instructions

### Run All Pipelines Sequentially
```bash
python ml/data_preprocessing/run_all_preprocessing.py
```

### Run an Individual Pipeline
```bash
python ml/data_preprocessing/preprocess_01_lsd_images.py
python ml/data_preprocessing/preprocess_03_environmental.py
python ml/data_preprocessing/preprocess_05_symptoms.py
python ml/data_preprocessing/preprocess_06_disease_telemetry.py
```

All processed outputs will be saved in `datasets/processed/` with complete JSON metadata and parameters ready for model training.
